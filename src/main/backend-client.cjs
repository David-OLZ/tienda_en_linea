'use strict';
// Cliente HTTP del proceso principal hacia el backend local. El renderer nunca habla directo con la red.
const ALLOWED_METHODS = new Set(['GET', 'POST', 'PUT', 'DELETE']);

function validateRequest({ method = 'GET', path } = {}) {
  if (!ALLOWED_METHODS.has(String(method).toUpperCase())) {
    throw new Error('Método no permitido.');
  }
  if (typeof path !== 'string' || !path.startsWith('/api/') || path.includes('..')) {
    throw new Error('Ruta no permitida.');
  }
}

function createClient(baseUrl, fetchImpl = globalThis.fetch) {
  return {
    async request(req) {
      validateRequest(req);
      const { method = 'GET', path, body } = req;
      const hasBody = body !== undefined;
      const res = await fetchImpl(baseUrl + path, {
        method: method.toUpperCase(),
        headers: hasBody ? { 'Content-Type': 'application/json' } : {},
        body: hasBody ? JSON.stringify(body) : undefined,
      });
      let data = null;
      try { data = await res.json(); } catch { /* respuesta sin cuerpo */ }
      return { status: res.status, ok: res.ok, data };
    },
  };
}

module.exports = { createClient, validateRequest };
