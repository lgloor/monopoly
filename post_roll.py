from typing import Callable

import constants
from auction import initialize_auction
from constants import *


def get_enabled_post_roll_actions(player: str, state: dict) -> list[tuple[str, Callable[[], str]]]:
    enabled: list[tuple[str, Callable[[], str]]] = []
    if (is_do_nothing_on_own_property_enabled(player, state)
            or is_do_nothing_on_go_enabled(player, state)
            or is_do_nothing_on_free_parking_enabled(player, state)
            or is_do_nothing_on_jail_enabled(player, state)
            or is_do_nothing_on_mortgaged_property_enabled(player, state)):
        enabled.append(('Do nothing',
                        lambda: end_post_roll(state, player)))
    if is_pay_street_rent_enabled(player, state):
        enabled.append((f'Pay rent for {state[BOARD][state[PLAYERS][player][POSITION]][NAME]}',
                        lambda: pay_street_rent(player, state)))
    if is_pay_rail_rent_enabled(player, state):
        enabled.append((f'Pay rent for {state[BOARD][state[PLAYERS][player][POSITION]][NAME]}',
                        lambda: pay_rail_rent(player, state)))
    if is_prevent_bankruptcy_on_street_rent_enabled(player, state):
        enabled.append((f'Prevent bankruptcy on rent for {state[BOARD][state[PLAYERS][player][POSITION]][NAME]}',
                        lambda: prevent_bankruptcy_on_street_rent(player, state)))
    if is_prevent_bankruptcy_on_rail_rent_enabled(player, state):
        enabled.append((f'Prevent bankruptcy on rent for {state[BOARD][state[PLAYERS][player][POSITION]][NAME]}',
                        lambda: prevent_bankruptcy_on_rail_rent(player, state)))
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
    if is_go_to_jail_enabled(player, state):
        enabled.append(('Go to jail',
                        lambda: do_go_to_jail(player, state)))
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


def end_post_roll(state: dict, player: str):
    state[PHASE] = DOUBLES_CHECK
    position = state[PLAYERS][player][POSITION]
    return f"{player} does nothing because they landed on {state[BOARD][position][NAME]}"


def is_pay_street_rent_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    if (square[TYPE] != STREET
            or square[OWNER] in {None, player}
            or square[MORTGAGED]):
        return False

    rent = get_street_rent(state, position)
    money = state[PLAYERS][player][MONEY]
    return money >= rent


