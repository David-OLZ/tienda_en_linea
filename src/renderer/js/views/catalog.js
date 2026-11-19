import { catalogHash } from '../router.js';
import { debounce, escapeHtml, formatMoney } from '../format.js';
import { alertBox, errorMessage, spinner, toast } from '../ui.js';

function stockBadge(p) {
  if (!p.available) return '<span class="badge text-bg-danger">Agotado</span>';
  if (p.low_stock) return `<span class="badge text-bg-warning">¡Últimas ${p.stock}!</span>`;
  return '<span class="badge text-bg-success">Disponible</span>';
}

function productCard(p) {
  return `<div class="col">
    <div class="card h-100 product-card">
      <a class="text-decoration-none text-center pt-3" href="#/producto/${p.id}" aria-label="Ver ${escapeHtml(p.name)}">
        <span class="product-emoji">${p.emoji}</span></a>
      <div class="card-body d-flex flex-column">
        <span class="small text-body-secondary">${escapeHtml(p.category_name)}</span>
        <h2 class="h6 card-title"><a class="text-reset text-decoration-none" href="#/producto/${p.id}">${escapeHtml(p.name)}</a></h2>
        <div class="mb-2">${stockBadge(p)}</div>
        <div class="mt-auto">
          <div class="fs-5 fw-bold mb-2">${formatMoney(p.price_cents)}</div>
          <div class="d-flex gap-2">
            <a class="btn btn-outline-secondary btn-sm flex-fill" href="#/producto/${p.id}">Detalle</a>
            <button class="btn btn-primary btn-sm flex-fill" data-add="${p.id}" ${p.available ? '' : 'disabled'}>Agregar</button>
          </div>
        </div>
      </div>
    </div>
  </div>`;
}

export async function render(container, ctx, route) {
  const state = {
    q: route.query.q || '',
    category: route.query.category || '',
    sort: route.query.sort || 'name',
    available: route.query.available === '1',
  };
  container.innerHTML = spinner();
  let categories;
  try {
    ({ categories } = await ctx.api.categories());
  } catch (e) {
    container.innerHTML = alertBox(errorMessage(e));
    return;
  }

  const total = categories.reduce((n, c) => n + c.product_count, 0);
  container.innerHTML = `
    <div class="row g-4">
      <aside class="col-lg-3">
        <div class="list-group" id="category-list">
          <button type="button" class="list-group-item list-group-item-action d-flex justify-content-between" data-category="">
            Todas <span class="badge text-bg-secondary">${total}</span></button>
          ${categories.map((c) => `<button type="button" class="list-group-item list-group-item-action d-flex justify-content-between" data-category="${c.id}">
            ${escapeHtml(c.name)} <span class="badge text-bg-secondary">${c.product_count}</span></button>`).join('')}
        </div>
      </aside>
      <section class="col-lg-9">
        <form class="row g-2 mb-3" id="filters" role="search">
          <div class="col-md-6"><input type="search" class="form-control" id="q" placeholder="Buscar productos…" value="${escapeHtml(state.q)}" aria-label="Buscar"></div>
          <div class="col-md-3">
            <select class="form-select" id="sort" aria-label="Ordenar">
              <option value="name">Nombre (A-Z)</option>
              <option value="price_asc">Precio: menor a mayor</option>
              <option value="price_desc">Precio: mayor a menor</option>
            </select>
          </div>
          <div class="col-md-3 d-flex align-items-center">
            <div class="form-check"><input class="form-check-input" type="checkbox" id="available">
            <label class="form-check-label" for="available">Solo disponibles</label></div>
          </div>
        </form>
        <div id="results"></div>
      </section>
    </div>`;

  const sortEl = container.querySelector('#sort');
  const availableEl = container.querySelector('#available');
  const qEl = container.querySelector('#q');
  sortEl.value = state.sort;
  availableEl.checked = state.available;

  const paintCategories = () => {
    container.querySelectorAll('[data-category]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.category === state.category);
    });
  };

  async function load() {
    paintCategories();
    history.replaceState(null, '', catalogHash(state));
    const results = container.querySelector('#results');
    results.innerHTML = spinner();
    try {
      const { products } = await ctx.api.products({
        q: state.q, category: state.category, sort: state.sort, available: state.available,
      });
      results.innerHTML = products.length
        ? `<p class="text-body-secondary small">${products.length} producto(s)</p>
           <div class="row row-cols-1 row-cols-sm-2 row-cols-xl-3 g-3">${products.map(productCard).join('')}</div>`
        : alertBox('No encontramos productos con esos filtros. Prueba con otra búsqueda o categoría.', 'info');
    } catch (e) {
      results.innerHTML = alertBox(errorMessage(e));
    }
  }

  container.querySelector('#filters').addEventListener('submit', (e) => e.preventDefault());
  qEl.addEventListener('input', debounce(() => { state.q = qEl.value.trim(); load(); }, 250));
  sortEl.addEventListener('change', () => { state.sort = sortEl.value; load(); });
  availableEl.addEventListener('change', () => { state.available = availableEl.checked; load(); });
  container.querySelector('#category-list').addEventListener('click', (e) => {
    const btn = e.target.closest('[data-category]');
    if (!btn) return;
    state.category = btn.dataset.category;
    load();
  });
  container.querySelector('#results').addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-add]');
    if (!btn) return;
    btn.disabled = true;
    try {
      await ctx.session.add(Number(btn.dataset.add), 1);
      toast('Producto agregado al carrito.');
    } catch (err) {
      toast(errorMessage(err), 'warning');
    } finally {
      btn.disabled = false;
    }
  });

  load();
}
