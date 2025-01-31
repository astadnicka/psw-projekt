# user.py
import json
import os

class User:
    USERS_FILE = "users.json"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.isAdmin = False

    @classmethod
    def load_users(cls):
        """Ładowanie użytkowników z pliku JSON."""
        if not os.path.exists(cls.USERS_FILE):
            with open(cls.USERS_FILE, "w") as f:
                json.dump([], f)
        with open(cls.USERS_FILE, "r") as f:
            return json.load(f)

    @classmethod
    def save_users(cls, users):
        """Zapisywanie użytkowników do pliku JSON."""
        with open(cls.USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)

    def create(self):
        """Dodawanie nowego użytkownika."""
        users = self.load_users()
        if any(u["username"] == self.username for u in users):
            raise ValueError(f"Użytkownik o nazwie '{self.username}' już istnieje.")
        users.append({"username": self.username, "password": self.password})
        self.save_users(users)

    @classmethod
    def read(cls, username):
        """Wyszukiwanie użytkownika po nazwie użytkownika."""
        users = cls.load_users()
        user = next((u for u in users if u["username"] == username), None)
        return user

    @classmethod
    def update(cls, username, new_password):
        """Aktualizacja hasła użytkownika."""
        users = cls.load_users()
        user = next((u for u in users if u["username"] == username), None)
        if not user:
            raise ValueError(f"Użytkownik o nazwie '{username}' nie istnieje.")
        user["password"] = new_password
        cls.save_users(users)

    @classmethod
    def delete(cls, username):
        """Usuwanie użytkownika."""
        users = cls.load_users()
        filtered_users = [u for u in users if u["username"] != username]
        if len(filtered_users) == len(users):
            raise ValueError(f"Użytkownik o nazwie '{username}' nie istnieje.")
        cls.save_users(filtered_users)
    
    