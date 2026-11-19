"""Validación y normalización de entradas del usuario."""
import re

from .config import MAX_UNITS_PER_LINE
from .errors import ValidationError
from .text import normalize

MEXICAN_STATES = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas",
    "Chihuahua", "Ciudad de México", "Coahuila", "Colima", "Durango", "Estado de México",
    "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "Michoacán", "Morelos", "Nayarit",
    "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí",
    "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas",
]
_STATES_BY_KEY = {normalize(s): s for s in MEXICAN_STATES}

REQUIRED = "Este campo es obligatorio."
_INT_RE = re.compile(r"[+-]?[0-9]+", re.ASCII)
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}", re.ASCII)
_NUMBER_RE = re.compile(r"[A-Za-z0-9/\- ]+", re.ASCII)
_POSTAL_RE = re.compile(r"[0-9]{5}", re.ASCII)


def parse_quantity(value):
    """Convierte la cantidad recibida a entero >= 1 o lanza ValidationError."""
    def fail(msg):
        raise ValidationError(msg, fields={"quantity": msg})

    if isinstance(value, bool):
        fail("La cantidad debe ser un número entero.")
    if isinstance(value, int):
        qty = value
    elif isinstance(value, float) and value.is_integer():
        qty = int(value)
    elif isinstance(value, str) and _INT_RE.fullmatch(value.strip()):
        qty = int(value.strip())
    else:
        fail("La cantidad debe ser un número entero.")
    if qty < 1:
        fail("La cantidad mínima es 1.")
    if qty > MAX_UNITS_PER_LINE:
        fail(f"La cantidad máxima por producto es {MAX_UNITS_PER_LINE}.")
    return qty


def _clean(value):
    if value is None or isinstance(value, (dict, list, bool)):
        return ""
    return " ".join(str(value).split())


def _full_name(v):
    if not v:
        return REQUIRED
    if len(v) > 80:
        return "El nombre es demasiado largo (máximo 80 caracteres)."
    if any(not (c.isalpha() or c in " .'’-") for c in v):
        return "El nombre solo puede contener letras, espacios, puntos, apóstrofos y guiones."
    if len(v.split(" ")) < 2:
        return "Escribe tu nombre y al menos un apellido."
    return None


def _email(v):
    if not v:
        return REQUIRED
    if len(v) > 254 or ".." in v.split("@")[0] or not _EMAIL_RE.fullmatch(v):
        return "Escribe un correo válido, por ejemplo nombre@dominio.com."
    return None


def _normalize_phone(v):
    digits = re.sub(r"[\s().-]", "", v)
    if digits.startswith("+52"):
        digits = digits[3:]
    elif digits.startswith("52") and len(digits) == 12:
        digits = digits[2:]
    return digits


def _phone(v):
    if not v:
        return REQUIRED
    if not re.fullmatch(r"[0-9]{10}", v, re.ASCII):
        return "El teléfono debe tener 10 dígitos."
    return None


def _text_field(label, min_len, max_len, require_alpha=True):
    def check(v):
        if not v:
            return REQUIRED
        if len(v) < min_len:
            return f"{label} es demasiado corto (mínimo {min_len} caracteres)."
        if len(v) > max_len:
            return f"{label} es demasiado largo (máximo {max_len} caracteres)."
        if require_alpha and not any(c.isalpha() for c in v):
            return f"{label} debe contener letras."
        return None
    return check


def _number(v, required):
    if not v:
        return REQUIRED if required else None
    if len(v) > 10 or not _NUMBER_RE.fullmatch(v) or not any(c.isalnum() for c in v):
        return "Usa hasta 10 caracteres (letras, números, guion o /). Ejemplo: 123, 45-B o S/N."
    return None


def _city(v):
    if not v:
        return REQUIRED
    if len(v) < 2 or len(v) > 60 or any(not (c.isalpha() or c in " .'’-") for c in v):
        return "Escribe un nombre de ciudad válido (solo letras)."
    return None


def _postal(v):
    if not v:
        return REQUIRED
    if not _POSTAL_RE.fullmatch(v):
        return "El código postal debe tener 5 dígitos."
    return None


def _references(v):
    if len(v) > 120:
        return "Las referencias no pueden superar 120 caracteres."
    return None


def validate_customer(data):
    """Valida los datos de contacto y entrega. Devuelve el diccionario limpio o lanza ValidationError."""
    if not isinstance(data, dict):
        raise ValidationError("Los datos del cliente son obligatorios.", fields={"_": REQUIRED})

    raw = {k: _clean(data.get(k)) for k in (
        "full_name", "email", "phone", "street", "ext_number", "int_number",
        "neighborhood", "city", "state", "postal_code", "references")}
    raw["email"] = raw["email"].lower()
    raw["phone"] = _normalize_phone(raw["phone"]) if raw["phone"] else ""

    checks = {
        "full_name": _full_name,
        "email": _email,
        "phone": _phone,
        "street": _text_field("La calle", 3, 80),
        "ext_number": lambda v: _number(v, True),
        "int_number": lambda v: _number(v, False),
        "neighborhood": _text_field("La colonia", 3, 60),
        "city": _city,
        "postal_code": _postal,
        "references": _references,
    }
    errors = {}
    for field, check in checks.items():
        problem = check(raw[field])
        if problem:
            errors[field] = problem

    if not raw["state"]:
        errors["state"] = REQUIRED
    elif normalize(raw["state"]) not in _STATES_BY_KEY:
        errors["state"] = "Selecciona un estado de la lista."
    else:
        raw["state"] = _STATES_BY_KEY[normalize(raw["state"])]

    if errors:
        raise ValidationError("Revisa los datos marcados.", fields=errors)
    return raw
