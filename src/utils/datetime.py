from datetime import datetime

from pytz import timezone

tz = timezone("America/Sao_Paulo")


def get_now_datetime() -> datetime:
    return datetime.now(tz=tz)
