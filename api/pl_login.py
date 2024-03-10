from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.security.http import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.validate_models import (CreateUser, CreateUser_Response,
                                 AuthUser_Request, Token, ShowUser, DeleteUser_Request,
                                 UpdateUser_Request)
from database.session import get_db
from actions.bll_login import (_require_token, _register_user, _auth_user,
                               _update_user, _delete_user, _cookie_auth, get_cookie_id,
                               get_data_from_cookie)
from settings import COOKIE_ID #вынести в переменные окружения

login_router = APIRouter()


@login_router.post('/registration', response_model=CreateUser_Response)
async def register_user(body: CreateUser,
                        db: AsyncSession = Depends(get_db)): # -> Union[HTTPException | CreateUser_Response]:
    user = await _register_user(body, db)
    if user is None:
        raise HTTPException(status_code=409, detail='Invalid credentials')
    response = Response()
    auth_credentials = AuthUser_Request(
        email=body.email,
        password=body.password
    )
    cookie = await _cookie_auth(db, auth_credentials)
    response.set_cookie(key=COOKIE_ID, value=cookie.session_id)  # httponly=True
    if cookie:
        return (
        #     CreateUser_Response(
        #     name=user.name,
        #     surname=user.surname,
        #     email=user.email,
        #     token=cookie.jwt_token
        # ),
        response)


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
                      session: AsyncSession = Depends(get_db),
                      cookie_id=Depends(get_cookie_id)):
    try:
        updated_user = await _update_user(session, body=credentials,
                                          cookie_id=cookie_id)
    except Exception as e:
        print(f"{e}")
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


@login_router.get('/check_cookie', response_description='get info from cookie')
async def check_cookie(cookie_id: str = Depends(get_cookie_id),
                       session: AsyncSession = Depends(get_db)):
    cookie = await get_data_from_cookie(session, cookie_id)
    if cookie is None:
        return HTTPException(status_code=402, detail='unauthorized')
    return cookie