import os
from random import Random

ROOT = os.path.dirname(os.path.abspath(__file__))
N_PLAYERS: int = 3
STARTING_MONEY: int = 1500
TOTAL_MONEY: int = 118_660

PLAYERS = 'players'
URL = 'url'
BANKRUPT = 'bankrupt'
IN_JAIL = 'in_jail'
JAIL_TIME = 'jail_time'
CONSECUTIVE_DOUBLES = 'consecutive_doubles'
BANK = 'bank'
BANK_MONEY = 'bank_money'
DEBT = 'debt'
CREDITOR = 'creditor'
AMOUNT = 'amount'
NEXT_PHASE = 'next_phase'
ORDER = 'order'
ACTIVE = 'active'
GOOJF_CC_OWNER = 'goojf_cc_owner'
GOOJF_CH_OWNER = 'goojf_ch_owner'

STREET = 'street'
RAIL = 'rail'
UTILITY = 'util'
CHANCE = 'chance'
COMMUNITY_CHEST = 'community_chest'
TAX = 'tax'
GO = 'go'
GO_TO_JAIL = 'go_to_jail'
FREE_PARKING = 'free_parking'
JAIL = 'jail'
MORTGAGED = 'mortgaged'
LEVEL = 'level'
HOUSE_COST = 'house_cost'
RENT = 'rent'
OWNER = 'owner'
VALUE = 'value'
TYPE = 'type'
NAME = 'name'
SET = 'set'

BOARD = 'board'
POSITION = 'position'
MONEY = 'money'

PHASE = 'phase'
PRE_ROLL = 'pre-roll'
ROLL = 'roll'
POST_ROLL = 'post-roll'
DOUBLES_CHECK = 'doubles-check'
FREE_4_ALL = 'free-4-all'
FREE_4_ALL_ORDER = 'free-4-all-order'
BANKRUPTCY_PREVENTION = 'bankruptcy-prevention'
AUCTION = 'auction'

ASSET = 'asset'
INITIATOR = 'initiator'
BID = 'bid'
LAST_ACTION = 'last-action'
ROUND = 'round'
WINNER = 'winner'
CHANGE = 'change'
PASS = 'pass'
STAND = 'stand'

UNKNOWN = 'unknown'
NONE = 'none'

COLLECT = 'collect'
PAY = 'pay'
ADVANCE_TO = 'advance_to'
GOOFJ_CC = 'goojf_cc'
GOOFJ_CH = 'goojf_ch'

