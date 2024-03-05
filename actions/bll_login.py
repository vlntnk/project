import uuid

from fastapi import HTTPException, Depends, Request
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database.db_models import Users
from database.dal import UserDAL
from api.validate_models import (CreateUser,
                                 AuthUser_Request, ShowUser,
                                 UpdateUser_Request, Cookie_model)
from database.session import get_db
from jwt_token import generate_jwt
from hashing import Hasher
from settings import COOKIE_ID #вынести в переменные окружения


http_bearer = HTTPBearer()


async def get_cookie_id(request: Request):
    return request.cookies.get(COOKIE_ID)


async def get_data_from_cookie(session: AsyncSession, cookie_id):
    if cookie_id is not None:
        # print(cookie_id, "func")
        async with session.begin():
            dal_object = UserDAL(session)
            record = await dal_object.get_from_cookie(cookie_id)
        if record is not None:
            return Cookie_model(
                session_id=record.session_id,
                jwt_token=record.jwt_token
            )
    raise HTTPException(status_code=400, detail="error")


async def _register_user(body: CreateUser, session) -> Optional[Users]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user_dal(
            name=body.name,
            surname=body.surname,
            email=body.email,
            password=str(Hasher.get_password_hash(body.password))[2:-1],
            categories=body.categories
        )
        return user


async def _get_user_by_email(email: str, session: AsyncSession) -> Optional[Users]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_email_dal(email)
        print(0, user)
        return user
# Get user by email используется не только в функциях представления,
# но и другими crud функциями для получения пользователя из бд


async def _auth_user(body: AuthUser_Request, session): #Подумать над Depends от user by email
    user = await _get_user_by_email(body.email, session)
    if user is not None:
        if Hasher.verify_password(body.password, user.hashed_password.encode()):
            payload = {
                'sub': str(user.user_id),
                'name': user.name,
                'surname': user.surname,
                'email': user.email
            }
            access_token = generate_jwt.encode_jwt(payload)
            return str(access_token)
        raise HTTPException(status_code=404, detail='User is not found, perhaps incorrect email or password')
    raise HTTPException(status_code=404, detail='User is not found, perhaps incorrect email or password')


async def _require_token(
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
        session: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        payload = generate_jwt.decode_jwt(token=credentials.credentials)
    except HTTPException:
        raise HTTPException(status_code=401, detail='Unauthorized, expired time')
    if payload:
        user = await _get_user_by_email(payload['email'], session)
        return ShowUser(
            user_id=str(user.user_id),
            name=user.name,
            surname=user.surname,
            email=user.email,
        )
    raise HTTPException(status_code=401, detail='Unauthorized')


async def _delete_user(session, request_user, cookie_id):
    if cookie_id is not None:
        cookie_data = await get_data_from_cookie(cookie_id, session)
        email = generate_jwt.decode_jwt(cookie_data.jwt_token)
        user_from_db = await _get_user_by_email(email['email'], session)
        if user_from_db is None:
            raise HTTPException(status_code=404, detail='User not found')
        if Hasher.verify_password(request_user.password, user_from_db.hashed_password.encode()):
            async with session.begin():
                user_dal = UserDAL(session)
                db_response = await user_dal.delete_user_dal(user_from_db.user_id)
                if db_response:
                    return db_response
                raise HTTPException(status_code=502, detail='Database error')
        raise HTTPException(status_code=403, detail='Incorrect password')
    raise HTTPException(status_code=401, detail='Unauthorized')


async def _update_user(session, body: UpdateUser_Request, cookie_id):
    async with session.begin():
        if cookie_id is not None:
            cookie_data = await get_data_from_cookie(session, cookie_id)
            user_id = generate_jwt.decode_jwt(cookie_data.jwt_token)['sub']
            user_dal = UserDAL(session)
            try:
                updated_user = await user_dal.update_user_dal(user_id=user_id,
                                                            **body.dict(exclude_none=True))
            except Exception as e:
                raise HTTPException(status_code=406, detail=e)
            if updated_user is not None:
                return updated_user


async def _cookie_auth(session, body: AuthUser_Request):
    user_token = await _auth_user(body, session)
    session_id = str(uuid.uuid4().hex)
    async with session.begin():
        cookie_dal = UserDAL(session)
        cookie = await cookie_dal.add_to_cookie_dal(session_id=session_id, token=user_token)
    return cookie



