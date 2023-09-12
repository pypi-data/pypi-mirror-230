import datetime
import time


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_FORMAT_MS = '%Y-%m-%d %H:%M:%S.%f'
DATETIME_FORMAT_BRIEF = '%Y%m%d%H%M'

def now():
    return datetime.datetime.now()

def dtime2str(dtime):
    return dtime.strftime(DATETIME_FORMAT)

def dtime2str_ms(dtime):
    return dtime.strftime(DATETIME_FORMAT_MS)

def dtime2str_brief(dtime):
    return dtime.strftime(DATETIME_FORMAT_BRIEF)

def str_2dtime(str_val):
    try:
        return datetime.datetime.strptime(str_val, DATETIME_FORMAT)
    except:
        pass
    return datetime.datetime.strptime(str_val, DATETIME_FORMAT_MS)

def timestamp2dtime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def dtime2ts(dtime):
    return time.mktime(dtime.timetuple())


