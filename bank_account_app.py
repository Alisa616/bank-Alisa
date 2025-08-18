import tkinter as tk
from tkinter import messagebox, filedialog
import json
import hashlib
import sqlite3



def center_main_window(root, width, height):
    root.geometry(f"{width}x{height}")
    root.update_idletasks()

    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2

    root.geometry(f"{width}x{height}+{x}+{y}")

class BankAccount:
    def __init__(self, owner, balance=0.0, password=None):
        self.owner = owner
        self._balance = balance
        self._password = password

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Невозможно внести отрицательную сумму")
        self._balance += amount

    def set_password(self, password):
        if password is None:
            raise ValueError("Невозможно установить пароль")
        self._password = self.hash_password(password)

    def check_password(self, password_input):
        return self._password == self.hash_password(password_input)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()



    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Невозможно снять отрицательную сумму")
        if amount > self.balance:
            raise ValueError("Недостаточно средств")
        self._balance -= amount

    def transfer(self, target_account, amount: float):
        self.withdraw(amount)
        target_account.deposit(amount)

    @property
    def password(self):
        return self._password


    def to_dict(self):
        return {"owner": self.owner, "balance": self.balance, "password": self.password}

    @staticmethod
    def from_dict(data):
        return BankAccount(data["owner"], data["balance"], data["password"])


    def __str__(self):
        return f"Аккаунт {self.owner} - {self.balance:.2f} руб."

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







