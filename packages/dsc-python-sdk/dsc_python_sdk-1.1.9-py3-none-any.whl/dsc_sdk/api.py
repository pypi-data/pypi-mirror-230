import requests
import json
from typing import Tuple, Dict, List
import codecs
from .wallet import Wallet
from hexbytes import HexBytes
from eth_account import Account
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from .exceptions import ApiException
from .constants import *
from dataclasses import dataclass

@dataclass
class ERCBalance:
    contract_address: str
    symbol: str
    amount: str
    decimal: int
    token_type: str # may be ERC20, ERC721, ERC1155

class DscAPI:
    """
    Base class to perform operations on Decimal API.
    Create new instance of api with passing base URL to DecimalAPI class.

    gate_url: url to decimal gate
    web3_url: http url to operate with EVM (need for erc20 tokens)
    """

    def __init__(self, gate_url: str, web3_url: str = ""):
        self.gate_url = gate_url
        if self.gate_url[-1] != '/':
            self.gate_url += '/'
        self.web3_url = web3_url
        self.__base_denom = MAINNET_BASE_COIN
        if self.gate_url == MAINNET_GATE:
            self.__base_denom = MAINNET_BASE_COIN
        if self.gate_url == TESTNET_GATE:
            self.__base_denom = TESTNET_BASE_COIN
        if self.gate_url == DEVNET_GATE:
            self.__base_denom = DEVNET_BASE_COIN
    
    def get_parameters(self):
        """
        load base blockchain parameters: chain_id, base denom
        """
        resp = self.__request_gate("rpc/genesis/chain")
        self.__chain_id = resp

    def get_chain_id(self):
        return self.__chain_id

    def get_block_latest(self):
        resp = json.loads(self.__request_gate(f'block/height'))
        try:
            return int(resp)
        except KeyError:
            return 0

    def get_blocks(self, limit: int = 10, offset: int = 0):
        resp = json.loads(self.__request_gate(f'blocks?limit={limit}&offset={offset}'))
        try:
            return resp["result"]
        except KeyError:
            return {}

    def get_block(self, height):
        resp = json.loads(self.__request_gate(f'block/{height}'))
        try:
            return resp["result"]
        except KeyError:
            return {}

    def get_block_validator(self, height):
        resp = json.loads(self.__request_gate(f'block/{height}/validators'))
        try:
            return resp["result"]
        except KeyError:
            return {}

    def get_base_denom(self):
        return self.__base_denom

    def get_account_number_and_sequence(self, address: str) -> Tuple[int, int]:
        self.__validate_address(address)
        resp = json.loads(self.__request_gate(f'rpc/auth/accounts/{address}'))
        try:
            return (int(resp["account"]["base_account"]["account_number"]), int(resp["account"]["base_account"]["sequence"]))
        except KeyError:
            return (0, 0)

    def get_account_balances(self, address: str) -> Dict[str, str]:
        self.__validate_address(address)
        resp = json.loads(self.__request_gate(f'address/{address}/balances'))
        try:
            result = {}
            for k,v in resp["result"].items():
                result[k] = v["amount"]
            return result
        except KeyError:
            return {}

    def get_transactions_address(self, address: str, limit: int = 10, offset: int = 0) -> Dict[str, str]:
        self.__validate_address(address)
        resp = json.loads(self.__request_gate(f'address/{address}/txs?limit={limit}&offset={offset}'))
        try:
            return resp["result"]
        except KeyError:
            return {}

    def get_coin_price(self, symbol: str) -> float:
        resp = json.loads(self.__request_gate(f'coin/{symbol}'))
        try:
            return float(resp["result"]['priceBase'])
        except KeyError:
            return 0.0

    def get_coin_by_symbol(self, symbol: str) -> Dict[str, str]:
        resp = json.loads(self.__request_gate(f'coin/{symbol}'))
        try:
            return resp["result"]['priceBase']
        except KeyError:
            return {}

    def get_coins(self, order: str = 'symbol', type_order: str = 'DESC', limit: int = 100, offset: int = 0) -> Dict[str, str]:
        resp = json.loads(self.__request_gate(f'coins?order[{order}]={type_order}&limit={limit}&offset={offset}'))
        try:
            return resp["result"]
        except KeyError:
            return {}

    def get_nft_tokens(self, address: str) -> Dict[str, str]:
        self.__validate_address(address)
        resp = json.loads(self.__request_gate(f'address/{address}/nfts'))
        try:
            return resp["result"]
        except KeyError:
            return {}

    def get_account_erc_balances(self, hex_address: str) -> List[ERCBalance]:
        resp = json.loads(self.__request_gate(f'evm-accounts/{hex_address}/balance'))
        result = []
        for subkey in ["evmAccountERC20TokenBalances", "evmAccountERC721TokenBalances", "evmAccountERC1155TokenBalances"]:
            for bal in resp["result"]["evmTokenAccountBalances"][subkey]:
                result.append(
                    ERCBalance(bal["evmToken"]["address"], bal["evmToken"]["symbol"], bal["amount"],
                        bal["evmToken"]["decimals"], bal["evmToken"]["evmTokenTypeName"])
                )
        return result

    def broadcast(self, tx_bytes: bytes):
        resp = json.loads(self.__request_gate("rpc/txs", method="post", payload={"hexTx": tx_bytes.hex()}))
        return TxResult(
            hash = resp["result"]["hash"],
            code = resp["result"]["code"],
            log = resp["result"]["log"],
            codespace = resp["result"]["codespace"],
        )

    def calculate_fee(self, tx_bytes: bytes, fee_denom: str) -> str:
        ''' Calculate fee using gateway method /tx/estimate'''
        resp = self.__request_gate("tx/estimate", method="post", payload = {
            "tx_bytes": tx_bytes.hex(),
            "denom": fee_denom,
        })
        obj = json.loads(resp)
        if obj.get("ok", False):
            return obj["result"]["commission"]
        return ""
    
    def get_erc20_tokens(self, limit=10, offset=0):
        ''' Get list of known erc20 token by query gateway '''
        obj = json.loads(self.__request_gate("evm-tokens/list", options={"limit": limit, "offset": offset}))
        if not obj["ok"]:
            return []
        return obj["result"]["evmTokensList"]

    def erc20_build_token(self, name: str, symbol: str, supply: str, max_supply: str,
            mintable: bool, burnable: bool, capped: bool) -> bytes:
        ''' Build smart contract bytecode for erc20 token
        name: human readable long name
        symbol: token symbol (denom)
        supply: initial token supply in eth (bip)
        max_supply: maximal token supply in eth (bip)
        mintable: boolean - allow to mint
        burnable: boolean - allow to burn
        capped: boolean
        '''
        resp = self.__request_gate("evm-token/data", options={
            "name": name,
            "symbol": symbol,
            "supply": supply,
            "maxSupply": max_supply,
            "mintable": mintable,
            "burnable": burnable,
            "capped": capped,
        })
        obj = json.loads(resp)
        if not obj["ok"]:
            return None
        return HexBytes(obj["result"])

    def erc20_create_token(self, wallet: Wallet, contract_bytecode: bytes):
        ethacc = Account.from_key(wallet.get_private_key_bytes())
        w3conn = Web3(Web3.HTTPProvider(self.web3_url))
        w3conn.middleware_onion.add(construct_sign_and_send_raw_middleware(ethacc))
        txhash = w3conn.eth.send_transaction({
            "from": ethacc.address,
            "data": contract_bytecode,
        })
        return w3conn.eth.wait_for_transaction_receipt(txhash)
    
    def erc20_contract_instance(self, wallet: Wallet, address: str, abi):
        ''' Construct contract of web3 where default account is :wallet: '''
        ethacc = Account.from_key(wallet.get_private_key_bytes())
        w3conn = Web3(Web3.HTTPProvider(self.web3_url))
        w3conn.middleware_onion.add(construct_sign_and_send_raw_middleware(ethacc))
        return w3conn.eth.contract(Web3.toChecksumAddress(address), abi=abi)

    @staticmethod
    def __validate_address(address: str):
        if len(address) < 41 or not address.startswith('d0'):
            raise Exception('Invalid address')

    def __request_gate(self, path: str, method: str = 'get', payload=None, options={}):
        url = (self.gate_url + path)
        if method == 'get':
            if len(options) > 0:
                response = requests.get(url, params=options)
            else:
                response = requests.get(url)
        else:
            response = requests.post(url, payload)
        # process errors for rpc
        try:
            obj = json.loads(response.text)
            if ("statusCode" in obj) and ("message" in obj):
                raise ApiException(obj["statusCode"], obj["message"])
        except:
            pass
        return response.text        

class TxResult:
    def __init__(self, hash="", code=0, log="", codespace=""):
        self.hash = hash
        self.code = code
        self.log = log
        self.codespace = codespace

