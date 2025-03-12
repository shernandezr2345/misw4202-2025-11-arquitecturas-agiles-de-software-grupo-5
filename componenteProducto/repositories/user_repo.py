from models.users import User
from db import db

class UserRepository:

    @staticmethod
    def find_by_username(username):
        """Busca un usuario por su nombre de usuario"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create_user(username, password_hash):
        """Crea un nuevo usuario"""
        user = User(username=username, password=password_hash)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_all_users():
        """Obtiene todos los usuarios"""
        return User.query.all()