import { escapeHtml, formatMoney, pluralize } from '../format.js';
import { alertBox, errorMessage, spinner, toast } from '../ui.js';

export async function render(container, ctx, route) {
  container.innerHTML = spinner();
  let product;
  try {
    ({ product } = await ctx.api.product(route.params.id));
  } catch (e) {
    container.innerHTML = alertBox(errorMessage(e)) + '<a class="btn btn-primary" href="#/">Volver a la tienda</a>';
    return;
  }
  const inCart = (ctx.session.cart?.items || []).find((i) => i.product_id === product.id)?.quantity || 0;

  const availability = !product.available
    ? '<span class="badge text-bg-danger fs-6">Agotado</span>'
    : `<span class="badge text-bg-${product.low_stock ? 'warning' : 'success'} fs-6">${pluralize(product.stock, 'unidad disponible', 'unidades disponibles')}</span>`;

  container.innerHTML = `
    <nav aria-label="breadcrumb"><ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="#/">Tienda</a></li>
      <li class="breadcrumb-item">${escapeHtml(product.category_name)}</li>
      <li class="breadcrumb-item active" aria-current="page">${escapeHtml(product.name)}</li>
    </ol></nav>
    <div class="card"><div class="card-body"><div class="row g-4">
      <div class="col-md-5 text-center py-4 bg-body-secondary rounded"><span class="product-emoji-lg">${product.emoji}</span></div>
      <div class="col-md-7">
        <p class="text-body-secondary small mb-1">SKU ${escapeHtml(product.sku)}</p>
        <h1 class="h3">${escapeHtml(product.name)}</h1>
        <p class="mb-3">${availability}</p>
        <p>${escapeHtml(product.description)}</p>
        <p class="display-6 fw-bold">${formatMoney(product.price_cents)}</p>
        <p class="small text-body-secondary">Los precios no incluyen IVA; se calcula en el carrito.</p>
        <div id="feedback"></div>
        ${product.available ? `
        <div class="d-flex gap-2 align-items-end flex-wrap">
          <div><label class="form-label" for="qty">Cantidad</label>
            <input type="number" class="form-control qty-input" id="qty" min="1" max="${product.stock}" value="1"></div>
          <button class="btn btn-primary" id="add">Agregar al carrito</button>
          <a class="btn btn-outline-secondary" href="#/carrito">Ver carrito</a>
        </div>
        ${inCart ? `<p class="small text-body-secondary mt-2" id="in-cart">Ya tienes ${pluralize(inCart, 'unidad', 'unidades')} en tu carrito.</p>` : ''}`
        : '<a class="btn btn-outline-secondary" href="#/">Ver otros productos</a>'}
      </div>
    </div></div></div>`;

  const add = container.querySelector('#add');
  if (!add) return;
  add.addEventListener('click', async () => {
    const feedback = container.querySelector('#feedback');
    feedback.innerHTML = '';
    add.disabled = true;
    try {
      const cart = await ctx.session.add(product.id, container.querySelector('#qty').value);
      const now = cart.items.find((i) => i.product_id === product.id)?.quantity || 0;
      toast('Producto agregado al carrito.');
      feedback.innerHTML = alertBox(`Listo. Tienes ${pluralize(now, 'unidad', 'unidades')} de este producto en tu carrito.`, 'success');
    } catch (err) {
      feedback.innerHTML = alertBox(errorMessage(err), 'warning');
    } finally {
      add.disabled = false;
    }
  });
}
