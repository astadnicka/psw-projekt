import json
import os
import bcrypt

class User:
    USERS_FILE = "users.json"

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.isAdmin = False

    @classmethod
    def load_users(cls):
        if not os.path.exists(cls.USERS_FILE):
            with open(cls.USERS_FILE, "w") as f:
                json.dump([], f)
        with open(cls.USERS_FILE, "r") as f:
            return json.load(f)

    @classmethod
    def save_users(cls, users):
        with open(cls.USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)

    def create(self):
        users = self.load_users()
        if any(u["username"] == self.username for u in users):
            raise ValueError(f"Użytkownik o nazwie '{self.username}' już istnieje.")
        
        users.append({"username": self.username, "password": self.password.decode('utf-8'), "isAdmin": self.isAdmin})
        self.save_users(users)

    @classmethod
    def read(cls, username):
        users = cls.load_users()
        user = next((u for u in users if u["username"] == username), None)
        return user

    @classmethod
    def update(cls, username, new_password):
        users = cls.load_users()
        user = next((u for u in users if u["username"] == username), None)
        if not user:
            raise ValueError(f"Użytkownik o nazwie '{username}' nie istnieje.")
        user["password"] = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cls.save_users(users)

    @classmethod
    def delete(cls, username):
        users = cls.load_users()
        filtered_users = [u for u in users if u["username"] != username]
        if len(filtered_users) == len(users):
            raise ValueError(f"Użytkownik o nazwie '{username}' nie istnieje.")
        cls.save_users(filtered_users)

    @classmethod
    def verify_password(cls, username, password):
        user = cls.read(username)
        if user:
            return bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
        return False
