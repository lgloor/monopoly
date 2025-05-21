from free_4_all import give_turn_to_next_active_player
from post_roll import pay_player
from pre_roll import *


def get_enabled_bankruptcy_prevention_actions(player: str, state: dict) -> list[tuple[str, Callable[[], str]]]:
    if can_pay_off_debt(player, state):
        return [('Pay off debt', lambda: pay_off_debt(player, state))]

    enabled = []
    for idx in get_mortgageable_property_idxs(player, state):
        enabled.append((f'Mortgage {state[BOARD][idx][NAME]}',
                        lambda: mortgage_property(player, state, idx)))
    for idx in get_downgradeable_street_idxs(player, state):
        enabled.append((f'Downgrade {state[BOARD][idx][NAME]}',
                        lambda: downgrade_street(player, state, idx)))

    if len(enabled) == 0:
        return [('Go bankrupt', lambda: go_bankrupt(player, state))]

    return enabled


def can_pay_off_debt(player: str, state: dict) -> bool:
    return state[PLAYERS][player][MONEY] >= state[DEBT][AMOUNT]


def pay_off_debt(player: str, state: dict):
    amount = state[DEBT][AMOUNT]
    creditor = state[DEBT][CREDITOR]
    if creditor == BANK:
        pay_bank(player, state, amount)
    else:
        pay_player(player, creditor, amount, state)
    state[PHASE] = state[DEBT][NEXT_PHASE]
    state[DEBT] = None
    return f"{player} pays off debt of {amount} to {creditor}"


def go_bankrupt(player: str, state: dict):
    creditor = state[DEBT][CREDITOR]
    if creditor == BANK:
        transfer_all_assets_to_bank(player, state)
    else:
        transfer_all_assets_to_player(player, creditor, state)

    state[PLAYERS][player][BANKRUPT] = True
    state[DEBT] = None

    give_turn_to_next_active_player(player, state)
    return f"{player} goes bankrupt, transfers all assets to {creditor}"



def transfer_all_assets_to_bank(player: str, state: dict):
    pay_bank(player, state, state[PLAYERS][player][MONEY])

    if state[GOOJF_CH_OWNER] == player:
        state[GOOJF_CH_OWNER] = None

    if state[GOOJF_CC_OWNER] == player:
        state[GOOJF_CC_OWNER] = None

    for square in state[BOARD]:
        if not is_property(square):
            continue
        if square[OWNER] == player:
            square[OWNER] = None
            square[MORTGAGED] = False


def transfer_all_assets_to_player(p_from: str, p_to: str, state: dict):
    pay_player(p_from, p_to, state[PLAYERS][p_from][MONEY], state)

    if state[GOOJF_CH_OWNER] == p_from:
        state[GOOJF_CH_OWNER] = p_to

    if state[GOOJF_CC_OWNER] == p_from:
        state[GOOJF_CC_OWNER] = p_to

    for square in state[BOARD]:
        if is_property(square) and square[OWNER] == p_from:
            square[OWNER] = p_to
