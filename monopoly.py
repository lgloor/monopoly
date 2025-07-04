import itertools
import random
import threading
import time
from typing import Callable

import git
import yaml

from auction import get_enabled_auction_actions
from bankruptcy_prevention import get_enabled_bankruptcy_prevention_actions
from constants import *
from doubles_check import doubles_check
from free_4_all import get_enabled_free_4_all_actions
from post_roll import get_enabled_post_roll_actions
from pre_roll import get_enabled_pre_roll_actions
from roll import get_enabled_roll_actions
from termination import is_terminate_enabled, terminate, is_terminated


def simulate_monopoly(repos: list[git.Repo], initial_commit: git.Commit):
    rand = Random(initial_commit.hexsha)
    terminated = False
    while not terminated:
        repo = rand.choice(repos)
        if not os.path.exists(f"{repo.working_tree_dir}/state.yml"):
            merge_from_remotes(repo)
            terminated = False
        else:
            terminated = take_action(repo, sim=True, rand=rand)


def take_action(repo: git.Repo, sim: bool = False, rand: Random = None) -> bool:
    # push if origin exists and has unpushed commits first in case of connection loss after taking an action.
    threading.Thread(target=push_if_origin_exists_and_has_unpushed, args=(repo,), daemon=True).start()
    player, state = read_player_and_state(repo)

    if is_terminated(state):
        final_push_success = push_if_origin_exists_and_has_unpushed(repo)
        if final_push_success:
            print("Game is terminated, WINNER: ", state[WINNER])
            return True
        else:
            return False

    enabled_actions = get_enabled_actions(player, state, sim)

    if len(enabled_actions) == 0:
        merge_from_remotes(repo)
        return False

    if len(enabled_actions) == 1:
        message, action = enabled_actions[0]
    else:
        if sim:
            message, action = rand.choice(enabled_actions)
        else:
            message, action = get_wanted_action(enabled_actions)

    print(f"Executing action: {message}")
    if sim:
        start_time = time.time_ns()

    commit_message = action()
    check_invariants_and_commit(commit_message, repo, state)

    if sim:
        execution_time = time.time_ns() - start_time
        with open(f"{os.getcwd()}/action_times.log", "a") as log_file:
            log_file.write(f"{execution_time}\n")
    return False


def read_player_and_state(repo: git.Repo) -> tuple[str, dict]:
    with open(f"{repo.working_tree_dir}/.git/.name", 'r') as f:
        player = f.read().strip()
    with open(f"{repo.working_tree_dir}/state.yml", 'r') as f:
        state = yaml.safe_load(f)
    return player, state


def get_enabled_actions(player: str, state: dict, sim: bool) -> list:
    if is_terminate_enabled(state):
        return [("Terminate", lambda: terminate(player, state))]

    enabled: list[tuple[str, Callable[[], str]]] = []

    active_player = state[ORDER][state[ACTIVE]]
    if active_player == player:
        if state[PHASE] == PRE_ROLL:
            enabled.extend(get_enabled_pre_roll_actions(player, state))
        elif state[PHASE] == ROLL:
            enabled.extend(get_enabled_roll_actions(player, state))
        elif state[PHASE] == POST_ROLL:
            enabled.extend(get_enabled_post_roll_actions(player, state))
        elif state[PHASE] == DOUBLES_CHECK:
            enabled.append(("Doubles check",
                            lambda: doubles_check(player, state)))
        elif state[PHASE] == BANKRUPTCY_PREVENTION:
            enabled.extend(get_enabled_bankruptcy_prevention_actions(player, state))

    if state[PHASE] == FREE_4_ALL:
        enabled.extend(get_enabled_free_4_all_actions(player, state))
    elif state[PHASE] == AUCTION:
        enabled.extend(get_enabled_auction_actions(player, state, sim))
    return enabled


def merge_from_remotes(repo: git.Repo):
    for remote in repo.remotes:
        if remote.name == 'origin':
            # Skip the origin remote, as it is not a player remote.
            continue

        try:
            remote.fetch('main')
        except Exception as e:
            # remote or its main branch is not available. Just try the next one.
            continue

        try:
            repo.git.merge(f'{remote.name}/main')
        except git.CommandError as e:
            print(f"Failed to merge from {remote.name} in repo {repo.working_tree_dir}")
            raise e


