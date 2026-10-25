import { h, heading, button } from './dom.js';
import { icon } from './icons.js';
import { initI18n, t, getLanguage, setLanguage } from './i18n.js';
import { setupScreen, tvMenu } from './screens/setup.js';
import { connectScreen } from './screens/connect.js';

const root = document.getElementById('app');
const header = document.getElementById('header');
const token = document.querySelector('meta[name=cleanyourtv-token]').content;
const state = {
  screen: 'start', brand: 'google', prepared: false, connection: 'idle', candidates: null,
  manualIP: '', ip: '', lists: [], matched: [], list: null, device: null, restore: false,
  busy: false, error: null, output: '', result: null, homeKey: false, keepHome: false,
};
let lastScreen;
let currentJob;

async function api(path, body) {
  const response = await fetch(`/api/${path}`, body === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'x-cleanyourtv-token': token }, body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error);
  return data;
}

function render() {
  const focused = document.activeElement?.id;
  document.title = t('app.name');
  header.replaceChildren(h('div', { className: 'header-brand' }, h('span', { className: 'wordmark' }, t('app.name'))),
    h('div', { className: 'header-actions' }, h('div', { className: 'language', role: 'group', 'aria-label': t('language.label') },
      ['ms', 'en'].map(code => button(t(`language.${code}`), () => { setLanguage(code); render(); }, {
        id: `language-${code}`, 'aria-pressed': String(getLanguage() === code),
      }))), button(t('common.exit'), actions.exit, { id: 'exit', disabled: state.busy })));
  const flow = ['setup', 'connect', 'choose', 'progress', 'done'];
  const step = state.screen === 'confirm' ? 2 : state.screen === 'launcher' ? 4 : flow.indexOf(state.screen);
  const indicator = step >= 0 && h('nav', { 'aria-label': t('flow.label') }, h('ol', { className: 'steps' },
    ['setup', 'connect', 'choose', 'clean', 'done'].map((key, i) => h('li', {
      'aria-current': i === step ? 'step' : null, className: i < step ? 'complete' : '',
    }, t(`flow.${key}`)))));
  const screen = screens[state.screen]();
  root.replaceChildren(...[indicator, state.error && h('div', { className: 'error-card stack', role: 'alert' },
    h('p', {}, t(`error.${state.error}`))), screen].filter(Boolean));
  if (lastScreen !== state.screen) {
    root.querySelector('h1')?.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: 'instant' });
  } else if (focused) document.getElementById(focused)?.focus({ preventScroll: true });
  lastScreen = state.screen;
}

function chooseScreen() {
  const matched = state.lists.filter(item => state.matched.includes(item.name));
  const brands = [...new Set(state.lists.map(item => item.brand))].sort();
  const pick = item => button(item.tv, () => { state.list = item; render(); }, {
    'aria-pressed': String(state.list?.name === item.name), id: `list-${item.name}`,
  });
  return h('section', { className: 'screen' }, heading(t(state.restore ? 'restore.title' : 'choose.title'), t('choose.note')),
    state.device && h('p', {}, `${state.device['ro.product.manufacturer']} ${state.device['ro.product.model']} · Android ${state.device['ro.build.version.release']}`),
    state.restore && h('p', {}, t('restore.pick')),
    matched.length > 0 && h('div', { className: 'card stack' }, h('h2', {}, t('choose.matched')), matched.map(pick)),
    h('div', { className: 'stack' }, h('h2', {}, t('choose.browse')), brands.map(brand => h('details', { className: 'category' },
      h('summary', {}, brand), h('div', { className: 'app-list' }, state.lists.filter(item => item.brand === brand).map(pick))))),
    state.list && h('div', { className: 'card stack' }, h('h2', {}, state.list.tv),
      h('p', { className: 'small' }, state.list.name),
      h('pre', { className: 'list-header' }, state.list.header),
      state.list.packages.map(entry => h('div', { className: 'app-copy package-copy' },
        h('code', {}, entry.package), entry.comment && h('p', { className: 'small' }, entry.comment)))),
    h('div', { className: 'actions' }, button(t('common.back'), () => actions.go('connect')),
      button(t('common.next'), () => actions.go('confirm'), { primary: true, disabled: !state.list, id: 'choose-next' })));
}

