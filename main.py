import git

from constants import *
from monopoly import simulate_monopoly, take_action
from repo_util import init_monopoly_simulation_repos, init_monopoly_repo, join_new_game, rejoin_game


def create_new_game():
    path = get_non_existing_path_from_input("Enter a new path for the game: ")
    player_name = get_non_empty_string_from_input("Enter player name: ")
    player_url = get_non_empty_string_from_input("Enter the url for the other players to reach this game: ")

    n_other_players = get_int_from_input_in_range("Enter the number of other players (1-5): ", 1, 5)
    players = [{NAME: player_name, URL: player_url}]
    for i in range(n_other_players):
        other_player_name = get_non_empty_string_from_input(f"Enter name for player {i + 1}: ")
        other_player_url = get_non_empty_string_from_input(f"Enter url for player {i + 1}: ")
        players.append({NAME: other_player_name, URL: other_player_url})

    repo = init_monopoly_repo(path, player_name, players)
    game_loop(repo)


def join_game():
    path = get_non_existing_path_from_input("Enter a new path for the game: ")
    player_name = get_non_empty_string_from_input("Enter player name: ")
    initiator_url = get_non_empty_string_from_input("Enter the url for the initiator: ")

    repo = join_new_game(path, player_name, initiator_url)
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
    3. Rejoin an active game""")
    choice = get_int_from_input_in_range("Please select an option (1-3): ",
                                         1, 3)
    match choice:
        case 1:
            create_new_game()
        case 2:
            join_game()
        case 3:
            rejoin()


def game_loop(repo: git.Repo):
    terminated = False
    while not terminated:
        terminated = take_action(repo)


if __name__ == '__main__':
    run_simulations(3)
