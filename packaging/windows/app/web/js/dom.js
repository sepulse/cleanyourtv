/** Create text nodes only; registry and server data never become HTML. */
export function h(tag, attributes = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attributes)) {
    if (key.startsWith('on')) node.addEventListener(key.slice(2).toLowerCase(), value);
    else if (key === 'className') node.className = value;
    else if (['checked', 'disabled', 'open', 'value', 'hidden', 'indeterminate'].includes(key)) node[key] = value;
    else if (value !== undefined && value !== null && value !== false) node.setAttribute(key, String(value));
  }
  for (const child of children.flat(Infinity)) {
    if (child !== null && child !== undefined && child !== false) node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}
export function button(label, action, { primary = false, ...attributes } = {}) {
  return h('button', { type: 'button', className: primary ? 'button primary' : 'button', onclick: action, ...attributes }, label);
}
export function heading(title, description) {
  return h('div', { className: 'screen-heading' }, h('h1', { tabindex: '-1' }, title), description && h('p', {}, description));
}
