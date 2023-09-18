import datetime

def local_time():
    utc_time = datetime.datetime.utcnow()
    time_delta = datetime.timedelta(hours=8)
    my_time = utc_time + time_delta
    return my_time
