from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.chatbot.langchain_bot import ask_question
import uvicorn
import os

from uuid import uuid4
import asyncio
from typing import Dict

# from starlette.websockets import WebSocket, WebSocketDisconnect
from fastapi import FastAPI, WebSocket

from pydantic import BaseModel


app = FastAPI()

# Mount the 'html' directory to serve static files
app.mount("/static", StaticFiles(directory="html"), name="static")

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


# Root endpoint to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def get():
    with open("html/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        user_message = data.get("message")

        # Process the message with LangChain
        response = process_user_message(user_message)

        # Send the response back to the user
        await websocket.send_json({"text": response})


@app.post("/process_message")
async def process_message(request: Request):
    data = await request.json()
    user_message = data.get("message", {}).get("text", "")
    if not user_message:
        return JSONResponse({"error": "No message provided"}, status_code=400)
    response_text = ask_question(user_message)
    return JSONResponse({"response": response_text})


from fastapi.concurrency import run_in_threadpool


# Define the input model for chat messages
class ChatMessage(BaseModel):
    message: str


@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """
    Backend chat endpoint integrated with LangChain.
    """
    user_message = chat_message.message  # Get the user's message

    try:
        # Pass the user's message to the LangChain function
        bot_reply = ask_question(user_message)
    except Exception as e:
        # Handle errors gracefully
        bot_reply = "Sorry, I encountered an error while processing your request."

    return {"reply": bot_reply}


# @app.post("/chat")
# async def chat(request: Request):
#     data = await request.json()
#     user_message = data.get("message")
#     sender_id = data.get("sender")
#     if not user_message:
#         return JSONResponse(content=[], status_code=200)
#     # Run the synchronous function in a thread pool
#     response_text = await run_in_threadpool(ask_question, user_message)
#     return JSONResponse(content=[{"recipient_id": sender_id, "text": response_text}])


# In-memory storage for conversations
conversations: Dict[str, "Conversation"] = {}


class Conversation:
    def __init__(self):
        self.id = str(uuid4())
        self.messages = asyncio.Queue()
        self.users = set()

    async def broadcast(self, message):
        for user in self.users:
            await user.send_json(message)


import uuid
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse


@app.get("/directline/conversations/{conversation_id}/activities")
async def get_activities(conversation_id: str, watermark: int = 0):
    if conversation_id in conversations:
        activities = conversations[conversation_id]["activities"]
        new_activities = activities[watermark:]
        return JSONResponse(
            {"activities": new_activities, "watermark": watermark + len(new_activities)}
        )
    else:
        return JSONResponse({"error": "Conversation not found"}, status_code=404)


@app.post("/directline/token")
async def generate_token():
    conversation_id = str(uuid.uuid4())
    conversations[conversation_id] = {"activities": []}
    return JSONResponse({"token": conversation_id})


@app.post("/directline/conversations")
async def create_conversation(request: Request):
    conversation_id = str(uuid.uuid4())
    conversations[conversation_id] = {"activities": []}
    return JSONResponse(
        {
            "conversationId": conversation_id,
            "streamUrl": f"ws://{request.client.host}:{request.url.port}/directline/conversations/{conversation_id}/stream",
            "expires_in": 1800,
        }
    )


@app.websocket("/directline/conversations/{conversation_id}/stream")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    if conversation_id not in conversations:
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("text")
            if user_message:
                # Process the message
                response_text = await process_user_message(
                    user_message, conversation_id
                )
                # Send the response back to the user
                await websocket.send_json(
                    {"type": "message", "from": {"id": "bot"}, "text": response_text}
                )
    except WebSocketDisconnect:
        pass


async def process_user_message(message: str, userID: str) -> str:
    # Use userID as needed
    response = await asyncio.get_event_loop().run_in_executor(
        None, ask_question, message
    )
    return response


@app.post("/api/chat")
async def chat_handler(request: Request):
    data = await request.json()
    message = data.get("message")
    user_id = data.get("userId")
    if not message or not user_id:
        return JSONResponse({"error": "Invalid input"}, status_code=400)

    reply = await process_user_message(message, user_id)
    return JSONResponse({"reply": reply})


@app.post("/webhook")
async def tawk_webhook(request: Request):
    payload = await request.json()
    event = payload.get("event")
    message = payload.get("message", {})
    visitor = payload.get("visitor", {})

    if event == "chat:start":
        # Handle chat start event if needed
        pass
    elif event == "chat:message":
        user_message = message.get("text")
        if user_message:
            # Process the message with LangChain
            response_text = process_user_message(user_message)
            # Send the response back to the user
            await send_message_to_tawk(visitor, response_text)

    return {"status": "success"}


import httpx


async def send_message_to_tawk(visitor, message):
    api_token = "YOUR_TAWKTO_API_TOKEN"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    conversation_id = visitor.get("activeConversation", {}).get("id")
    url = f"https://api.tawk.to/conversation/{conversation_id}/message"

    payload = {
        "text": message,
        "type": "chat",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 201:
            # Handle the error accordingly
            print(f"Error sending message: {response.text}")


from fastapi import FastAPI, HTTPException, Request


@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()  # Extract JSON payload
        message = data.get("message")
        userID = data.get("userID")

        if not message or not userID:
            raise HTTPException(status_code=400, detail="Missing 'message' or 'userID'")

        response = await process_user_message(message, userID)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from typing import List

clients: List[WebSocket] = []


@app.websocket("/socket.io/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            # Receive a message from the client
            data = await websocket.receive_text()
            print(f"Message received: {data}")

            # Process the message (e.g., call a chatbot function)
            response = f"You said: {data}"  # Replace with your chatbot logic

            # Send the response back to the client
            await websocket.send_text(response)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        clients.remove(websocket)


# Rasa webhook URL
RASA_WEBHOOK_URL = "http://localhost:5005/webhooks/rest/webhook"


class ChatMessage(BaseModel):
    sender: str
    message: str


@app.post("/webhooks/rest/webhook")
async def chat_with_langchain(chat_message: ChatMessage):
    """
    Receives a message from the webchat widget, processes it using LangChain, and responds.
    """
    try:
        # Process the message with LangChain (example only)
        response = f"LangChain response to '{chat_message.message}'"

        # Return the response in the format expected by the widget
        return [{"text": response}]
    except Exception as e:
        return [{"text": f"Error: {e}"}]


# Keep track of connected clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


from fastapi_socketio import SocketManager

manager = ConnectionManager()
socket_manager = SocketManager(app)


@app.websocket("/socket.io/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept WebSocket connection
    try:
        while True:
            data = await websocket.receive_text()  # Receive a message from the client
            response = f"Echo: {data}"  # Simple echo response for testing
            await websocket.send_text(response)  # Send the response back
    except WebSocketDisconnect:
        print("WebSocket disconnected")


@socket_manager.on("user_uttered")  # Rasa Webchat emits "user_uttered" events
async def handle_user_uttered(sid, data):
    print(f"Message received from client {sid}: {data}")
    # Echo the received message
    response = {"text": f"You said: {data['message']}"}
    await socket_manager.emit("bot_uttered", response, to=sid)  # Send response back


from app.parsers.sity_parcer import get_all_apartments
from app.services.apartment_service import save_apartments, delete_all_apartments
from fastapi import FastAPI, HTTPException, status


@app.get("/reset-apartments", status_code=status.HTTP_200_OK)
def reset_apartments():
    """
    Endpoint to reset and seed the apartments table.
    """
    try:
        # Step 1: Delete all apartments
        delete_all_apartments()

        # Step 2: Fetch new apartment data
        apartments = get_all_apartments()

        # Step 3: Save the fetched apartments to the database
        save_apartments(apartments)

        return {"message": "Apartments table reset and seeded successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while resetting apartments: {str(e)}",
        )


if __name__ == "__main__":
    # For local development
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
