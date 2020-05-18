import os
import serial
import time
import concurrent.futures
from functools import partial
from helper import cell_info, cell_port

from ohcoach_reader_constants import *

class UserInterface:

    def __init__(self):
        create_dir_if_not_exists(PATH_DATA_SAVE_DIR)
        self.hub_mcu_port = None

    def find_dock(self):
        self.hub_mcu_port = get_hub_com_port(TARGET_PORT_VENDOR_ID)
        # 도킹에서 셀로 init명령
        transmit_command_to_hub_mcu(self.hub_mcu_port, CELL_INIT_COMMAND)

    def processing_dock(self):
        for command in START_READ_WHOLE_CELL_DATA:
            time.sleep(1)

            # jaeuk : receive_user_input_command 에서 키보드로 start을 입력하면
            # line 1~6개의 cell line on command 들어감
            transmit_command_to_hub_mcu(self.hub_mcu_port, command)
            print("Waiting to opening port....")
            time.sleep(CELL_BOOT_COM_PORT_OPEN_TIME)

            list_ports = cell_port.read_ports_compatible_os_system(self.hub_mcu_port)
            print(list_ports)

            list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year \
                , list_mic_sec_min_hour, list_bad_block = cell_info.check_is_data_and_save_cell_filename(list_ports)
            print(list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year
                  , list_mic_sec_min_hour, list_bad_block)

            filename_list = make_filename(list_cell_serial_data, list_cell_firm_ver, list_day_month_year,
                                          list_mic_sec_min_hour, list_bad_block)
            print("Main filename = ", filename_list)

            print("---------------------Save GPS data---------------------")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(partial(read_and_save_gps_data), list_ports_with_data
                             , filename_list)

            print("---------------------Save IMU data---------------------")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(partial(read_and_save_imu_data), list_ports_with_data
                             , filename_list)

    def off_dock(self):
        # transmit_command_to_hub_mcu(hub_mcu_port, hub_command)
        transmit_command_to_hub_mcu(self.hub_mcu_port, CELL_OFF_COMMAND)

# 파일 입출력 관련 helper 만들기
def create_dir_if_not_exists(directory):
    print("Check data directory")

    if not os.path.isdir(directory):
        os.mkdir(directory)

def read_and_save_gps_data(port, filename):
    print(port + " Start reading GPS data")
    with serial.Serial(port, BAUDRATE, timeout=0.1) as ser, \
            open('gps_imu_data/%s.gp' % filename, mode='w+b') as f:

        gps = bytes.fromhex(SYSCOMMAND_OLD_UPLOAD_GPS_DATA)
        ser.write(gps)

        # jaeuk : 여기서 직접 찍어서 확인해보니 string 으로 출력이 나옵니다.
        print("jaeuk =", filename)

        gps_data_reading_end_flag = 1
        while gps_data_reading_end_flag:
            data = ser.read(CELL_GPS_IMU_READ_CHUCK_SIZE)
            f.write(data)
            str_data = str(data)
            # jaeuk : find는 찾고자하는 문자열이 있으면 문자열의 시작 위치를 리턴하고
            # 원하는 문자열이 없을 시에 -1을 리턴하는데, if -1: 일 때도 if 문으로 들어가기 때문에
            # != -1 조건이 필요. 실제로 != -1 를 빼면 코드가 돌아가지 않음
            if (str_data.find(GPS_END_STR)) != -1:
                print("Find GPSEND")
                gps_data_reading_end_flag = 0
        print(port + " GPS data save is done")

def read_and_save_imu_data(port, filename):
    print(port + " Start reading IMU data")
    print("jaeuk =", filename)

    with serial.Serial(port, BAUDRATE, timeout=0.1) as ser, \
            open('gps_imu_data/%s.im' % filename, mode='w+b') as f:
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
            if (str_data.find(IMU_END_STR)) != -1:
                print("Find IMUEND")
                imu_data_reading_end_flag = 0
        print(port + " IMU data save is done")


# 단순 filename 만드는 함수
def make_filename(serial_num, firm_ver, day, sec, bad):
    filename = ''
    filename_list = []
    print(len(serial_num))
    for i in range(0, len(serial_num)):
        print(serial_num[i], firm_ver[i], day[i], sec[i], bad[i])
        filename = '%s_%s_%s_%s_%s' % (serial_num[i], firm_ver[i], day[i], sec[i], bad[i])
        print("filename = ", filename)
        filename_list.append(filename)

    return filename_list

# serial 쪽이므로 helper cell_port.py 로 이동
def get_hub_com_port(target_vendor_id):
    hub_port_name = ''
    for port in serial.tools.list_ports.comports():
        print(port.vid)
        print(port.device)
        print(port.pid)
        if port.vid == target_vendor_id:
            print("Find hub COM port")
            hub_port_name = port.device
            print(hub_port_name)
    if hub_port_name == '':
        print("Please make sure USB port is plug in.")
        print("EXIT")
        exit()
    return hub_port_name

def transmit_command_to_hub_mcu(hub_port, COMMAND):
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


if __name__ == '__main__':
    objectUI = UserInterface()

    is_processing = True

    objectUI.find_dock()

    if is_processing:
        objectUI.processing_dock()
    else:
        objectUI.off_dock()







