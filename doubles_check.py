from constants import *


def doubles_check(player: str, state: dict):
    if state[PLAYERS][player][CONSECUTIVE_DOUBLES] > 0:
        state[PHASE] = PRE_ROLL
    else:
        initialize_free_4_all(state)
