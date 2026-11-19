// Mantiene el id del carrito (localStorage) y el último estado conocido. Sin dependencias del DOM.
import { ApiError } from './api.js';

const STORAGE_KEY = 'tienda.cartId';

export function createCartSession(api, storage) {
  let cartId = null;
  let verified = false;
  let cart = null;
  const listeners = new Set();

  const publish = (next) => {
    cart = next;
    listeners.forEach((fn) => fn(cart));
    return cart;
  };

  function readStored() {
    try { return storage.getItem(STORAGE_KEY); } catch { return null; }
  }
  function writeStored(id) {
    try { storage.setItem(STORAGE_KEY, id); } catch { /* sin almacenamiento: el carrito vive solo en memoria */ }
  }

  async function newCart() {
    const { cart_id: id } = await api.createCart();
    cartId = id;
    verified = true;
    writeStored(id);
    return id;
  }

  async function ensureCartId() {
    if (cartId && verified) return cartId;
    cartId = cartId || readStored();
    if (cartId) {
      try {
        await api.getCart(cartId);
        verified = true;
        return cartId;
      } catch (e) {
        if (!(e instanceof ApiError && e.status === 404)) throw e;
      }
    }
    return newCart();
  }

  return {
    get cartId() { return cartId; },
    get cart() { return cart; },
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
    async load() { return publish(await api.getCart(await ensureCartId())); },
    async add(productId, quantity = 1) { return publish(await api.addItem(await ensureCartId(), productId, quantity)); },
    async setQuantity(productId, quantity) { return publish(await api.setQuantity(await ensureCartId(), productId, quantity)); },
    async remove(productId) { return publish(await api.removeItem(await ensureCartId(), productId)); },
    async clear() { return publish(await api.clearCart(await ensureCartId())); },
  };
}
