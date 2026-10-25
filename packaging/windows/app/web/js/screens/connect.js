import { h, heading, button } from '../dom.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import { tvMenu } from './setup.js';

export function connectScreen(state, actions) {
  const busy = ['scanning', 'connecting'].includes(state.connection);
  if (state.connection === 'unauthorized') return h('section', { className: 'screen' },
    heading(t('connect.authorizeTitle'), t('connect.authorizeBody')),
    h('div', { className: 'card stack' },
      h('div', { className: 'tv-dialog', role: 'img', 'aria-label': t('connect.mockLabel') },
        h('h3', {}, tvMenu('allowTitle')),
        h('div', { className: 'mock-check' }, h('span', { className: 'mock-box' }, icon('check')), tvMenu('alwaysAllow')),
        h('div', { className: 'mock-allow' }, tvMenu('allow'))),
      h('p', { className: 'small' }, t('connect.authorizeHint')),
      h('p', { className: 'status', role: 'status', 'aria-live': 'polite' }, h('span', { className: 'spinner', 'aria-hidden': 'true' }), t('connect.waiting'))));

  const manual = h('form', { className: 'manual-form', onsubmit: event => {
    event.preventDefault(); actions.connect({ ip: state.manualIP.trim(), port: 5555 });
  } }, h('h3', {}, t('connect.manualTitle')),
  h('div', { className: 'field' }, h('label', { for: 'manual-ip' }, t('connect.ipLabel')),
    h('input', { type: 'text', id: 'manual-ip', inputmode: 'decimal', autocomplete: 'off', required: true,
      placeholder: t('connect.ipPlaceholder'), value: state.manualIP, 'aria-describedby': 'ip-hint', disabled: busy,
      oninput: event => { state.manualIP = event.target.value; } }),
    h('p', { id: 'ip-hint', className: 'small' }, t('connect.manualHint'))),
  h('button', { type: 'submit', className: 'button', disabled: busy }, t('connect.manualButton')));
  return h('section', { className: 'screen' }, heading(t('connect.title'), t('connect.intro')),
    h('div', { role: 'status', 'aria-live': 'polite' }, busy ? h('div', { className: 'card stack' },
      state.connection === 'scanning' ? h('div', { className: 'radar', 'aria-hidden': 'true' }, icon('tv')) : h('span', { className: 'spinner', 'aria-hidden': 'true' }),
      h('p', {}, t(state.connection === 'scanning' ? 'connect.scanning' : 'connect.connecting'))) : null),
    !busy && button(t('connect.find'), actions.discover, { primary: true, id: 'find-tv' }),
    !busy && state.candidates?.length > 0 && h('div', { className: 'stack' }, h('h2', {}, t('connect.found')),
      state.candidates.map((candidate, i) => h('div', { className: 'card tv-card' }, icon('tv'),
        h('div', { className: 'tv-info' }, h('h3', {}, t('connect.tv')), h('p', {}, candidate.ip)),
        button(t('connect.pick'), () => actions.connect(candidate), { id: `pick-${i}`, 'aria-label': `${t('connect.pick')} ${candidate.ip}` })))),
    !busy && state.candidates?.length === 0 && h('div', { className: 'card stack', role: 'status' },
      h('h2', {}, t('connect.none')), h('p', {}, t('connect.tips'))),
    !busy && h('div', { className: 'card' }, manual),
    button(t('common.back'), () => actions.go('setup'), { disabled: busy }));
}
