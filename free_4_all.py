from pre_roll import *


def get_enabled_free_4_all_actions(player: str, state: dict) -> list[tuple[str, Callable[[], str]]]:
    if (len(state[FREE_4_ALL_ORDER]) == 0
            and state[ORDER][state[ACTIVE]] == player):
        return [("Give turn to next active player", lambda: give_turn_to_next_active_player(player, state))]

    if not is_own_turn_in_f4a(player, state):
        return []

    enabled = [("Conclude free 4 all actions", lambda: conclude_f4a_actions(player, state))]

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


def is_own_turn_in_f4a(player: str, state: dict) -> bool:
    return (not len(state[FREE_4_ALL_ORDER]) == 0
            and state[FREE_4_ALL_ORDER][0] == player)


def give_turn_to_next_active_player(player: str, state: dict):
    next_active = (state[ACTIVE] + 1) % len(state[ORDER])
    while state[PLAYERS][state[ORDER][next_active]][BANKRUPT]:
        next_active = (next_active + 1) % len(state[ORDER])

    state[FREE_4_ALL_ORDER] = None
    state[ACTIVE] = next_active
    state[PHASE] = PRE_ROLL
    return f"{player} gives turn to {state[ORDER][next_active]}"


def conclude_f4a_actions(player: str ,state: dict):
    state[FREE_4_ALL_ORDER].pop(0)
    return f"{player} concludes free 4 all actions"
