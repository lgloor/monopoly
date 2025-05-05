from random import Random
from typing import Callable

import constants
from constants import *


def get_enabled_post_roll_actions(player: str, state: dict) -> list[tuple[str, Callable[[], None]]]:
    enabled = []
    if (is_do_nothing_on_own_property_enabled(player, state)
            or is_do_nothing_on_go_enabled(player, state)
            or is_do_nothing_on_free_parking_enabled(player, state)
            or is_do_nothing_on_jail_enabled(player, state)
            or is_do_nothing_on_mortgaged_property_enabled(player, state)):
        enabled.append(('Do nothing',
                        lambda: end_post_roll(state)))
    if is_pay_street_or_rail_rent_enabled(player, state):
        enabled.append((f'Pay rent for {state[BOARD][state[PLAYERS][player][POSITION]][NAME]}',
                        lambda: pay_street_or_rail_rent(player, state)))
    if is_prevent_bankruptcy_on_street_or_rail_rent_enabled(player, state):
        enabled.append((f'Prevent bankruptcy on rent for {state[BOARD][state[PLAYERS][player][POSITION]][NAME]}',
                        lambda: prevent_bankruptcy_on_street_or_rail_rent(player, state)))
    if is_try_pay_util_rent_enabled(player, state):
        enabled.append(('Try to pay utility rent',
                        lambda: try_pay_util_rent(player, state)))
    if is_pay_tax_enabled(player, state):
        enabled.append(('Pay tax',
                        lambda: pay_tax(player, state)))
    if is_prevent_bankruptcy_on_tax_enabled(player, state):
        enabled.append(('Prevent bankruptcy on tax',
                        lambda: prevent_bankruptcy_on_tax(player, state)))
    if is_buy_property_enabled(player, state):
        enabled.append((f'Buy property {state[BOARD][state[PLAYERS][player][POSITION]][NAME]}',
                        lambda: buy_property(player, state)))
    if is_auction_property_enabled(player, state):
        enabled.append((f'Auction property {state[BOARD][state[PLAYERS][player][POSITION]][NAME]}',
                        lambda: auction_property(player, state)))
    if is_draw_and_execute_card_enabled(player, state):
        enabled.append(('Draw and execute card',
                        lambda: draw_and_execute_card(player, state)))
    return enabled


def is_do_nothing_on_own_property_enabled(player: str, state: dict) -> bool:
    square = state[BOARD][state[PLAYERS][player][POSITION]]
    return is_property(square) and square[OWNER] == player


def is_do_nothing_on_go_enabled(player: str, state: dict) -> bool:
    square = state[BOARD][state[PLAYERS][player][POSITION]]
    return square[TYPE] == GO


def is_do_nothing_on_free_parking_enabled(player: str, state: dict) -> bool:
    square = state[BOARD][state[PLAYERS][player][POSITION]]
    return square[TYPE] == FREE_PARKING


def is_do_nothing_on_jail_enabled(player: str, state: dict) -> bool:
    square = state[BOARD][state[PLAYERS][player][POSITION]]
    return square[TYPE] == JAIL


def is_do_nothing_on_mortgaged_property_enabled(player: str, state: dict) -> bool:
    square = state[BOARD][state[PLAYERS][player][POSITION]]
    return is_property(square) and square[MORTGAGED]


def end_post_roll(state: dict):
    state[PHASE] = DOUBLES_CHECK


def is_pay_street_or_rail_rent_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    if (square[TYPE] not in {STREET, RAIL}
            or square[OWNER] in {None, player}):
        return False

    rent = square[RENT][square[LEVEL]]
    money = state[PLAYERS][player][MONEY]
    return not square[MORTGAGED] and money >= rent


