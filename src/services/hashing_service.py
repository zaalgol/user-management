import bcrypt

class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    @staticmethod
    def check_password(hashed_password: str, user_password: str) -> bool:
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))
