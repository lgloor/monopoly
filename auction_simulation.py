import git

from auction_local import simulate_auction
from constants import ROOT, STARTING_MONEY, N_PLAYERS
from repo_util import init_auction_repo


def sim(repo_number: int):
    name = f'auction_{repo_number}'
    player_names = [f'a{repo_number}_p{i}' for i in range(N_PLAYERS)]
    try:
        money = [STARTING_MONEY for _ in range(N_PLAYERS)]
        repo, initial_commit = init_auction_repo(ROOT, name, player_names, money)
        initialize_state(repo, initial_commit, player_names)
    except FileExistsError:
        print('Repo already exists, loading latest state')
        repo = git.Repo(f'{ROOT}/{name}')
        initial_commit = next(repo.iter_commits(rev='HEAD', reverse=True))

    simulate_auction(repo, initial_commit, player_names)


def initialize_state(repo: git.Repo, initial_commit: git.Commit, player_names: list[str]):
    for name in player_names:
        repo.create_head(name, commit=initial_commit.hexsha)


def run_simulations(start_number: int, iterations: int):
    for i in range(start_number, start_number + iterations):
        sim(i)


if __name__ == '__main__':
    run_simulations(start_number=1, iterations=1)
