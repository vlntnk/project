import uuid

from fastapi import APIRouter, HTTPException, Depends, Response, Cookie, Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database.db_models import Users
from database.dal import UserDAL
from api.validate_models import (CreateUser, CreateUser_Response,
                                 AuthUser_Request, Token, ShowUser, DeleteUser_Request,
                                 UpdateUser_Request, Cookie_model)
from database.session import get_db
from jwt_token import generate_jwt
from hashing import Hasher
from settings import COOKIE_ID #вынести в переменные окружения

login_router = APIRouter()

http_bearer = HTTPBearer()


async def get_cookie_id(request: Request):
    return request.cookies.get(COOKIE_ID)


async def get_data_from_cookie(cookie_id: str = Depends(get_cookie_id),
                       session: AsyncSession = Depends(get_db)):
    print(cookie_id, 'cookie_id')
    if cookie_id is not None:
        # print(cookie_id, "func")
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
            password=str(Hasher.get_password_hash(body.password))[2:-1]
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
            cookie_data = await get_data_from_cookie(cookie_id, session)
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
    print(session_id, "uuid")
    async with session.begin():
        cookie_dal = UserDAL(session)
        cookie = await cookie_dal.add_to_cookie_dal(session_id=session_id, token=user_token)
    return cookie


async def get_data_from_cookie(cookie_id: str = Depends(get_cookie_id),
                       session: AsyncSession = Depends(get_db)):
    print(cookie_id, 'cookie_id')
    if cookie_id is not None:
        # print(cookie_id, "func")
        dal_object = UserDAL(session)
        record = await dal_object.get_from_cookie(cookie_id)
        if record is not None:
            return Cookie_model(
                session_id=record.session_id,
                jwt_token=record.jwt_token
            )
    raise HTTPException(status_code=400, detail="error")


@login_router.post('/registration', response_model=CreateUser_Response)
async def register_user(body: CreateUser, db: AsyncSession = Depends(get_db)): # -> Union[HTTPException | CreateUser_Response]:
    user = await _register_user(body, db)
    if user is None:
        raise HTTPException(status_code=409, detail='Invalid credentials')
    reg_token = await _auth_user(body, db)
    return CreateUser_Response(
        name=user.name,
        surname=user.surname,
        email=user.email,
        token=reg_token
    )


@login_router.post('/auth')
async def auth_user(body: AuthUser_Request, session: AsyncSession = Depends(get_db)):
    try:
        token = await _auth_user(body, session)
        return Token(
            access_token=token,
            token_type="Bearer"
        )
    except HTTPException:
        #вынести эту ошибку в отдельную переменную
        return HTTPException(status_code=404, detail='User is not found, perhaps incorrect email')


@login_router.post('/some_secret_page')
async def some_secret_page(user: ShowUser = Depends(_require_token)):
    try:
        if user is not None:
            return ShowUser(
                id=user.id,
                name=user.name,
                surname=user.surname,
                email=user.email,
            )
    except Exception:
        return HTTPException(status_code=401, detail='Unauthorized, expired time')
    return HTTPException(status_code=401, detail='Unauthorized')


@login_router.delete('/delete_user')
async def delete_user(user: DeleteUser_Request,
                      session: AsyncSession = Depends(get_db),
                      cookie_id=Depends(get_cookie_id)):
    try:
        await _delete_user(session, cookie_id=cookie_id, request_user=user)
    except HTTPException as error:
        return HTTPException(status_code=400, detail=error)
    else:
        return Response(content='User deleted')


@login_router.put('/update_user')
async def update_user(credentials: UpdateUser_Request,
#                       user: ShowUser = Depends(_require_token),
                      session: AsyncSession = Depends(get_db),
                      cookie_id=Depends(get_cookie_id)):
    try:
        updated_user = await _update_user(session, body=credentials,
                                          cookie_id=cookie_id)
    except Exception as e:
        return HTTPException(status_code=406, detail=e)
    return updated_user


@login_router.post('/login_by_cookie')
async def login_by_cookie(body: AuthUser_Request,
                          session: AsyncSession = Depends(get_db)):
    response = Response()
    cookie = await _cookie_auth(session, body)
    response.set_cookie(key=COOKIE_ID, value=cookie.session_id)#httponly=True
    if cookie:
        return response
    return {"error": "error"}


@login_router.get('/check_cookie')
async def check_cookie(cookie_id: str = Depends(get_cookie_id),
                       session: AsyncSession = Depends(get_db)):
    print(cookie_id, 'cookie_id')
    if cookie_id is not None:
        # print(cookie_id, "func")
        dal_object = UserDAL(session)
        record = await dal_object.get_from_cookie(cookie_id)
        if record is not None:
            return Cookie_model(
                session_id=record.session_id,
                jwt_token=record.jwt_token
            )
    raise HTTPException(status_code=400, detail="error")