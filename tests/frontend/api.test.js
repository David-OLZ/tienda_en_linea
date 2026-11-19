import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiError, buildQuery, createApi } from '../../src/renderer/js/api.js';

function fakeTransport(response) {
  const calls = [];
  const transport = async (req) => { calls.push(req); return response; };
  return { transport, calls };
}

test('buildQuery ignora vacíos y convierte booleanos', () => {
  assert.equal(buildQuery({ q: '', category: undefined, sort: 'name' }), '?sort=name');
  assert.equal(buildQuery({ available: true, q: 'a b' }), '?available=1&q=a+b');
  assert.equal(buildQuery({}), '');
});

test('las peticiones usan método, ruta y cuerpo correctos', async () => {
  const { transport, calls } = fakeTransport({ ok: true, status: 200, data: {} });
  const api = createApi(transport);
  await api.addItem('c1', 7, 2);
  await api.setQuantity('c1', 7, 3);
  await api.removeItem('c1', 7);
  await api.pay('c1');
  assert.deepEqual(calls[0], { method: 'POST', path: '/api/cart/c1/items', body: { product_id: 7, quantity: 2 } });
  assert.deepEqual(calls[1], { method: 'PUT', path: '/api/cart/c1/items/7', body: { quantity: 3 } });
  assert.deepEqual(calls[2], { method: 'DELETE', path: '/api/cart/c1/items/7', body: undefined });
  assert.deepEqual(calls[3], { method: 'POST', path: '/api/cart/c1/payment', body: undefined });
});

test('errores del servidor se convierten en ApiError', async () => {
  const payload = { error: { code: 'validation_error', message: 'Revisa los datos', fields: { email: 'mal' } } };
  const api = createApi(async () => ({ ok: false, status: 422, data: payload }));
  await assert.rejects(api.saveCustomer('c1', {}), (err) => {
    assert.ok(err instanceof ApiError);
    assert.equal(err.status, 422);
    assert.equal(err.code, 'validation_error');
    assert.deepEqual(err.fields, { email: 'mal' });
    assert.equal(err.message, 'Revisa los datos');
    return true;
  });
});

test('ApiError tiene mensaje por defecto si no hay cuerpo', () => {
  const err = new ApiError(500, null);
  assert.equal(err.message, 'Ocurrió un error inesperado.');
});
