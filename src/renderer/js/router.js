// Rutas basadas en el hash de la URL. Sin dependencias del DOM.
export function parseHash(hash) {
  const raw = (hash || '').replace(/^#/, '');
  const [pathPart, queryPart = ''] = raw.split('?');
  const query = Object.fromEntries(new URLSearchParams(queryPart));
  const segments = pathPart.split('/').filter(Boolean);

  if (segments.length === 0) return { name: 'catalog', params: {}, query };
  if (segments[0] === 'producto' && /^\d+$/.test(segments[1] || '') && segments.length === 2) {
    return { name: 'product', params: { id: Number(segments[1]) }, query };
  }
  const simple = { carrito: 'cart', datos: 'checkout', revision: 'review', pago: 'payment' };
  if (segments.length === 1 && simple[segments[0]]) {
    return { name: simple[segments[0]], params: {}, query };
  }
  return { name: 'notFound', params: {}, query };
}

export function catalogHash({ q = '', category = '', sort = 'name', available = false } = {}) {
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (category) params.set('category', category);
  if (sort && sort !== 'name') params.set('sort', sort);
  if (available) params.set('available', '1');
  const qs = params.toString();
  return qs ? `#/?${qs}` : '#/';
}
