import fastapi
import loguru
import uvicorn
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.vectorstores.base import VectorStore
from typing import Optional, List
from domains.settings import config_settings
from domains.injestion.routes import router as injestion_router
from domains.retreival.routes import run_rag, RagUseCase, Message
from domains.agents.routes import react_orchestrator
from loguru import logger

import whisper
app = fastapi.FastAPI()
vectorstore: Optional[VectorStore] = None

whisper_model = whisper.load_model("base")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Sec-WebSocket-Accept"],  # Ensure WebSocket headers are exposed
)

from domains.agents.routes import router as agents_router

# Include other API routes
app.include_router(
    injestion_router,
    prefix="/runner",
)


app.include_router(
    agents_router,
    prefix="/agents",
)

from fastapi import  Query, UploadFile, File


@app.post("/transcribe_audio")
async def transcribe_audio(file: UploadFile = File(...)):
    """Endpoint to transcribe audio to text using Whisper."""
    try:
        audio_bytes = await file.read()
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)

        result = whisper_model.transcribe("temp_audio.wav")
        return {"transcription": result["text"]}
    except Exception as e:
        logger.exception("Error transcribing audio")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/run_agents")
async def get_run_agents(
    query: str = Query(..., description="The query or task to be processed by the agents"),
    thread_id: str = Query(..., description="The identifier for the task or conversation")
):
    """GET API endpoint for running agents."""
    try:
        result = await react_orchestrator(query=query, id=thread_id)
        return {"result": result}
    except Exception as e:
        logger.exception("Error running agents")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/run_rag")
async def websocket_run_rag(websocket: WebSocket):
    """WebSocket endpoint for running RAG model queries."""
    await websocket.accept()
    try:
        data = await websocket.receive_json()  # Receive parameters as JSON

        # Run the RAG model
        await run_rag(
            language=data.get("language", "en"),
            chat_context=data.get("chat_context", []),
            websocket=websocket,
            namespace=data.get("namespace", config_settings.PINECONE_DEFAULT_DEV_NAMESPACE),
            question=data.get("question", ""),
        )
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close(code=1011)  # 1011 = Internal Server Error


if __name__ == "__main__":
    uvicorn.run("service:app", host="0.0.0.0", port=8081)