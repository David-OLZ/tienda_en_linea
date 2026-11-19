import { escapeHtml } from '../format.js';
import { alertBox, errorMessage, spinner, stepper } from '../ui.js';

const FIELDS = [
  { name: 'full_name', label: 'Nombre completo', col: 'col-md-6', autocomplete: 'name', max: 80 },
  { name: 'email', label: 'Correo electrónico', col: 'col-md-6', type: 'email', autocomplete: 'email', max: 254 },
  { name: 'phone', label: 'Teléfono (10 dígitos)', col: 'col-md-4', type: 'tel', autocomplete: 'tel', max: 20 },
  { name: 'street', label: 'Calle', col: 'col-md-5', autocomplete: 'address-line1', max: 80 },
  { name: 'ext_number', label: 'Número exterior', col: 'col-md-3', max: 10 },
  { name: 'int_number', label: 'Número interior (opcional)', col: 'col-md-3', max: 10 },
  { name: 'neighborhood', label: 'Colonia', col: 'col-md-5', max: 60 },
  { name: 'postal_code', label: 'Código postal', col: 'col-md-4', inputmode: 'numeric', autocomplete: 'postal-code', max: 5 },
  { name: 'city', label: 'Ciudad', col: 'col-md-6', autocomplete: 'address-level2', max: 60 },
  { name: 'state', label: 'Estado', col: 'col-md-6', select: true },
  { name: 'references', label: 'Referencias de entrega (opcional)', col: 'col-12', max: 120 },
];

function fieldHtml(f, value, states) {
  const id = `f-${f.name}`;
  const control = f.select
    ? `<select class="form-select" id="${id}" name="${f.name}" autocomplete="address-level1">
        <option value="">Selecciona…</option>
        ${states.map((s) => `<option value="${escapeHtml(s)}" ${s === value ? 'selected' : ''}>${escapeHtml(s)}</option>`).join('')}
      </select>`
    : `<input class="form-control" id="${id}" name="${f.name}" type="${f.type || 'text'}" value="${escapeHtml(value)}"
        maxlength="${f.max}" ${f.autocomplete ? `autocomplete="${f.autocomplete}"` : ''} ${f.inputmode ? `inputmode="${f.inputmode}"` : ''}>`;
  return `<div class="${f.col}"><label class="form-label" for="${id}">${f.label}</label>${control}
    <div class="invalid-feedback" data-error-for="${f.name}"></div></div>`;
}

function showErrors(form, fields) {
  form.querySelectorAll('.is-invalid').forEach((el) => el.classList.remove('is-invalid'));
  let first = null;
  for (const [name, message] of Object.entries(fields)) {
    const input = form.elements[name];
    const feedback = form.querySelector(`[data-error-for="${name}"]`);
    if (!input || !feedback) continue;
    input.classList.add('is-invalid');
    feedback.textContent = message;
    first = first || input;
  }
  if (first) first.focus();
}

export async function render(container, ctx) {
  container.innerHTML = spinner();
  let cart;
  let customer;
  try {
    cart = await ctx.session.load();
    if (cart.items.length === 0) { location.hash = '#/carrito'; return; }
    ({ customer } = await ctx.api.getCustomer(ctx.session.cartId));
  } catch (e) {
    container.innerHTML = alertBox(errorMessage(e));
    return;
  }
  const values = customer || {};

  container.innerHTML = `${stepper('checkout')}
    <h1 class="h3 mb-3">Datos de contacto y entrega</h1>
    <div id="form-alert"></div>
    <form id="customer-form" class="card card-body" novalidate>
      <div class="row g-3">${FIELDS.map((f) => fieldHtml(f, values[f.name] || '', ctx.config.states)).join('')}</div>
      <div class="d-flex justify-content-between mt-4">
        <a class="btn btn-outline-secondary" href="#/carrito">← Volver al carrito</a>
        <button class="btn btn-primary" type="submit">Revisar mi compra</button>
      </div>
    </form>`;

  const form = container.querySelector('#customer-form');
  const banner = container.querySelector('#form-alert');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    banner.innerHTML = '';
    const data = Object.fromEntries(new FormData(form).entries());
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = true;
    try {
      await ctx.api.saveCustomer(ctx.session.cartId, data);
      location.hash = '#/revision';
    } catch (err) {
      if (err.code === 'validation_error') {
        banner.innerHTML = alertBox('Revisa los campos marcados en rojo.', 'danger');
        showErrors(form, err.fields);
      } else if (err.code === 'empty_cart') {
        location.hash = '#/carrito';
      } else {
        banner.innerHTML = alertBox(errorMessage(err));
      }
    } finally {
      submit.disabled = false;
    }
  });
}
