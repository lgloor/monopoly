from collections.abc import Callable
from random import Random

from constants import *


def get_enabled_roll_actions(player: str, state: dict) -> list[tuple[str, Callable[[], str]]]:
    if state[PHASE] != ROLL:
        return []
    enabled: list[tuple[str, Callable[[], str]]] = []
    if is_roll_and_move_enabled(player, state):
        enabled.append(("Roll and move", lambda: roll_and_move(player, state)))
    if is_roll_in_jail_enabled(player, state):
        enabled.append(("Roll in jail", lambda: roll_in_jail(player, state)))
    return enabled


def is_roll_and_move_enabled(player: str, state: dict) -> bool:
    return not state[PLAYERS][player][IN_JAIL]


def roll_and_move(player: str, state: dict):
    rand = Random(str(state))
    d1 = rand.randint(1, 6)
    d2 = rand.randint(1, 6)

    if d1 == d2:
        if state[PLAYERS][player][CONSECUTIVE_DOUBLES] == 2:
            # Is third consecutive doubles -> go straight to jail
            go_to_jail(player, state)
            return f"{player} rolled {d1}, {d2}, third consecutive doubles, go to jail, move to free 4 all"
        else:
            state[PLAYERS][player][CONSECUTIVE_DOUBLES] += 1
    else:
        state[PLAYERS][player][CONSECUTIVE_DOUBLES] = 0

    move_after_roll(player, state, d1 + d2)
    state[PHASE] = POST_ROLL
    new_position = state[PLAYERS][player][POSITION]
    return f"{player} rolls {d1}, {d2}, moves to {state[BOARD][new_position][NAME]} at position {new_position}"


def is_roll_in_jail_enabled(player: str, state: dict) -> bool:
    return state[PLAYERS][player][IN_JAIL]


def roll_in_jail(player: str, state: dict):
    rand = Random(str(state))
    d1 = rand.randint(1, 6)
    d2 = rand.randint(1, 6)

    if d1 == d2:
        # Do not increase consecutive doubles because turn
        # ends right away after leaving jail with doubles
        state[PLAYERS][player][IN_JAIL] = False
        state[PLAYERS][player][JAIL_TIME] = 0
        move_after_roll(player, state, d1 + d2)
        state[PHASE] = POST_ROLL
        new_position = state[PLAYERS][player][POSITION]
        return f"{player} rolls {d1}, {d2} in jail, doubles, moves to {state[BOARD][new_position][NAME]}"
    elif state[PLAYERS][player][JAIL_TIME] == 2:
        # Missed doubles for the third time
        move_after_roll(player, state, d1 + d2)
        state[PLAYERS][player][IN_JAIL] = False
        state[PLAYERS][player][JAIL_TIME] = 0
        if state[PLAYERS][player][MONEY] >= 50:
            pay_bank(player, state, 50)
            new_position = state[PLAYERS][player][POSITION]
            return f"{player} rolls {d1}, {d2} in jail, missed doubles 3x, pays $50 to get out of jail, moves to {state[BOARD][new_position][NAME]}"
        else:
            state[PHASE] = BANKRUPTCY_PREVENTION
            state[DEBT] = {CREDITOR: BANK,
                           AMOUNT: 50,
                           NEXT_PHASE: POST_ROLL}
            return f"{player} rolls {d1}, {d2} in jail, missed doubles 3x, cannot pay $50 to get out of jail, enters bankruptcy prevention phase"
    else:
        state[PLAYERS][player][JAIL_TIME] += 1
        initialize_free_4_all(state)
        return f"{player} rolls {d1}, {d2} in jail, missed doubles {state[PLAYERS][player][JAIL_TIME]}x, stays in jail"


def move_after_roll(player: str, state: dict, amount: int):
    old_pos = state[PLAYERS][player][POSITION]
    new_pos = (old_pos + amount) % len(INIT_BOARD)
    collect_if_pass_go(player, state, old_pos, new_pos)
    state[PLAYERS][player][POSITION] = new_pos
