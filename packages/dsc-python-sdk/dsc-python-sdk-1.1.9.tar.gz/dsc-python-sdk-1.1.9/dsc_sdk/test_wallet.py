import unittest

from .wallet import Wallet, check_address_validity, d0_to_hex, hex_to_d0

class TestWallet(unittest.TestCase):
    def test_wallet_create(self):
        w = Wallet()
        self.assertEqual(w.get_address()[:3], "d01")
    def test_wallet_mnemonic(self):
        w = Wallet("error crane rich oval street radar price bundle very lava climb siege comic tell wrong ten gap silent shine lawsuit wise horse ball pretty")
        self.assertEqual(w.get_address(), "d01uhvauapn5slk2wq4tglxvctl4qlylnqdu9q0qd")
        w = Wallet("mad kitten give wine plate gadget hungry reject cram junior swing jealous various genre method wheel pulp symbol fun silent blossom urban blur vapor")
        self.assertEqual(w.get_address(), "d01plcsd4tfrzggxf3znv09gk437r87gee4qf94zx")
    def test_address_validity(self):
        self.assertTrue(check_address_validity("d01uhvauapn5slk2wq4tglxvctl4qlylnqdu9q0qd"))
        self.assertFalse(check_address_validity("d01uhvauapn5slk2wq4tglxvctl4qlylnqdu9q0q"))
    def test_address_conversion(self):
        self.assertEqual(d0_to_hex("d01tlykyxn3zddwm7w89raurwuvwa5apv4w4dgzyk"), "0x5fc9621a71135aedf9c728fbc1bb8c7769d0b2ae")
        