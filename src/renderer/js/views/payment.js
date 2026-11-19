import { escapeHtml, formatMoney } from '../format.js';
import { alertBox, errorMessage, spinner, stepper, totalsTable } from '../ui.js';
import { customerBlock, loadSummary } from './review.js';

export async function render(container, ctx) {
  container.innerHTML = spinner();
  const summary = await loadSummary(ctx, container);
  if (!summary) return;

  container.innerHTML = `${stepper('payment')}
    <h1 class="h3 mb-3">Pago</h1>
    <div class="row g-4">
      <div class="col-lg-7">
        <div class="card"><div class="card-body">
          <h2 class="h5 mb-3">Método de pago</h2>
          <div class="btn-group mb-3 w-100" role="group" aria-label="Método de pago">
            <input type="radio" class="btn-check" name="method" id="m-card" checked>
            <label class="btn btn-outline-primary" for="m-card">Tarjeta</label>
            <input type="radio" class="btn-check" name="method" id="m-paypal">
            <label class="btn btn-outline-primary" for="m-paypal">PayPal</label>
            <input type="radio" class="btn-check" name="method" id="m-mp">
            <label class="btn btn-outline-primary" for="m-mp">Mercado Pago</label>
          </div>
          <form id="pay-form" class="row g-3" novalidate autocomplete="off">
            <div class="col-12"><label class="form-label" for="p-name">Nombre en la tarjeta</label>
              <input class="form-control" id="p-name" autocomplete="off"></div>
            <div class="col-12"><label class="form-label" for="p-number">Número de tarjeta</label>
              <input class="form-control" id="p-number" inputmode="numeric" placeholder="•••• •••• •••• ••••" autocomplete="off"></div>
            <div class="col-6"><label class="form-label" for="p-exp">Vencimiento</label>
              <input class="form-control" id="p-exp" placeholder="MM/AA" autocomplete="off"></div>
            <div class="col-6"><label class="form-label" for="p-cvv">CVV</label>
              <input class="form-control" id="p-cvv" inputmode="numeric" autocomplete="off"></div>
            <div class="col-12 small text-body-secondary">Pantalla de demostración: estos datos no se envían ni se guardan.</div>
            <div class="col-12"><div id="pay-result"></div>
              <button class="btn btn-success btn-lg w-100" type="submit" id="pay-btn">Pagar ${formatMoney(summary.totals.total_cents)}</button></div>
          </form>
        </div></div>
      </div>
      <div class="col-lg-5">
        <div class="card mb-3"><div class="card-body">
          <h2 class="h5 mb-3">Resumen final</h2>
          <ul class="list-unstyled small mb-3">${summary.items.map((i) =>
            `<li class="d-flex justify-content-between"><span>${i.quantity} × ${escapeHtml(i.name)}</span><span>${formatMoney(i.line_total_cents)}</span></li>`).join('')}</ul>
          ${totalsTable(summary.totals, summary.tax_rate_percent, formatMoney)}
        </div></div>
        <div class="card"><div class="card-body"><h2 class="h6">Entrega</h2>${customerBlock(summary.customer)}</div></div>
        <a class="btn btn-link mt-2" href="#/revision">← Volver a la revisión</a>
      </div>
    </div>`;

  const result = container.querySelector('#pay-result');
  container.querySelector('#pay-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = container.querySelector('#pay-btn');
    btn.disabled = true;
    result.innerHTML = '';
    try {
      // No se envía ningún dato de tarjeta: el backend solo informa que el pago no está disponible.
      await ctx.api.pay(ctx.session.cartId);
      result.innerHTML = alertBox('El pago no pudo procesarse.', 'danger');
    } catch (err) {
      const unavailable = err.code === 'payment_unavailable';
      result.innerHTML = `<div class="alert alert-${unavailable ? 'warning' : 'danger'}" role="alert">
        ${unavailable ? '<strong>Función no disponible.</strong> ' : ''}${escapeHtml(errorMessage(err))}</div>`;
    } finally {
      btn.disabled = false;
    }
  });
}
