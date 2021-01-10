import logging
from typing import Callable

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import RedirectResponse, UJSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

from src import __version__
from src.routers import conversation, whatsapp
from src.settings import BASE_PATH, DEBUG, HOST, PORT, WORKERS
from src.talkers import whatsapp_talker

app = FastAPI(
    title="Whatsapp API",
    version=__version__,
    description="API para automação do whatsapp web",
    docs_url=f"{BASE_PATH}/docs",
    redoc_url=f"{BASE_PATH}/redoc",
    openapi_url=f"{BASE_PATH}/openapi.json",
)

app.include_router(whatsapp.router)
app.include_router(conversation.router)


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S")


@app.middleware("http")
async def check_is_logged(request: Request, call_next: Callable):
    if request.url.path != app.url_path_for("qrcode") and not whatsapp_talker.is_logged:
        return RedirectResponse(app.url_path_for("qrcode"))

    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def unprocessable_entity_error(request, exc: RequestValidationError):
    return UJSONResponse(content={"message": exc.errors()}, status_code=HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(Exception)
async def unknown_error(request, exc: Exception):
    return UJSONResponse(content={"message": str(exc)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


@app.exception_handler(HTTPException)
async def http_error(request, exc: HTTPException):
    return UJSONResponse(content={"message": exc.detail}, status_code=exc.status_code)


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=HOST,
        port=PORT,
        debug=DEBUG,
        log_level="info",
        access_log=True,
        workers=WORKERS,
        timeout_keep_alive=50,
    )
