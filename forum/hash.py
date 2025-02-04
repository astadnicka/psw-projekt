from app.model.user import User
import bcrypt

def hash_existing_passwords():
    users = User.load_users()
    for user in users:
        if not user["password"].startswith("$2b$"):
            user["password"] = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    User.save_users(users)

hash_existing_passwords()
print("Hasła zostały pomyślnie zaktualizowane.")
