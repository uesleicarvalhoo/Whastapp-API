from decouple import config

HOST = config("HOST", default="0.0.0.0")
PORT = config("PORT", default=8000, cast=int)
WORKERS = config("WORKERS", default=2, cast=int)
BASE_PATH = config("BASE_PATH", default="")
DEBUG = config("DEBUG", default=False, cast=bool)
WHATSAPP_WAIT_CHECK_LOGGED = config("WHATSAPP_WAIT_CHECK_LOGGED", default=10, cast=int)
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT", cast=int)
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_NAME = config("DB_NAME")

SQLALCHEMY_DB_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
