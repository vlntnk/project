import uvicorn
from fastapi import FastAPI, APIRouter, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from api.pl_login import login_router
from api.pl_sales import sales_router
from api.gateway import gateway
from my_socket import socket_router
from my_socket import test_r
from Maps.parse import get_json

app = FastAPI(title='Menu app')
templates = Jinja2Templates(directory="./Maps")

app.mount('/static', StaticFiles(directory="Maps/static"), name='static')
main_api_router = APIRouter()
main_api_router.include_router(login_router, prefix='/user', tags=['User operations'])
main_api_router.include_router(sales_router, prefix='/sales', tags=['Sales operations'])
main_api_router.include_router(gateway)
main_api_router.include_router(socket_router)
main_api_router.include_router(test_r)
app.include_router(main_api_router)


@app.get('/home', response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse("index.html", context={"request": request})
    except Exception as e:
        print(f'{e}')


@app.get('/registration', response_class=HTMLResponse)
async def registration(request: Request):
    try:
        # data = get_json()
        return templates.TemplateResponse("registration.html", context={"request": request})
    except Exception as e:
        print(f'{e}')


@app.get('/profile', response_class=HTMLResponse)
async def sales(request: Request):
    try:
        return templates.TemplateResponse('profile.html', context={"request": request})
    except Exception as e:
        print(f'{e}')


@app.get('/settings', response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})


if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=5000, reload=True)
