let language = 'ms';
let messages = {};
const unavailable = 'CleanYourTV could not load its language files. Reload this page. / CleanYourTV tidak dapat memuatkan fail bahasa. Muat semula halaman ini.';
export async function initI18n() {
  const [en, ms] = await Promise.all(['en', 'ms'].map(async code => {
    const response = await fetch(`/i18n/${code}.json`);
    if (!response.ok) throw new Error('I18N_UNAVAILABLE');
    return response.json();
  }));
  messages = { en, ms };
  const response = await fetch('/api/state');
  if (!response.ok) throw new Error('I18N_UNAVAILABLE');
  language = (await response.json()).language;
  document.documentElement.lang = language;
}
export function t(key, vars = {}) {
  const n = vars.n ?? vars.total;
  const selected = n === 1 && (messages[language]?.[`${key}.one`] || messages.en?.[`${key}.one`]) ? `${key}.one` : key;
  const message = messages[language]?.[selected] || messages.en?.[selected]
    || (key === 'error.I18N_UNAVAILABLE' ? unavailable : key);
  return message.replace(/\{(\w+)\}/g, (match, name) => vars[name] === undefined ? match : String(vars[name]));
}
export function getLanguage() { return language; }
export function setLanguage(value) {
  if (!['ms', 'en'].includes(value)) return;
  language = value;
  document.documentElement.lang = value;
}
