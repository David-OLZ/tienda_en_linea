import test from 'node:test';
import assert from 'node:assert/strict';
import { catalogHash, parseHash } from '../../src/renderer/js/router.js';

test('rutas simples', () => {
  assert.equal(parseHash('').name, 'catalog');
  assert.equal(parseHash('#/').name, 'catalog');
  assert.equal(parseHash('#/carrito').name, 'cart');
  assert.equal(parseHash('#/datos').name, 'checkout');
  assert.equal(parseHash('#/revision').name, 'review');
  assert.equal(parseHash('#/pago').name, 'payment');
});

test('ruta de producto con id numérico', () => {
  assert.deepEqual(parseHash('#/producto/12'), { name: 'product', params: { id: 12 }, query: {} });
});

test('rutas inválidas', () => {
  assert.equal(parseHash('#/producto/abc').name, 'notFound');
  assert.equal(parseHash('#/producto').name, 'notFound');
  assert.equal(parseHash('#/producto/1/extra').name, 'notFound');
  assert.equal(parseHash('#/nada').name, 'notFound');
});

test('query del catálogo', () => {
  const route = parseHash('#/?q=caf%C3%A9&category=2&available=1');
  assert.equal(route.name, 'catalog');
  assert.deepEqual(route.query, { q: 'café', category: '2', available: '1' });
});

test('catalogHash omite valores por defecto y ida y vuelta', () => {
  assert.equal(catalogHash({}), '#/');
  const hash = catalogHash({ q: 'taza azul', category: '3', sort: 'price_asc', available: true });
  assert.deepEqual(parseHash(hash).query, { q: 'taza azul', category: '3', sort: 'price_asc', available: '1' });
});
