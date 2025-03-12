from repositories.user_repo import UserRepository

class UserView:

    @staticmethod
    def register_user(username, password_hash):
        user = UserRepository.create_user(username, password_hash)
        if not user:
            return {"message": "User creation failed"}, 400
        return user, 201

    @staticmethod
    def get_user_by_username(username):
        user = UserRepository.find_by_username(username)
        if not user:
            return {"message": "User not found"}, 404
        return {
            "id": user.id,
            "username": user.username,
            "password_hash": user.password_hash
        }, 200

    @staticmethod
    def get_all_users():
        users = UserRepository.get_all_users()
        if not users:
            return {"message": "No users found"}, 404
        return users, 200