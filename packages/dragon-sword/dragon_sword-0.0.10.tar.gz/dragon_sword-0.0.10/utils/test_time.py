from unittest import TestCase
from utils.time import get_now, parse_time_str, format_time


class Test(TestCase):
    def test_parse_time_str(self):
        time_str = "2023-01-01 12:12:12"
        self.assertEqual(format_time(parse_time_str(time_str)), time_str)
