import csv
import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    USERS_FILE = "users.csv"

    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def get_by_id(cls, user_id):
        users = cls.get_all_users()
        for user in users:
            if user.id == str(user_id):
                return user
        return None

    @classmethod
    def get_by_username(cls, username):
        users = cls.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None

    @classmethod
    def get_all_users(cls):
        users = []

        # Create the file if it doesn't exist
        if not os.path.exists(cls.USERS_FILE):
            with open(cls.USERS_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "username", "password_hash"])
            return users

        # Read users from file
        with open(cls.USERS_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(cls(row["id"], row["username"], row["password_hash"]))

        return users

    @classmethod
    def register(cls, username, password):
        # Check if username already exists
        if cls.get_by_username(username):
            return False

        users = cls.get_all_users()

        # Find the highest ID and add 1, or start with 1 if no users
        next_id = 1
        if users:
            next_id = max(int(u.id) for u in users) + 1

        # Create password hash
        password_hash = generate_password_hash(password)

        # Create new user
        new_user = cls(str(next_id), username, password_hash)

        # Add to list and save
        users.append(new_user)
        cls.save_all_users(users)

        return new_user

    @classmethod
    def save_all_users(cls, users):
        with open(cls.USERS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "username", "password_hash"])
            for user in users:
                writer.writerow([user.id, user.username, user.password_hash])

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
