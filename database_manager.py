import sqlite3
from bank_account import BankAccount


class Database_manager:
    def __init__(self, db_path="bank_accounts.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Создает таблицу accounts, если ее нет"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT UNIQUE NOT NULL,
                balance REAL NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def save_account(self, account):
        """Сохраняет новый аккаунт в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO accounts(owner, balance, password)
                VALUES(?, ?, ?)
            ''', (account.owner, account.balance, account.password))

            conn.commit()
            print(f"account {account.owner} saved")

        except sqlite3.IntegrityError:
            raise ValueError(f"account {account.owner} already exists")
        finally:
            conn.close()

    def update_account_balance(self, owner, new_balance):
        """Обновляет баланс аккаунта в базе данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE accounts
            WHERE owner=?
            AND balance=?
        ''', (owner, new_balance))

        conn.commit()
        conn.close()

    def load_all_accounts(self):
        """Загружает все аккаунты из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT owner, balance, password FROM accounts
        ''')

        rows = cursor.fetchall()

        accounts = []
        for row in rows:
            owner, balance, password = row
            account = BankAccount(owner, balance)
            account._password = password
            accounts.append(account)

        conn.close()
        return accounts

    def account_exists(self, owner):
        """Проверяет существование аккаунтов в базе данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM accounts
            WHERE owner=?
        ''', (owner,))

        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def delete_account(self, owner):
        """Удаление аккаунта"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM accounts
            WHERE owner=?
        ''', (owner,))


        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()

        print(f"account {owner} deleted")
        return rows_affected > 0

    def update_accounts_after_transfer(self, sender_owner, sender_balance, receiver_owner, receiver_balance):
        """Обновляет баланс аккаунтов после перевода(транзакции)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('BEGIN TRANSACTION')

            cursor.execute("""
                UPDATE accounts
                SET balance=?
                WHERE owner=?
                """, (sender_owner, sender_balance))


            cursor.execute("""
                UPDATE accounts
                SET balance=?
                WHERE owner=?
                """, (receiver_owner, receiver_balance))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            conn.close()

    def get_account(self, owner):
        """Получает один аккаунт из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT owner, balance, password
            FROM accounts''', (owner,))

        row = cursor.fetchone()
        conn.close()

        if row:
            owner, balance, password = row
            account = BankAccount(owner, balance)
            account._password = password
            return account
        return None