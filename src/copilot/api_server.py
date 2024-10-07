#!/usr/bin/env python
import json

from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from copilot.connection_manager import connection_manager
import aiofiles
import copilot.config_assistant as ca

app = FastAPI()
templates = Jinja2Templates(directory="templates")
#app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    # Render the HTML template
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/process/csv/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    # accept connections
    await connection_manager.connect(websocket)
    try:
        while True:
            # receive text from the user
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg["cmd"] == 'entity':
                file_name = msg["filename"]
                config_entity = ca.discover_config_entity(file_name, client_id)
                result  = dict(msg=config_entity, cmd=msg['cmd'])
            elif msg["cmd"] == 'columns':
                cols = ca.discover_column_mappings(client_id)
                result = dict(msg=cols, cmd=msg['cmd'])
            else:
                err = dict(err="error")
                result = dict(msg=err, cmd=msg['cmd'])
            res = json.dumps(result)
            await connection_manager.send_personal_message(res, websocket)
            # broadcast message to the connected user
            await connection_manager.broadcast(f"Client #{client_id}: {data}", websocket)

    # WebSocketDisconnect exception will be raised when client is disconnected
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast(f"Client #{client_id} left the chat", websocket)

@app.post("/api/upload/file/{client_id}")
async def create_upload_file(file: UploadFile, client_id: str):
    # copy the uploaded file to /tmp for processing
    out_file_path = f"/tmp/smart_configurator/{file.filename}"
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)
    return {"filename": file.filename, "client_id": client_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)