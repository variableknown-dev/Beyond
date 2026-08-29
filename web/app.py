from pathlib import Path
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.aarya import Aarya
from models.gemini_provider import GeminiProvider
from web.platform import WebPlatform


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Aarya",
    description="Aarya AI Assistant Web Interface",
    version="1.0.0",
)


# =========================================================
# STATIC FILES
# =========================================================

STATIC_DIR = Path(__file__).parent / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# =========================================================
# AARYA
# =========================================================

platform = WebPlatform()

model_provider = GeminiProvider(
    model="gemini-3.7-flash"
)

aarya = Aarya(
    platform=platform,
    model_provider=model_provider,
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str


# =========================================================
# RESPONSE MODEL
# =========================================================

class ChatResponse(BaseModel):
    response: str


# =========================================================
# FRONTEND
# =========================================================

@app.get("/")
async def home():

    return FileResponse(
        STATIC_DIR / "index.html"
    )


# =========================================================
# NORMAL CHAT API
# =========================================================

@app.post(
    "/api/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:

        return ChatResponse(
            response=""
        )

    try:

        response = aarya.chat(
            message
        )

        return ChatResponse(
            response=response
        )

    except Exception as error:

        print()
        print("========================================")
        print("AARYA NORMAL CHAT ERROR")
        print("========================================")

        traceback.print_exc()

        print("========================================")
        print()

        return ChatResponse(
            response=(
                "Sorry, I ran into an error "
                "while generating that response."
            )
        )


# =========================================================
# STREAMING CHAT API
# =========================================================

@app.post(
    "/api/chat/stream"
)
async def chat_stream(request: ChatRequest):

    message = request.message.strip()

    if not message:

        return StreamingResponse(
            iter(()),
            media_type="text/plain",
        )

    def generate():

        try:

            for chunk in aarya.chat_stream(
                message
            ):

                if chunk:

                    yield chunk

        except Exception as error:

            print()
            print("========================================")
            print("AARYA STREAMING CHAT ERROR")
            print("========================================")

            traceback.print_exc()

            print("========================================")
            print()

            yield (
                "\n\nSorry, I ran into "
                "an error while generating "
                "that response."
            )

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
