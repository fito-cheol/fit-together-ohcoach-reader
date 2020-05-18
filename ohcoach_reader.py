import os
import time
import serial
import concurrent.futures
from functools import partial
import serial.tools.list_ports

from common import ohcoach_reader_constants
from helper import cell_info, cell_port


#TODO: 싱글 커맨드 보낼때 씹히는것 고려해서 리스폰 없으면 3번 더 보내기

# 데이터를 저장할 폴더가 있는지 체크 후 없으면 생성
def create_dir_if_not_exists(directory):
    print("Check data directory")

    if not os.path.isdir(directory):
        os.mkdir(directory)


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


def receive_user_input_command(question):
    reply = str(input(question + ':')).lower().strip()
    user_input_command = reply
    if user_input_command == "off":
        return_start_input = ohcoach_reader_constants.CELL_OFF_COMMAND
    elif user_input_command == "start":
        return_start_input = ohcoach_reader_constants.START_READ_WHOLE_CELL_DATA

    return return_start_input


def transmit_command_to_hub_mcu(hub_port, COMMAND):
    print("Hub port = ", hub_port)
    hub_mcu_uart = serial.Serial(hub_port, ohcoach_reader_constants.BAUDRATE)

    # EXECUTE CELL INIT
    hub = bytes.fromhex(COMMAND)
    hub_mcu_uart.write(hub)
    if COMMAND == ohcoach_reader_constants.CELL_OFF_COMMAND:
        print("Close all port...")
        in_bin = hub_mcu_uart.read(10)
        in_bin = in_bin.decode()
        print(in_bin)
        exit()
    elif COMMAND == ohcoach_reader_constants.CELL_INIT_COMMAND:
        in_bin = hub_mcu_uart.read(27)
    else:
        in_bin = hub_mcu_uart.read(23)

    print(in_bin.decode('utf-8'))


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


def read_and_save_gps_data(port, filename):
    print(port + " Start reading GPS data")
    with serial.Serial(port, ohcoach_reader_constants.BAUDRATE, timeout=0.1) as ser, \
            open('gps_imu_data/%s.gp' % filename, mode='w+b') as f:

        gps = bytes.fromhex(ohcoach_reader_constants.SYSCOMMAND_OLD_UPLOAD_GPS_DATA)
        ser.write(gps)

        # jaeuk : 여기서 직접 찍어서 확인해보니 string 으로 출력이 나옵니다.
        print("jaeuk =", filename)

        gps_data_reading_end_flag = 1
        while gps_data_reading_end_flag:
            data = ser.read(ohcoach_reader_constants.CELL_GPS_IMU_READ_CHUCK_SIZE)
            f.write(data)
            str_data = str(data)
            # jaeuk : find는 찾고자하는 문자열이 있으면 문자열의 시작 위치를 리턴하고
            # 원하는 문자열이 없을 시에 -1을 리턴하는데, if -1: 일 때도 if 문으로 들어가기 때문에
            # != -1 조건이 필요. 실제로 != -1 를 빼면 코드가 돌아가지 않음
            if (str_data.find(ohcoach_reader_constants.GPS_END_STR)) != -1:
                print("Find GPSEND")
                gps_data_reading_end_flag = 0
        print(port + " GPS data save is done")


def read_and_save_imu_data(port, filename):
    print(port + " Start reading IMU data")
    print("jaeuk =", filename)

    with serial.Serial(port, ohcoach_reader_constants.BAUDRATE, timeout=0.1) as ser, \
            open('gps_imu_data/%s.im' % filename, mode='w+b') as f:
        imu_cal = bytes.fromhex(ohcoach_reader_constants.SYSCOMMAND_SET_READ_IMU_CAL)
        ser.write(imu_cal)
        imu_cal_data = ser.read(ohcoach_reader_constants.CELL_IMU_CAL_RESP_SIZE)
        print(imu_cal_data)
        imu_cal_data = imu_cal_data[5:-3]
        f.write(imu_cal_data)
        print("calibration data  = ", imu_cal_data)

        imu = bytes.fromhex(ohcoach_reader_constants.SYSCOMMAND_OLD_UPLOAD_IMU_DATA)
        ser.write(imu)
        imu_data_reading_end_flag = 1

        while imu_data_reading_end_flag:
            data = ser.read(ohcoach_reader_constants.CELL_GPS_IMU_READ_CHUCK_SIZE)
            f.write(data)
            str_data = str(data)
            if (str_data.find(ohcoach_reader_constants.IMU_END_STR)) != -1:
                print("Find IMUEND")
                imu_data_reading_end_flag = 0
        print(port + " IMU data save is done")

# jaeuk :  코드가 마무리 되면 erase 함수 추가 예정
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
    filename_list = []
    hub_mcu_port = get_hub_com_port(ohcoach_reader_constants.TARGET_PORT_VENDOR_ID)
    print("main = ", hub_mcu_port)

    hub_command = receive_user_input_command("Enter 'start' OR 'off'")
    create_dir_if_not_exists(ohcoach_reader_constants.PATH_DATA_SAVE_DIR)
    start = time.time()
    is_off = hub_command == ohcoach_reader_constants.CELL_OFF_COMMAND
    if is_off:
        # jaeuk : 이 경우는 cell 전체를 off 하는 경우이기 때문에 다음 프로세스를 진행하지 않고
        # 그대로 끝나기 때문에 리턴 값을 받지 않음
        transmit_command_to_hub_mcu(hub_mcu_port, hub_command)

    transmit_command_to_hub_mcu(hub_mcu_port, ohcoach_reader_constants.CELL_INIT_COMMAND)

    # start 일경우
    for command in hub_command:
        time.sleep(1)

        # jaeuk : receive_user_input_command 에서 키보드로 start을 입력하면
        # line 1~6개의 cell line on command 들어감
        transmit_command_to_hub_mcu(hub_mcu_port, command)
        print("Waiting to opening port....")
        time.sleep(ohcoach_reader_constants.CELL_BOOT_COM_PORT_OPEN_TIME)

        list_ports = cell_port.read_ports_compatible_os_system(hub_mcu_port)
        print(list_ports)

        list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year\
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


    print("Code execution time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

    print("ALL process is END")
    print("Close all cell ports and cmd window after 5 seconds")
    time.sleep(5)
    transmit_command_to_hub_mcu(hub_mcu_port, ohcoach_reader_constants.CELL_OFF_COMMAND)


