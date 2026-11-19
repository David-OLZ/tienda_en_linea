// Cliente de la API. El transporte se inyecta (en Electron es IPC) para poder probarlo.
export class ApiError extends Error {
  constructor(status, payload) {
    const err = (payload && payload.error) || {};
    super(err.message || 'Ocurrió un error inesperado.');
    this.name = 'ApiError';
    this.status = status;
    this.code = err.code || 'unknown';
    this.fields = err.fields || {};
    this.details = err.details || {};
  }
}

export function buildQuery(params = {}) {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '' || value === false) continue;
    qs.set(key, value === true ? '1' : String(value));
  }
  const text = qs.toString();
  return text ? `?${text}` : '';
}

export function createApi(transport) {
  async function call(method, path, body) {
    const res = await transport({ method, path, body });
    if (!res.ok) throw new ApiError(res.status, res.data);
    return res.data;
  }
  const cart = (id) => `/api/cart/${encodeURIComponent(id)}`;

  return {
    config: () => call('GET', '/api/config'),
    categories: () => call('GET', '/api/categories'),
    products: (params) => call('GET', `/api/products${buildQuery(params)}`),
    product: (id) => call('GET', `/api/products/${id}`),
    createCart: () => call('POST', '/api/cart'),
    getCart: (id) => call('GET', cart(id)),
    addItem: (id, productId, quantity = 1) => call('POST', `${cart(id)}/items`, { product_id: productId, quantity }),
    setQuantity: (id, productId, quantity) => call('PUT', `${cart(id)}/items/${productId}`, { quantity }),
    removeItem: (id, productId) => call('DELETE', `${cart(id)}/items/${productId}`),
    clearCart: (id) => call('DELETE', `${cart(id)}/items`),
    getCustomer: (id) => call('GET', `${cart(id)}/customer`),
    saveCustomer: (id, customer) => call('PUT', `${cart(id)}/customer`, customer),
    getSummary: (id) => call('GET', `${cart(id)}/summary`),
    pay: (id) => call('POST', `${cart(id)}/payment`),
  };
}
