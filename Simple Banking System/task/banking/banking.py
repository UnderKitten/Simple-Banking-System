# Write your code here
from random import sample
import sqlite3


class BankingSystem:
    def __init__(self):
        self.card_data = None
        self.database()

    def menu(self) -> None:
        while True:
            print("1. Create an account\n2. Log into account\n0. Exit")
            choice: str = input()
            if choice == '1':
                self.create_account()
            elif choice == '2':
                self.login()
            elif choice == '0':
                print('Bye!')
                exit()
            else:
                print('Unknown option.')

    @staticmethod
    def database(card=None, pin=None, balance=None) -> None:
        with sqlite3.connect('card.s3db') as data:
            cursor = data.cursor()
            if not card:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS card (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                number TEXT NOT NULL UNIQUE,
                pin TEXT NOT NULL,
                balance INTEGER DEFAULT 0 NOT NULL
                );
                ''')
            elif card:
                cursor.execute('''
                INSERT OR IGNORE INTO card (number, pin, balance)
                VALUES (?, ?, ?);
                ''', (card, pin, balance))
                cursor.execute('''
                UPDATE card SET balance = (?) WHERE number = (?);
                ''', (balance, card))

    @staticmethod
    def check_credentials(card, close) -> tuple:
        with sqlite3.connect('card.s3db') as data:
            cursor = data.cursor()
            if not close:
                cursor.execute('''
                SELECT number, pin, balance FROM card WHERE number LIKE (?);
                ''', (card,))
                return cursor.fetchone()
            else:
                cursor.execute('''
                DELETE FROM card WHERE number = (?)''', (card,))



    @staticmethod
    def luhn_algorithm(card_number: str) -> bool:
        number = [int(i) for i in card_number]
        for x, num in enumerate(number):
            if (x + 1) % 2 == 0:
                continue
            n = num * 2
            number[x] = n if n < 10 else n - 9
        return sum(number) % 10 == 0

    @staticmethod
    def generate_numbers() -> tuple:
        while True:
            random_card = ''.join(['400000'] + [str(n) for n in sample(range(9), 9)] + ['7'])
            random_PIN = ''.join([str(n) for n in sample(range(9), 4)])
            if not BankingSystem.check_credentials(random_card, False):
                if BankingSystem.luhn_algorithm(random_card):
                    yield random_card, random_PIN
            else:
                continue

    def create_account(self) -> None:
        card, PIN = next(self.generate_numbers())
        self.database(card, PIN, 0)
        print('\nYour card has been created')
        print(f'Your card number:\n{card}')
        print(f'Your card PIN:\n{PIN}\n')

    def login(self) -> None:
        card: str = input('Enter your card number:\n')
        PIN: str = input('Enter your PIN:\n')
        try:
            self.card_data = self.check_credentials(card, False)
            if self.card_data[1] == PIN:
                print('You have successfully logged in!\n')
                self.account()
            else:
                print('Wrong card number or PIN\n')
        except (KeyError, TypeError):
            print('Wrong card number or PIN\n')

    def add_balance(self) -> None:
        addition = input('Enter how much money you want to transfer:\n')
        new_balance = self.card_data[2] + int(addition)
        self.database(self.card_data[0], self.card_data[1], new_balance)

    def transfer_money(self) -> None:
        print('\nTransfer\nEnter card Number')
        transfer_card_number = input()
        while True:
            if not self.luhn_algorithm(transfer_card_number):
                print('Probably you made a mistake in the card number. Please try again!\n')
                return
            elif not self.check_credentials(transfer_card_number, False):
                print('Such a card does not exist.\n')
                return
            else:
                break
        transfer_card_data = self.check_credentials(transfer_card_number, False)
        transfer_amount = int(input('Enter how much money you want to transfer:\n'))
        while True:
            if transfer_amount > self.card_data[2]:
                print('Not enough money!\n')
                return
            else:
                new_balance_sender = self.card_data[2] - transfer_amount
                new_balance_receiver = transfer_card_data[2] + transfer_amount
                self.database(transfer_card_data[0], transfer_card_data[1], new_balance_receiver)
                self.database(self.card_data[0], self.card_data[1], new_balance_sender)
                return

    def account(self) -> None:
        while True:
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            choice = input()
            if choice == '1':
                print(f"\nBalance: {self.card_data[2]}\n")
            elif choice == '2':
                self.add_balance()
                self.card_data = self.check_credentials(self.card_data[0], False)
                print('Success!\n')
            elif choice == '3':
                self.transfer_money()
            elif choice == '4':
                self.check_credentials(self.card_data[0], True)
            elif choice == '5':
                self.card_data = None
                print('You have successfully logged out!\n')
                return
            elif choice == '0':
                print('Bye!')
                exit()
            else:
                print('Unknown option.\n')


BankingSystem().menu()