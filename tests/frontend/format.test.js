import test from 'node:test';
import assert from 'node:assert/strict';
import { escapeHtml, formatMoney, pluralize, debounce } from '../../src/renderer/js/format.js';

test('formatMoney muestra pesos con centavos', () => {
  assert.equal(formatMoney(109900), '$1,099.00');
  assert.equal(formatMoney(5), '$0.05');
  assert.equal(formatMoney(0), '$0.00');
});

test('pluralize usa singular solo para 1', () => {
  assert.equal(pluralize(1, 'unidad', 'unidades'), '1 unidad');
  assert.equal(pluralize(0, 'unidad', 'unidades'), '0 unidades');
  assert.equal(pluralize(5, 'unidad', 'unidades'), '5 unidades');
});

test('escapeHtml neutraliza caracteres peligrosos', () => {
  assert.equal(escapeHtml('<img src=x onerror="a()">'), '&lt;img src=x onerror=&quot;a()&quot;&gt;');
  assert.equal(escapeHtml("O'Neil & Co"), 'O&#39;Neil &amp; Co');
  assert.equal(escapeHtml(null), '');
});

test('debounce ejecuta solo la última llamada', async () => {
  const calls = [];
  const fn = debounce((v) => calls.push(v), 20);
  fn(1); fn(2); fn(3);
  await new Promise((r) => setTimeout(r, 60));
  assert.deepEqual(calls, [3]);
});
