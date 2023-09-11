from . import hex_to_d0
from .proto.decimal.coin.v1 import tx_pb2 as coin_tx
from .proto.decimal.nft.v1 import tx_pb2 as nft_tx
from .proto.decimal.multisig.v1 import tx_pb2 as multisig_tx
from .proto.decimal.swap.v1 import tx_pb2 as swap_tx
from .proto.decimal.validator.v1 import tx_pb2 as validator_tx
from .proto.decimal.validator.v1 import validator_pb2 as validator_types
from .proto.cosmos.base.v1beta1 import coin_pb2 as cosmos_coin
from .proto.cosmos.crypto.ed25519 import keys_pb2 as ed25519
from .transaction import packToAny

from typing import List


### decimal coin transactions

def MsgCreateCoin(sender: str, denom: str, title: str, crr: int,
                  initial_volume: str, initial_reserve: str, limit_volume: str,
                  identity: str) -> coin_tx.MsgCreateCoin:
    return coin_tx.MsgCreateCoin(
        sender=sender,
        denom=denom,
        title=title,
        crr=crr,
        initial_volume=initial_volume,
        initial_reserve=initial_reserve,
        limit_volume=limit_volume,
        identity=identity,
    )


def MsgUpdateCoin(sender: str, denom: str, limit_volume: str, identity: str, min_volume: str) -> coin_tx.MsgUpdateCoin:
    return coin_tx.MsgUpdateCoin(
        sender=sender,
        denom=denom,
        limit_volume=limit_volume,
        identity=identity,
        min_volume=min_volume,
    )


def MsgBuyCoin(sender: str, denom_to_buy: str, amount_to_buy: str,
               denom_to_sell: str) -> coin_tx.MsgBuyCoin:
    return coin_tx.MsgBuyCoin(
        sender=sender,
        coin_to_buy=cosmos_coin.Coin(denom=denom_to_buy, amount=amount_to_buy),
        max_coin_to_sell=cosmos_coin.Coin(denom=denom_to_sell, amount="0")
    )


def MsgSellCoin(sender: str, denom_to_sell: str, amount_to_sell: str,
                denom_to_buy: str) -> coin_tx.MsgSellCoin:
    return coin_tx.MsgSellCoin(
        sender=sender,
        coin_to_sell=cosmos_coin.Coin(denom=denom_to_sell, amount=amount_to_sell),
        min_coin_to_buy=cosmos_coin.Coin(denom=denom_to_buy, amount="0")
    )


def MsgSendCoin(sender: str, recipient: str, denom: str, amount: str) -> coin_tx.MsgSendCoin:
    if recipient.find('0x') == 0:
        recipient = hex_to_d0(recipient)

    return coin_tx.MsgSendCoin(
        sender=sender,
        recipient=recipient,
        coin=cosmos_coin.Coin(denom=denom, amount=amount)
    )


def MultiSendEntry(recipient: str, denom: str, amount: str) -> coin_tx.MultiSendEntry:
    return coin_tx.MultiSendEntry(
        recipient=recipient,
        coin=cosmos_coin.Coin(denom=denom, amount=amount),
    )


def MsgMultiSendCoin(sender: str, sends: List[coin_tx.MultiSendEntry]) -> coin_tx.MsgMultiSendCoin:
    return coin_tx.MsgMultiSendCoin(
        sender=sender,
        sends=sends,
    )


def MsgBurnCoin(sender: str, denom: str, amount: str) -> coin_tx.MsgBurnCoin:
    return coin_tx.MsgBurnCoin(
        sender=sender,
        coin=cosmos_coin.Coin(denom=denom, amount=amount),
    )


def MsgRedeemCheck(sender: str, check: str, proof: str) -> coin_tx.MsgRedeemCheck:
    return coin_tx.MsgRedeemCheck(
        sender=sender,
        check=check,
        proof=proof,
    )


### decimal multisig transactions

def MsgCreateWallet(sender: str, owners: List[str], weights: List[int], threshold: int) -> multisig_tx.MsgCreateWallet:
    return multisig_tx.MsgCreateWallet(
        sender=sender,
        owners=owners,
        weights=weights,
        threshold=threshold,
    )


