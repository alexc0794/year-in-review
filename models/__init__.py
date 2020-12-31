import pytz
from dateutil.parser import parse
from datetime import datetime
from tzlocal import get_localzone


def utc_timestamp_to_datetime(timestamp: str) -> datetime:
    date = parse(timestamp)
    if date.tzinfo is None:
        utc = pytz.timezone('UTC')
        date = utc.localize(date)
    date = date.astimezone(get_localzone())
    return date
