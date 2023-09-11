import unittest

from .number_helpers import ether_to_wei, finney_to_wei

class TestHelpers(unittest.TestCase):
    def test_ether_to_wei(self):
        self.assertEqual("1000000000000000000", ether_to_wei(1))
        self.assertEqual("30000000000000000000", ether_to_wei(30))
    def test_finney_to_wei(self):
        self.assertEqual("1000000000000000", finney_to_wei(1))
        self.assertEqual("30000000000000000", finney_to_wei(30))
