import { escapeHtml, formatMoney, pluralize } from '../format.js';
import { alertBox, errorMessage, spinner, stepper, toast, totalsTable } from '../ui.js';

function row(i) {
  return `<tr data-row="${i.product_id}">
    <td><span class="fs-3 me-2">${i.emoji}</span>
      <a class="text-reset" href="#/producto/${i.product_id}">${escapeHtml(i.name)}</a>
      ${i.issue ? `<div class="text-danger small mt-1">${escapeHtml(i.issue_message)}</div>` : ''}</td>
    <td class="text-end">${formatMoney(i.unit_price_cents)}</td>
    <td class="text-center"><input type="number" class="form-control form-control-sm qty-input mx-auto ${i.issue ? 'is-invalid' : ''}"
      min="1" max="${Math.max(i.stock, 1)}" value="${i.quantity}" data-qty="${i.product_id}" aria-label="Cantidad de ${escapeHtml(i.name)}"></td>
    <td class="text-end fw-semibold">${formatMoney(i.line_total_cents)}</td>
    <td class="text-end"><button class="btn btn-outline-danger btn-sm" data-remove="${i.product_id}" aria-label="Quitar ${escapeHtml(i.name)}">Quitar</button></td>
  </tr>`;
}

export async function render(container, ctx) {
  container.innerHTML = spinner();
  let cart;
  try {
    cart = await ctx.session.load();
  } catch (e) {
    container.innerHTML = alertBox(errorMessage(e));
    return;
  }

  if (cart.items.length === 0) {
    container.innerHTML = `${stepper('cart')}
      <div class="text-center py-5"><div class="display-1">🛒</div>
      <h1 class="h4 mt-3">Tu carrito está vacío</h1>
      <p class="text-body-secondary">Explora la tienda y agrega los productos que te interesen.</p>
      <a class="btn btn-primary" href="#/">Ir a la tienda</a></div>`;
    return;
  }

  container.innerHTML = `${stepper('cart')}
    <h1 class="h3 mb-3">Tu carrito (${pluralize(cart.totals.items_count, 'artículo', 'artículos')})</h1>
    ${cart.has_issues ? alertBox('Hay productos con problemas de existencia. Corrígelos para continuar.', 'warning') : ''}
    <div class="row g-4">
      <div class="col-lg-8"><div class="card"><div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead><tr><th>Producto</th><th class="text-end">Precio</th><th class="text-center">Cantidad</th><th class="text-end">Importe</th><th></th></tr></thead>
          <tbody>${cart.items.map(row).join('')}</tbody>
        </table></div></div>
        <div class="d-flex justify-content-between mt-3">
          <a class="btn btn-outline-secondary" href="#/">← Seguir comprando</a>
          <button class="btn btn-outline-danger" id="clear">Vaciar carrito</button>
        </div>
      </div>
      <div class="col-lg-4"><div class="card"><div class="card-body">
        <h2 class="h5 mb-3">Resumen</h2>
        ${totalsTable(cart.totals, ctx.config.tax_rate_percent, formatMoney)}
        <a class="btn btn-primary w-100 mt-3 ${cart.has_issues ? 'disabled' : ''}" href="#/datos" ${cart.has_issues ? 'aria-disabled="true"' : ''}>Continuar con mis datos</a>
      </div></div></div>
    </div>`;

  container.querySelectorAll('[data-qty]').forEach((input) => {
    input.addEventListener('change', async () => {
      try {
        await ctx.session.setQuantity(Number(input.dataset.qty), input.value);
      } catch (e) {
        toast(errorMessage(e), 'warning');
      }
      ctx.rerender();
    });
  });
  container.querySelectorAll('[data-remove]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      try {
        await ctx.session.remove(Number(btn.dataset.remove));
        toast('Producto quitado del carrito.', 'secondary');
      } catch (e) {
        toast(errorMessage(e), 'warning');
      }
      ctx.rerender();
    });
  });
  container.querySelector('#clear').addEventListener('click', async () => {
    if (!window.confirm('¿Quieres vaciar todo el carrito?')) return;
    try {
      await ctx.session.clear();
    } catch (e) {
      toast(errorMessage(e), 'warning');
    }
    ctx.rerender();
  });
}
