from datetime import datetime
from typing import Optional
import pandas as pd
import pytz

US_Eastern_TZ = pytz.timezone('US/Eastern')
YMD_Format = "%Y-%m-%d"
YYYYMDHHMM_Format = "YYYY-M-D HH:mm"
YMDHMS_Format = "%Y-%m-%d %H:%M:%S"

class TimeUtils:

    @staticmethod
    def convert_unix_ts(ts: int, tz: pytz.timezone = US_Eastern_TZ) -> Optional[datetime]:
        '''convert unix timestamp to datetime with the given timezone, US East by default'''
        if ts is None:
            return None

        if isinstance(ts, pd.Timestamp):
            ts = ts.to_pydatetime().timestamp()

        while ts > 1e10:
            ts = ts/1000
        return datetime.fromtimestamp(ts, tz)

    @staticmethod
    def us_east_now() -> datetime:
        return datetime.now().astimezone(US_Eastern_TZ)