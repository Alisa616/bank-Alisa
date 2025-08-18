import tkinter as tk
from tkinter import messagebox, filedialog
import json
from bank_account import BankAccount
from database_manager import Database_manager
from utils import center_main_window, validate_float, format_currency


class BankApp:
    def __init__(self, root):
        self.root = root
        self.db_manager = Database_manager()
        self.root.title("Bank Accounts - 1.0")
        center_main_window(self.root, 500, 500)

        self.create_widgets()

        self.update_account_list()

        # self.update_statistics()

    def create_widgets(self):
        """Создает все виджеты интерфейса"""

        title_label =  tk.Label(self.root, text="Банковская система",
                                font=('Arial', 16, 'bold'), fg="#2E4057")
        title_label.place(x=180, y=10)

        btn_create = tk.Button(self.root, text="Создать аккаунт",
                               command=self.open_create_account_window,
                               width=15, bg="#4CAF50", fg="white")
        btn_create.place(x=20, y=50)

        btn_transfer = tk.Button(self.root, text="Перевод средств",
                                 command=self.open_transfer_money_window,
                                 width=15, bg="#F44336", fg="white")
        btn_transfer.place(x=20, y=90)

        btn_delete = tk.Button(self.root, text="Удалить аккаунт",
                               command=self.open_delete_account_window,
                               width=15, bg="#4CAF50", fg="white")
        btn_delete.place(x=20, y=130)

        btn_deposit = tk.Button(self.root, text="Пополнить счет",
                               command=self.open_deposit_window,
                               width=15, bg="#FF9800", fg="white")
        btn_deposit.place(x=20, y=170)

        btn_withdraw = tk.Button(self.root, text="Снять средства",
                               command=self.open_withdraw_window,
                               width=15, bg="#9C27B0", fg="white")
        btn_withdraw.place(x=20, y=210)

        btn_refresh = tk.Button(self.root, text="🔄 Обновить",
                               command=self.refresh_all,
                               width=15, bg="#607D8B", fg="white")
        btn_refresh.place(x=20, y=260)

        self.label_accounts = tk.Label(self.root, text="Список аккаунтов",
                                       font=('Arial', 12, 'bold'))
        self.label_accounts.place(x=200, y=80)

        list_frame = tk.Frame(self.root)
        list_frame.place(x=200, y=80)

        scrollbar = tk.Scrollbar(self.root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_accounts = tk.Listbox(self.root, height=15, width=40,
                                           yscrollcommand=scrollbar.set,
                                           font=('Courier', 10))
        self.listbox_accounts.pack(side=tk.RIGHT)
        scrollbar.config(command=self.listbox_accounts.yview)

        self.stats_frame = tk.Frame(self.root, relief=tk.RAISED, bd=2)
        self.stats_frame.place(x=20, y=320)


    def update_account_list(self):
        self.listbox_accounts.delete(0, tk.END)
        accounts = self.db_manager.load_all_accounts()

        if not accounts:
            self.listbox_accounts.insert(tk.END, "Нет аккаунта в бд")
        else:
            for account in accounts:
                display_text = f'{account.owner:<20} | {account.balance:>12.2f}'
                self.listbox_accounts.insert(tk.END, display_text)


    def update_statistics(self):
        """Обновляет статистику"""
        pass


    def refresh_all(self):
        """Обновляет весь интерфейс"""
        pass


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

    def open_delete_account_window(self):
        """Открывает окно для удаления аккаунта"""
        pass

    def open_deposit_window(self):
        """Открывает окно пополнения счета"""
        pass

    def open_withdraw_window(self):
        """Открывает окно снятия средств"""
        pass

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

def main():
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
