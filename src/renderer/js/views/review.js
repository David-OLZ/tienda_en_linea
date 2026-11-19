import { escapeHtml, formatMoney } from '../format.js';
import { alertBox, errorMessage, spinner, stepper, totalsTable } from '../ui.js';

export function customerBlock(c) {
  const interior = c.int_number ? ` int. ${escapeHtml(c.int_number)}` : '';
  return `<address class="mb-0">
    <strong>${escapeHtml(c.full_name)}</strong><br>
    ${escapeHtml(c.street)} ${escapeHtml(c.ext_number)}${interior}, ${escapeHtml(c.neighborhood)}<br>
    ${escapeHtml(c.city)}, ${escapeHtml(c.state)}. C.P. ${escapeHtml(c.postal_code)}<br>
    ${c.references ? `<span class="text-body-secondary">Referencias: ${escapeHtml(c.references)}</span><br>` : ''}
    ${escapeHtml(c.email)} · ${escapeHtml(c.phone)}</address>`;
}

export async function loadSummary(ctx, container) {
  try {
    await ctx.session.load();
    return await ctx.api.getSummary(ctx.session.cartId);
  } catch (e) {
    if (e.code === 'empty_cart') { location.hash = '#/carrito'; return null; }
    if (e.code === 'incomplete_checkout') { location.hash = '#/datos'; return null; }
    const extra = e.code === 'insufficient_stock' ? '<a class="btn btn-primary" href="#/carrito">Corregir mi carrito</a>' : '';
    container.innerHTML = alertBox(errorMessage(e), e.code === 'insufficient_stock' ? 'warning' : 'danger') + extra;
    return null;
  }
}

export async function render(container, ctx) {
  container.innerHTML = spinner();
  const summary = await loadSummary(ctx, container);
  if (!summary) return;

  container.innerHTML = `${stepper('review')}
    <h1 class="h3 mb-3">Revisa tu compra</h1>
    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card mb-3"><div class="table-responsive"><table class="table align-middle mb-0">
          <thead><tr><th>Producto</th><th class="text-end">Precio</th><th class="text-center">Cant.</th><th class="text-end">Importe</th></tr></thead>
          <tbody>${summary.items.map((i) => `<tr>
            <td><span class="fs-4 me-2">${i.emoji}</span>${escapeHtml(i.name)}</td>
            <td class="text-end">${formatMoney(i.unit_price_cents)}</td>
            <td class="text-center">${i.quantity}</td>
            <td class="text-end">${formatMoney(i.line_total_cents)}</td></tr>`).join('')}</tbody>
        </table></div></div>
        <div class="card"><div class="card-body">
          <div class="d-flex justify-content-between align-items-start">
            <h2 class="h6">Datos de entrega</h2><a href="#/datos" class="small">Editar</a></div>
          ${customerBlock(summary.customer)}
        </div></div>
      </div>
      <div class="col-lg-4"><div class="card"><div class="card-body">
        <h2 class="h5 mb-3">Total a pagar</h2>
        ${totalsTable(summary.totals, summary.tax_rate_percent, formatMoney)}
        <a class="btn btn-success w-100 mt-3" href="#/pago">Continuar al pago</a>
        <a class="btn btn-link w-100" href="#/carrito">Modificar carrito</a>
      </div></div></div>
    </div>`;
}