def pay_street_rent(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    owner = square[OWNER]
    rent = get_street_rent(state, position)

    pay_player(player, owner, rent, state)
    state[PHASE] = DOUBLES_CHECK
    return f"{player} pays rent for {square[NAME]} to {owner} (${rent})"


def get_street_rent(state: dict, position: int) -> int:
    street = state[BOARD][position]
    if street[LEVEL] > 0:
        return street[RENT][street[LEVEL]]
    owner = street[OWNER]
    if owns_all_of_same_set(owner, street[SET], state):
        return street[RENT][0] * 2
    return street[RENT][0]


def is_pay_rail_rent_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    if (square[TYPE] != RAIL
            or square[OWNER] in {None, player}
            or square[MORTGAGED]):
        return False

    rent = get_rail_rent(state, position)
    money = state[PLAYERS][player][MONEY]
    return money >= rent


def pay_rail_rent(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    owner = square[OWNER]
    rent = get_rail_rent(state, position)
    pay_player(player, owner, rent, state)
    state[PHASE] = DOUBLES_CHECK
    return f"{player} pays rent for {square[NAME]} to {owner} (${rent})"


def get_rail_rent(state: dict, position: int) -> int:
    square = state[BOARD][position]
    owner = square[OWNER]
    n_owned_railroads = 0
    for s in state[BOARD]:
        if (s[TYPE] == RAIL
                and s[OWNER] == owner):
            n_owned_railroads += 1
    return 25 * (2 ** (n_owned_railroads - 1))


def is_prevent_bankruptcy_on_street_rent_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    if (square[TYPE] != STREET
            or square[OWNER] in {None, player}
            or square[MORTGAGED]):
        return False

    rent = get_street_rent(state, position)
    money = state[PLAYERS][player][MONEY]
    return money < rent


def prevent_bankruptcy_on_street_rent(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    owner = square[OWNER]
    rent = square[RENT][square[LEVEL]]

    debt = {
        CREDITOR: owner,
        AMOUNT: rent,
        NEXT_PHASE: DOUBLES_CHECK
    }

    state[DEBT] = debt
    state[PHASE] = BANKRUPTCY_PREVENTION
    return f"{player} must prevent bankruptcy on rent for {square[NAME]} to {owner} (${rent})"


def is_prevent_bankruptcy_on_rail_rent_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    if (square[TYPE] != RAIL
            or square[OWNER] in {None, player}
            or square[MORTGAGED]):
        return False

    rent = get_rail_rent(state, position)
    money = state[PLAYERS][player][MONEY]
    return money < rent


def prevent_bankruptcy_on_rail_rent(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    owner = square[OWNER]
    rent = get_rail_rent(state, position)

    debt = {
        CREDITOR: owner,
        AMOUNT: rent,
        NEXT_PHASE: DOUBLES_CHECK
    }

    state[DEBT] = debt
    state[PHASE] = BANKRUPTCY_PREVENTION
    return f"{player} must prevent bankruptcy on rent for {square[NAME]} to {owner} (${rent})"


def is_try_pay_util_rent_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return (square[TYPE] == UTILITY
            and square[OWNER] not in {None, player}
            and not square[MORTGAGED])


def try_pay_util_rent(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]

    rand = Random(str(state))
    d1 = rand.randint(1, 6)
    d2 = rand.randint(1, 6)

    owner = square[OWNER]
    multiplier = 10 if owns_both_utilities(owner, state) else 4
    rent = (d1 + d2) * multiplier

    if state[PLAYERS][player][MONEY] >= rent:
        pay_player(player, owner, rent, state)
        state[PHASE] = DOUBLES_CHECK
        return f"{player} pays rent for utility {square[NAME]} to {owner} (({d1} + {d2}) * {multiplier} = ${rent})"
    else:
        state[PHASE] = BANKRUPTCY_PREVENTION
        state[DEBT] = {
            CREDITOR: owner,
            AMOUNT: rent,
            NEXT_PHASE: DOUBLES_CHECK
        }
        return f"{player} must prevent bankruptcy on rent for {square[NAME]} to {owner} (({d1} + {d2}) * {multiplier} = ${rent})"


def owns_both_utilities(owner: str, state: dict) -> bool:
    owned_utilities = [s for s in state[BOARD] if s[TYPE] == UTILITY and s[OWNER] == owner]
    return len(owned_utilities) == 2


def is_pay_tax_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return square[TYPE] == TAX and state[PLAYERS][player][MONEY] >= square[VALUE]


def pay_tax(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    amount = square[VALUE]
    pay_bank(player, state, amount)
    state[PHASE] = DOUBLES_CHECK
    return f"{player} pays tax for {square[NAME]} (${amount})"


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
        AMOUNT: tax,
        NEXT_PHASE: DOUBLES_CHECK
    }
    return f"{player} must prevent bankruptcy on tax for {square[NAME]} (${tax})"


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
    state[PHASE] = DOUBLES_CHECK
    return f"{player} buys {square[NAME]} (${amount})"


def is_auction_property_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return (is_property(square)
            and square[OWNER] is None)


def auction_property(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    initialize_auction(player, position, state)
    return f"{player} starts an auction for {state[BOARD][position][NAME]}"


def is_go_to_jail_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return square[TYPE] == GO_TO_JAIL

def do_go_to_jail(player, state):
    go_to_jail(player, state)
    return f"{player} lands on Go to Jail"


def is_draw_and_execute_card_enabled(player: str, state: dict) -> bool:
    position = state[PLAYERS][player][POSITION]
    square = state[BOARD][position]
    return square[TYPE] in {COMMUNITY_CHEST, CHANCE}


def draw_and_execute_card(player: str, state: dict):
    position = state[PLAYERS][player][POSITION]
    square_type = state[BOARD][position][TYPE]
    if square_type == COMMUNITY_CHEST:
        commit_message = draw_cc_card(player, state)
    else:
        commit_message = draw_chance_card(player, state)

    return commit_message


def draw_cc_card(player: str, state: dict):
    cards = state[COMMUNITY_CHEST]
    n_cards = len(cards)
    max_idx = n_cards - 1 if not state[GOOJF_CC_OWNER] else (n_cards - 2)
    commit_message = _draw_and_execute_card(player, state, cards, max_idx)
    return commit_message


def draw_chance_card(player: str, state: dict):
    cards = state[CHANCE]
    n_cards = len(cards)
    max_idx = n_cards - 1 if not state[GOOJF_CH_OWNER] else (n_cards - 2)
    commit_message = _draw_and_execute_card(player, state, cards, max_idx)
    return commit_message


def _draw_and_execute_card(player: str, state: dict, cards: list, max_idx: int):
    rand = Random(str(state))
    idx = rand.randint(0, max_idx)
    card = cards[idx]
    position = state[PLAYERS][player][POSITION]
    square_name = state[BOARD][position][NAME]

    match card[TYPE]:
        case constants.COLLECT:
            collect_from_bank(player, state, card[AMOUNT])
            state[PHASE] = DOUBLES_CHECK
            return f"{player} draws card {idx} from {square_name} and collects ${card[AMOUNT]}"
        case constants.PAY:
            if state[PLAYERS][player][MONEY] >= card[AMOUNT]:
                pay_bank(player, state, card[AMOUNT])
                state[PHASE] = DOUBLES_CHECK
                return f"{player} draws card {idx} from {square_name} and pays ${card[AMOUNT]}"
            else:
                state[PHASE] = BANKRUPTCY_PREVENTION
                state[DEBT] = {
                    CREDITOR: BANK,
                    AMOUNT: card[AMOUNT],
                    NEXT_PHASE: DOUBLES_CHECK
                }
                return f"{player} draws card {idx} from {square_name} and must prevent bankruptcy for ${card[AMOUNT]}"
        case constants.ADVANCE_TO:
            advance_to_square(player, state, card[SQUARE])
            return f"{player} draws card {idx} from {square_name} and advances to {state[BOARD][card[SQUARE]][NAME]} (idx: {card[SQUARE]})"
            # Phase remains POST_ROLL -> pay rent if owned by other player etc.
        case constants.GO_TO_JAIL:
            go_to_jail(player, state)
            return f"{player} draws card {idx} from {square_name} and goes to jail"
        case constants.GOOFJ_CC:
            state[GOOJF_CC_OWNER] = player
            state[PHASE] = DOUBLES_CHECK
            return f"{player} draws card {idx} from {square_name} and gets Get Out of Jail Free Community Chest"
        case constants.GOOFJ_CH:
            state[GOOJF_CH_OWNER] = player
            state[PHASE] = DOUBLES_CHECK
            return f"{player} draws card {idx} from {square_name} and gets Get Out of Jail Free Chance"
        case _:
            raise ValueError(f"Unknown card type: {card[TYPE]}")


def advance_to_square(player: str, state: dict, square: int):
    old_pos = state[PLAYERS][player][POSITION]
    state[PLAYERS][player][POSITION] = square
    collect_if_pass_go(player, state, old_pos, square)


def pay_player(p_from: str, p_to: str, amount: int, state: dict):
    state[PLAYERS][p_from][MONEY] -= amount
    state[PLAYERS][p_to][MONEY] += amount
