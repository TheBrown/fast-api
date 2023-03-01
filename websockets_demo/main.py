import logging

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
<title>Chat</title>
</head>
<body>
<h1>WebSocket Chat</h1>
<form action="" onsubmit="sendMessage(event)">
<input type="text" id="messageText" autocomplete="off"/>
<button style="margin-left: 8px">Send</button>
<ul id="messages">
</ul>
<script>
var ws = new WebSocket("ws://localhost:8000/ws");
ws.onmessage = function(event) {
var messages = document.getElementById('messages')
var message = document.createElement('li')
var content = document.createTextNode(event.data)
message.appendChild(content)
messages.appendChild(message)
};
function sendMessage(event) {
var input = document.getElementById("messageText")
ws.send(input.value)
input.value = ''
event.preventDefault()
}
</script>
</form>
</body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data:
            await websocket.send_text(f"Message text was: {data}")
