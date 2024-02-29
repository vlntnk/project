import bcrypt


class Hasher:

    @staticmethod
    def verify_password(plain_password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> bytes:
        salt = bcrypt.gensalt()
        password_bytes: bytes = password.encode('utf-8')
        return bcrypt.hashpw(password_bytes, salt)
