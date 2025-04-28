import os

import git
import yaml
from git import Repo, Commit


def init_repo(path: str, name: str) -> tuple[Repo, Commit]:
    """
    Initialize a git repository with the given path and name
    :param path: directory to create the repository in
    :param name: repository name
    :return: git.Repo object
    """

    if os.path.exists(f'{path}/{name}'):
        raise FileExistsError(f'Repo {name} already exists')

    repo = git.Repo.init(f"{path}/{name}", initial_branch=name)
    author = git.Actor("init", "init@repo.com")
    initial_commit = repo.index.commit(
        f"initial commit {name}",
        author=author,
        committer=author
    )

    print(f"Repository {name} created\n with initial commit: {initial_commit}")
    return repo, initial_commit


def init_auction_repo(path: str, name: str, players: list[str], initial_money: list[int], creator: str = None) -> tuple[Repo, Commit]:
    if os.path.exists(f'{path}/{name}'):
        raise FileExistsError(f'Repo {name} already exists')

    assert not len(players) == 0, "Players list cannot be empty"

    if not creator:
        creator = players[0]
    else:
        assert creator in players, "Creator must be one of players"

    repo = git.Repo.init(f"{path}/{name}", initial_branch=creator)

    # Create initial state
    init_state = {}
    for i, player in enumerate(players):
        init_state[player] = {
            'money': initial_money[i],
            'winner': 'UNKNOWN',
            'bid': 0,
            'last_action': 'CHANGE',
            'round': 1
        }

    # Create a file to store initial state
    with open(f"{path}/{name}/state.yml", 'w') as f:
        yaml.dump(init_state, f)

    # Add the initial state file to the repository
    repo.index.add([f"{path}/{name}/state.yml"])

    author = git.Actor(creator, f"{creator}@auction.com")
    initial_commit = repo.index.commit(
        f"initial commit {name}",
        author=author,
        committer=author
    )

    # Create branches for each player
    for player in players:
        repo.create_head(player, commit=initial_commit.hexsha)

    print(f"Auction Repository {name} created\n with initial commit: {initial_commit}")
    return repo, initial_commit
