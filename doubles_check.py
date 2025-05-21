from constants import *


def doubles_check(player: str, state: dict):
    if state[PLAYERS][player][CONSECUTIVE_DOUBLES] > 0:
        state[PHASE] = PRE_ROLL
        return f"{player} has rolled doubles, gets another turn"
    else:
        initialize_free_4_all(state)
        return f"{player} has not rolled doubles, move to free 4 all"
