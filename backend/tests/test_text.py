import unittest

from tienda.text import normalize, plural_units


class TextTests(unittest.TestCase):
    def test_normalize_removes_accents_case_and_extra_spaces(self):
        self.assertEqual(normalize("  CAFÉ   Molído "), "cafe molido")

    def test_plural_units(self):
        self.assertEqual(plural_units(1), "1 unidad")
        self.assertEqual(plural_units(3), "3 unidades")


if __name__ == "__main__":
    unittest.main()
