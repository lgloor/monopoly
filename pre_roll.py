from constants import *
from typing import Callable


def get_enabled_pre_roll_actions(player: str, state: dict) -> list[tuple[str, Callable[[], str]]]:
    enabled = [('End pre-roll',
                lambda: end_pre_roll(state, player))]
    if is_play_goojf_ch_enabled(player, state):
        enabled.append(('Play Get Out of Jail Free Chance',
                        lambda: play_goojf_ch(player, state)))
    if is_play_goojf_cc_enabled(player, state):
        enabled.append(('Play Get Out of Jail Free Community Chest',
                        lambda: play_goojf_cc(player, state)))
    if is_pay_jail_fine_enabled(player, state):
        enabled.append(('Pay Jail Fine $50',
                        lambda: pay_jail_fine(player, state)))

    # Default parameters in lambdas are needed to capture current value of idx.
    # Otherwise, it will be the last value of idx in the loop.
    for idx in get_unmortgageable_property_idxs(player, state):
        enabled.append((f'Unmortgage {state[BOARD][idx][NAME]}',
                        lambda idx_=idx: unmortgage_property(player, state, idx_)))
    for idx in get_mortgageable_property_idxs(player, state):
        enabled.append((f'Mortgage {state[BOARD][idx][NAME]}',
                        lambda idx_=idx: mortgage_property(player, state, idx_)))
    for idx in get_upgradeable_street_idxs(player, state):
        enabled.append((f'Upgrade {state[BOARD][idx][NAME]}',
                        lambda idx_=idx: upgrade_street(player, state, idx_)))
    for idx in get_downgradeable_street_idxs(player, state):
        enabled.append((f'Downgrade {state[BOARD][idx][NAME]}',
                        lambda idx_=idx: downgrade_street(player, state, idx_)))

    return enabled


def end_pre_roll(state: dict, player: str) -> str:
    state[PHASE] = ROLL
    return f"{player} ends pre-roll phase"


def is_play_goojf_ch_enabled(player: str, state: dict) -> bool:
    return state[GOOJF_CH_OWNER] == player and state[PLAYERS][player][IN_JAIL]


def play_goojf_ch(player: str, state: dict):
    state[GOOJF_CH_OWNER] = None
    state[PLAYERS][player][IN_JAIL] = False
    state[PLAYERS][player][JAIL_TIME] = 0
    return f"{player} plays Get Out of Jail Free Chance"


def is_play_goojf_cc_enabled(player: str, state: dict) -> bool:
    return state[GOOJF_CC_OWNER] == player and state[PLAYERS][player][IN_JAIL]


def play_goojf_cc(player: str, state: dict):
    state[GOOJF_CC_OWNER] = None
    state[PLAYERS][player][IN_JAIL] = False
    state[PLAYERS][player][JAIL_TIME] = 0
    return f"{player} plays Get Out of Jail Free Community Chest"


def is_pay_jail_fine_enabled(player: str, state: dict) -> bool:
    return state[PLAYERS][player][IN_JAIL] and state[PLAYERS][player][MONEY] >= 50


def pay_jail_fine(player: str, state: dict):
    pay_bank(player, state, 50)
    state[PLAYERS][player][IN_JAIL] = False
    state[PLAYERS][player][JAIL_TIME] = 0
    return f"{player} pays $50 jail fine"


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
    prop[MORTGAGED] = False
    pay_bank(player, state, unmortgage_cost)
    return f"{player} unmortgages {prop[NAME]} for ${unmortgage_cost}"


def get_mortgageable_property_idxs(player: str, state: dict) -> list[int]:
    mortgageable_properties = []
    for i, square in enumerate(state[BOARD]):
        if (not is_property(square)
                or square[OWNER] != player
                or square[MORTGAGED]):
            continue

        # Cannot mortgage streets where any street from the same set has buildings
        if square[TYPE] == STREET and any_street_from_same_set_has_buildings(state, i):
            continue

        mortgageable_properties.append(i)

    return mortgageable_properties


def any_street_from_same_set_has_buildings(state: dict, prop_idx: int) -> bool:
    street = state[BOARD][prop_idx]
    for square in state[BOARD]:
        if (square[TYPE] == STREET
                and square[SET] == street[SET]
                and square[LEVEL] > 0):
            return True
    return False


# Mortgaging property does not change the rent level
# E.g. if 2 railroads are owned, even if one is mortgaged, the rent will still be 50
def mortgage_property(player: str, state: dict, prop_idx: int):
    prop = state[BOARD][prop_idx]
    mortgage_value = prop[VALUE] // 2
    prop[MORTGAGED] = True
    collect_from_bank(player, state, mortgage_value)
    return f"{player} mortgages {prop[NAME]} for ${mortgage_value}"


def get_upgradeable_street_idxs(player: str, state: dict) -> list[int]:
    upgradeable_streets = []
    money = state[PLAYERS][player][MONEY]
    for i, square in enumerate(state[BOARD]):
        if (square[TYPE] == STREET
                and square[LEVEL] < 5
                and money >= square[HOUSE_COST]
                and owns_all_of_same_set(player, square[SET], state)
                and all_from_set_are_higher_or_equal_level(state, square[SET], square[LEVEL])):
            upgradeable_streets.append(i)
    return upgradeable_streets


def all_from_set_are_higher_or_equal_level(state: dict, n_set: int, level: int):
    for s in state[BOARD]:
        if (s[TYPE] == STREET
                and s[SET] == n_set
                and s[LEVEL] < level):
            return False
    return True


def upgrade_street(player: str, state: dict, prop_idx: int):
    prop = state[BOARD][prop_idx]
    house_cost = prop[HOUSE_COST]
    prop[LEVEL] += 1
    pay_bank(player, state, house_cost)
    return f"{player} upgrades {prop[NAME]} for ${house_cost} to level {prop[LEVEL]}"


def get_downgradeable_street_idxs(player: str, state: dict) -> list[int]:
    downgradeable_streets = []
    for i, square in enumerate(state[BOARD]):
        if (square[TYPE] == STREET
                and square[OWNER] == player
                and square[LEVEL] > 0
                and all_from_set_are_lower_or_equal_level(state, square[SET], square[LEVEL])):
            downgradeable_streets.append(i)
    return downgradeable_streets


def all_from_set_are_lower_or_equal_level(state: dict, n_set: int, level: int):
    for s in state[BOARD]:
        if (s[TYPE] == STREET
                and s[SET] == n_set
                and s[LEVEL] > level):
            return False
    return True


def downgrade_street(player: str, state: dict, prop_idx: int):
    prop = state[BOARD][prop_idx]
    house_cost = prop[HOUSE_COST]
    prop[LEVEL] -= 1
    collect_from_bank(player, state, house_cost // 2)
    return f"{player} downgrades {prop[NAME]} for ${house_cost // 2} to level {prop[LEVEL]}"
