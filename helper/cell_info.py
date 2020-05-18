from datetime import datetime


def get_time_when_file_create():
    date_day_month_year = datetime.today()
    day_month_year = str(date_day_month_year.day) + str(date_day_month_year.month) \
                     + str(date_day_month_year.year)
    print(day_month_year)
    time_sec_min_hour = datetime.now()
    sec_min_hour = str(time_sec_min_hour.microsecond)[0:5] + str(time_sec_min_hour.second) \
                   + str(time_sec_min_hour.minute) + str(time_sec_min_hour.hour)
    print(sec_min_hour)

    return day_month_year, sec_min_hour
