import serial
import sys
import glob
import concurrent.futures
from functools import partial
import os
import time
from datetime import datetime
import serial.tools.list_ports

#TODO: 싱글 커맨드 보낼때 씹히는것 고려해서 리스폰 없으면 3번 더 보내기


CELL_INIT_COMMAND = "43 45 4C 4C 5F 45 4E 5F 49 4E 49 54 0D 0A"
CELL_OFF_COMMAND = "43 45 4C 4C 5F 4F 46 46 0D 0A"
CELL_ON_PREFIX_COMMAND = "43 45 4C 4C "
CELL_ON_SUFFIX_COMMAND = " 5F 4F 4E 0D 0A"
CELL_GPS_IMU_READ_CHUCK_SIZE = 2048
CELL_IMU_CAL_RESP_SIZE = 128
CELL_BOOT_COM_PORT_OPEN_TIME = 12
BAUDRATE = 230400
TARGET_PORT_VENDOR_ID = 1155

SYSCOMMAND_CELL_POWER_ON = ""
SYSCOMMAND_CELL_POWER_OFF = ""
SYSCOMMAND_HW_INFORMATION = "AC C0 01 10 7D"
SYSCOMMAND_HW_INFORMATION_RESP_SIZE = 23
SYSCMD_GET_BADBLOCK_NUMBER = "AC C0 01 D6 BB"
SYSCMD_GET_BADBLOCK_NUMBER_RESP_SIZE = 6
SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_SIZE = "AC C0 01 11 7C"
SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_RESP_SIZE = 9
SYSCOMMAND_SET_READ_IMU_CAL = "AC C0 01 24 49"
SYSCOMMAND_OLD_UPLOAD_GPS_DATA = "AC C0 02 E0 00 8E"
SYSCOMMAND_OLD_UPLOAD_IMU_DATA = "AC C0 01 E1 8C"
SYSCOMMAND_ERASE_NAND_FLASH = "AC C0 01 15 78"
SYSCMD_CELL_POWER_OFF = "AC C0 01 17 7A"

START_READ_WHOLE_CELL_DATA = ["43 45 4C 4C 31 5F 4F 4E 0D 0A", "43 45 4C 4C 32 5F 4F 4E 0D 0A", "43 45 4C 4C 33 5F 4F 4E 0D 0A",
                              "43 45 4C 4C 34 5F 4F 4E 0D 0A", "43 45 4C 4C 35 5F 4F 4E 0D 0A", "43 45 4C 4C 36 5F 4F 4E 0D 0A"]

user_input_command = ''


def find_hub_com_port():
    hub_port_name = ''
    for port in serial.tools.list_ports.comports():
        print(port.vid)
        print(port.device)
        print(port.pid)
        if port.vid == TARGET_PORT_VENDOR_ID:
            print("Find hub COM port")
            hub_port_name = port.device
            print(hub_port_name)
    if hub_port_name == '':
        print("Please make sure USB port is plug in.")
        print("EXIT")
        exit()
    return hub_port_name


def write_uart_and_single_command():
    '''
    '''


# WINDOWS = 1, LINUX & CYGWIN = 2, macOS = 3
def check_os():
    if sys.platform.startswith('win'):
        print("\nOS = Windows")
        os_system_flag = 1
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        print("\nOS = liunx, cygwin")
        os_system_flag = 2
    elif sys.platform.startswith('darwin'):
        print("\nOS = darwin(MacOS)")
        os_system_flag = 3
    else:
        raise EnvironmentError('Unsupported platform')

    return os_system_flag


def recv_user_input_command(question):
    global user_input_command
    reply = str(input(question + ':')).lower().strip()
    user_input_command = reply
    if user_input_command == "off":
        return_start_input = CELL_OFF_COMMAND
    elif user_input_command == "start":
        return_start_input = START_READ_WHOLE_CELL_DATA

    return return_start_input


def start_cell_check_is_port_open(hub_port, COMMAND):
    print("Hub port = ", hub_port)
    hub_mcu_uart = serial.Serial(hub_port, BAUDRATE)

    # EXECUTE CELL INIT
    hub = bytes.fromhex(COMMAND)
    hub_mcu_uart.write(hub)
    if COMMAND == CELL_OFF_COMMAND:
        print("Close all port...")
        in_bin = hub_mcu_uart.read(10)
        in_bin = in_bin.decode()
        print(in_bin)
        exit()
    elif COMMAND == CELL_INIT_COMMAND:
        in_bin = hub_mcu_uart.read(27)
    else:
        in_bin = hub_mcu_uart.read(23)

    print(in_bin.decode('utf-8'))


