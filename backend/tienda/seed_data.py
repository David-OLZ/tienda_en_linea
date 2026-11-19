"""Catálogo inicial: 6 categorías y 36 productos. Precios en pesos (se convierten a centavos al cargar)."""

CATEGORIES = [
    "Electrónica", "Hogar y cocina", "Ropa y accesorios",
    "Deportes", "Libros y papelería", "Juguetes",
]

# (sku, nombre, descripción, precio MXN, existencia, emoji, categoría)
PRODUCTS = [
    ("ELE-001", "Audífonos inalámbricos Bluetooth", "Audífonos con cancelación de ruido y hasta 30 horas de batería.", 899.00, 25, "🎧", "Electrónica"),
    ("ELE-002", "Bocina portátil resistente al agua", "Bocina Bluetooth con protección IPX7 y 12 horas de reproducción.", 649.00, 18, "🔊", "Electrónica"),
    ("ELE-003", "Cargador USB-C 65 W", "Cargador rápido compatible con laptops, tabletas y teléfonos.", 459.00, 40, "🔌", "Electrónica"),
    ("ELE-004", "Teclado mecánico compacto", "Teclado de 75% con switches lineales e iluminación blanca.", 1199.00, 12, "⌨️", "Electrónica"),
    ("ELE-005", "Mouse inalámbrico ergonómico", "Mouse de diseño vertical con sensor de 1600 DPI.", 349.00, 30, "🖱️", "Electrónica"),
    ("ELE-006", "Smartwatch deportivo", "Reloj inteligente con GPS, monitor de ritmo cardiaco y 7 días de batería.", 1799.00, 0, "⌚", "Electrónica"),

    ("HOG-001", "Cafetera de goteo 12 tazas", "Cafetera programable con jarra de vidrio y filtro permanente.", 799.00, 15, "☕", "Hogar y cocina"),
    ("HOG-002", "Licuadora 1.5 L", "Licuadora de 600 W con vaso de vidrio y 3 velocidades.", 1099.00, 10, "🥤", "Hogar y cocina"),
    ("HOG-003", "Juego de sartenes antiadherentes", "Set de 3 sartenes con recubrimiento antiadherente y mango frío.", 1349.00, 8, "🍳", "Hogar y cocina"),
    ("HOG-004", "Set de cuchillos de cocina", "Seis piezas de acero inoxidable con base de madera.", 579.00, 14, "🔪", "Hogar y cocina"),
    ("HOG-005", "Lámpara de escritorio LED", "Lámpara con brazo flexible y tres niveles de intensidad.", 299.00, 3, "💡", "Hogar y cocina"),
    ("HOG-006", "Juego de sábanas matrimonial", "Sábanas de microfibra suave, 4 piezas.", 649.00, 20, "🛏️", "Hogar y cocina"),

    ("ROP-001", "Playera básica de algodón", "Playera unisex de cuello redondo, 100% algodón.", 189.00, 60, "👕", "Ropa y accesorios"),
    ("ROP-002", "Sudadera con capucha", "Sudadera de felpa interior con bolsa frontal.", 599.00, 22, "🧥", "Ropa y accesorios"),
    ("ROP-003", "Jeans corte recto", "Mezclilla resistente con un ligero porcentaje de elastano.", 749.00, 18, "👖", "Ropa y accesorios"),
    ("ROP-004", "Tenis casuales", "Tenis ligeros con suela flexible para uso diario.", 1099.00, 16, "👟", "Ropa y accesorios"),
    ("ROP-005", "Gorra ajustable", "Gorra de algodón con cierre ajustable.", 229.00, 35, "🧢", "Ropa y accesorios"),
    ("ROP-006", "Mochila urbana", "Mochila de 20 litros con compartimento acolchonado.", 679.00, 2, "🎒", "Ropa y accesorios"),

    ("DEP-001", "Tapete de yoga antiderrapante", "Tapete de 6 mm con superficie antiderrapante y correa.", 349.00, 28, "🧘", "Deportes"),
    ("DEP-002", "Mancuernas ajustables 10 kg", "Par de mancuernas con discos intercambiables.", 999.00, 9, "🏋️", "Deportes"),
    ("DEP-003", "Balón de futbol No. 5", "Balón cosido a máquina para césped y duela.", 399.00, 45, "⚽", "Deportes"),
    ("DEP-004", "Botella deportiva 750 ml", "Botella libre de BPA con tapa de seguridad.", 149.00, 80, "🥛", "Deportes"),
    ("DEP-005", "Bicicleta de montaña rodada 29", "Cuadro de aluminio, 21 velocidades y frenos de disco.", 6499.00, 4, "🚵", "Deportes"),
    ("DEP-006", "Cuerda para saltar", "Cuerda de velocidad con rodamientos y mangos de espuma.", 99.00, 0, "🪢", "Deportes"),

    ("LIB-001", "Cuaderno profesional cuadro grande", "Cuaderno de 100 hojas con pasta dura.", 59.00, 120, "📓", "Libros y papelería"),
    ("LIB-002", "Set de plumas de gel (12 piezas)", "Plumas de punto fino en 12 colores.", 89.00, 70, "🖊️", "Libros y papelería"),
    ("LIB-003", "Agenda 2027", "Agenda semanal con pasta flexible y separadores.", 199.00, 40, "📅", "Libros y papelería"),
    ("LIB-004", "Libro de cocina mexicana", "Más de 150 recetas tradicionales con fotografías.", 349.00, 17, "📖", "Libros y papelería"),
    ("LIB-005", "Calculadora científica", "Calculadora con más de 240 funciones y pantalla de dos líneas.", 279.00, 25, "🧮", "Libros y papelería"),
    ("LIB-006", "Marcadores de colores (24 piezas)", "Marcadores de doble punta para dibujo y rotulación.", 159.00, 33, "🖍️", "Libros y papelería"),

    ("JUG-001", "Bloques de construcción 500 piezas", "Cubeta con bloques compatibles y guía de ideas.", 449.00, 26, "🧱", "Juguetes"),
    ("JUG-002", "Rompecabezas 1000 piezas", "Rompecabezas de paisaje con acabado mate.", 249.00, 19, "🧩", "Juguetes"),
    ("JUG-003", "Carrito de control remoto", "Auto todoterreno con batería recargable y alcance de 30 m.", 599.00, 11, "🚗", "Juguetes"),
    ("JUG-004", "Muñeca de trapo", "Muñeca artesanal de tela suave, 35 cm.", 279.00, 14, "🪆", "Juguetes"),
    ("JUG-005", "Juego de mesa familiar", "Juego de estrategia para 2 a 6 jugadores.", 389.00, 21, "🎲", "Juguetes"),
    ("JUG-006", "Peluche de oso", "Oso de peluche hipoalergénico de 40 cm.", 259.00, 5, "🧸", "Juguetes"),
]