SQUARE = 'square'
JAIL_IDX = 10
INIT_BOARD = [
    {TYPE: GO, NAME: GO},
    {TYPE: STREET, NAME: 'Mediterranean Avenue', VALUE: 60, OWNER: None, RENT: [2, 10, 30, 90, 160, 250],
     HOUSE_COST: 50, LEVEL: 0, SET: 1, MORTGAGED: False},
    {TYPE: COMMUNITY_CHEST, NAME: COMMUNITY_CHEST},
    {TYPE: STREET, NAME: 'Baltic Avenue', VALUE: 60, OWNER: None, RENT: [4, 20, 60, 180, 320, 450], HOUSE_COST: 50,
     LEVEL: 0, SET: 1, MORTGAGED: False},
    {TYPE: TAX, NAME: 'Income Tax', VALUE: 200},
    {TYPE: RAIL, NAME: 'Reading Railroad', VALUE: 200, OWNER: None, MORTGAGED: False},
    {TYPE: STREET, NAME: 'Oriental Avenue', VALUE: 100, OWNER: None, RENT: [6, 30, 90, 270, 400, 550],
     HOUSE_COST: 50, LEVEL: 0, SET: 2, MORTGAGED: False},
    {TYPE: CHANCE, NAME: 'Chance'},
    {TYPE: STREET, NAME: 'Vermont Avenue', VALUE: 100, OWNER: None, RENT: [6, 30, 90, 270, 400, 550],
     HOUSE_COST: 50, LEVEL: 0, SET: 2, MORTGAGED: False},
    {TYPE: STREET, NAME: 'Connecticut Avenue', VALUE: 120, OWNER: None, RENT: [8, 40, 100, 300, 450, 600],
     HOUSE_COST: 50, LEVEL: 0, SET: 2, MORTGAGED: False},

    {TYPE: JAIL, NAME: JAIL},
    {TYPE: STREET, NAME: 'St. Charles Place', VALUE: 140, OWNER: None, RENT: [10, 50, 150, 450, 625, 750],
     HOUSE_COST: 100, LEVEL: 0, SET: 3, MORTGAGED: False},
    {TYPE: UTILITY, NAME: 'Electric Company', VALUE: 150, OWNER: None, MORTGAGED: False},
    {TYPE: STREET, NAME: 'States Avenue', VALUE: 140, OWNER: None, RENT: [10, 50, 150, 450, 625, 750],
     HOUSE_COST: 100, LEVEL: 0, SET: 3, MORTGAGED: False},
    {TYPE: STREET, NAME: 'Virginia Avenue', VALUE: 160, OWNER: None, RENT: [12, 60, 180, 500, 700, 900],
     HOUSE_COST: 100, LEVEL: 0, SET: 3, MORTGAGED: False},
    {TYPE: RAIL, NAME: 'Pennsylvania Railroad', VALUE: 200, OWNER: None, MORTGAGED: False},
    {TYPE: STREET, NAME: 'St. James Place', VALUE: 180, OWNER: None, RENT: [14, 70, 200, 550, 750, 950],
     HOUSE_COST: 100, LEVEL: 0, SET: 4, MORTGAGED: False},
    {TYPE: COMMUNITY_CHEST, NAME: COMMUNITY_CHEST},
    {TYPE: STREET, NAME: 'Tennessee Avenue', VALUE: 180, OWNER: None, RENT: [14, 70, 200, 550, 750, 950],
     HOUSE_COST: 100, LEVEL: 0, SET: 4, MORTGAGED: False},
    {TYPE: STREET, NAME: 'New York Avenue', VALUE: 200, OWNER: None, RENT: [16, 80, 220, 600, 800, 1000],
     HOUSE_COST: 100, LEVEL: 0, SET: 4, MORTGAGED: False},

    {TYPE: FREE_PARKING, NAME: FREE_PARKING},
    {TYPE: STREET, NAME: 'Kentucky Avenue', VALUE: 220, OWNER: None, RENT: [18, 90, 250, 700, 875, 1050],
     HOUSE_COST: 150, LEVEL: 0, SET: 5, MORTGAGED: False},
    {TYPE: CHANCE, NAME: CHANCE},
    {TYPE: STREET, NAME: 'Indiana Avenue', VALUE: 220, OWNER: None, RENT: [18, 90, 250, 700, 875, 1050],
     HOUSE_COST: 150, LEVEL: 0, SET: 5, MORTGAGED: False},
    {TYPE: STREET, NAME: 'Illinois Avenue', VALUE: 240, OWNER: None, RENT: [20, 100, 300, 750, 925, 1100],
     HOUSE_COST: 150, LEVEL: 0, SET: 5, MORTGAGED: False},
    {TYPE: RAIL, NAME: 'B&O Railroad', VALUE: 200, OWNER: None, MORTGAGED: False},
    {TYPE: STREET, NAME: 'Atlantic Avenue', VALUE: 260, OWNER: None, RENT: [22, 110, 330, 800, 975, 1150],
     HOUSE_COST: 150, LEVEL: 0, SET: 6, MORTGAGED: False},
    {TYPE: STREET, NAME: 'Ventnor Avenue', VALUE: 260, OWNER: None, RENT: [22, 110, 330, 800, 975, 1150],
     HOUSE_COST: 150, LEVEL: 0, SET: 6, MORTGAGED: False},
    {TYPE: UTILITY, NAME: 'Water Works', VALUE: 150, OWNER: None, MORTGAGED: False},
    {TYPE: STREET, NAME: 'Marvin Gardens', VALUE: 280, OWNER: None, RENT: [24, 120, 360, 850, 1025, 1200],
     HOUSE_COST: 150, LEVEL: 0, SET: 6, MORTGAGED: False},

    {TYPE: GO_TO_JAIL, NAME: GO_TO_JAIL},
    {TYPE: STREET, NAME: 'Pacific Avenue', VALUE: 300, OWNER: None, RENT: [26, 130, 390, 900, 1100, 1275],
     HOUSE_COST: 200, LEVEL: 0, SET: 7, MORTGAGED: False},
    {TYPE: STREET, NAME: 'North Carolina Avenue', VALUE: 300, OWNER: None, RENT: [26, 130, 390, 900, 1100, 1275],
     HOUSE_COST: 200, LEVEL: 0, SET: 7, MORTGAGED: False},
    {TYPE: COMMUNITY_CHEST, NAME: COMMUNITY_CHEST},
    {TYPE: STREET, NAME: 'Pennsylvania Avenue', VALUE: 320, OWNER: None, RENT: [28, 150, 450, 1000, 1200, 1400],
     HOUSE_COST: 200, LEVEL: 0, SET: 7, MORTGAGED: False},
    {TYPE: RAIL, NAME: 'Short Line', VALUE: 200, OWNER: None, MORTGAGED: False},
    {TYPE: CHANCE, NAME: CHANCE},
    {TYPE: STREET, NAME: 'Park Place', VALUE: 350, OWNER: None, RENT: [35, 175, 500, 1100, 1300, 1500],
     HOUSE_COST: 200, LEVEL: 0, SET: 8, MORTGAGED: False},
    {TYPE: TAX, NAME: 'Luxury Tax', VALUE: 100},
    {TYPE: STREET, NAME: 'Boardwalk', VALUE: 400, OWNER: None, RENT: [50, 200, 600, 1400, 1700, 2000],
     HOUSE_COST: 200, LEVEL: 0, SET: 8, MORTGAGED: False},
]

