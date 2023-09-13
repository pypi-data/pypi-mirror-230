import time
from datetime import date, timedelta, datetime
from liveramp_automation.utils.log import Logger

"""
The MACROS() API prepared some expected time format.
You could invole the time format like: yesterday.format(**MACROS) at any code snippet.
"""
MACROS = {
    "yesterday": (date.today() - timedelta(days=1)).strftime("%Y%m%d"),
    "today": date.today().strftime("%Y%m%d"),
    "dayOfYear": (date.today().timetuple()).tm_yday,
    "now": datetime.now().strftime("%Y%m%d%H%M%S"),
    "now_format": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "nowconnect": datetime.now().strftime("%Y%m%d-%H%M%S"),  # data ingestion must be in yyyymmdd-hhmmss format
    "three_days_ago": (date.today() - timedelta(days=3)).strftime("%Y%m%d"),
    "two_hours_from_now": (datetime.now() + timedelta(hours=2)).strftime("%Y%m%d-%H%M%S"),
    "24hours_before_now": (datetime.now() - timedelta(hours=24)).strftime("%Y%m%d%H%M%S"),
    "one_year_later": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
    "one_year_later_eng": '{dt:%b} {dt.day} {dt.year}'.format(dt=datetime.now() + timedelta(days=365))
}

DefAULT_WAIT_TIME = 2


def fixed_wait(seconds: int = DefAULT_WAIT_TIME) -> None:
    """Pause the program's execution for a specified number of seconds.

    :param seconds: The number of seconds to wait (default is 3 seconds).
    :return: None
    """
    time.sleep(seconds)
    Logger.info("Pause the program's execution for {} seconds.".format(seconds))
