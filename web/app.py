import base64
import binascii
from pathlib import Path
import re
import secrets
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from brain.context import clear as clear_conversation
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


SESSION_COOKIE = "beyond_session"
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 30
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{43}$")
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_CHAT_BODY_BYTES = 12 * 1024 * 1024


@app.middleware("http")
async def assign_conversation_session(request: Request, call_next):
    """Give each browser its own opaque conversation identifier."""

    if request.url.path in {"/api/chat", "/api/chat/stream"}:
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > MAX_CHAT_BODY_BYTES:
            return JSONResponse({"detail": "Chat request is too large. Images must be 8 MB or smaller."}, status_code=413)

    session_id = request.cookies.get(SESSION_COOKIE, "")
    is_new_session = not SESSION_ID_PATTERN.fullmatch(session_id)
    if is_new_session:
        session_id = secrets.token_urlsafe(32)

    request.state.session_id = session_id
    response = await call_next(request)

    if is_new_session:
        forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
        response.set_cookie(
            key=SESSION_COOKIE,
            value=session_id,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            secure=request.url.scheme == "https" or forwarded_proto == "https",
            samesite="lax",
            path="/",
        )

    return response


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

class LocationContext(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value):
        if value is not None and not -90 <= value <= 90:
            raise ValueError("Invalid latitude")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value):
        if value is not None and not -180 <= value <= 180:
            raise ValueError("Invalid longitude")
        return value

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value):
        if value:
            if len(value) > 64:
                raise ValueError("Invalid timezone")
            try:
                ZoneInfo(value)
            except (ZoneInfoNotFoundError, ValueError):
                raise ValueError("Invalid timezone")
        return value


class ImageAttachment(BaseModel):
    mime_type: str
    data: str = Field(min_length=1, max_length=11_184_812)


class ChatRequest(BaseModel):
    message: str
    location: LocationContext | None = None
    image: ImageAttachment | None = None


def decode_image_attachment(image):
    if image is None:
        return None, None

    supported_types = {"image/png", "image/jpeg", "image/webp"}
    if image.mime_type not in supported_types:
        raise HTTPException(status_code=415, detail="Use a PNG, JPEG, or WebP image.")

    try:
        image_bytes = base64.b64decode(image.data, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="The image upload is invalid.")

    if not image_bytes or len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Images must be 8 MB or smaller.")

    signatures = {
        "image/png": image_bytes.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": image_bytes.startswith(b"\xff\xd8\xff"),
        "image/webp": image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP",
    }
    if not signatures[image.mime_type]:
        raise HTTPException(status_code=415, detail="The file content does not match its image type.")

    return image_bytes, image.mime_type


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
def chat(chat_request: ChatRequest, request: Request):

    message = chat_request.message.strip()
    image_bytes, image_mime_type = decode_image_attachment(chat_request.image)

    if not message and image_bytes:
        message = "Describe this image."

    if not message:

        return ChatResponse(
            response=""
        )

    try:

        response = beyond.chat(
            message,
            session_id=request.state.session_id,
            user_location=chat_request.location.model_dump(exclude_none=True) if chat_request.location else None,
            image_data=image_bytes,
            image_mime_type=image_mime_type,
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
async def chat_stream(chat_request: ChatRequest, request: Request):

    message = chat_request.message.strip()
    session_id = request.state.session_id
    image_bytes, image_mime_type = decode_image_attachment(chat_request.image)

    if not message and image_bytes:
        message = "Describe this image."

    if not message:

        return StreamingResponse(
            iter(()),
            media_type="text/plain",
        )

    def generate():

        try:

            for chunk in beyond.chat_stream(
                message,
                session_id=session_id,
                user_location=chat_request.location.model_dump(exclude_none=True) if chat_request.location else None,
                image_data=image_bytes,
                image_mime_type=image_mime_type,
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


@app.post("/api/chat/reset")
async def reset_chat(request: Request):
    """Clear only the current browser session's conversation context."""

    clear_conversation(session_id=request.state.session_id)
    return {"status": "ok"}