# 데이터를 저장할 폴더가 있는지 체크 후 없으면 생성
def check_is_data_directory():
    print("Check data directory")
    check_dir = "gps_imu_data"
    if not os.path.isdir(check_dir):
        os.mkdir(check_dir)


def read_ohcoach_cells_ports_depend_on_os(hub_port_name):
    os_system_flag = check_os()
    print(os_system_flag)
    print(hub_port_name)
    print("Read all cell ports")
    if os_system_flag == 1:
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif os_system_flag == 2:
        os_system_flag = 2
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif os_system_flag == 3:
        ports = glob.glob('/dev/cu.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    if os_system_flag == 1:
        start_index = result.index(hub_port_name)
        result = result[start_index+1:start_index+7]
    elif os_system_flag == 2:
        print("linux")
    elif os_system_flag == 3:
        start_index = result.index(hub_port_name)
        result = result[start_index + 1:start_index + 7]
    else:
        raise EnvironmentError('Unsupported platform')

    return result


# GPS / IMU 데이터가 있는지 없는지 체크한 다음 데이터가 있다면 파일명을 만들어준다.
# 데이터가 없다면 데이터가 없는 포트 리스트에 append
def check_is_data_and_save_cell_serial_num(port_list):
    return_port_list = []
    return_no_data_port_list = []
    return_cell_serial_num_list = []
    return_cell_bad_sector_num = []
    return_cell_firm_ver = []
    return_cell_day_month_year = []
    return_cell_millisec_sec_min_hour = []

    for i in range(0, len(port_list)):
        check_port = port_list[i]
        usart = serial.Serial(check_port, BAUDRATE)
        hex_buf = bytes.fromhex(SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_SIZE)
        usart.write(hex_buf)

        in_bin = usart.read(SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_RESP_SIZE)
        in_hex = hex(int.from_bytes(in_bin, byteorder='big'))

        sum_data = (int(in_hex[10], 16) + int(in_hex[11], 16) +int(in_hex[12], 16) + int(in_hex[13], 16))
        if sum_data:
            print("Read GPS, IMU data from", check_port)
            hex_buf = bytes.fromhex(SYSCOMMAND_HW_INFORMATION)
            usart.write(hex_buf)
            in_bin = usart.read(SYSCOMMAND_HW_INFORMATION_RESP_SIZE)
            in_hex = hex(int.from_bytes(in_bin, byteorder='big'))

            serial_number = int(in_hex[10:14], 16)
            firm_ver = int(in_hex[15:19], 16)

            print(serial_number)
            print(firm_ver)

            hex_buf = bytes.fromhex(SYSCMD_GET_BADBLOCK_NUMBER)
            usart.write(hex_buf)
            in_bin = usart.read(SYSCMD_GET_BADBLOCK_NUMBER_RESP_SIZE)
            in_hex = hex(int.from_bytes(in_bin, byteorder='big'))
            bad_sector_num = in_hex[13:15]
            print("bad sector", in_hex)
            print("TRUE bad sector", in_hex[13:15])

            date_day_month_year = datetime.today()
            day_month_year = str(date_day_month_year.day) + str(date_day_month_year.month) \
                             + str(date_day_month_year.year)
            print(day_month_year)
            time_sec_min_hour = datetime.now()
            sec_min_hour = str(time_sec_min_hour.microsecond)[0:5] + str(time_sec_min_hour.second) \
                           + str(time_sec_min_hour.minute) + str(time_sec_min_hour.hour)
            print(sec_min_hour)

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
        # Returns only ports with data
    return return_port_list, return_cell_serial_num_list, return_cell_firm_ver, return_cell_day_month_year\
        , return_cell_millisec_sec_min_hour, return_cell_bad_sector_num


class read_gps_imu_data:

    def __init__(self, port):
        self.p = port

    def read_and_save_gps_data(port, serial_num, firm, day, sec, bad):
        print(port + " Start reading GPS data")
        ser = serial.Serial(port, BAUDRATE, timeout=0.1)
        gps = bytes.fromhex(SYSCOMMAND_OLD_UPLOAD_GPS_DATA)
        ser.write(gps)

        f = open('gps_imu_data/%s_%s_%s_%s_%s.gp' % (serial_num, firm, day, sec, bad), mode='w+b')
        gps_data_reading_end_flag = 1
        while gps_data_reading_end_flag:
            data = ser.read(CELL_GPS_IMU_READ_CHUCK_SIZE)
            f.write(data)
            str_data = str(data)
            if (str_data.find('GPSEND')) != -1:
                print("Find GPSEND")
                gps_data_reading_end_flag = 0
        print(port + " GPS data save is done")
        ser.close()

        # ----------------------------------------------------------

    def read_and_save_imu_data(port, serial_num, firm, day, sec, bad):
        print(port + " Start reading IMU data")
        ser = serial.Serial(port, BAUDRATE, timeout=0.1)

        f = open('gps_imu_data/%s_%s_%s_%s_%s.im' % (serial_num, firm, day, sec, bad), mode='w+b')
        imu_cal = bytes.fromhex(SYSCOMMAND_SET_READ_IMU_CAL)
        ser.write(imu_cal)
        imu_cal_data = ser.read(CELL_IMU_CAL_RESP_SIZE)
        print(imu_cal_data)
        imu_cal_data = imu_cal_data[5:-3]
        f.write(imu_cal_data)
        print("calibration data  = ", imu_cal_data)

        imu = bytes.fromhex(SYSCOMMAND_OLD_UPLOAD_IMU_DATA)
        ser.write(imu)
        imu_data_reading_end_flag = 1

        while imu_data_reading_end_flag:
            data = ser.read(CELL_GPS_IMU_READ_CHUCK_SIZE)
            f.write(data)
            str_data = str(data)
            if (str_data.find('IMUEND')) != -1:
                print("Find IMUEND")
                imu_data_reading_end_flag = 0
        print(port + " IMU data save is done")
        ser.close()

'''
def erase_nand_flash(target_cell_port):
    print("Hub port = ", target_cell_port)
    erase_target_cell = serial.Serial(target_cell_port, BAUDRATE)
    write_command = bytes.fromhex(SYSCOMMAND_ERASE_NAND_FLASH)
    erase_target_cell.write(write_command)
    print("Erase nand flash...")
    in_bin = erase_target_cell.read(10)
    in_bin = in_bin.decode()
    print(in_bin)
'''


if __name__ == '__main__':
    hub_mcu_port = find_hub_com_port()
    print("main = ", hub_mcu_port)

    hub_command = recv_user_input_command("Enter 'start' OR 'off'")
    check_is_data_directory()
    start = time.time()
    if hub_command == CELL_OFF_COMMAND:
        start_cell_check_is_port_open(hub_mcu_port, hub_command)

    if len(hub_command) > 2:
        start_cell_check_is_port_open(hub_mcu_port, CELL_INIT_COMMAND)
        for i in range(0, 6):
            time.sleep(1)
            start_cell_check_is_port_open(hub_mcu_port, hub_command[i])
            print("Waiting to opening port....")
            time.sleep(CELL_BOOT_COM_PORT_OPEN_TIME)

            list_ports = read_ohcoach_cells_ports_depend_on_os(hub_mcu_port)
            print(list_ports)
            list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year\
                , list_mic_sec_min_hour, list_bad_block = check_is_data_and_save_cell_serial_num(list_ports)
            print(list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year
                  , list_mic_sec_min_hour, list_bad_block)

            print("---------------------Save GPS data---------------------")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(partial(read_gps_imu_data.read_and_save_gps_data), list_ports_with_data
                             , list_cell_serial_data, list_cell_firm_ver, list_day_month_year
                             , list_mic_sec_min_hour, list_bad_block)

            print("---------------------Save IMU data---------------------")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(partial(read_gps_imu_data.read_and_save_imu_data), list_ports_with_data
                             , list_cell_serial_data, list_cell_firm_ver, list_day_month_year
                             , list_mic_sec_min_hour, list_bad_block)
    else :
        print("OFF all cells")

    print("Code execution time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

    print("ALL process is END")
    print("Close all cell ports and cmd window after 10 seconds")
    time.sleep(10)
    start_cell_check_is_port_open(hub_mcu_port, CELL_OFF_COMMAND)


