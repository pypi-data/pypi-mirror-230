import unittest
from parameterized import parameterized

from spartaORM.utils.boolean import str_to_bool


class TestStrToBool(unittest.TestCase):
    @parameterized.expand(
        [
            ("True", True),
            ("true", True),
            (True, True),
            ("false", False),
            ("False", False),
            (None, False),
        ]
    )
    def test_str_to_bool(self, value, expected):
        self.assertEqual(str_to_bool(value), expected)
