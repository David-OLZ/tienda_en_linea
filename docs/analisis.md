# Análisis del sistema: tienda en línea

## Qué debe hacer
Una persona abre la tienda, busca productos, los agrega al carrito, captura sus datos de entrega, revisa su compra y llega a la pantalla de pago. El pago no funciona: solo avisa que todavía no está disponible.

## Comportamiento normal
- El catálogo tiene 36 productos en 6 categorías, guardados en SQLite.
- Se puede buscar por texto (sin importar acentos ni mayúsculas), filtrar por categoría, ordenar por nombre o precio y ocultar agotados.
- La ficha del producto muestra descripción, precio y existencia.
- En el carrito se cambia la cantidad, se quitan productos o se vacía todo.
- El total se calcula como subtotal + IVA del 16 %, redondeando el impuesto al centavo.
- El resumen final muestra productos, cantidades, importes, total y datos de entrega.
- Al pulsar «Pagar» se muestra un aviso claro de función no disponible y no se hace ningún cargo.

## Situaciones problemáticas y cómo se manejan
- **Producto agotado:** no se puede agregar; el botón aparece deshabilitado y el servidor también lo rechaza.
- **Cantidad mayor a la existencia:** se rechaza con un mensaje que dice cuántas unidades quedan (considerando lo que ya hay en el carrito).
- **Cantidades sin sentido** (0, negativas, decimales, texto, más de 99): error de validación.
- **Modificar o quitar un producto que no está en el carrito:** error 404 con mensaje claro.
- **La existencia baja mientras el cliente compra:** la línea se marca con problema y no se puede continuar hasta corregirla.
- **Carrito vacío:** no se puede capturar datos, revisar ni intentar pagar.
- **Datos del cliente incorrectos o incompletos:** cada campo se valida (nombre y apellido, correo, teléfono de 10 dígitos, código postal de 5 dígitos, estado de la lista, etc.) y el error se muestra junto al campo.
- **Saltarse pasos** (ir al pago sin datos): la aplicación regresa al paso que falta.
- **Carrito guardado que ya no existe:** se crea uno nuevo automáticamente.
- **Python no encontrado o backend caído:** se muestra un mensaje de error en lugar de fallar en silencio.

## Fuera de alcance
Cobro real, facturación, seguimiento de pedidos, cuentas de usuario, administración de inventario y recomendaciones.
