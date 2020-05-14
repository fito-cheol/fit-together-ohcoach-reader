import serial
import ohcoach_reader_constants
from datetime import datetime

# TODO fileIO쪽보다 Cell 관련으로 묶어야 하는 함수
# jaeuk : fileIO 쪽과 cell 관련 어떤 다름으로 정의되는지?
# 각 cell에 serial 통신으로 명령을 보내서 fileIO에 필요한 값들(파일명)을 리턴하는 곳임

def check_cell_has_data(usart):
    hex_buf = bytes.fromhex(ohcoach_reader_constants.SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_SIZE)
    usart.write(hex_buf)

    in_bin = usart.read(ohcoach_reader_constants.SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_RESP_SIZE)
    in_hex = hex(int.from_bytes(in_bin, byteorder='big'))

    sum_data = (int(in_hex[10], 16) + int(in_hex[11], 16) + int(in_hex[12], 16) + int(in_hex[13], 16))

    return sum_data

# TODO fileIO쪽보다 Cell 관련으로 묶어야 하는 함수
def get_hw_info(usart):
    hex_buf = bytes.fromhex(ohcoach_reader_constants.SYSCOMMAND_HW_INFORMATION)
    usart.write(hex_buf)
    in_bin = usart.read(ohcoach_reader_constants.SYSCOMMAND_HW_INFORMATION_RESP_SIZE)
    in_hex = hex(int.from_bytes(in_bin, byteorder='big'))

    serial_number = int(in_hex[10:14], 16)
    firm_ver = int(in_hex[15:19], 16)
    serial_number = str(serial_number)
    firm_ver = str(firm_ver)
    print(serial_number)
    print(firm_ver)

    return serial_number, firm_ver

# TODO fileIO쪽보다 Cell 관련으로 묶어야 하는 함수
def get_cell_badblock_number(usart):
    hex_buf = bytes.fromhex(ohcoach_reader_constants.SYSCMD_GET_BADBLOCK_NUMBER)
    usart.write(hex_buf)
    in_bin = usart.read(ohcoach_reader_constants.SYSCMD_GET_BADBLOCK_NUMBER_RESP_SIZE)
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


# GPS / IMU 데이터가 있는지 없는지 체크한 다음 데이터가 있다면 파일명을 만들어준다.
# 데이터가 없다면 return_no_data_port_list에 append
def check_is_data_and_save_cell_filename(port_list):
    return_port_list = []
    return_no_data_port_list = []
    return_cell_serial_num_list = []
    return_cell_bad_sector_num = []
    return_cell_firm_ver = []
    return_cell_day_month_year = []
    return_cell_millisec_sec_min_hour = []

    for i in range(0, len(port_list)):
        check_port = port_list[i]
        usart = serial.Serial(check_port, ohcoach_reader_constants.BAUDRATE)
        sum_data = check_cell_has_data(usart)
        if sum_data:
            print("Read GPS, IMU data from", check_port)
            serial_number, firm_ver = get_hw_info(usart)
            bad_sector_num = get_cell_badblock_number(usart)
            day_month_year, sec_min_hour = get_time_when_file_create()

            # 시리얼번호_펌웨어 버전_스타트타임_badblock_개수.
            return_port_list.append(check_port)
            return_cell_serial_num_list.append(serial_number)
            return_cell_firm_ver.append(firm_ver)
            return_cell_day_month_year.append(day_month_year)
            return_cell_millisec_sec_min_hour.append(sec_min_hour)
            return_cell_bad_sector_num.append(bad_sector_num)
        else:
            print("No data port :", check_port)
            return_no_data_port_list.append(check_port)
    print("No data port list = ", return_no_data_port_list)
        # Returns only ports with filename data
    return return_port_list, return_cell_serial_num_list, return_cell_firm_ver, return_cell_day_month_year\
        , return_cell_millisec_sec_min_hour, return_cell_bad_sector_num
