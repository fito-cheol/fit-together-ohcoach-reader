from datetime import datetime
from common.ohcoach_reader_constants import *


def check_cell_has_data(usart):
    hex_buf = bytes.fromhex(SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_SIZE)
    usart.write(hex_buf)

    in_bin = usart.read(SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_RESP_SIZE)
    in_hex = hex(int.from_bytes(in_bin, byteorder='big'))

    sum_data = (int(in_hex[10], 16) + int(in_hex[11], 16) + int(in_hex[12], 16) + int(in_hex[13], 16))

    return sum_data


def get_hw_info(usart):
    hex_buf = bytes.fromhex(SYSCOMMAND_HW_INFORMATION)
    usart.write(hex_buf)
    in_bin = usart.read(SYSCOMMAND_HW_INFORMATION_RESP_SIZE)
    in_hex = hex(int.from_bytes(in_bin, byteorder='big'))

    serial_number = int(in_hex[10:14], 16)
    firm_ver = int(in_hex[15:19], 16)
    serial_number = str(serial_number)
    firm_ver = str(firm_ver)
    print(serial_number)
    print(firm_ver)

    return serial_number, firm_ver


def get_cell_badblock_number(usart):
    hex_buf = bytes.fromhex(SYSCMD_GET_BADBLOCK_NUMBER)
    usart.write(hex_buf)
    in_bin = usart.read(SYSCMD_GET_BADBLOCK_NUMBER_RESP_SIZE)
    in_hex = hex(int.from_bytes(in_bin, byteorder='big'))
    bad_sector_num = in_hex[13:15]
    print("bad sector", in_hex)
    print("TRUE bad sector", in_hex[13:15])

    return bad_sector_num


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
