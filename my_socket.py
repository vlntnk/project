from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from geopy.distance import geodesic

from actions.bll_login import get_data_from_cookie
from database.session import get_db
from actions.bll_login import get_cookie_id
from jwt_token.generate_jwt import decode_jwt
from database.dal import SalesDAL

socket_router = APIRouter()

test_r = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@test_r.get('/get_data')
async def get_data_notif(session: AsyncSession = Depends(get_db),
                         cookie_id=Depends(get_cookie_id)):
    cookie = await get_data_from_cookie(session, cookie_id)
    data = decode_jwt(cookie.jwt_token)
    radius = data['radius']
    dal_object = SalesDAL(session)
    coords = await dal_object.get_coords()
    return [coords, radius]


@socket_router.websocket('/ws')
async def get_position(websocket: WebSocket, radius=0, coords=[]):
    await manager.connect(websocket)
    print('hello websocket')
    try:
        while True:
            data = await websocket.receive_json()
            print(data)
            for coord in data['data_user'][0]:
                lat = data['lastPosition']['latitude']
                long = data['lastPosition']['longitude']
                distance = geodesic((lat, long), coord).meters
                if distance <= data['data_user'][1]:
                    print('hello')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