def get_wanted_action(enabled_actions):
    print('==============================================================================================')
    print("Possible actions:")
    for i, (message, action) in enumerate(enabled_actions):
        print(f"{i + 1}: {message}")
    choice = get_int_from_input_in_range("Choose an action: ",
                                         1, len(enabled_actions))
    return enabled_actions[choice - 1]  # adjust for 0-indexing


def check_invariants_and_commit(message, repo, state):
    check_invariants(state)
    with open(f"{repo.working_tree_dir}/state.yml", 'w') as f:
        yaml.dump(state, f)
    repo.index.add(f"{repo.working_tree_dir}/state.yml")
    repo.index.commit(f"{message}")


def push_if_origin_exists_and_has_unpushed(repo: git.Repo) -> bool:
    #  Return True if push was successful or not required, False otherwise.

    try:
        origin = repo.remote("origin")
    except ValueError:
        # The repo does not have an origin remote
        # e.g. case in simulations
        # just ignore it
        return True
    try:
        has_unpushed_commits = repo.git.rev_list('origin/main..main', count=True) != '0'
    except git.exc.GitCommandError:
        # the origin main branch does not yes have any commits
        has_unpushed_commits = True

    if has_unpushed_commits:
        try:
            origin.push().raise_if_error()
        except Exception as e:
            # push failed, try again the next time
            return False
    return True

def check_invariants(state: dict):
    try:
        check_street_levels(state)
        check_player_money(state)
        check_total_money(state)
        if state[AUCTION] is not None:
            check_auction_invariants(state)
    except Exception as e:
        print("Invariant check failed:", e)
        print("State on error:", state)
        raise e


def check_street_levels(state: dict):
    for square in state[BOARD]:
        if square[TYPE] == STREET:
            if square[LEVEL] > 5:
                raise Exception(f"Street {square[NAME]} has level {square[LEVEL]} > 5")
            if square[LEVEL] < 0:
                raise Exception(f"Street {square[NAME]} has level {square[LEVEL]} < 0")
            n_set = square[SET]
            for square2 in state[BOARD]:
                if square2[TYPE] == STREET and square2[SET] == n_set:
                    if abs(square2[LEVEL] - square2[LEVEL]) > 1:
                        raise Exception("Streets from same set have levels with difference > 1")


def check_player_money(state: dict):
    for player in state[PLAYERS]:
        if state[PLAYERS][player][MONEY] < 0:
            raise Exception(f"Player {player} has negative money")
        if state[PLAYERS][player][MONEY] > TOTAL_MONEY:
            raise Exception(f"Player {player} has too much money")


def check_total_money(state: dict):
    total = state[BANK_MONEY]
    for player in state[PLAYERS]:
        total += state[PLAYERS][player][MONEY]

    if total != TOTAL_MONEY:
        raise Exception(f"Total money in the game is {total}, should be {TOTAL_MONEY}")


def check_auction_invariants(state: dict):
    check_auction_agreement(state)
    check_solvability(state)
    check_win_with_higher_bid(state)


def check_auction_agreement(state: dict):
    auction_state = state[AUCTION]
    auction_players = auction_state[PLAYERS]

    for p1, p2 in itertools.combinations(auction_players.keys(), 2):
        if (auction_players[p1][WINNER] != UNKNOWN
                and auction_players[p2][WINNER] != UNKNOWN
                and auction_players[p1][WINNER] != auction_players[p2][WINNER]):
            raise Exception(f"Players {p1} and {p2} disagree on the auction winner")


def check_solvability(state: dict):
    auction_state = state[AUCTION]
    auction_players = auction_state[PLAYERS]
    for p in auction_players.keys():
        if not 0 <= auction_players[p][BID] <= state[PLAYERS][p][MONEY]:
            raise Exception(f"Player {p} bid of {auction_players[p][BID]} but only has {state[PLAYERS][p][MONEY]}")


def check_win_with_higher_bid(state: dict):
    auction_players = state[AUCTION][PLAYERS]
    for p1, p2 in itertools.combinations(auction_players.keys(), 2):
        if auction_players[p2][WINNER] == p1 and not auction_players[p1][BID] > auction_players[p2][BID]:
            raise Exception(f"Player {p2} thinks that {p1} is the winner with a bid of {auction_players[p1][BID]} \
            but player {p2} has a higher bid of {auction_players[p2][BID]}")
