// Authored SVG geometry, never parsed as markup.
const paths = {
  tv: ['M3 4h18v13H3z', 'M8 21h8M12 17v4'],
  settings: ['M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1z', 'M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0'],
  tap: ['M8 11V5a2 2 0 0 1 4 0v7-4a2 2 0 0 1 4 0v4-2a2 2 0 0 1 4 0v6l-3 5H9l-5-7a2 2 0 0 1 3-2l1 1'],
  toggle: ['M7 6h10a6 6 0 0 1 0 12H7A6 6 0 0 1 7 6', 'M19 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0'],
  lock: ['M5 10h14v11H5z', 'M8 10V6a4 4 0 0 1 8 0v4M12 14v3'],
  check: ['M5 12l4 4L19 6'],
  optional: ['M12 3 2 21h20L12 3z', 'M12 9v5M12 17v1'],
  skip: ['M5 10a8 8 0 1 1 1 9M5 10V3M5 10h7'],
  error: ['M6 6l12 12M6 18 18 6'],
};
export function icon(name, className = '') {
  const ns = ['http:', '', 'www.w3.org', '2000', 'svg'].join('/');
  const svg = document.createElementNS(ns, 'svg');
  for (const [key, value] of Object.entries({ viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor',
    'stroke-width': '1.75', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'aria-hidden': 'true', class: `icon ${className}` })) svg.setAttribute(key, value);
  for (const d of paths[name] ?? paths.tv) {
    const path = document.createElementNS(ns, 'path');
    path.setAttribute('d', d);
    svg.append(path);
  }
  return svg;
}
