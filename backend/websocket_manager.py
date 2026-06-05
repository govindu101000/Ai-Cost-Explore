from collections import defaultdict


class ConnectionManager:

    def __init__(self):
        self.connections = defaultdict(list)

    async def connect(
        self,
        websocket,
        analysis_id: str
    ):

        await websocket.accept()

        self.connections[
            analysis_id
        ].append(websocket)

    def disconnect(
        self,
        websocket,
        analysis_id: str
    ):

        if analysis_id not in self.connections:
            return

        try:
            self.connections[
                analysis_id
            ].remove(websocket)

        except ValueError:
            pass

    async def send_progress(
        self,
        analysis_id: str,
        message: str
    ):

        clients = self.connections.get(
            analysis_id,
            []
        )

        disconnected = []

        for ws in clients:

            try:
                await ws.send_json({
                    "message": message
                })

            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(
                ws,
                analysis_id
            )


manager = ConnectionManager()