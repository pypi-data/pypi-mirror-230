import unittest
from dzy import utils
from freezegun import freeze_time


class TestDW(unittest.TestCase):

    @freeze_time("2021-08-01")
    def test_get_today_str(self):

        self.assertEqual(utils.get_today_str(), "20210801")


if __name__ == '__main__':
    unittest.main()
