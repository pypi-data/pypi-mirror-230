import base64

from Crypto.Hash import keccak
from mnemonic import Mnemonic
from coincurve import PublicKey, PrivateKey
from bip32 import BIP32
import bech32
from hexbytes import HexBytes
from web3 import Web3

from .proto.ethermint.crypto.v1.ethsecp256k1 import keys_pb2 as ethermint_crypto

DERIVATION_PATH = "m/44'/60'/0'/0/0"
VALIDATOR_PREFIX = 'd0valoper'
ADDRESS_PREFIX = 'd0'


class Wallet:
    """
    Decimal wallet class
    Wallet() creates wallet with random mnemonic
    """

    def __init__(self, mnemonic: str = None):
        mnemo = Mnemonic('english')
        if not mnemonic:
            mnemonic = mnemo.generate()

        if not mnemo.check(mnemonic):
            raise Exception('Invalid Mnemonic')
        self.__mnemonic = mnemonic

        # Generate and save seed
        seed = mnemo.to_seed(mnemonic)
        self._seed = seed
        self._sequence = 0
        self._chain_id = ""
        # Derive public key
        self.__generate_keys()
        self.__generate_address()
        self.__generate_validator_address()

    def get_address(self) -> str:
        '''
        returns addres of the wallet
        '''
        return self._address

    def get_ethereum_address(self) -> str:
        '''
        returns hex addres of the wallet in lower case (need for search)
        '''
        return self._ethereum_address

    def get_checksum_address(self) -> str:
        '''
        returns hex addres of the wallet in mixed case (need for contract calls)
        '''
        return self._checksum_address

    def get_mnemonic(self) -> str:
        '''
        returns mnemonic of the wallet
        '''
        return self.__mnemonic

    def get_validator_address(self) -> str:
        '''
        returns validator of the wallet
        '''
        return self._validator_address

    def get_private_key_bytes(self) -> str:
        '''
        generates private key
        '''
        return self._private_key

    def get_public_key_bytes(self) -> str:
        '''
        generates public key
        '''
        return self._public_key

    def get_public_key(self) -> ethermint_crypto.PubKey:
        return self._public_key_eth

    def set_sequence(self, seq: int):
        '''
        set wallet sequence
        '''
        self._sequence = seq

    def get_sequence(self) -> int:
        '''
        get wallet sequence
        '''
        return self._sequence

    def increment_sequence(self):
        self._sequence += 1

    def set_chain_id(self, chain_id: str):
        '''
        set chain id for transaction signing
        '''
        self._chain_id = chain_id

    def get_chain_id(self) -> str:
        '''
        get chain id
        '''
        return self._chain_id

    def set_account_number(self, acc_number: int):
        '''
        set account number for transaction signing
        '''
        self._account_number = acc_number

    def get_account_number(self) -> int:
        '''
        get account number
        '''
        return self._account_number

    def __generate_address(self):
        prepared_hash = self.__hash_public_key()
        address = bech32.bech32_encode(ADDRESS_PREFIX, bech32.convertbits(prepared_hash, 8, 5))
        self._address = address
        self._ethereum_address = HexBytes(prepared_hash).hex()
        self._checksum_address = Web3.toChecksumAddress(self._ethereum_address)

    def __generate_validator_address(self):
        prepared_hash = self.__hash_public_key()
        address = bech32.bech32_encode(VALIDATOR_PREFIX, bech32.convertbits(prepared_hash, 8, 5))
        self._validator_address = address

    def __generate_keys(self):
        bip32 = BIP32.from_seed(self._seed)
        self._private_key = bip32.get_privkey_from_path(DERIVATION_PATH)
        self._public_key_binary = PublicKey.from_valid_secret(self._private_key).format(compressed=False)
        self._public_key = base64.b64encode(self._public_key_binary)
        self._public_key_eth = ethermint_crypto.PubKey(
            key=PublicKey.from_valid_secret(self._private_key).format(compressed=True)
        )
        self._private_key_eth = PrivateKey(
            secret=self._private_key
        )

    def __hash_public_key(self):
        # ethereum address calculation
        keccak_hash = keccak.new(data=self._public_key_binary[1:], digest_bits=256).digest()[-20:]
        return keccak_hash

    def sign_bytes(self, msg: bytes) -> bytes:
        return self._private_key_eth.sign_recoverable(msg, hasher=None)


def check_address_validity(address: str) -> bool:
    prefix, addr_bytes = bech32.bech32_decode(address)
    if prefix != ADDRESS_PREFIX:
        return False
    if prefix == None or addr_bytes == None:
        return False
    if len(addr_bytes) != 32:
        return False
    return True


def d0_to_hex(address: str) -> str:
    prefix, addr_bytes = bech32.bech32_decode(address)
    if prefix == None or addr_bytes == None:
        return None
    addr5to8 = bech32.convertbits(addr_bytes, 5, 8)
    return HexBytes(bytes(addr5to8)).hex()


def hex_to_d0(address: str) -> str:
    addr8to5 = bech32.convertbits(HexBytes(address), 8, 5)
    return bech32.bech32_encode(ADDRESS_PREFIX, addr8to5)


def checksum_address(address: str) -> str:
    return Web3.toChecksumAddress(address)
