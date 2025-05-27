import logging

import git

from constants import *
from monopoly import simulate_monopoly, take_action
from repo_util import init_monopoly_simulation_repos, init_monopoly_repo, join_new_game, rejoin_game


def create_new_game():
    print("""
    Great! Let's create a new game of Monopoly.
    1. If you are not in the directory where you want to create the game, please exit and change to it now.
    2. Create a new empty (i.e. no readme file or previous commits) git repository on a server (e.g. github) and copy its URL.
        a. Make sure the other players do the same and you have their access to their URLs.""")
    player_url = get_non_empty_string_from_input("Enter the URL of your repository here: ")
    player_name = get_non_empty_string_from_input("Enter your nickname for the game: ")

    n_other_players = get_int_from_input_in_range("Enter the number of other players (1-5): ", 1, 5)
    players = [{NAME: player_name, URL: player_url}]
    for i in range(n_other_players):
        other_player_name = get_non_empty_string_from_input(f"Enter nickname for player {i + 1}: ")
        other_player_url = get_non_empty_string_from_input(f"Enter url for player {other_player_name}: ")
        players.append({NAME: other_player_name, URL: other_player_url})

    repo = init_monopoly_repo(player_url, player_name, players)
    game_loop(repo)


def join_game():
    print("""
        Great! Let's join a new game of Monopoly.
        1. If you are not in the directory where you want to create the game, please exit and change to it now.
        2. Create a new empty (i.e. no readme file or previous commits) git repository on a server (e.g. github) and copy its URL.
        3. Make sure that you also have the URL of the initiator of the game.""")
    player_url = get_non_empty_string_from_input("Enter the URL of your repository here: ")
    player_name = get_non_empty_string_from_input("Enter your nickname. (It must match the one that the initiator assigned for you): ")
    initiator_url = get_non_empty_string_from_input("Enter the URL for the initiator: ")

    repo = join_new_game(player_url, player_name, initiator_url)
    game_loop(repo)


def rejoin():
    path = get_existing_path_from_input("Enter the path of the existing game: ")
    repo = rejoin_game(path)
    game_loop(repo)


def run_simulations(n=1):
    for i in range(n):
        name = f'monopoly_{i}'
        player_names = [f'm{i}_p{j}' for j in range(3)]
        try:
            repos, initial_commit = init_monopoly_simulation_repos(ROOT, name, player_names)
        except FileExistsError:
            print('Game already exists, loading repos')
            repos = [git.Repo(f'{ROOT}/{name}/{player}') for player in player_names]
            initial_commit = next(repos[0].iter_commits(rev='HEAD', reverse=True))
            print('Loaded initial commit:', initial_commit.hexsha)
        simulate_monopoly(repos, initial_commit)


def main():
    print("""
    Welcome to monopoly!
    
    1. Create a new game
    2. Join a new game
    3. Rejoin an active game
    4. Run simulations""")
    choice = get_int_from_input_in_range("Please select an option (1-4): ",
                                         1, 4)
    match choice:
        case 1:
            create_new_game()
        case 2:
            join_game()
        case 3:
            rejoin()
        case 4:
            n = get_int_from_input("Enter the number of simulations to run: ")
            run_simulations(n)


def game_loop(repo: git.Repo):
    terminated = False
    # suppress error output for git push and fetch
    logging.getLogger("git.remote").setLevel(logging.ERROR)
    while not terminated:
        terminated = take_action(repo)


if __name__ == '__main__':
    main()
