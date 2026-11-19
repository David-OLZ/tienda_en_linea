import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { createClient, validateRequest } = require('../../src/main/backend-client.cjs');
const { pythonCandidates } = require('../../src/main/backend-process.cjs');

test('solo se permiten rutas /api/ y métodos conocidos', () => {
  assert.doesNotThrow(() => validateRequest({ method: 'GET', path: '/api/products' }));
  assert.throws(() => validateRequest({ method: 'GET', path: 'http://malo.com' }));
  assert.throws(() => validateRequest({ method: 'GET', path: '/api/../etc' }));
  assert.throws(() => validateRequest({ method: 'PATCH', path: '/api/x' }));
  assert.throws(() => validateRequest({}));
});

test('el cliente envía JSON y devuelve status y datos', async () => {
  let seen;
  const fakeFetch = async (url, options) => {
    seen = { url, options };
    return { status: 201, ok: true, json: async () => ({ cart_id: 'abc' }) };
  };
  const client = createClient('http://127.0.0.1:9999', fakeFetch);
  const res = await client.request({ method: 'post', path: '/api/cart/x/items', body: { product_id: 1 } });
  assert.equal(seen.url, 'http://127.0.0.1:9999/api/cart/x/items');
  assert.equal(seen.options.method, 'POST');
  assert.equal(seen.options.body, '{"product_id":1}');
  assert.deepEqual(res, { status: 201, ok: true, data: { cart_id: 'abc' } });
});

test('respuesta sin JSON devuelve data nulo', async () => {
  const client = createClient('http://x', async () => ({ status: 500, ok: false, json: async () => { throw new Error('vacío'); } }));
  assert.deepEqual(await client.request({ path: '/api/health' }), { status: 500, ok: false, data: null });
});

test('orden de candidatos de Python por plataforma', () => {
  assert.equal(pythonCandidates('win32', undefined)[0].cmd, 'py');
  assert.equal(pythonCandidates('linux', undefined)[0].cmd, 'python3');
  assert.equal(pythonCandidates('linux', '/ruta/python')[0].cmd, '/ruta/python');
});