def MsgCreateTransaction(sender: str, wallet: str, msg) -> multisig_tx.MsgCreateTransaction:
    return multisig_tx.MsgCreateTransaction(
        sender=sender,
        wallet=wallet,
        content=packToAny(msg),
    )


def MsgSignTransaction(sender: str, id: str) -> multisig_tx.MsgSignTransaction:
    return multisig_tx.MsgSignTransaction(
        sender=sender,
        id=id,
    )


### decimal nft transactions

def MsgMintToken(sender: str, denom: str, token_id: str, token_uri: str, allow_mint: bool,
                 recipient: str, quantity: int, reserve_denom: str, reserve_amount: str) -> nft_tx.MsgMintToken:
    return nft_tx.MsgMintToken(
        sender=sender,
        denom=denom,
        token_id=token_id,
        token_uri=token_uri,
        allow_mint=allow_mint,
        recipient=recipient,
        quantity=quantity,
        reserve=cosmos_coin.Coin(denom=reserve_denom, amount=reserve_amount),
    )


def MsgUpdateToken(sender: str, token_id: str, token_uri: str) -> nft_tx.MsgUpdateToken:
    return nft_tx.MsgUpdateToken(
        sender=sender,
        token_id=token_id,
        token_uri=token_uri,
    )


def MsgUpdateReserve(sender: str, token_id: str, sub_token_ids: List[int],
                     reserve_denom: str, reserve_amount: str) -> nft_tx.MsgUpdateReserve:
    return nft_tx.MsgUpdateReserve(
        sender=sender,
        token_id=token_id,
        sub_token_ids=sub_token_ids,
        reserve=cosmos_coin.Coin(denom=reserve_denom, amount=reserve_amount),
    )


def MsgSendToken(sender: str, recipient: str, token_id: str, sub_token_ids: List[int]) -> nft_tx.MsgSendToken:
    return nft_tx.MsgSendToken(
        sender=sender,
        recipient=recipient,
        token_id=token_id,
        sub_token_ids=sub_token_ids,
    )


def MsgBurnToken(sender: str, token_id: str, sub_token_ids: List[int]) -> nft_tx.MsgBurnToken:
    return nft_tx.MsgBurnToken(
        sender=sender,
        token_id=token_id,
        sub_token_ids=sub_token_ids,
    )


### decimal swap transactions

def MsgInitializeSwap(sender: str, recipient: str, amount: str, token_symbol: str,
                      transaction_number: str, from_chain: int, dest_chain: int) -> swap_tx.MsgInitializeSwap:
    return swap_tx.MsgInitializeSwap(
        sender=sender,
        recipient=recipient,
        amount=amount,
        token_symbol=token_symbol,
        transaction_number=transaction_number,
        from_chain=from_chain,
        dest_chain=dest_chain,
    )


### decimal validator transactions

def MsgCreateValidator(operator_address: str, reward_address: str, pubkey: bytes,
                       moniker: str, identity: str, website: str, security_contact: str, details: str,
                       commission: str, stake_denom: str, stake_amount: str) -> validator_tx.MsgCreateValidator:
    return validator_tx.MsgCreateValidator(
        operator_address=operator_address,
        reward_address=reward_address,
        consensus_pubkey=packToAny(ed25519.PubKey(key=pubkey)),
        description=validator_types.Description(
            moniker=moniker,
            identity=identity,
            website=website,
            security_contact=security_contact,
            details=details,
        ),
        commission=commission,
        stake=cosmos_coin.Coin(denom=stake_denom, amount=stake_amount),
    )


def MsgEditValidator(operator_address: str, reward_address: str,
                     moniker: str, identity: str, website: str, security_contact: str,
                     details: str) -> validator_tx.MsgEditValidator:
    return validator_tx.MsgEditValidator(
        operator_address=operator_address,
        reward_address=reward_address,
        description=validator_types.Description(
            moniker=moniker,
            identity=identity,
            website=website,
            security_contact=security_contact,
            details=details,
        )
    )


def MsgSetOnline(validator: str) -> validator_tx.MsgSetOnline:
    return validator_tx.MsgSetOnline(
        validator=validator
    )


