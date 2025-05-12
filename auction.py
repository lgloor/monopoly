from random import Random
from typing import Callable

from constants import *


def initialize_auction(initiator: str, square_idx: int, state: dict):
    assert state[AUCTION] is None, "Cannot start auction when one is already in progress"
    auction = {
        ASSET: square_idx,
        INITIATOR: initiator,
        PLAYERS: {}
    }

    for p in state[ORDER]:
        if state[PLAYERS][p][BANKRUPT]:
            continue
        auction[PLAYERS][p] = {
            BID: 0,
            LAST_ACTION: CHANGE,
            ROUND: 0,
            WINNER: UNKNOWN
        }

    state[PHASE] = AUCTION
    state[AUCTION] = auction


def get_enabled_auction_actions(player: str, state: dict, simulation: bool = False) -> list[tuple[str, Callable[[], None]]]:
    if state[PLAYERS][player][BANKRUPT]:
        return []

    enabled = []

    if is_bid_enabled(player, state):
        enabled.append(("Bid", lambda: bid(player, state, simulation)))

    return enabled


def is_bid_enabled(player: str, state: dict) -> bool:
    auction_state = state[AUCTION]
    has_enough_money = highest_known_bid(auction_state) < state[PLAYERS][player][MONEY]
    return (common_preconditions(player, auction_state)
            and has_enough_money)


def highest_known_bid(auction_state: dict) -> int:
    max_bid = 0
    players_ = auction_state[PLAYERS]
    for p in players_.keys():
        max_bid = max(max_bid, players_[p][BID])
    return max_bid


def bid(player: str, state: dict, simulation: bool):
    highest_bid = highest_known_bid(state[AUCTION])
    money = state[PLAYERS][player][MONEY]
    if simulation:
        rand = Random(str(state))
        amount = rand.randint(highest_bid, money)
    else:
        while True:
            try:
                amount = int(input(f"Enter your bid (current highest: {highest_bid}, remaining money: {money}): "))
                if not highest_bid + 1 <= amount <= money:
                    raise ValueError
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a valid bid.")

    state[AUCTION][PLAYERS][player][BID] = amount
    state[AUCTION][PLAYERS][player][LAST_ACTION] = BID


def common_preconditions(player: str, auction_state: dict) -> bool:
    passed = auction_state[PLAYERS][player][LAST_ACTION] == PASS
    winner_unknown = auction_state[PLAYERS][player][WINNER] == UNKNOWN
    no_action_in_current_round = auction_state[PLAYERS][player][LAST_ACTION] == CHANGE
    return (not passed
            and winner_unknown
            and no_action_in_current_round
            and is_ready_for_action(player, auction_state)
            and exists_other_player_in_same_round(player, auction_state))


def is_ready_for_action(player: str, auction_state: dict) -> bool:
    players_: dict = auction_state[PLAYERS]
    for p in players_.keys():
        if not (players_[p][ROUND] == players_[player][ROUND]
                or players_[p][LAST_ACTION] == PASS):
            return False
    return True


def exists_other_player_in_same_round(player: str, auction_state: dict) -> bool:
    players_: dict = auction_state[PLAYERS]
    for p in players_.keys():
        if p != player and players_[p][ROUND] == players_[player][ROUND]:
            return True
    return False
