import unittest

from .tx_types import *

class TestConstructors(unittest.TestCase):
    ### coin
    def test_create_coin(self):
        msg = MsgCreateCoin("d01", "del", "deldeldel", 10, "1000000000", "1000000000", "1000000000", "asjdgajghsd")
        self.assertTrue(msg.IsInitialized())
    def test_update_coin(self):
        msg = MsgUpdateCoin("d01", "del", "1000000000", "asjdgajghsd")
        self.assertTrue(msg.IsInitialized())
    def test_buy_coin(self):
        msg = MsgBuyCoin("d01", "del", "1000000000", "asg", "10000")
        self.assertTrue(msg.IsInitialized())
    def test_sell_coin(self):
        msg = MsgSellCoin("d01", "del", "1000000000", "asg", "10000")
        self.assertTrue(msg.IsInitialized())
    def test_send_coin(self):
        msg = MsgSendCoin("d01", "d01", "del", "1000000000")
        self.assertTrue(msg.IsInitialized())
    def test_multi_send_coin(self):
        sends = [
            MultiSendEntry("d011", "del", "100"),
            MultiSendEntry("d012", "del", "200"),
        ]
        msg = MsgMultiSendCoin("d01", sends)
        self.assertTrue(msg.IsInitialized())
    def test_burn_coin(self):
        msg = MsgBurnCoin("d01", "del", "123")
        self.assertTrue(msg.IsInitialized())
    def test_redeem_check(self):
        msg = MsgRedeemCheck("d01", "abcdef0123", "123")
        self.assertTrue(msg.IsInitialized())

    ### multisig
    def test_create_wallet(self):
        msg = MsgCreateWallet("d01", ["d011", "d012"], [1,2], 3)
        self.assertTrue(msg.IsInitialized())
    def test_create_transaction(self):
        submsg = MsgBuyCoin("d01", "del", "1000000000", "asg", "10000")
        msg = MsgCreateTransaction("d01", "d01www", submsg)
        self.assertTrue(msg.IsInitialized())
    def test_sign_transaction(self):
        msg = MsgSignTransaction("d01", "d0mstx1")
        self.assertTrue(msg.IsInitialized())
    
    ### nft
    def test_mint_token(self):
        msg = MsgMintToken("d01", "nftcollection", "asad3413asd", "https://localhost:1111",
            True, "d01aaa", 10, "del", "123")
        self.assertTrue(msg.IsInitialized())
    def test_update_token(self):
        msg = MsgUpdateToken("d01", "asd1232", "https://localhost:123")
        self.assertTrue(msg.IsInitialized())
    def test_update_reserve(self):
        msg = MsgUpdateReserve("d01", "asvasdasd", [1,2,3], "del", "123")
        self.assertTrue(msg.IsInitialized())
    def test_send_token(self):
        msg = MsgSendToken("d01", "d01aaa", "aaasdasd", [1,2,3])
        self.assertTrue(msg.IsInitialized())
    def test_burn_token(self):
        msg = MsgBurnToken("d01", "asdasda", [1,2,3])
        self.assertTrue(msg.IsInitialized())
    
    ### swap
    def test_initalize_swap(self):
        msg = MsgInitializeSwap("d01", "d01aaa", "123", "tdel", "123456", 1, 2)
        self.assertTrue(msg.IsInitialized())
    
    ### validator
    def test_create_validator(self):
        msg = MsgCreateValidator("d0valoper1asa", "d01aaa", b"asdaas",
            "moniker", "identity", "https://website", "security_contact@website", "details",
            "0.11", "del", "123")
        self.assertTrue(msg.IsInitialized())
    def test_edit_validator(self):
        msg = MsgEditValidator("d0valoper1asa", "d01aaa",
            "moniker", "identity", "https://website", "security_contact@website", "details")
        self.assertTrue(msg.IsInitialized())
    def test_set_online(self):
        msg = MsgSetOnline("d0valoper1aaa")
        self.assertTrue(msg.IsInitialized())
    def test_set_offline(self):
        msg = MsgSetOffline("d0valoper1aaa")
        self.assertTrue(msg.IsInitialized())
    def test_delegate(self):
        msg = MsgDelegate("d01aaa", "d0valoper1bbbb", "del", "1000000")
        self.assertTrue(msg.IsInitialized())
    def test_delegate_nft(self):
        msg = MsgDelegateNFT("d01aaa", "d0valoper1bbbb", "tokenasasas", [1,2,3])
        self.assertTrue(msg.IsInitialized())
    def test_redelegate(self):
        msg = MsgRedelegate("d01aaa", "d0valoper1bbbbb", "d0valoper1cccc", "del", "1000202")
        self.assertTrue(msg.IsInitialized())
    def test_redelegate_nft(self):
        msg = MsgRedelegateNFT("d01aaa", "d0valoper1bbbbb", "d0valoper1cccc", "tokenaaaaa", [1,2,3])
        self.assertTrue(msg.IsInitialized())
    def test_undelegate(self):
        msg = MsgUndelegate("d01aaa", "d0valoper1bbbbb", "del", "1000202")
        self.assertTrue(msg.IsInitialized())
    def test_undelegate_nft(self):
        msg = MsgUndelegateNFT("d01aaa", "d0valoper1bbbbb", "tokenaaaa", [1,2,3])
        self.assertTrue(msg.IsInitialized())
    def test_cancel_redelegation(self):
        msg = MsgCancelRedelegation("d01aaa", "d0valoper1bbbbb", "d0valoper1cccc", 100, "del", "1000202")
        self.assertTrue(msg.IsInitialized())
    def test_cancel_redelegation_nft(self):
        msg = MsgCancelRedelegationNFT("d01aaa", "d0valoper1bbbbb", "d0valoper1cccc", 100, "tokenaaaa", [1,2,3])
        self.assertTrue(msg.IsInitialized())
    def test_cancel_undelegation(self):
        msg = MsgCancelUndelegation("d01aaa", "d0valoper1bbbbb", 100, "del", "1000202")
        self.assertTrue(msg.IsInitialized())
    def test_cancel_undelegation_nft(self):
        msg = MsgCancelUndelegationNFT("d01aaa", "d0valoper1bbbbb", 100, "tokenaaaa", [1,2,3])
        self.assertTrue(msg.IsInitialized())