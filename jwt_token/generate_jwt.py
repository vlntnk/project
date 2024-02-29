from datetime import timedelta, datetime
import jwt
from fastapi import HTTPException

from settings import AuthJWT

settings = AuthJWT()


def encode_jwt(payload: dict,
               private_key: str = settings.private_key_path.read_text(),
               algorithm: str = settings.algorithm,
               access_timedelta: timedelta | None = None,
               access_minutes: int = settings.access_expire):
    now = datetime.utcnow()
    if access_timedelta:
        expire = now + access_timedelta
    else:
        expire = now + timedelta(minutes=access_minutes)
    to_encode_payload = payload.copy()
    to_encode_payload.update(exp=expire, iat=now)
    encoded = jwt.encode(to_encode_payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(token: str | bytes,
               public_key: str = settings.public_key_path.read_text(),
               algorithm: str = settings.algorithm):
    try:
        decoded = jwt.decode(token, public_key, algorithms=algorithm)
    except Exception:
        raise HTTPException(status_code=401, detail='Unauthorized, expired time')
    return decoded
