import unittest

from tienda.errors import ValidationError
from tienda.validators import parse_quantity, validate_customer
from tests.helpers import CUSTOMER


class ParseQuantityTests(unittest.TestCase):
    def test_valid_values(self):
        self.assertEqual(parse_quantity(3), 3)
        self.assertEqual(parse_quantity("4"), 4)
        self.assertEqual(parse_quantity(2.0), 2)

    def test_invalid_values(self):
        for bad in (0, -1, "-3", "abc", "", None, 1.5, True, [], "1e3", 100):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    parse_quantity(bad)


class CustomerValidationTests(unittest.TestCase):
    def fields_with(self, **changes):
        data = {**CUSTOMER, **changes}
        with self.assertRaises(ValidationError) as ctx:
            validate_customer(data)
        return ctx.exception.fields

    def test_valid_customer_is_normalized(self):
        clean = validate_customer({**CUSTOMER, "email": " MARIA@Example.COM ", "state": "chihuahua"})
        self.assertEqual(clean["email"], "maria@example.com")
        self.assertEqual(clean["phone"], "6561234567")
        self.assertEqual(clean["state"], "Chihuahua")

    def test_phone_accepts_country_code(self):
        self.assertEqual(validate_customer({**CUSTOMER, "phone": "+52 (656) 123-4567"})["phone"], "6561234567")

    def test_optional_fields_can_be_missing(self):
        data = {k: v for k, v in CUSTOMER.items() if k not in ("int_number", "references")}
        self.assertEqual(validate_customer(data)["int_number"], "")

    def test_missing_required_fields(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_customer({})
        for field in ("full_name", "email", "phone", "street", "ext_number",
                      "neighborhood", "city", "state", "postal_code"):
            self.assertIn(field, ctx.exception.fields)
        self.assertNotIn("int_number", ctx.exception.fields)

    def test_not_a_dict(self):
        with self.assertRaises(ValidationError):
            validate_customer("hola")

    def test_name_rules(self):
        self.assertIn("full_name", self.fields_with(full_name="María"))
        self.assertIn("full_name", self.fields_with(full_name="Maria 123"))
        self.assertIn("full_name", self.fields_with(full_name="   "))

    def test_email_rules(self):
        for bad in ("maria", "maria@", "maria@dominio", "@dominio.com", "ma..ria@dominio.com", "maria@dom ino.com"):
            with self.subTest(email=bad):
                self.assertIn("email", self.fields_with(email=bad))

    def test_phone_rules(self):
        for bad in ("12345", "abcdefghij", "65612345678901"):
            with self.subTest(phone=bad):
                self.assertIn("phone", self.fields_with(phone=bad))

    def test_postal_code_rules(self):
        for bad in ("3200", "320000", "abcde", "32 00"):
            with self.subTest(cp=bad):
                self.assertIn("postal_code", self.fields_with(postal_code=bad))

    def test_state_must_be_in_list(self):
        self.assertIn("state", self.fields_with(state="Narnia"))

    def test_exterior_number_rules(self):
        self.assertIn("ext_number", self.fields_with(ext_number="@@"))
        self.assertIn("ext_number", self.fields_with(ext_number="12345678901"))
        self.assertEqual(validate_customer({**CUSTOMER, "ext_number": "S/N"})["ext_number"], "S/N")

    def test_city_rejects_digits(self):
        self.assertIn("city", self.fields_with(city="Juárez 2"))

    def test_references_too_long(self):
        self.assertIn("references", self.fields_with(references="x" * 121))


if __name__ == "__main__":
    unittest.main()
