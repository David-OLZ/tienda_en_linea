import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiError } from '../../src/renderer/js/api.js';
import { createCartSession } from '../../src/renderer/js/cartSession.js';

function memoryStorage(initial = {}) {
  const data = { ...initial };
  return { getItem: (k) => data[k] ?? null, setItem: (k, v) => { data[k] = v; }, data };
}

function fakeApi({ existing = [] } = {}) {
  const carts = new Set(existing);
  let counter = 0;
  const empty = (id) => ({ cart_id: id, items: [], totals: { items_count: 0 }, has_issues: false });
  return {
    carts,
    createCart: async () => { const id = `cart-${++counter}`; carts.add(id); return { cart_id: id }; },
    getCart: async (id) => {
      if (!carts.has(id)) throw new ApiError(404, { error: { code: 'not_found', message: 'no existe' } });
      return empty(id);
    },
    addItem: async (id) => ({ ...empty(id), totals: { items_count: 1 } }),
  };
}

test('crea un carrito nuevo y lo guarda cuando no hay uno guardado', async () => {
  const storage = memoryStorage();
  const session = createCartSession(fakeApi(), storage);
  await session.load();
  assert.equal(session.cartId, 'cart-1');
  assert.equal(storage.data['tienda.cartId'], 'cart-1');
});

test('reutiliza el carrito guardado si existe', async () => {
  const storage = memoryStorage({ 'tienda.cartId': 'viejo' });
  const api = fakeApi({ existing: ['viejo'] });
  const session = createCartSession(api, storage);
  await session.load();
  assert.equal(session.cartId, 'viejo');
  assert.equal(api.carts.size, 1);
});

test('si el carrito guardado ya no existe (404) crea otro', async () => {
  const storage = memoryStorage({ 'tienda.cartId': 'borrado' });
  const session = createCartSession(fakeApi(), storage);
  await session.load();
  assert.equal(session.cartId, 'cart-1');
  assert.equal(storage.data['tienda.cartId'], 'cart-1');
});

test('otros errores no se tragan', async () => {
  const api = fakeApi();
  api.getCart = async () => { throw new ApiError(500, null); };
  const session = createCartSession(api, memoryStorage({ 'tienda.cartId': 'x' }));
  await assert.rejects(session.load(), ApiError);
});

test('notifica a los suscriptores en cada cambio', async () => {
  const session = createCartSession(fakeApi(), memoryStorage());
  const seen = [];
  const unsubscribe = session.subscribe((cart) => seen.push(cart.totals.items_count));
  await session.load();
  await session.add(1, 1);
  unsubscribe();
  await session.add(1, 1);
  assert.deepEqual(seen, [0, 1]);
});

test('funciona aunque el almacenamiento lance errores', async () => {
  const broken = { getItem() { throw new Error('x'); }, setItem() { throw new Error('x'); } };
  const session = createCartSession(fakeApi(), broken);
  await session.load();
  assert.equal(session.cartId, 'cart-1');
});
