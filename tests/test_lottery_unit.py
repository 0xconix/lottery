from asyncio import exceptions
from brownie import network
import pytest
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery
from scripts.tools import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link, get_contract
from brownie import exceptions

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()

    # 2,000 eth / usd
    # usdEntryFee is 5
    # 2000/1 == 5/x == 0.0025
    expected_entrance_fee = Web3.toWei(0.0025, 'ether')
    entrance_fee = lottery.getEntranceFee()
    assert expected_entrance_fee == entrance_fee

def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({'from': get_account(), 'value': lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    assert lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({'from': account})
    assert lottery.lottery_state() == 2 # CALCULATING_WINNER

def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    lottery.enter({'from': get_account(index=1), 'value': lottery.getEntranceFee()})
    lottery.enter({'from': get_account(index=2), 'value': lottery.getEntranceFee()})
    fund_with_link(lottery)
    tx = lottery.endLottery({'from': account})
    request_id = tx.events['RequestedRandomness']['requestId']
    STATIC_RNG = 777
    get_contract('vrf_coordinator').callBackWithRandomness(
        request_id,
        777,
        lottery.address,
        {'from': account}
    )
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    # 777 % 3 = 0
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
