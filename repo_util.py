from os import mkdir

import git
import yaml
from git import Repo, Commit

from constants import *


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


def init_auction_repo(path: str, name: str, players: list[str], initial_money: list[int], creator: str = None) -> tuple[
    Repo, Commit]:
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

def init_monopoly_simulation_repos(path: str, name: str, players: list[str]) -> tuple[list[Repo], Commit]:
    if os.path.exists(f'{path}/{name}'):
        raise FileExistsError(f'Directory {name} already exists')
    else:
        mkdir(f"{path}/{name}")

    assert not len(players) == 0, "Players list cannot be empty"

    repos: list[Repo] = []
    for player in players:
        mkdir(f"{path}/{name}/{player}")
        repo = git.Repo.init(f"{path}/{name}/{player}", initial_branch='main')
        with open(f"{path}/{name}/{player}/.git/.name", 'w') as f:
            f.write(player)

        others = [other for other in players if other != player]
        for other in others:
            repo.create_remote(other, f"../{other}")

        repos.append(repo)

    initiating_repo = repos[0]
    init_state = {
        ACTIVE: 0,
        ORDER: players,
        PHASE: PRE_ROLL,
        FREE_4_ALL_ORDER: None,
        GOOJF_CH_OWNER: None,
        GOOJF_CC_OWNER: None,
        BANK_MONEY: TOTAL_MONEY - len(players) * STARTING_MONEY,
        WINNER: None,
        DEBT: None,
        AUCTION: None,
        PLAYERS: {},
        BOARD: INIT_BOARD,
        COMMUNITY_CHEST: CC_CARDS,
        CHANCE: CH_CARDS
    }

    for player in players:
        init_state[PLAYERS][player] = {
            MONEY: STARTING_MONEY,
            BANKRUPT: False,
            IN_JAIL: False,
            JAIL_TIME: 0,
            POSITION: 0,
            CONSECUTIVE_DOUBLES: 0
        }

    state_file_path = f"{initiating_repo.working_tree_dir}/state.yml"
    with open(state_file_path, 'w') as f:
        yaml.dump(init_state, f)

    initiating_repo.index.add(state_file_path)
    initial_commit = initiating_repo.index.commit(f"initial commit {name}")
    return repos, initial_commit


def init_monopoly_repo(player_url: str, player_name:str, players: list[dict[str, str]]) -> Repo:
    assert not len(players) == 0, "Players list cannot be empty"

    to_path = f"./monopoly_{player_name}"
    repo = Repo.clone_from(player_url, to_path)

    init_state = {
        ACTIVE: 0,
        ORDER: [p[NAME] for p in players],
        PHASE: PRE_ROLL,
        FREE_4_ALL_ORDER: None,
        GOOJF_CH_OWNER: None,
        GOOJF_CC_OWNER: None,
        BANK_MONEY: TOTAL_MONEY - len(players) * STARTING_MONEY,
        WINNER: None,
        DEBT: None,
        AUCTION: None,
        PLAYERS: {},
        BOARD: INIT_BOARD,
        COMMUNITY_CHEST: CC_CARDS,
        CHANCE: CH_CARDS
    }

    for player in players:
        name = player[NAME]
        url = player[URL]
        init_state[PLAYERS][name] = {
            URL: url,
            MONEY: STARTING_MONEY,
            BANKRUPT: False,
            IN_JAIL: False,
            JAIL_TIME: 0,
            POSITION: 0,
            CONSECUTIVE_DOUBLES: 0
        }

    with open(f"{repo.working_dir}/.git/.name", 'w') as f:
        f.write(player_name)

    with open(f"{repo.working_dir}/state.yml", 'w') as f:
        yaml.dump(init_state, f)

    repo.index.add(f"{repo.working_dir}/state.yml")
    repo.index.commit(f"initial commit monopoly")

    others = [player for player in players if player['name'] != player_name]
    for other in others:
        name = other[NAME]
        url = other[URL]
        repo.create_remote(name, url)

    print(f"""
    The repository has successfully been initialized at {to_path}. 
    The other players can now join using the URL {player_url}""")
    return repo


def join_new_game(player_url: str, player_name: str, initiator_url: str):
    to_path = f"./monopoly_{player_name}"
    repo = Repo.clone_from(player_url, to_path)
    with open(f"{repo.working_dir}/.git/.name", 'w') as f:
        f.write(player_name)

    init_remote = repo.create_remote('initiator', initiator_url)

    print(f"Joining game at {initiator_url}")
    while True:
        try:
            repo.git.pull('initiator', 'main')
            break
        except:
            continue

    repo.delete_remote(init_remote)

    with open(f"{repo.working_dir}/state.yml", 'r') as f:
        state = yaml.safe_load(f)
        players: dict = state[PLAYERS]
        for name, p_state in players.items():
            if name == player_name:
                continue
            repo.create_remote(name, p_state[URL])

    print(f"Joined successfully")
    return repo


def rejoin_game(path: str) -> Repo:
    if not os.path.exists(path):
        raise FileNotFoundError(f'Directory {path} does not exist')

    return Repo(path)