class BankApp:
    def __init__(self, root):
        self.root = root
        self.db_manager = Database_manager()
        self.accounts = []
        self.root.title("Bank Accounts")
        center_main_window(self.root, 500, 500)


        btn_create = tk.Button(root, text="Создать аккаунт", command=self.open_create_account_window)
        btn_create.place(x=0, y=0)

        btn_transfer = tk.Button(root, text="Перевод средств", command=self.open_transfer_money_window)
        btn_transfer.place(x=0, y=30)

        scrollbar = tk.Scrollbar(root)
        scrollbar.place(x=250, y=70, height=200)
        self.label_accounts = tk.Label(root, text="Список аккаунтов").place(x=250, y=50)
        self.listbox_accounts = tk.Listbox(root, height=12, width=40, yscrollcommand=scrollbar.set)
        self.listbox_accounts.place(x=250, y=70)
        scrollbar.config(command=self.listbox_accounts.yview)



        self.btn_save = tk.Button(root, text="Сохранить в файл", command=self.save_to_file, bg="#EE82EE")
        self.btn_save.place(x=250, y=175)

        self.btn_open = tk.Button(root, text="Открыть файл", command=self.load_from_file, bg="#EE82EE")
        self.btn_open.place(x=400, y=175)

    def open_create_account_window(self):
        window = tk.Toplevel(self.root)
        window.title("Создание аккаунта")
        center_main_window(window, 300, 300)
        tk.label_create = tk.Label(window, text="Создание нового аккаунта", font=("Arial", 13, "bold"), fg="#7B68EE")
        tk.label_create.place(x=40, y=10)

        tk.label_name = tk.Label(window, text="Имя владельца").place(x=90, y=50)
        entry_name = tk.Entry(window)
        entry_name.place(x=90, y=70)

        tk.label_balance = tk.Label(window, text="Начальный баланс").place(x=90, y=100)
        entry_balance = tk.Entry(window)
        entry_balance.place(x=90, y=120)

        tk.label_password = tk.Label(window, text="Пароль").place(x=90, y=150)
        entry_password = tk.Entry(window, show="*")
        entry_password.place(x=90, y=170)

        tk.label_password_confirm = tk.Label(window, text="Подтвердить пароль").place(x=90, y=200)
        entry_password_confirm = tk.Entry(window, show="*")
        entry_password_confirm.place(x=90, y=220)


        def create_account():
            name = entry_name.get().strip()
            balance = entry_balance.get().strip()
            password = entry_password.get().strip()
            password_confirm = entry_password_confirm.get().strip()
            print("Пароли ",password, password_confirm)
            if not name:
                messagebox.showerror("Ошибка", "Имя не может быть пустым")
                return
            if not balance:
                messagebox.showerror("Ошибка", "Баланс не может быть пустым")
                return
            if not balance.isdigit():
                messagebox.showerror("Ошибка", "Баланс должен быть числом")
                return
            if not password or not password_confirm:
                messagebox.showerror("Ошибка", "Заполните поле пароля")
                return

            try:
                account = BankAccount(name)
                account.set_password(password)
                account.deposit(float(balance))
                self.accounts.append(account)
                self.db_manager.save_account(account)
                self.update_account_list()
                messagebox.showinfo("Успех", f"Аккаунт для {entry_name.get()} создан")
                entry_name.delete(0, tk.END)
                entry_balance.delete(0, tk.END)

                window.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка",str(e))

        btn_create = tk.Button(window, text="Создать аккаунт", command=create_account, bg="#EE82EE")
        btn_create.place(x=90, y=250)




    def open_transfer_money_window(self):
        window = tk.Toplevel(self.root)
        window.title("Перевод средств")
        center_main_window(window, 300, 300)

        tk.label_sender = tk.Label(window, text="Отправитель").place(x=20, y=30)
        entry_sender = tk.Entry(window)
        entry_sender.place(x=20, y=50)

        tk.label_receiver = tk.Label(window, text="Получатель").place(x=150, y=30)
        entry_receiver = tk.Entry(window)
        entry_receiver.place(x=150, y=50)

        tk.label_sum = tk.Label(window, text="Сумма перевода").place(x=100, y=80)
        entry_sum = tk.Entry(window)
        entry_sum.place(x=100, y=100)

        tk.label_password = tk.Label(window, text="Пароль отправителя")
        tk.label_password.place(x=100, y=130)
        entry_password = tk.Entry(window, show="*")
        entry_password.place(x=100, y=150)


        def transfer_money():
            sender_name = entry_sender.get().strip()
            receiver_name = entry_receiver.get().strip()
            sum_text = entry_sum.get().strip()
            password = entry_password.get().strip()

            if not sender_name or not receiver_name or not sum_text or not password:
                messagebox.showerror("Ошибка", "Введите значение")
                return

            try:
                amount = float(sum_text)
                if amount < 0:
                    messagebox.showerror("Ошибка", "Сумма должна быть положительна")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом")
                return

            sender = self.db_manager.get_account(sender_name)
            if sender is None:
                messagebox.showerror("Ошибка", "Отправитель не найден")
                return



            for account in self.accounts:
                if receiver_name == account.owner:
                    receiver = account
                    break
            if receiver is None:
                messagebox.showerror("Ошибка", "Получатель не найден")
                return
            if not sender.check_password(password):
                messagebox.showerror("Ошибка", "Неверный пароль отправителя")
                return
            try:
                sender.transfer(receiver, float(sum_text))
                self.update_account_list()
                messagebox.showinfo("Успех",
                                    f"{float(sum_text):.2f} руб. Переведено от {sender.owner} к {receiver.owner}")
            except ValueError as e:
                messagebox.showerror("Ошибка", e)

            finally:
                window.destroy()


        btn_transfer = tk.Button(window, text="Перевести", command=transfer_money, bg="#EE82EE")
        btn_transfer.place(x=100, y=190)



    def update_account_list(self):
        self.listbox_accounts.delete(0, tk.END)
        for account in self.accounts:
            self.listbox_accounts.insert(tk.END, account)

    def save_to_file(self):
        if not self.accounts:
            messagebox.showwarning("Внимание", "Нет аккаунтов для сохранения")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Сохранить как"
        )
        if not filepath:
            return

        try:
            data = [account.to_dict() for account in self.accounts]
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Успех",f"Данные сохранены в файл:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении:\n{e}")


    def load_from_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON файлы", "*.json")],
            title="Открыть файл аккаунтов"
        )
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.accounts = [BankAccount.from_dict(account) for account in data]
            self.update_account_list()
            messagebox.showinfo("Успех", f"Загружено аккаунтов: {len(self.accounts)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")





if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()

