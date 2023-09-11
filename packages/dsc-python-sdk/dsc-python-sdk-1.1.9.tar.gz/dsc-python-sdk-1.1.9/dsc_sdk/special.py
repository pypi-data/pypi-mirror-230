from .wallet import Wallet
from .transaction import Transaction
from .tx_types import MsgSendCoin, MsgSellCoin
from .number_helpers import ether_to_wei

def BuildSendAllCoin(signer: Wallet, api, recipient: str, coin_denom: str) -> bytes:
    balances = api.get_account_balances(signer.get_address())
    if coin_denom not in balances:
        raise BuildException(f"account doesn't have coin {coin_denom}")
    full_amount = int(balances[coin_denom])
    amount_to_send = full_amount
    # calculate fee
    if coin_denom != api.get_base_denom():
        msg = MsgSendCoin(signer.get_address(), recipient, coin_denom, str(amount_to_send))
    else:
        # simulate_fee will fail, if we trying to send full amount of base coin
        msg = MsgSendCoin(signer.get_address(), recipient, coin_denom, ether_to_wei(1))
    tx = Transaction().build_tx(msg)
    tx.set_fee(coin_denom, ether_to_wei(1))
    fee_amount = tx.calculate_fee(signer, coin_denom, api)
    # build tx
    amount_to_send = full_amount - fee_amount
    msg = MsgSendCoin(signer.get_address(), recipient, coin_denom, str(amount_to_send))
    tx = Transaction().build_tx(msg)
    tx.set_fee(coin_denom, str(fee_amount))
    return tx.sign(signer)


def BuildSellAllCoin(signer: Wallet, api, coin_sell: str, coin_buy: str) -> bytes:
    balances = api.get_account_balances(signer.get_address())
    if coin_sell not in balances:
        raise BuildException(f"account doesn't have coin {coin_sell}")
    full_amount = int(balances[coin_sell])
    amount_to_sell = full_amount
    # calculate fee
    if coin_sell != api.get_base_denom():
        msg = MsgSellCoin(signer.get_address(), coin_sell, str(amount_to_sell), coin_buy, ether_to_wei(1))
    else:
        # simulate_fee will fail, if we trying to send full amount of base coin
        msg = MsgSellCoin(signer.get_address(), coin_sell, str(amount_to_sell), coin_buy, ether_to_wei(1))
    tx = Transaction().build_tx(msg)
    tx.set_fee(coin_sell, ether_to_wei(1))
    fee_amount = tx.calculate_fee(signer, coin_sell, api)
    # build tx
    amount_to_sell = full_amount - fee_amount
    msg = MsgSellCoin(signer.get_address(), coin_sell, str(amount_to_sell), coin_buy, ether_to_wei(1))
    tx = Transaction().build_tx(msg)
    tx.set_fee(coin_sell, str(fee_amount))
    return tx.sign(signer)

