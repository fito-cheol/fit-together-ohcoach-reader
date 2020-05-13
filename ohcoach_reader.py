import os
import time
import serial
import concurrent.futures
from functools import partial
from datetime import datetime
import serial.tools.list_ports

import ohcoach_reader_constants
import read_line_cell_ports
import making_filename

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


def converge_filename(serial_num, firm_ver, day, sec, bad):
    filename = ''
    filename_list = []
    print(len(serial_num))
    for i in range(0, len(serial_num)):
        print(serial_num[i], firm_ver[i], day[i], sec[i], bad[i])
        filename = '%s_%s_%s_%s_%s' % (serial_num[i], firm_ver[i], day[i], sec[i], bad[i])
        print("filename = ", filename)
        filename_list.append(filename)

    return filename_list


def read_and_save_gps_data(port, filename_list):
    print(port + " Start reading GPS data")
    ser = serial.Serial(port, ohcoach_reader_constants.BAUDRATE, timeout=0.1)
    gps = bytes.fromhex(ohcoach_reader_constants.SYSCOMMAND_OLD_UPLOAD_GPS_DATA)
    ser.write(gps)

    # TODO  읽는 부분과 쓰는 부분을 나눌 수 있음
    # jaeuk : data 읽으면서 동시에 기록하지 않으면 데이터가 누락이 생겨
    # serial port 상에서 임의의 딜레이를 추가해야 되어
    # 오히려 reading 시간이 늘어나 읽고 쓰기를 동시에 진행 했습니다.
    f = open('gps_imu_data/%s.gp' % filename_list, mode='w+b')
    gps_data_reading_end_flag = 1
    while gps_data_reading_end_flag:
        data = ser.read(ohcoach_reader_constants.CELL_GPS_IMU_READ_CHUCK_SIZE)
        f.write(data)
        str_data = str(data)
        if (str_data.find(ohcoach_reader_constants.GPS_END_STR)) != -1:
            print("Find GPSEND")
            gps_data_reading_end_flag = 0
    print(port + " GPS data save is done")
    ser.close()


def read_and_save_imu_data(port, filename_list):
    print(port + " Start reading IMU data")
    ser = serial.Serial(port, ohcoach_reader_constants.BAUDRATE, timeout=0.1)

    f = open('gps_imu_data/%s.im' % filename_list, mode='w+b')
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
    ser.close()

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
    if hub_command == ohcoach_reader_constants.CELL_OFF_COMMAND:
        # TODO  transmit_command_to_hub_mcu 리턴값이 없는 이유
        # jaeuk : 이 경우는 cell 전체를 off 하는 경우이기 때문에 다음 프로세스를 진행하지 않고
        # 그대로 끝나기 때문에 리턴 값을 받지 않음
        transmit_command_to_hub_mcu(hub_mcu_port, hub_command)

    # TODO  hub command의 길이를 확인하는 이유
    # jaeuk: 테스트를 위해 사용자 input을 start / off / 1~6 line으로 한정 되었는데 off가 아닌 상태에서
    # 한 자리 숫자 길이 보다 큰 start 가 들어오면 reading을 진행
    if len(hub_command) > 2:
        transmit_command_to_hub_mcu(hub_mcu_port, ohcoach_reader_constants.CELL_INIT_COMMAND)
        # TODO 왜 6번 루프 도는지 궁금
        # jaeuk : Ohcoach 덱의 라인이 총 6개 때문입니다.
        for i in range(0, ohcoach_reader_constants.TOTAL_DECK_LINE_NUMBER):
            # TODO 1초 슬립 쓰는 이유
            # jaeuk : 라인이 바뀌는 와중에 USB 덱의 포트가 열리는 시간을 조금 벌어주기 위함으로 넣음
            time.sleep(1)
            # TODO  hub_command[i]가 의미하는 바는??
            # jaeuk : receive_user_input_command 에서 키보드로 start을 입력하면
            # line 1~6개의 cell line on command 들어감
            transmit_command_to_hub_mcu(hub_mcu_port, hub_command[i])
            print("Waiting to opening port....")
            time.sleep(ohcoach_reader_constants.CELL_BOOT_COM_PORT_OPEN_TIME)

            list_ports = read_line_cell_ports.read_ports(hub_mcu_port)
            print(list_ports)
            list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year\
                , list_mic_sec_min_hour, list_bad_block = making_filename.check_is_data_and_save_cell_filename(list_ports)
            print(list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year
                  , list_mic_sec_min_hour, list_bad_block)

            filename_list = converge_filename(list_cell_serial_data, list_cell_firm_ver, list_day_month_year,
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

    else:
        print("OFF all cells")

    print("Code execution time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

    print("ALL process is END")
    print("Close all cell ports and cmd window after 10 seconds")
    time.sleep(10)
    transmit_command_to_hub_mcu(hub_mcu_port, ohcoach_reader_constants.CELL_OFF_COMMAND)


