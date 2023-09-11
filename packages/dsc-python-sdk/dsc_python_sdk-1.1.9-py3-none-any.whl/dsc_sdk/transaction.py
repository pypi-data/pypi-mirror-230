from .proto.cosmos.tx.v1beta1 import tx_pb2 as cosmos_tx
from .proto.cosmos.tx.signing.v1beta1 import signing_pb2 as cosmos_signing
from .proto.cosmos.base.v1beta1 import coin_pb2 as cosmos_coin

import google.protobuf.any_pb2 as any_pb2

from .wallet import Wallet
from .exceptions import BuildException
from Crypto.Hash import keccak
import ctypes

from decimal import Decimal

class Transaction:
    def __init__(self):
        self._tx_body = None
        self._auth_info = None
        self._fee = None

    @classmethod
    def build_tx(self, msg):
        tx = Transaction()
        tx._tx_body = cosmos_tx.TxBody(
            messages = [packToAny(msg)],
            memo = "",
        )
        tx._fee = cosmos_tx.Fee(
            gas_limit = 0,
        )
        return tx

    def set_memo(self, memo: str):
        self._tx_body.memo = memo

    def set_fee(self, denom: str, amount: str):
        if amount == "0":
            self._fee = cosmos_tx.Fee(
                gas_limit = 0,
            )
        else:
            self._fee = cosmos_tx.Fee(
                amount = [cosmos_coin.Coin(denom=denom, amount=amount)],
                gas_limit = 0,
            )
    
    def sign(self, signer: Wallet) -> bytes:
        auth_info  = cosmos_tx.AuthInfo(
            signer_infos = [
                cosmos_tx.SignerInfo(
                    public_key = packToAny(signer.get_public_key()),
                    mode_info = cosmos_tx.ModeInfo(single=cosmos_tx.ModeInfo.Single(mode=1)),
                    sequence = signer.get_sequence(),
                )
            ],
            fee = self._fee,
        )
        signDoc = cosmos_tx.SignDoc(
            body_bytes = self._tx_body.SerializeToString(deterministic=True),
            auth_info_bytes = auth_info.SerializeToString(deterministic=True),
            chain_id = signer.get_chain_id(),
            account_number = signer.get_account_number(),
        )        
        hsh = keccak.new(data=signDoc.SerializeToString(deterministic=True), digest_bits=256).digest()
        signature = signer.sign_bytes(hsh)
        txraw = cosmos_tx.TxRaw(
            body_bytes = self._tx_body.SerializeToString(),
            auth_info_bytes = auth_info.SerializeToString(),
            signatures = [signature],
        )
        return txraw.SerializeToString(deterministic=True)

    def calculate_fee(self, signer: Wallet, denom: str, api):
        '''
        calculate fee in coin 'denom' by use api.calculate_fee
        '''
        bz = self.sign(signer)
        fail_count = 0
        old_amount = 0
        amount = 1
        while old_amount != amount:
            comm = api.calculate_fee(bz, denom)
            if comm != "":
                old_amount = amount
                amount = int(comm)
                #+10% for additional bytes after set_fee and possible price changes
                amount = (Decimal(amount)*Decimal(1.1)).to_integral_value()
                self.set_fee(denom, str(amount))
            else:
                raise BuildException("can't calculate fee")
        return amount
        

def packToAny(msg) -> any_pb2.Any:
    any = any_pb2.Any()
    any.Pack(msg, type_url_prefix='/')
    return any