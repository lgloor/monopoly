import itertools
from random import Random

import git
import yaml


def simulate_auction(repo: git.Repo, initial_commit: git.Commit, players: list[str]) -> None:
    """
    Simulate the auction process
    :param repo: git repository
    :param initial_commit: initial commit of the repository
    :param players: names of the players
    """

    # Use the initial commit to seed the random number generator
    # This way, the simulation will be deterministic
    # and can be reproduced if something fails
    rand = Random(initial_commit.hexsha)

    while not terminated(repo, players):
        p = rand.choice(players)
        possible_actions = [lambda: merge(repo, rand.choice(sorted(list(set(players).difference({p})))), p)]
        state = read_state(repo, p)
        if is_bid_enabled(p, state):
            possible_actions.append(lambda: bid(p, rand.randint(highest_known_bid(state) + 1, state[p]['money']), repo))
        if is_stand_enabled(p, state):
            possible_actions.append(lambda: stand(p, repo))
        if is_pass_enabled(p, state):
            possible_actions.append(lambda: do_pass(p, repo))
        if is_next_round_enabled(p, state):
            possible_actions.append(lambda: next_round(p, repo))
        if is_choose_winner_enabled(p, state):
            possible_actions.append(lambda: choose_winner(p, repo))
        rand.choice(possible_actions)()


def terminated(repo: git.Repo, players: list[str]) -> bool:
    """
    Check if all players know that everyone knows who the winner is
    :param repo: git repository
    :param players:
    :return:
    """
    for p in players:
        state = read_state(repo, p)
        for p2 in players:
            if state[p2]['winner'] == 'UNKNOWN':
                return False
    return True


def is_bid_enabled(p: str, state: dict) -> bool:
    """
    Check if the player is allowed to bid
    :param p: player name
    :param state: state of current branch
    :return: True if the player is allowed to bid, False otherwise
    """

    has_enough_money = highest_known_bid(state) < state[p]['money']
    return (common_preconditions(p, state)
            and has_enough_money)


def highest_known_bid(state: dict) -> int:
    max_bid = 0
    for p in state.keys():
        max_bid = max(max_bid, state[p]['bid'])
    return max_bid


def bid(p: str, amount: int, repo: git.Repo) -> None:
    """
    Perform a bid for the player
    :param p: player name
    :param amount: amount to bid
    :param repo: current repository
    """

    state = read_state(repo, p)
    state[p]['bid'] = amount
    state[p]['last_action'] = 'BID'

    write_and_commit(repo, state, p, f"{p} bid {amount}")


def is_stand_enabled(p: str, state: dict) -> bool:
    """
    Check if the player is allowed to stand
    :param p: player name
    :param state: state of current branch
    :return: True if the player is allowed to stand, False otherwise
    """

    return (common_preconditions(p, state)
            and all_other_bids_lower(p, state))


def stand(p: str, repo: git.Repo) -> None:
    state = read_state(repo, p)
    state[p]['last_action'] = 'STAND'

    write_and_commit(repo, state, p, f"{p} stand")


def is_pass_enabled(p: str, state: dict) -> bool:
    """
    Check if the player is allowed to pass
    :param p: player name
    :param state: state of current branch
    :return: True if the player is allowed to pass, False otherwise
    """

    return common_preconditions(p, state)


def do_pass(p: str, repo: git.Repo) -> None:
    state = read_state(repo, p)
    state[p]['last_action'] = 'PASS'

    write_and_commit(repo, state, p, f"{p} pass")


def common_preconditions(p: str, state: dict) -> bool:
    passed = state[p]['last_action'] == 'PASS'
    winner_unknown = state[p]['winner'] == 'UNKNOWN'
    no_action_in_current_round = state[p]['last_action'] == 'CHANGE'
    return (not passed
            and winner_unknown
            and no_action_in_current_round
            and is_ready_for_action(p, state)
            and exists_player_in_same_round(p, state))


def exists_player_in_same_round(p: str, state: dict) -> bool:
    for p2 in state.keys():
        if p2 == p:
            continue
        if state[p2]['round'] == state[p]['round']:
            return True
    return False


def is_ready_for_action(p: str, state: dict) -> bool:
    for p2 in state.keys():
        if not (state[p2]['round'] == state[p]['round']
                or state[p2]['last_action'] == 'PASS'):
            return False
    return True


def all_other_bids_lower(p: str, state: dict) -> bool:
    for p2 in state.keys():
        if p2 == p:
            continue
        if state[p2]['bid'] >= state[p]['bid']:
            return False
    return True


def merge(repo: git.Repo, sender: str, receiver: str) -> None:
    """
    Merge the state of the sender into the receiver
    :param repo: git repository
    :param sender: player who is sending the state
    :param receiver: player who is receiving the state
    """

    sender_state = read_state(repo, sender)
    sender_parent = repo.head.commit
    receiver_state = read_state(repo, receiver)
    receiver_parent = repo.head.commit

    merged = _merge_states(sender_state, receiver_state)

    write_and_commit(repo, merged, receiver,
                     f"{receiver} received and merged {sender}'s state",
                     [sender_parent, receiver_parent])