def MsgSetOffline(validator: str) -> validator_tx.MsgSetOffline:
    return validator_tx.MsgSetOffline(
        validator=validator
    )


def MsgDelegate(delegator: str, validator: str,
                coin_denom: str, coin_amount: str) -> validator_tx.MsgDelegate:
    return validator_tx.MsgDelegate(
        delegator=delegator,
        validator=validator,
        coin=cosmos_coin.Coin(denom=coin_denom, amount=coin_amount),
    )


def MsgDelegateNFT(delegator: str, validator: str, token_id: str,
                   sub_token_ids: List[int]) -> validator_tx.MsgDelegateNFT:
    return validator_tx.MsgDelegateNFT(
        delegator=delegator,
        validator=validator,
        token_id=token_id,
        sub_token_ids=sub_token_ids,
    )


def MsgRedelegate(delegator: str, validator_src: str, validator_dst: str,
                  coin_denom: str, coin_amount: str) -> validator_tx.MsgRedelegate:
    return validator_tx.MsgRedelegate(
        delegator=delegator,
        validator_src=validator_src,
        validator_dst=validator_dst,
        coin=cosmos_coin.Coin(denom=coin_denom, amount=coin_amount),
    )


def MsgRedelegateNFT(delegator: str, validator_src: str, validator_dst: str,
                     token_id: str, sub_token_ids: List[int]) -> validator_tx.MsgRedelegateNFT:
    return validator_tx.MsgRedelegateNFT(
        delegator=delegator,
        validator_src=validator_src,
        validator_dst=validator_dst,
        token_id=token_id,
        sub_token_ids=sub_token_ids,
    )


def MsgUndelegate(delegator: str, validator: str,
                  coin_denom: str, coin_amount: str) -> validator_tx.MsgUndelegate:
    return validator_tx.MsgUndelegate(
        delegator=delegator,
        validator=validator,
        coin=cosmos_coin.Coin(denom=coin_denom, amount=coin_amount),
    )


def MsgUndelegateNFT(delegator: str, validator: str, token_id: str,
                     sub_token_ids: List[int]) -> validator_tx.MsgUndelegateNFT:
    return validator_tx.MsgUndelegateNFT(
        delegator=delegator,
        validator=validator,
        token_id=token_id,
        sub_token_ids=sub_token_ids,
    )


def MsgCancelRedelegation(delegator: str, validator_src: str, validator_dst: str, creation_height: int,
                          coin_denom: str, coin_amount: str) -> validator_tx.MsgCancelRedelegation:
    return validator_tx.MsgCancelRedelegation(
        delegator=delegator,
        validator_src=validator_src,
        validator_dst=validator_dst,
        creation_height=creation_height,
        coin=cosmos_coin.Coin(denom=coin_denom, amount=coin_amount),
    )


def MsgCancelRedelegationNFT(delegator: str, validator_src: str, validator_dst: str, creation_height: int,
                             token_id: str, sub_token_ids: List[int]) -> validator_tx.MsgCancelRedelegationNFT:
    return validator_tx.MsgCancelRedelegationNFT(
        delegator=delegator,
        validator_src=validator_src,
        validator_dst=validator_dst,
        creation_height=creation_height,
        token_id=token_id,
        sub_token_ids=sub_token_ids,
    )


def MsgCancelUndelegation(delegator: str, validator: str, creation_height: int,
                          coin_denom: str, coin_amount: str) -> validator_tx.MsgCancelUndelegation:
    return validator_tx.MsgCancelUndelegation(
        delegator=delegator,
        validator=validator,
        creation_height=creation_height,
        coin=cosmos_coin.Coin(denom=coin_denom, amount=coin_amount),
    )


def MsgCancelUndelegationNFT(delegator: str, validator: str, creation_height: int,
                             token_id: str, sub_token_ids: List[int]) -> validator_tx.MsgCancelUndelegationNFT:
    return validator_tx.MsgCancelUndelegationNFT(
        delegator=delegator,
        validator=validator,
        token_id=token_id,
        creation_height=creation_height,
        sub_token_ids=sub_token_ids,
    )