CC_CARDS = [
    {TYPE: COLLECT, AMOUNT: 50},
    {TYPE: PAY, AMOUNT: 50},
    {TYPE: ADVANCE_TO, SQUARE: 39},
    {TYPE: GO_TO_JAIL},
    {TYPE: GOOFJ_CC}
]

CH_CARDS = [
    {TYPE: COLLECT, AMOUNT: 50},
    {TYPE: PAY, AMOUNT: 50},
    {TYPE: ADVANCE_TO, SQUARE: 0},
    {TYPE: GO_TO_JAIL},
    {TYPE: GOOFJ_CH}
]


def collect_from_bank(player: str, state: dict, amount: int):
    remaining_bank_money = state[BANK_MONEY]
    if remaining_bank_money >= amount:
        state[PLAYERS][player][MONEY] += amount
        state[BANK_MONEY] -= amount
    else:
        state[PLAYERS][player][MONEY] += remaining_bank_money
        state[BANK_MONEY] = 0


def pay_bank(player: str, state: dict, amount: int):
    state[PLAYERS][player][MONEY] -= amount
    state[BANK_MONEY] += amount


def go_to_jail(player: str, state: dict):
    player_state = state[PLAYERS][player]
    player_state[IN_JAIL] = True
    player_state[CONSECUTIVE_DOUBLES] = 0
    player_state[POSITION] = JAIL_IDX
    initialize_free_4_all(state)


def collect_if_pass_go(player: str, state: dict, old_pos: int, new_pos: int):
    if new_pos < old_pos:
        collect_from_bank(player, state, 200)


def is_property(square: dict) -> bool:
    return square[TYPE] in {STREET, RAIL, UTILITY}


def owns_all_of_same_set(owner: str, n_set: int, state: dict) -> bool:
    for s in state[BOARD]:
        if (s[TYPE] == STREET
                and s[SET] == n_set
                and s[OWNER] != owner):
            return False
    return True


def initialize_free_4_all(state: dict):
    assert state[FREE_4_ALL_ORDER] is None, 'Free for all must not be initialized'
    rand = Random(str(state))
    f4a_order: list[str] = [p for p in state[ORDER] if not state[PLAYERS][p][BANKRUPT]]
    rand.shuffle(f4a_order)

    state[PHASE] = FREE_4_ALL
    state[FREE_4_ALL_ORDER] = f4a_order


def get_int_from_input(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter an integer.")


def get_int_from_input_in_range(prompt: str, min_value: int, max_value: int) -> int:
    while True:
        value = get_int_from_input(prompt)
        if min_value <= value <= max_value:
            return value
        else:
            print(f"Invalid input. Please enter an integer between {min_value} and {max_value}.")


def get_non_existing_path_from_input(prompt: str) -> str:
    while True:
        path = input(prompt)
        if not os.path.exists(path):
            return path
        else:
            print(f"Path {path} already exists. Please enter a different path.")


def get_existing_path_from_input(prompt: str) -> str:
    while True:
        path = input(prompt)
        if os.path.exists(path):
            return path
        else:
            print(f"Path {path} does not exist. Please enter a different path.")


def get_non_empty_string_from_input(prompt: str) -> str:
    while True:
        value = input(prompt)
        if value.strip():
            return value
        else:
            print("Invalid input. Please enter a non-empty string.")