def _merge_states(sender_state: dict, receiver_state: dict) -> dict:
    merged = {}
    for p in sender_state.keys():
        if sender_state[p] == receiver_state[p]:
            merged[p] = sender_state[p]
        elif sender_state[p]['round'] > receiver_state[p]['round']:
            merged[p] = sender_state[p]
        elif sender_state[p]['round'] < receiver_state[p]['round']:
            merged[p] = receiver_state[p]
        elif sender_state[p]['winner'] != 'UNKNOWN' and receiver_state[p]['winner'] == 'UNKNOWN':
            merged[p] = sender_state[p]
        elif sender_state[p]['winner'] == 'UNKNOWN' and receiver_state[p]['winner'] != 'UNKNOWN':
            merged[p] = receiver_state[p]
        elif sender_state[p]['last_action'] == 'CHANGE' and not receiver_state[p]['last_action'] == 'CHANGE':
            merged[p] = receiver_state[p]
        elif sender_state[p]['last_action'] != 'CHANGE' and receiver_state[p]['last_action'] == 'CHANGE':
            merged[p] = sender_state[p]
        else:
            raise Exception('Forgot some condition')
    return merged


def is_next_round_enabled(p: str, state: dict) -> bool:
    passed = state[p]['last_action'] == 'PASS'
    winner_unknown = state[p]['winner'] == 'UNKNOWN'
    made_action_in_current_round = state[p]['last_action'] != 'CHANGE'
    return (not passed
            and winner_unknown
            and made_action_in_current_round
            and all_made_action_or_are_ahead(p, state))


def all_made_action_or_are_ahead(p: str, state: dict) -> bool:
    for p2 in state.keys():
        passed = state[p2]['last_action'] == 'PASS'
        made_action = (state[p2]['last_action'] != 'CHANGE'
                       or state[p2]['round'] > state[p]['round'])
        if not (passed or made_action):
            return False
    return True


def next_round(p: str, repo: git.Repo) -> None:
    state = read_state(repo, p)
    state[p]['round'] += 1
    state[p]['last_action'] = 'CHANGE'

    write_and_commit(repo, state, p, f"{p} moved to next round")


def is_choose_winner_enabled(p: str, state: dict) -> bool:
    winner_unknown = state[p]['winner'] == 'UNKNOWN'
    return (winner_unknown
            and (all_have_passed(state) or winner_exists(state)))


def all_have_passed(state: dict) -> bool:
    for p in state.keys():
        if not state[p]['last_action'] == 'PASS':
            return False
    return True


def winner_exists(state: dict) -> bool:
    for p in state.keys():
        if state[p]['last_action'] == 'PASS':
            continue

        if all_others_meet_conditions(p, state):
            return True
    return False


def all_others_meet_conditions(p: str, state: dict) -> bool:
    """
    Check if all other players meet the conditions for player p to be the winner
    :param p: player to check for
    :param state: current state
    :return: True if all other players meet the conditions, False otherwise
    """
    others = set(state.keys()).difference({p})
    for p2 in others:
        if (state[p2]['last_action'] != 'PASS' or
                state[p]['bid'] <= state[p2]['bid'] or
                state[p]['round'] <= state[p2]['round']):
            return False
    return True


def choose_winner(p: str, repo: git.Repo) -> None:
    state = read_state(repo, p)
    if all_have_passed(state):
        winner = "NONE"
    else:
        winner: str = get_winner(state)

    state[p]['winner'] = winner

    write_and_commit(repo, state, p, f"{p} chose winner {winner}")


def get_winner(state: dict) -> str:
    for p in state.keys():
        if state[p]['last_action'] == 'PASS':
            continue

        return p
    return ""  # never happens because of the check in is_choose_winner_enabled


def write_and_commit(repo: git.Repo, state: dict, committer: str, message: str,
                     parents: list[git.Commit] | None = None) -> None:
    check_invariants(state)

    with open(f"{repo.working_tree_dir}/state.yml", 'w') as f:
        yaml.dump(state, f)

    author = git.Actor(committer, f"{committer}@auction.com")
    repo.index.add([f"{repo.working_tree_dir}/state.yml"])
    repo.index.commit(message,
                      parent_commits=parents,
                      author=author,
                      committer=author)


def check_invariants(state: dict) -> None:
    check_agreement(state)
    check_solvability(state)
    check_win_with_higher_bid(state)


def check_agreement(state: dict) -> None:
    players = state.keys()
    for p, p2 in itertools.product(players, players):
        if not (state[p]['winner'] == 'UNKNOWN'
                or state[p2]['winner'] == 'UNKNOWN'
                or state[p]['winner'] == state[p2]['winner']):
            raise Exception(f"Agreement invariant violated: {p} and {p2} disagree on the winner")


def check_solvability(state: dict) -> None:
    for p in state.keys():
        if state[p]['bid'] not in range(0, state[p]['money'] + 1):
            raise Exception(
                f"Solvability invariant violated: {p} has bid {state[p]['bid']} but only has {state[p]['money']} money")


def check_win_with_higher_bid(state: dict) -> None:
    for p, p2 in itertools.product(state.keys(), state.keys()):
        if p == p2:
            continue
        if state[p2]['winner'] == p and not state[p]['bid'] > state[p2]['bid']:
            raise Exception(
                f"Win with higher bid invariant violated: {p} won with a bid of {state[p]['bid']} but {p2} had a higher bid of {state[p2]['bid']}")


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
