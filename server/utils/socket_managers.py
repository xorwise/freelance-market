from starlette.websockets import WebSocket, WebSocketState


class SocketManager(object):
    active_connections: dict[int, WebSocket] = dict()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SocketManager, cls).__new__(cls)
        return cls.instance

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        del self.active_connections[user_id]

    async def send_direct_message(self, data, user_id: int):
        if user_id in self.active_connections:
            if (
                self.active_connections[user_id].application_state
                == WebSocketState.CONNECTED
            ):
                await self.active_connections[user_id].send_json(data)


class SocketChatManager(object):
    active_connections: dict[(int, int), WebSocket] = dict()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SocketChatManager, cls).__new__(cls)
        return cls.instance

    async def connect(self, websocket: WebSocket, user_id: int, dialog_id: int):
        await websocket.accept()
        self.active_connections[(user_id, dialog_id)] = websocket

    def disconnect(self, user_id: int, dialog_id: int):
        del self.active_connections[(user_id, dialog_id)]

    async def send_direct_message(self, data, user_id: int, dialog_id: int):
        if (user_id, dialog_id) in self.active_connections:
            if (
                self.active_connections[(user_id, dialog_id)].application_state
                == WebSocketState.CONNECTED
            ):
                print(data)
                await self.active_connections[(user_id, dialog_id)].send_json(data)
