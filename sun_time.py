import datetime
from suntime import Sun, SunTimeException

def get_sun_times():
    latitude = 32.0853
    longitude = 34.7818
    sun = Sun(latitude, longitude)
    today_sr = sun.get_sunrise_time()
    today_ss = sun.get_sunset_time()
    abd = datetime.date.today()
    abd_sr = sun.get_local_sunrise_time(abd)
    abd_ss = sun.get_local_sunset_time(abd)
    s_active = abd_sr.hour + 1.0 + (abd_sr.minute/60)
    e_active = abd_ss.hour - 1.0 + (abd_ss.minute/60)
    return (s_active, e_active)