# Tienda en línea (Electron + Bootstrap + Python/SQLite)

Aplicación de escritorio que permite explorar un catálogo, armar un carrito, capturar datos de entrega, revisar la compra y llegar a la pantalla de pago. El pago no está disponible: no hay conexión con bancos ni proveedores, solo se muestra el aviso.

## Requisitos
- Node.js 20 o superior
- Python 3.9 o superior (sin librerías externas)

## Cómo ejecutarla
```
npm install
npm start
```
La base de datos SQLite se crea sola en la carpeta de datos de la app y se llena con 36 productos la primera vez. Si Python no se detecta, define la variable `TIENDA_PYTHON` con la ruta del ejecutable.

## Pruebas
```
npm test            # todas
npm run test:py     # backend (84 pruebas, unittest)
npm run test:js     # frontend y proceso principal (23 pruebas, node:test)
```

## Estructura
```
backend/
  main.py                      arranque del servidor local
  tienda/
    config.py                  IVA, moneda, topes
    errors.py                  errores de dominio
    pricing.py                 cálculo de subtotal, IVA y total (centavos)
    validators.py              cantidades y datos del cliente
    text.py                    normalización de texto
    database.py, seed*.py      esquema SQLite y catálogo inicial
    repositories/              acceso a datos (catálogo, carrito)
    services/                  reglas: catálogo, carrito, compra, pago
    api/                       enrutador, endpoints y servidor HTTP
    app.py                     ensamblado de dependencias
  tests/                       pruebas unitarias del backend
src/
  main/                        Electron: ventana, lanzamiento de Python, puente a la API
  preload/preload.cjs          expone solo `tiendaApi.request` al renderer
  renderer/                    interfaz Bootstrap
    js/                        api, router, formato, sesión de carrito (puros)
    js/views/                  catálogo, producto, carrito, datos, revisión, pago
tests/frontend/                pruebas de los módulos puros
docs/analisis.md               análisis de requisitos y casos problemáticos
```

## Cómo se comunican las partes
El renderer no tiene acceso a la red ni a Node. Llama a `window.tiendaApi.request`, el proceso principal valida la ruta (solo `/api/...`) y la reenvía por HTTP al servidor Python, que escucha únicamente en `127.0.0.1` en un puerto libre.

## Notas de diseño
- Los importes se guardan y calculan en centavos enteros para evitar errores de redondeo.
- La existencia se valida en el servidor al agregar, al cambiar cantidad y de nuevo al revisar la compra.
- Los datos de tarjeta de la pantalla de pago nunca se envían al backend.
