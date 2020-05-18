import time, serial
import concurrent.futures
from functools import partial

from ohcoach_reader_constants import *
from helper.cell_port import get_hub_com_port
from helper import cell_info, cell_port


class Docking:

    def __init__(self):
        self.hub_mcu_port = get_hub_com_port(TARGET_PORT_VENDOR_ID)
        self.transmit_command_to_hub_mcu(CELL_INIT_COMMAND)

    def transmit_command_to_hub_mcu(self, command):
        print("Hub port = ", self.hub_mcu_port)
        hub_mcu_uart = serial.Serial(self.hub_mcu_port , BAUDRATE)

        # EXECUTE CELL INIT
        hub = bytes.fromhex(command)
        hub_mcu_uart.write(hub)
        if command == CELL_OFF_COMMAND:
            print("Close all port...")
            in_bin = hub_mcu_uart.read(10)
            in_bin = in_bin.decode()
            print(in_bin)
            exit()
        elif command == CELL_INIT_COMMAND:
            in_bin = hub_mcu_uart.read(27)
        else:
            in_bin = hub_mcu_uart.read(23)

        print(in_bin.decode('utf-8'))

    def processing_dock(self):
        for command in START_READ_WHOLE_CELL_DATA:
            # port 열리는 시간을 위해서 재움
            time.sleep(1)

            self.transmit_command_to_hub_mcu(command)
            print("Waiting to opening port....")
            time.sleep(CELL_BOOT_COM_PORT_OPEN_TIME)

            list_ports = cell_port.read_ports_compatible_os_system(self.hub_mcu_port)
            print(list_ports)

            list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year \
                , list_mic_sec_min_hour, list_bad_block = cell_info.check_is_data_and_save_cell_filename(list_ports)
            print(list_ports_with_data, list_cell_serial_data, list_cell_firm_ver, list_day_month_year
                  , list_mic_sec_min_hour, list_bad_block)

            filename_list = self.make_filename(list_cell_serial_data, list_cell_firm_ver, list_day_month_year,
                                          list_mic_sec_min_hour, list_bad_block)
            print("Main filename = ", filename_list)

            print("---------------------Save GPS data---------------------")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(partial(self.read_and_save_gps_data), list_ports_with_data
                             , filename_list)

            print("---------------------Save IMU data---------------------")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(partial(self.read_and_save_imu_data), list_ports_with_data
                             , filename_list)

    def off_dock(self):
        self.transmit_command_to_hub_mcu(CELL_OFF_COMMAND)

    @staticmethod
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

    # TODO CellLine 클래스에 들어갈 Method
    @staticmethod
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

    # TODO CellLine 클래스에 들어갈 Method
    @staticmethod
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
