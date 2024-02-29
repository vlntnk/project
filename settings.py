from envparse import Env
from pydantic import BaseModel
from pathlib import Path

enviorment = Env()
BASE_DIR = Path(__file__).parent

REAL_DATABASE_URL = enviorment.str('REAL_DATABASE_URL',
            default='postgresql+asyncpg://postgres:postgresql@localhost:8000/menu')


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / 'jwt_keys' / 'jwt-private.pem'
    public_key_path: Path = BASE_DIR / 'jwt_keys' / 'jwt-public.pem'
    algorithm: str = 'RS256'
    access_expire: int = 15


COOKIE_ID = 'yura_marat_valik_loxi'
