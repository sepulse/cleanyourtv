import { h, heading, button } from '../dom.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';

const brands = ['google', 'xiaomi', 'tcl', 'sony', 'hisense', 'other'];
export function tvMenu(name) {
  return h('span', { className: 'tv-menu' }, h('strong', {}, t(`tvMenu.${name}.ms`)),
    t('tvMenu.separator'), h('em', {}, t(`tvMenu.${name}.en`)), t('tvMenu.end'));
}
export function setupScreen(state, actions) {
  const select = brand => { state.brand = brand; state.prepared = false; actions.render(); };
  const branch = state.brand === 'xiaomi' || state.brand === 'hisense' ? 'devicePreferences' : 'system';
  const path = (...names) => names.flatMap((name, i) => i ? [t('setup.then'), tvMenu(name)] : [tvMenu(name)]);
  return h('section', { className: 'screen' }, heading(t('setup.title'), t('setup.intro')),
    h('div', { className: 'brand-tabs', role: 'tablist', 'aria-label': t('setup.brands') }, brands.map((brand, i) =>
      button(t(`brand.${brand}`), () => select(brand), { role: 'tab', id: `brand-${brand}`, 'aria-controls': 'setup-guide',
        'aria-selected': String(brand === state.brand), tabindex: brand === state.brand ? '0' : '-1',
        onkeydown: event => {
          let next;
          if (event.key === 'ArrowRight') next = (i + 1) % brands.length;
          if (event.key === 'ArrowLeft') next = (i + brands.length - 1) % brands.length;
          if (event.key === 'Home') next = 0;
          if (event.key === 'End') next = brands.length - 1;
          if (next !== undefined) { event.preventDefault(); select(brands[next]); document.getElementById(`brand-${brands[next]}`).focus(); }
        } }))),
    h('div', { className: 'card stack', id: 'setup-guide', role: 'tabpanel', 'aria-labelledby': `brand-${state.brand}` },
      h('ol', { className: 'setup-steps' },
        h('li', {}, icon('settings'), h('span', {}, t('setup.open'), path('settings', branch, 'about'))),
        h('li', {}, icon('tap'), h('span', {}, t('setup.press'), tvMenu('build'),
          t('setup.sevenTimes'), tvMenu('developerOptions'))),
        h('li', {}, icon('toggle'), h('span', {}, t('setup.open'), path('settings', branch, 'developerOptions'),
          t('setup.then'), t('setup.enable'), tvMenu('usbDebugging'), t('setup.or'), tvMenu('networkDebugging')))),
      h('p', { className: 'small' }, t('setup.debugNote')),
      h('label', { className: 'check-label', for: 'prepared' }, h('input', { id: 'prepared', type: 'checkbox', checked: state.prepared,
        onchange: event => { state.prepared = event.target.checked; actions.render(); } }), t('setup.done'))),
    h('div', { className: 'actions' }, button(t('common.back'), () => actions.go('start')),
      button(t('common.next'), () => actions.go('connect'), { id: 'setup-next', primary: true, disabled: !state.prepared })));
}
