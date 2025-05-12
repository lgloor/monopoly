from typing import Callable

import git
import yaml

from auction import get_enabled_auction_actions
from constants import *
from free_4_all import get_enabled_free_4_all_actions
from post_roll import get_enabled_post_roll_actions
from pre_roll import get_enabled_pre_roll_actions
from roll import get_enabled_roll_actions


def get_enabled_actions(player: str, state: dict) -> list:
    enabled: list[tuple[str, Callable[[], None]]] = []

    active_player = state[ORDER][state[ACTIVE]]
    if active_player == player:
        if state[PHASE] == PRE_ROLL:
            enabled.extend(get_enabled_pre_roll_actions(player, state))
        elif state[PHASE] == ROLL:
            enabled.extend(get_enabled_roll_actions(player, state))
        elif state[PHASE] == POST_ROLL:
            enabled.extend(get_enabled_post_roll_actions(player, state))

    if state[PHASE] == FREE_4_ALL:
        enabled.extend(get_enabled_free_4_all_actions(player, state))
    elif state[PHASE] == AUCTION:
        enabled.extend(get_enabled_auction_actions(player, state))
    return enabled


def read_player_and_state(repo: git.Repo) -> tuple[str, dict]:
    player = repo.active_branch.name
    with open(f"{repo.working_tree_dir}/state.yml", 'r') as f:
        state = yaml.safe_load(f)
    return player, state
