import yaml


def create_new_game():
    pass

def main():
    print("""
    Welcome to monopoly!
    
    1. Create a new game
    2. Join a new game
    3. Rejoin an active game""")
    choice = input("Please select an option (1-3): ")
    match choice:
        case "1":
            print("Creating a new game...")
            # Add logic to create a new game
        case "2":
            print("Joining a new game...")
            # Add logic to join a new game
        case "3":
            print("Rejoining an active game...")
            # Add logic to rejoin an active game
        case _:
            print("Invalid choice. Please select a valid option (1-3).")
            main()  # Restart the menu if the choice is invalid

if __name__ == '__main__':
    main()