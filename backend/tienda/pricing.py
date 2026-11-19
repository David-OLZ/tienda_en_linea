"""Cálculo de importes. Todo se maneja en centavos (enteros) para evitar errores de redondeo."""
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP

from .config import TAX_RATE


@dataclass(frozen=True)
class Totals:
    items_count: int
    subtotal_cents: int
    tax_cents: int
    total_cents: int

    def to_dict(self):
        return asdict(self)


def line_total(unit_price_cents, quantity):
    if unit_price_cents < 0 or quantity < 0:
        raise ValueError("Precio y cantidad no pueden ser negativos.")
    return unit_price_cents * quantity


def calculate_tax(subtotal_cents, rate=TAX_RATE):
    if subtotal_cents < 0:
        raise ValueError("El subtotal no puede ser negativo.")
    tax = (Decimal(subtotal_cents) * Decimal(rate)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(tax)


def calculate_totals(lines, rate=TAX_RATE):
    """`lines` es un iterable de (precio_unitario_en_centavos, cantidad)."""
    subtotal = 0
    count = 0
    for unit_price, quantity in lines:
        subtotal += line_total(unit_price, quantity)
        count += quantity
    tax = calculate_tax(subtotal, rate)
    return Totals(items_count=count, subtotal_cents=subtotal, tax_cents=tax, total_cents=subtotal + tax)
