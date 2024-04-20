from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import ExpiredSignatureError

from actions.bll_login import get_cookie_id, get_data_from_cookie
from database.session import get_db
from jwt_token.generate_jwt import decode_jwt

gateway = APIRouter()


@gateway.get('/')
async def gateway_(session: AsyncSession = Depends(get_db),
                        cookie_id=Depends(get_cookie_id)):
    try:
        if cookie_id is None:
            return RedirectResponse(url='http://localhost:5000/registration')
        else:
            cookie = await get_data_from_cookie(session, cookie_id)
            print(cookie, 'cookie gateway')
            print('gateway')
            try:
                decode_jwt(cookie.jwt_token)
                return RedirectResponse(url='http://localhost:5000/home')
            except Exception as e:
                print(f'{e}')
                return RedirectResponse(url='http://localhost:5000/registration')
    except Exception as e:
        print(f'{e}')

