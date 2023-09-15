import unittest

from spartaORM.utils.date import str_to_date


class TestStrToDate(unittest.TestCase):
    def test_str_to_date(self):
        date_from_str = str_to_date(date_str="2019-01-01")

        self.assertEqual(date_from_str.year, 2019)

    def test_str_to_date_with_format(self):
        date_from_str = str_to_date(date_str="01/01/2019", format="%d/%m/%Y")

        self.assertEqual(date_from_str.year, 2019)
