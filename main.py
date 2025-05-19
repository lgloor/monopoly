import git

from constants import *
from monopoly import simulate_monopoly
from repo_util import init_monopoly_simulation_repos


def create_new_game():
    pass


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
            print("Creating a new game...")
            # Add logic to create a new game
        case 2:
            print("Joining a new game...")
            # Add logic to join a new game
        case 3:
            print("Rejoining an active game...")
            # Add logic to rejoin an active game


if __name__ == '__main__':
    run_simulations(10)
