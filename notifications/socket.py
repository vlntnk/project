from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from typing import List
import uvicorn


class SocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, add_to_db: bool):
        # if add_to_db:
        #     await self.add_messages_to_database(message)
        for connection in self.active_connections:
            await connection.send_text(message)

    # @staticmethod
    # async def add_messages_to_database(message: str):
    #     async with async_session_maker() as session:
    #         stmt = insert(Messages).values(
    #             message=message
    #         )
    #         await session.execute(stmt)
    #         await session.commit()


socket_route = APIRouter()
manager = SocketManager()


@socket_route.websocket('/ws')
async def websocket(wb: WebSocket):
    await wb.accept()
    while True:
        data = wb.receive_text()
        await wb.send_text(f'Message text was {data}')

# if __name__ == '__main__':
#     uvicorn.run('main:app', host='localhost', port=5400, reload=True)