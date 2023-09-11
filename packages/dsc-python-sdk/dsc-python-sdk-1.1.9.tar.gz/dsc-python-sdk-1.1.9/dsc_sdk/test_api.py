import unittest

from .api import DscAPI
from .constants import *

class TestAPI(unittest.TestCase):
    def test_construct1(self):
        dsc = DscAPI(MAINNET_GATE, MAINNET_WEB3)
        self.assertEqual(dsc.get_base_denom(), MAINNET_BASE_COIN)
    def test_construct2(self):
        dsc = DscAPI(MAINNET_GATE)
        self.assertEqual(dsc.get_base_denom(), MAINNET_BASE_COIN)
    def test_construct3(self):
        dsc = DscAPI(TESTNET_GATE)
        self.assertEqual(dsc.get_base_denom(), TESTNET_BASE_COIN)
    def test_construct3(self):
        dsc = DscAPI(DEVNET_GATE)
        self.assertEqual(dsc.get_base_denom(), DEVNET_BASE_COIN)
