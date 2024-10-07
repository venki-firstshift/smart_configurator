from typing import List
from fastapi import WebSocket, Request, WebSocketDisconnect

class ConnectionManager:
    # initialize list for websockets connections
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    # accept and append the connection to the list
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    # remove the connection from list
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    # send personal message to the connection
    @classmethod
    async def send_personal_message(cls, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    # send message to the list of connections
    async def broadcast(self, message: str, websocket: WebSocket):
        for connection in self.active_connections:
            if connection == websocket:
                continue
            await connection.send_text(message)


# instance for handling and dealing with the websocket connections
connection_manager = ConnectionManager()