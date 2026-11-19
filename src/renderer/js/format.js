// Formato de dinero y textos. Sin dependencias del DOM.
const moneyFormatter = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' });

export function formatMoney(cents) {
  return moneyFormatter.format(cents / 100);
}

export function pluralize(n, singular, plural) {
  return `${n} ${n === 1 ? singular : plural}`;
}

export function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}
