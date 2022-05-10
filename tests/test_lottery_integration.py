from brownie import network
from scripts.deploy_lottery import deploy_lottery
from scripts.tools import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link
import pytest
import time

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})
    fee = lottery.getEntranceFee()
    print(fee)
    lottery.enter({'from': account, 'value': fee})
    lottery.enter({'from': account, 'value': fee})
    fund_with_link(lottery)
    print('Ending lottery...')
    lottery.endLottery({'from': account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0