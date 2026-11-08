from pathlib import Path
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.beyond import Beyond
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
    title="Beyond",
    description="Beyond AI Assistant Web Interface",
    version="1.0.0",
)


# =========================================================
# STATIC FILES
# =========================================================

STATIC_DIR = Path(__file__).parent / "static"
ERROR_PAGE = STATIC_DIR / "error.html"
ERROR_MESSAGE = (
    "Sorry, but we are currently experiencing a few errors in our code. "
    "We are working to resolve them promptly. We apologize for the inconvenience."
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, error: Exception):
    """Show a helpful fallback page for errors while the app is running."""

    traceback.print_exception(type(error), error, error.__traceback__)

    if request.url.path.startswith("/api/"):
        return PlainTextResponse(ERROR_MESSAGE, status_code=503)

    return FileResponse(ERROR_PAGE, status_code=503)


# =========================================================
# BEYOND
# =========================================================

platform = WebPlatform()

model_provider = GeminiProvider(
    model="gemini-3.5-flash-lite"
)

beyond = Beyond(
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
@app.head("/")
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
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:

        return ChatResponse(
            response=""
        )

    try:

        response = beyond.chat(
            message
        )

        return ChatResponse(
            response=response
        )

    except Exception as error:

        print()
        print("========================================")
        print("BEYOND NORMAL CHAT ERROR")
        print("========================================")

        traceback.print_exc()

        print("========================================")
        print()

        return JSONResponse(
            status_code=503,
            content={"response": ERROR_MESSAGE},
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

            for chunk in beyond.chat_stream(
                message
            ):

                if chunk:

                    yield chunk

        except Exception as error:

            print()
            print("========================================")
            print("BEYOND STREAMING CHAT ERROR")
            print("========================================")

            traceback.print_exc()

            print("========================================")
            print()

            yield f"\n\n{ERROR_MESSAGE}"

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
