from decouple import config

HOST = config("HOST", default="0.0.0.0")
PORT = config("PORT", default=8000, cast=int)
WORKERS = config("WORKERS", default=2, cast=int)
BASE_PATH = config("BASE_PATH", default="")
DEBUG = config("DEBUG", default=False, cast=bool)
WHATSAPP_WAIT_CHECK_LOGGED = config("WHATSAPP_WAIT_CHECK_LOGGED", default=10, cast=int)
