"""Constantes de negocio de la tienda."""
from decimal import Decimal

CURRENCY = "MXN"
TAX_RATE = Decimal("0.16")  # IVA
MAX_UNITS_PER_LINE = 99  # tope de seguridad por producto, además de la existencia
