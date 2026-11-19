// Arranque de la aplicación: enrutado, sesión de carrito y vistas.
import { createApi } from './api.js';
import { createCartSession } from './cartSession.js';
import { parseHash } from './router.js';
import { alertBox, errorMessage } from './ui.js';

const views = {
  catalog: () => import('./views/catalog.js'),
  product: () => import('./views/product.js'),
  cart: () => import('./views/cart.js'),
  checkout: () => import('./views/checkout.js'),
  review: () => import('./views/review.js'),
  payment: () => import('./views/payment.js'),
};

async function start() {
  const container = document.getElementById('view');
  const badge = document.getElementById('cart-badge');

  const api = createApi((req) => window.tiendaApi.request(req));
  const session = createCartSession(api, window.localStorage);
  session.subscribe((cart) => { badge.textContent = cart.totals.items_count; });

  let config;
  try {
    config = await api.config();
    await session.load();
  } catch (e) {
    container.innerHTML = alertBox(`No se pudo conectar con el servidor local. ${errorMessage(e)}`);
    return;
  }

  const ctx = { api, session, config, rerender: () => render() };

  async function render() {
    const route = parseHash(location.hash);
    if (route.name === 'notFound') {
      container.innerHTML = alertBox('Esa página no existe.', 'info') + '<a class="btn btn-primary" href="#/">Ir a la tienda</a>';
      return;
    }
    try {
      const view = await views[route.name]();
      await view.render(container, ctx, route);
    } catch (e) {
      container.innerHTML = alertBox(errorMessage(e));
    }
    window.scrollTo(0, 0);
  }

  window.addEventListener('hashchange', render);
  render();
}

start();
