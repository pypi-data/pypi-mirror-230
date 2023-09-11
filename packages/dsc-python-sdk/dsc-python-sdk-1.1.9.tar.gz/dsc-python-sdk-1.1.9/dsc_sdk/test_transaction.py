import unittest

from .proto.cosmos.base.v1beta1 import coin_pb2 as cosmos_coin

from .wallet import Wallet
from .transaction import Transaction
from .tx_types import MsgSendCoin
from .number_helpers import ether_to_wei

class TestTransaction(unittest.TestCase):
    def test_signing_bytes(self):
        self.maxDiff = None
        w1 = Wallet("plug tissue today frown increase race brown sail post march trick coconut laptop churn call child question match also spend play credit already travel")
        w2 = Wallet("layer pass tide basic raccoon olive trust satoshi coil harbor script shrimp health gadget few armed rival spread release welcome long dust almost banana")
        w1.set_account_number(173)
        w1.set_sequence(0)
        w1.set_chain_id("decimal_2020-22110900")
        msg = MsgSendCoin(w1.get_address(), w2.get_address(), "del", ether_to_wei(1))
        tx = Transaction.build_tx(msg)
        tx.set_memo("hello")
        bz = tx.sign(w1)
        self.assertEqual(bz.hex(), "0a9c010a92010a1c2f646563696d616c2e636f696e2e76312e4d736753656e64436f696e12720a29643031746c796b79786e337a6464776d377738397261757277757677613561707634773464677a796b122964303130647461766570683271303378333234346475766d643932676b7767796c6c3538636c3273761a1a0a0364656c121331303030303030303030303030303030303030120568656c6c6f125b0a570a4f0a282f65746865726d696e742e63727970746f2e76312e657468736563703235366b312e5075624b657912230a2103915d3a632aaec661cc693adb5341a5f104661e6f7a85db9df1d8a7a332f781fe12040a02080112001a41e951ac69ae665fa65f8193edec60f65318c335d49ff8e09b5aa43765ef54315a731345a99080b73b37511ad14c79159491be3b99adacec054c3ad44a364f4e7000")
