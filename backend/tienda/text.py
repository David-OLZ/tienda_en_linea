"""Utilidades de texto."""
import unicodedata


def normalize(text):
    """Minúsculas, sin acentos y con espacios compactados (para búsquedas y comparaciones)."""
    decomposed = unicodedata.normalize("NFKD", str(text))
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.lower().split())


def plural_units(n):
    return "1 unidad" if n == 1 else f"{n} unidades"