def pay_street_or_rail_rent(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    owner = square[OWNER]
    rent = square[RENT][square[LEVEL]]
    pay_player(player, owner, rent, state)
    state[PHASE] = DOUBLES_CHECK


def is_prevent_bankruptcy_on_street_or_rail_rent_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    if (square[TYPE] not in {STREET, RAIL}
            or square[OWNER] in {None, player}):
        return False

    rent = square[RENT][square[LEVEL]]
    money = state[PLAYERS][player][MONEY]
    return not square[MORTGAGED] and money < rent


def prevent_bankruptcy_on_street_or_rail_rent(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    owner = square[OWNER]
    rent = square[RENT][square[LEVEL]]

    debt = {
        CREDITOR: owner,
        DEBT: rent,
        NEXT_PHASE: DOUBLES_CHECK
    }

    state[DEBT] = debt
    state[PHASE] = BANKRUPTCY_PREVENTION


def is_try_pay_util_rent_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return square[TYPE] == UTILITY and square[OWNER] not in {None, player} and not square[MORTGAGED]


def try_pay_util_rent(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    level = square[LEVEL]

    rand = Random(str(state))
    d1 = rand.randint(1, 6)
    d2 = rand.randint(1, 6)
    multiplier = 4 if level == 0 else 10
    rent = (d1 + d2) * multiplier

    owner = square[OWNER]
    if state[PLAYERS][player][MONEY] >= rent:
        pay_player(player, owner, rent, state)
    else:
        state[PHASE] = BANKRUPTCY_PREVENTION
        state[DEBT] = {
            CREDITOR: owner,
            AMOUNT: rent,
            NEXT_PHASE: DOUBLES_CHECK
        }


def is_pay_tax_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return square[TYPE] == TAX and state[PLAYERS][player][MONEY] >= square[VALUE]


def pay_tax(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    amount = square[VALUE]
    pay_bank(player, state, amount)


def is_prevent_bankruptcy_on_tax_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return square[TYPE] == TAX and state[PLAYERS][player][MONEY] < square[VALUE]


def prevent_bankruptcy_on_tax(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    tax = square[VALUE]

    state[PHASE] = BANKRUPTCY_PREVENTION
    state[DEBT] = {
        CREDITOR: BANK,
        DEBT: tax,
        NEXT_PHASE: DOUBLES_CHECK
    }


# TODO if time: Differentiate between property types. For streets, check if
# player owns whole set. For railroads, check amount of railroads owned by
# player. For utilities, check amount of utilities owned by player and
# increase level accordingly.
def is_buy_property_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return (is_property(square)
            and square[OWNER] is None
            and state[PLAYERS][player][MONEY] >= square[VALUE])


def buy_property(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    amount = square[VALUE]

    pay_bank(player, state, amount)
    square[OWNER] = player


def is_auction_property_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return (is_property(square)
            and square[OWNER] is None)


def auction_property(player: str, state: dict):
    square_index = state[PLAYERS][player][POSITION]
    auction = {
        ASSET: square_index,
        INITIATOR: player,
        PLAYERS: {}
    }

    for p in state[ORDER]:
        auction[PLAYERS][p] = {
            BID: 0,
            LAST_ACTION: CHANGE,
            ROUND: 0,
            WINNER: UNKNOWN
        }

    state[PHASE] = AUCTION
    state[AUCTION] = auction


def is_draw_and_execute_card_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return square[TYPE] in {COMMUNITY_CHEST, CHANCE}


def draw_and_execute_card(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square_type = state[BOARD][position][TYPE]
    if square_type == COMMUNITY_CHEST:
        draw_cc_card(player, state)
    else:
        draw_chance_card(player, state)


def draw_cc_card(player: str, state: dict):
    cards = state[COMMUNITY_CHEST]
    n_cards = len(cards)
    max_idx = n_cards if not state[GOOJF_CC_OWNER] else (n_cards - 1)
    _draw_and_execute_card(player, state, cards, max_idx)


def draw_chance_card(player: str, state: dict):
    cards = state[CHANCE]
    n_cards = len(cards)
    max_idx = n_cards if not state[GOOJF_CH_OWNER] else (n_cards - 1)
    _draw_and_execute_card(player, state, cards, max_idx)


def _draw_and_execute_card(player: str, state: dict, cards: list, max_idx: int):
    rand = Random(str(state))
    idx = rand.randint(0, max_idx)
    card = cards[idx]

    match card[TYPE]:
        case constants.COLLECT:
            collect_from_bank(player, state, card[AMOUNT])
            state[PHASE] = DOUBLES_CHECK
        case constants.PAY:
            if state[PLAYERS][player][MONEY] >= card[AMOUNT]:
                pay_bank(player, state, card[AMOUNT])
            else:
                state[PHASE] = BANKRUPTCY_PREVENTION
                state[DEBT] = {
                    CREDITOR: BANK,
                    AMOUNT: card[AMOUNT],
                    NEXT_PHASE: DOUBLES_CHECK
                }
        case constants.ADVANCE_TO:
            advance_to_square(player, state, card[SQUARE])
            # Phase remains POST_ROLL -> pay rent if owned by other player etc.
        case constants.GO_TO_JAIL:
            go_to_jail(player, state)
            state[PHASE] = FREE_4_ALL
        case constants.GOOFJ_CC:
            state[GOOJF_CC_OWNER] = player
            state[PHASE] = DOUBLES_CHECK
        case constants.GOOFJ_CH:
            state[GOOJF_CH_OWNER] = player
            state[PHASE] = DOUBLES_CHECK
        case _:
            raise ValueError(f"Unknown card type: {card[TYPE]}")


def advance_to_square(player: str, state: dict, square: int):
    old_pos = state[PLAYERS][player][POSITION]
    state[PLAYERS][player][POSITION] = square
    collect_if_pass_go(player, state, old_pos, square)


def pay_player(p_from: str, p_to: str, amount: int, state: dict):
    state[PLAYERS][p_from][MONEY] -= amount
    state[PLAYERS][p_to][MONEY] += amount
