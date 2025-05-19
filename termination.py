from constants import *


def is_terminate_enabled(state: dict) -> bool:
    n_bankrupt = 0
    for player in state[PLAYERS].keys():
        if state[PLAYERS][player][BANKRUPT]:
            n_bankrupt += 1
    return n_bankrupt == len(state[PLAYERS]) - 1


def terminate(state: dict):
    for player in state[PLAYERS].keys():
        if not state[PLAYERS][player][BANKRUPT]:
            state[WINNER] = player
            break

def is_terminated(state: dict) -> bool:
    return state[WINNER] is not None
