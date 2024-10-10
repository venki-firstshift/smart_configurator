#!/usr/bin/env python
import json
from datetime import timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    FastAPI, UploadFile, WebSocket, WebSocketDisconnect,
    Request, Depends, HTTPException, status
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette.responses import RedirectResponse

from auth.jwt_auth import Token
from copilot.connection_manager import connection_manager
import aiofiles
import copilot.config_assistant as ca
from auth import jwt_auth

app = FastAPI()
#app.mount("/ui", StaticFiles(directory="ui"), name="static")


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

@app.get("/")
async def redirect():
    response = RedirectResponse(url='/ui/index.html')
    return response

@app.post("/api/upload/file/{client_id}")
async def create_upload_file(file: UploadFile, client_id: str):
    # copy the uploaded file to /tmp for processing
    out_file_path = f"/tmp/smart_configurator/{file.filename}"
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)
    return {"filename": file.filename, "client_id": client_id}

@app.post("/api/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = jwt_auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

# routes for invoking the discovery process using HTTP instead of WS
@app.post("/api/discover/entity/{client_id}/{file_name}")
async def discover_entity(client_id: str, file_name: str):
    config_entity = ca.discover_config_entity(file_name, client_id)
    result = dict(msg=config_entity, cmd='entity')
    return result

@app.post("/api/discover/entity/columns/{client_id}/{file_name}")
async def discover_entity(client_id: str, file_name: str):
    cols = ca.discover_column_mappings(client_id)
    result = dict(msg=cols, cmd='columns')
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)