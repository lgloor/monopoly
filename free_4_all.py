from random import Random

from pre_roll import *


def initialize_free_4_all(state: dict):
    assert state[FREE_4_ALL_ORDER] is None, 'Free for all must not be initialized'
    rand = Random(str(state))
    f4a_order: list[str] = [p for p in state[ORDER] if not state[PLAYERS][p][BANKRUPT]]
    rand.shuffle(f4a_order)

    state[PHASE] = FREE_4_ALL
    state[FREE_4_ALL_ORDER] = f4a_order


def get_enabled_free_4_all_actions(player: str, state: dict) -> list[tuple[str, Callable[[], None]]]:
    if (len(state[FREE_4_ALL_ORDER]) == 0
            and state[ORDER][state[ACTIVE]] == player):
        return [("Give turn to next active player", lambda: give_turn_to_next_active_player(state))]

    if not is_own_turn_in_f4a(player, state):
        return []

    enabled = [("Conclude free 4 all actions", lambda: conclude_f4a_actions(state))]

    for idx in get_unmortgageable_property_idxs(player, state):
        enabled.append((f'Unmortgage {state[BOARD][idx][NAME]}',
                        lambda: unmortgage_property(player, state, idx)))
    for idx in get_mortgageable_property_idxs(player, state):
        enabled.append((f'Mortgage {state[BOARD][idx][NAME]}',
                        lambda: mortgage_property(player, state, idx)))
    for idx in get_upgradeable_street_idxs(player, state):
        enabled.append((f'Upgrade {state[BOARD][idx][NAME]}',
                        lambda: upgrade_street(player, state, idx)))
    for idx in get_downgradeable_street_idxs(player, state):
        enabled.append((f'Downgrade {state[BOARD][idx][NAME]}',
                        lambda: downgrade_street(player, state, idx)))

    return enabled


def is_own_turn_in_f4a(player: str, state: dict) -> bool:
    return (not len(state[FREE_4_ALL_ORDER]) == 0
            and state[FREE_4_ALL_ORDER][0] == player)


def give_turn_to_next_active_player(state: dict):
    next_active = (state[ACTIVE] + 1) % len(state[ORDER])
    while state[PLAYERS][state[ORDER][next_active]][BANKRUPT]:
        next_active = (next_active + 1) % len(state[ORDER])

    state[FREE_4_ALL_ORDER] = None
    state[ACTIVE] = next_active
    state[PHASE] = PRE_ROLL


def conclude_f4a_actions(state: dict):
    state[FREE_4_ALL_ORDER].pop(0)
