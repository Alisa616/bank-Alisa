import hashlib


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