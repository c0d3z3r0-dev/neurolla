from terminal.account_manager import AccountManager
from terminal.bot_control import BotControl


class NeuroLLaTerminal:
    def __init__(self):
        self.accounts = AccountManager()
        self.bot = BotControl()

    def run(self):
        while True:
            print("\n=== NeuroLLa Dev Terminal ===")
            print("1. Show Accounts")
            print("2. Start Bot")
            print("3. Stop Bot")
            print("4. Portfolio Status")
            print("5. Exit")

            choice = input("> ")

            if choice == "1":
                self.accounts.show()

            elif choice == "2":
                self.bot.start()

            elif choice == "3":
                self.bot.stop()

            elif choice == "4":
                self.bot.status()

            elif choice == "5":
                break