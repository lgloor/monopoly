from constants import *
from typing import Callable


def get_enabled_pre_roll_actions(player: str, state: dict) -> list[tuple[str, Callable[[], None]]]:
    enabled = [('End pre-roll',
                lambda: end_pre_roll(state))]
    if is_play_goojf_ch_enabled(player, state):
        enabled.append(('Play Get Out of Jail Free Chance',
                        lambda: play_goojf_ch(player, state)))
    if is_play_goojf_cc_enabled(player, state):
        enabled.append(('Play Get Out of Jail Free Community Chest',
                        lambda: play_goojf_cc(player, state)))
    if is_pay_jail_fine_enabled(player, state):
        enabled.append(('Pay Jail Fine $50',
                        lambda: pay_jail_fine(player, state)))
    for idx in get_unmortgageable_property_idxs(player, state):
        enabled.append((f'Unmortgage {state[BOARD][idx][NAME]}',
                        lambda: unmortgage_property(player, state, idx)))
    for idx in get_mortgageable_property_idxs(player, state):
        enabled.append((f'Mortgage {state[BOARD][idx][NAME]}',
                        lambda: mortgage_property(player, state, idx)))

    return enabled


def end_pre_roll(state: dict):
    state[PHASE] = ROLL


def is_play_goojf_ch_enabled(player: str, state: dict) -> bool:
    return state[GOOJF_CH_OWNER] == player and state[PLAYERS][player][IN_JAIL]


def play_goojf_ch(player: str, state: dict):
    state[GOOJF_CH_OWNER] = None
    state[PLAYERS][player][IN_JAIL] = False
    state[PLAYERS][player][JAIL_TIME] = 0


def is_play_goojf_cc_enabled(player: str, state: dict) -> bool:
    return state[GOOJF_CC_OWNER] == player and state[PLAYERS][player][IN_JAIL]


def play_goojf_cc(player: str, state: dict):
    state[GOOJF_CC_OWNER] = None
    state[PLAYERS][player][IN_JAIL] = False
    state[PLAYERS][player][JAIL_TIME] = 0


def is_pay_jail_fine_enabled(player: str, state: dict) -> bool:
    return state[PLAYERS][player][IN_JAIL] and state[PLAYERS][player][MONEY] >= 50


def pay_jail_fine(player: str, state: dict):
    pay_bank(player, state, 50)
    state[PLAYERS][player][IN_JAIL] = False
    state[PLAYERS][player][JAIL_TIME] = 0


def get_unmortgageable_property_idxs(player: str, state: dict) -> list[int]:
    unmortgageable_properties = []

    for i, square in enumerate(state[BOARD]):
        if (not is_property(square)
                or square[OWNER] != player
                or not square[MORTGAGED]):
            continue

        mortgage_value = square[VALUE] // 2
        unmortgage_cost = mortgage_value + (mortgage_value // 10)
        if state[PLAYERS][player][MONEY] >= unmortgage_cost:
            unmortgageable_properties.append(i)

    return unmortgageable_properties


def unmortgage_property(player: str, state: dict, prop_idx: int):
    prop = state[BOARD][prop_idx]
    mortgage_value = prop[VALUE] // 2
    unmortgage_cost = mortgage_value + (mortgage_value // 10)
    pay_bank(player, state, unmortgage_cost)
    prop[MORTGAGED] = False


def get_mortgageable_property_idxs(player: str, state: dict) -> list[int]:
    mortgageable_properties = []
    for i, square in enumerate(state[BOARD]):
        if (not is_property(square)
                or square[OWNER] != player
                or square[MORTGAGED]):
            continue

        # Cannot mortgage streets with houses or hotels
        if square[TYPE] == STREET and square[LEVEL] > 1:
            continue

        mortgageable_properties.append(i)

    return mortgageable_properties


# Mortgaging property does not change the rent level
# E.g. if 2 railroads are owned, even if one is mortgaged, the rent will still be 50
def mortgage_property(player: str, state: dict, prop_idx: int):
    prop = state[BOARD][prop_idx]
    mortgage_value = prop[VALUE] // 2
    collect_from_bank(player, state, mortgage_value)
    prop[MORTGAGED] = True
