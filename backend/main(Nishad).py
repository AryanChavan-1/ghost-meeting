import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ghost Meeting Backend")

# Allow CORS for the extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Ghost Meeting Backend is running!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint to communicate with the Chrome Extension.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive data from the extension (e.g., transcript fragments)
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                logger.info(f"Received payload: {payload}")
                
                # TODO: Pass this data to scanner(Shreya).py and summarizer(Shreya).py
                # For now, echo an acknowledgment
                await manager.send_personal_message({
                    "type": "TRANSCRIPT_ACK",
                    "status": "success",
                    "received": payload
                }, websocket)
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode JSON from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
