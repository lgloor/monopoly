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


def get_enabled_auction_actions(player: str, state: dict, sim: bool = False) -> list[tuple[str, Callable[[], str]]]:
    if state[PLAYERS][player][BANKRUPT]:
        return []

    enabled = []

    if is_stand_enabled(player, state):
        enabled.append(("Stand (You have the highest current bid)",
                        lambda: stand(player, state)))
    if is_bid_enabled(player, state):
        enabled.append(("Bid",
                        lambda: bid(player, state, sim)))
    if is_pass_enabled(player, state):
        enabled.append(("Pass",
                        lambda: do_pass(player, state)))
    if is_next_round_enabled(player, state):
        enabled.append(("Next round",
                        lambda: next_round(player, state)))
    if is_choose_winner_enabled(player, state):
        enabled.append(("Choose winner",
                        lambda: choose_winner(player, state)))
    if is_close_action_enabled(player, state):
        enabled.append(("Close auction",
                        lambda: close_auction(player, state)))

    return enabled


def is_stand_enabled(player: str, state: dict) -> bool:
    auction_state = state[AUCTION]
    return (common_preconditions(player, auction_state)
            and all_other_bids_lower(player, auction_state))


def all_other_bids_lower(player: str, auction_state: dict) -> bool:
    players: dict = auction_state[PLAYERS]
    for p in players.keys():
        if p != player and players[p][BID] >= players[player][BID]:
            return False
    return True


def stand(player: str, state: dict):
    state[AUCTION][PLAYERS][player][LAST_ACTION] = STAND
    return f"{player} stands with a bid of {state[AUCTION][PLAYERS][player][BID]}"


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


def bid(player: str, state: dict, sim: bool):
    highest_bid = highest_known_bid(state[AUCTION])
    money = state[PLAYERS][player][MONEY]
    if sim:
        rand = Random(str(state))
        amount = rand.randint(highest_bid + 1, money)
    else:
        amount = get_int_from_input_in_range(
            f"Enter your bid (current highest: {highest_bid}, remaining money: {money}): ",
            highest_bid + 1, money)

    state[AUCTION][PLAYERS][player][BID] = amount
    state[AUCTION][PLAYERS][player][LAST_ACTION] = BID
    return f"{player} bids {amount}"


def is_pass_enabled(player: str, state: dict) -> bool:
    return common_preconditions(player, state[AUCTION])


def do_pass(player: str, state: dict):
    state[AUCTION][PLAYERS][player][LAST_ACTION] = PASS
    return f"{player} passes"


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


def is_next_round_enabled(player: str, state: dict) -> bool:
    passed = state[AUCTION][PLAYERS][player][LAST_ACTION] == PASS
    winner_unknown = state[AUCTION][PLAYERS][player][WINNER] == UNKNOWN
    made_action_in_current_round = state[AUCTION][PLAYERS][player][LAST_ACTION] != CHANGE
    return (not passed
            and winner_unknown
            and made_action_in_current_round
            and all_made_action_or_are_ahead(player, state))


def all_made_action_or_are_ahead(player: str, state: dict) -> bool:
    players: dict = state[AUCTION][PLAYERS]
    for p2 in players.keys():
        passed = players[p2][LAST_ACTION] == PASS
        made_action = (players[p2][LAST_ACTION] != CHANGE
                       or players[p2][ROUND] > players[player][ROUND])
        if not (passed or made_action):
            return False
    return True


def next_round(player: str, state: dict):
    state[AUCTION][PLAYERS][player][LAST_ACTION] = CHANGE
    state[AUCTION][PLAYERS][player][ROUND] += 1
    return f"{player} moves to next round ({state[AUCTION][PLAYERS][player][ROUND]})"


def is_choose_winner_enabled(player: str, state: dict) -> bool:
    winner_unknown = state[AUCTION][PLAYERS][player][WINNER] == UNKNOWN
    return (winner_unknown
            and (all_have_passed(state)
                 or winner_exists(state)))


def all_have_passed(state: dict) -> bool:
    players: dict = state[AUCTION][PLAYERS]
    for p in players.keys():
        if players[p][LAST_ACTION] != PASS:
            return False
    return True


def winner_exists(state: dict) -> bool:
    players: dict = state[AUCTION][PLAYERS]
    for p in players.keys():
        if meets_winning_conditions(p, state):
            return True
    return False


def meets_winning_conditions(player: str, state: dict) -> bool:
    players = state[AUCTION][PLAYERS]

    if players[player][LAST_ACTION] == PASS:
        return False

    others = set(players.keys()).difference({player})
    for p2 in others:
        if (players[p2][LAST_ACTION] != PASS
                or players[player][BID] <= players[p2][BID]
                or players[player][ROUND] <= players[p2][ROUND]):
            return False
    return True


def choose_winner(player: str, state: dict):
    if all_have_passed(state):
        winner = NONE
    else:
        winner = get_winner(state)

    state[AUCTION][PLAYERS][player][WINNER] = winner
    return f"{player} chooses {winner} as the winner of the auction"


def get_winner(state: dict) -> str:
    players = state[AUCTION][PLAYERS]
    for p in players.keys():
        if players[p][LAST_ACTION] != PASS:
            return p
    return ""  # never happens because of the check in is_choose_winner_enabled


def is_close_action_enabled(player: str, state: dict) -> bool:
    is_initiator = state[AUCTION][INITIATOR] == player
    return (is_initiator
            and all_chose_winner(state))


def all_chose_winner(state: dict) -> bool:
    players: dict = state[AUCTION][PLAYERS]
    for p in players.keys():
        if players[p][WINNER] == UNKNOWN:
            return False
    return True


def close_auction(player: str, state: dict):
    auction_state = state[AUCTION]
    winner = auction_state[PLAYERS][player][WINNER]

    state[PHASE] = DOUBLES_CHECK
    state[AUCTION] = None
    if winner != NONE:
        pay_bank(winner, state, auction_state[PLAYERS][winner][BID])
        state[BOARD][auction_state[ASSET]][OWNER] = winner
    return f"{player} closes auction"
