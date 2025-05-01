import os

import git
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
N_PLAYERS: int = 3
STARTING_MONEY: int = 40

def read_state(repo: git.Repo, p: str) -> dict:
    """
    Read the state from the repository for the specified player
    :param repo: git repository
    :param p: player who's state to read
    :return: state dictionary
    """

    repo.git.checkout(p)
    with open(f"{repo.working_tree_dir}/state.yml", 'r') as f:
        state = yaml.safe_load(f)
    return state