function confirmScreen() {
  return h('section', { className: 'screen' }, heading(t(state.restore ? 'restore.title' : 'confirm.title'), state.list.tv),
    h('div', { className: 'card stack' }, h('p', {}, t('confirm.count', { n: state.list.packages.length })),
      h('p', {}, t(state.restore ? 'restore.explain' : 'confirm.body')),
      h('h2', {}, t('confirm.comments')),
      state.list.packages.filter(entry => entry.comment).map(entry => h('div', { className: 'app-copy package-copy' },
        h('code', {}, entry.package), h('p', {}, entry.comment)))),
    h('div', { className: 'actions' }, button(t('common.back'), () => actions.go('choose')),
      button(t(state.restore ? 'restore.run' : 'confirm.run'), () => actions.run(state.restore ? 'restore' : 'disable'), { primary: true, id: 'confirm-run' })));
}

function progressScreen() {
  return h('section', { className: 'screen' }, heading(t('progress.title'), t('progress.wait')),
    h('p', { role: 'status' }, h('span', { className: 'spinner', 'aria-hidden': 'true' }), t('common.loading')),
    h('pre', { id: 'job-output', className: 'card job-output', role: 'log', 'aria-live': 'polite', 'aria-label': t('progress.output') }, state.output),
    !state.busy && currentJob && button(t('common.retry'), async () => {
      state.busy = true; state.error = null; render();
      try { finishJob(await pollJob(currentJob)); }
      catch { state.busy = false; state.error = 'SCRIPT'; render(); }
    }, { id: 'progress-retry' }));
}

function doneScreen() {
  const result = state.result;
  return h('section', { className: 'screen' }, heading(t(result.code === 0 ? 'done.title' : 'done.failed'), t('done.review')),
    result.summary && h('div', { className: 'card stack' }, ['disabled', 'enabled', 'skipped', 'absent'].map(key =>
      h('p', {}, t(`done.${key}`, { n: result.summary[key] })))),
    result.operation === 'restore' && h('p', {}, t('restore.launcher'), tvMenu('settings'), ' → ', tvMenu('apps'), '.'),
    h('pre', { className: 'card job-output' }, result.output),
    result.operation === 'disable' && result.code === 0 && button(t('launcher.offer'), () => actions.go('launcher'), { primary: true, id: 'launcher-offer' }),
    result.unknownHome && h('div', { className: 'card stack' }, h('p', {}, t('launcher.unknown')),
      h('label', { className: 'check-label', for: 'keep-home' }, h('input', { id: 'keep-home', type: 'checkbox', checked: state.keepHome,
        onchange: event => { state.keepHome = event.target.checked; render(); } }), t('launcher.keepHome')),
      button(t('common.retry'), () => actions.run('launcher'), { primary: true, disabled: !state.keepHome, id: 'launcher-retry' })),
    button(t('common.start'), () => actions.go('start'), { id: 'done-start' }));
}

function launcherScreen() {
  const xiaomi = /xiaomi/i.test(`${state.device?.['ro.product.manufacturer']} ${state.device?.['ro.product.brand']}`);
  return h('section', { className: 'screen' }, heading(t('launcher.title'), t('launcher.intro')),
    h('div', { className: 'card stack' }, h('p', {}, t('launcher.body')),
      xiaomi && h('label', { className: 'check-label', for: 'home-key' }, h('input', { id: 'home-key', type: 'checkbox', checked: state.homeKey,
        onchange: event => { state.homeKey = event.target.checked; } }), t('launcher.homeKey'))),
    h('div', { className: 'actions' }, button(t('common.skip'), () => actions.go('start'), { id: 'launcher-skip' }),
      button(t('launcher.install'), () => actions.run('launcher'), { primary: true, id: 'launcher-install' })));
}

