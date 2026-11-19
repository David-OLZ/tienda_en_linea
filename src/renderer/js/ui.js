// Utilidades de interfaz (usan el DOM y Bootstrap).
import { escapeHtml } from './format.js';

export function toast(message, variant = 'success') {
  const container = document.getElementById('toasts');
  const el = document.createElement('div');
  el.className = `toast align-items-center text-bg-${variant} border-0`;
  el.setAttribute('role', 'alert');
  el.innerHTML = `<div class="d-flex"><div class="toast-body">${escapeHtml(message)}</div>
    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button></div>`;
  container.appendChild(el);
  const instance = new window.bootstrap.Toast(el, { delay: 3500 });
  el.addEventListener('hidden.bs.toast', () => el.remove());
  instance.show();
}

export function alertBox(message, variant = 'danger') {
  return `<div class="alert alert-${variant}" role="alert">${escapeHtml(message)}</div>`;
}

export function spinner(text = 'Cargando…') {
  return `<div class="text-center py-5 text-body-secondary"><div class="spinner-border" role="status"></div><div class="mt-2">${escapeHtml(text)}</div></div>`;
}

const STEPS = [
  { key: 'cart', label: 'Carrito' },
  { key: 'checkout', label: 'Datos' },
  { key: 'review', label: 'Revisión' },
  { key: 'payment', label: 'Pago' },
];

export function stepper(active) {
  const activeIndex = STEPS.findIndex((s) => s.key === active);
  const items = STEPS.map((s, i) => {
    const state = i < activeIndex ? 'done' : i === activeIndex ? 'active' : 'todo';
    const dot = state === 'done' ? 'text-bg-success' : state === 'active' ? 'text-bg-primary' : 'text-bg-secondary';
    const text = state === 'todo' ? 'text-body-secondary' : 'fw-semibold';
    return `<li class="d-flex align-items-center gap-2 ${text}">
      <span class="step-dot rounded-circle d-inline-flex align-items-center justify-content-center ${dot}">${state === 'done' ? '✓' : i + 1}</span>
      <span>${s.label}</span></li>`;
  });
  return `<ol class="list-unstyled d-flex flex-wrap gap-4 mb-4">${items.join('')}</ol>`;
}

export function totalsTable(totals, taxPercent, formatMoney) {
  return `<dl class="row mb-0">
    <dt class="col-7 fw-normal">Subtotal</dt><dd class="col-5 text-end">${formatMoney(totals.subtotal_cents)}</dd>
    <dt class="col-7 fw-normal">IVA (${taxPercent}%)</dt><dd class="col-5 text-end">${formatMoney(totals.tax_cents)}</dd>
    <dt class="col-7 fs-5">Total</dt><dd class="col-5 text-end fs-5 fw-bold">${formatMoney(totals.total_cents)}</dd>
  </dl>`;
}

export function errorMessage(err) {
  return err && err.message ? err.message : 'Ocurrió un error inesperado.';
}