const screens = {
  start: () => h('section', { className: 'screen' }, h('div', { className: 'card stack' }, icon('tv', 'hero-icon'),
    heading(t('start.title'), t('app.promise')),
    button(t('start.begin'), () => { state.restore = false; actions.go('setup'); }, { primary: true, id: 'begin' }),
    button(t('restore.title'), () => { state.restore = true; actions.go('setup'); }, { className: 'link', id: 'restore-start' }))),
  setup: () => setupScreen(state, actions), connect: () => connectScreen(state, actions),
  choose: chooseScreen, confirm: confirmScreen, progress: progressScreen, done: doneScreen, launcher: launcherScreen,
  closed: () => h('section', { className: 'screen' }, heading(t('exit.title'), t('exit.body'))),
};

async function followJob(operation, body) {
  const { jobId } = await api(operation, body);
  currentJob = jobId;
  return pollJob(jobId);
}

async function pollJob(jobId) {
  for (;;) {
    const job = await api(`jobs/${jobId}`);
    state.output = job.output;
    const log = document.getElementById('job-output');
    if (log) log.textContent = job.output;
    if (job.done) return job;
    await new Promise(resolve => setTimeout(resolve, 400));
  }
}

function finishJob(job) {
  state.error = job.error ?? null;
  if (job.operation === 'discover') { state.candidates = job.candidates ?? []; state.screen = 'connect'; }
  else if (job.operation === 'connect') {
    if (job.code !== 0) { state.error = job.error ?? 'PROBE'; state.screen = 'connect'; }
    else {
      state.ip = job.ip; state.device = job.device; state.matched = job.matched;
      state.list = state.restore ? state.lists.find(item => item.name === job.lastList) ?? null : null;
      state.homeKey = false; state.keepHome = false; state.screen = 'choose';
    }
  } else { state.result = job; state.screen = 'done'; }
  state.busy = false; state.connection = 'idle'; render();
}

const actions = {
  render,
  go(screen) {
    if (state.busy) return;
    state.screen = screen; state.error = null; state.connection = 'idle';
    if (screen === 'start') { state.keepHome = false; state.homeKey = false; }
    render();
  },
  async discover() {
    if (state.busy) return;
    state.busy = true; state.error = null; state.connection = 'scanning'; render();
    try { finishJob(await followJob('discover', {})); }
    catch { state.error = 'SCRIPT'; }
    state.busy = false; state.connection = 'idle'; render();
  },
  async connect(candidate) {
    if (state.busy) return;
    state.busy = true; state.connection = 'unauthorized'; state.error = null; render();
    try {
      finishJob(await followJob('connect', { ip: candidate.ip, restore: state.restore }));
    } catch { state.error = 'INPUT'; }
    state.busy = false; state.connection = 'idle'; render();
  },
  async run(operation) {
    if (state.busy) return;
    state.busy = true; state.screen = 'progress'; state.error = null; state.output = ''; render();
    currentJob = null;
    try {
      finishJob(await followJob(operation, { ip: state.ip, list: state.list?.name, homeKey: state.homeKey, keepHome: state.keepHome }));
    } catch { state.error = 'SCRIPT'; }
    state.busy = false; render();
  },
  async exit() {
    if (state.busy) return;
    try { await api('exit', {}); state.screen = 'closed'; render(); }
    catch { state.error = 'SCRIPT'; render(); }
  },
};

try {
  await initI18n();
  const data = await api('state');
  state.lists = data.lists; state.manualIP = data.ip;
  if (data.job) {
    currentJob = data.job.id; state.ip = data.job.ip; state.restore = data.job.restore;
    state.list = state.lists.find(item => item.name === data.job.list); state.device = data.device;
    state.output = data.job.output; state.busy = true;
    state.screen = ['connect', 'discover'].includes(data.job.operation) ? 'connect' : 'progress';
    state.connection = data.job.operation === 'connect' ? 'unauthorized' : 'scanning'; render();
    try { finishJob(await pollJob(currentJob)); }
    catch { state.busy = false; state.error = 'SCRIPT'; render(); }
  } else render();
} catch {
  root.replaceChildren(h('p', { role: 'alert' }, t('error.I18N_UNAVAILABLE')));
}
