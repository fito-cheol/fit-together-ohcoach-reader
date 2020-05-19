import time, serial
import concurrent.futures
from functools import partial

from common.ohcoach_reader_constants import *
from helper import cell_info

class CellLine:

    def __init__(self, **kwargs):
        self.line_number = kwargs.get('line_number', None)
        self.start_read_command = START_READ_WHOLE_CELL_DATA[self.line_number]

        self.port_list = []
        self.serial_num_list = []
        self.bad_sector_list = []
        self.firm_ver_list = []
        self.day_month_year_list = []
        self.sec_min_hour_list = []

        self.yes_data_port_list = []
        self.no_data_port_list = []
        self.no_data_serial_num_list = []

        self.filename_list = []
        
    def make_filename(self):
        # self.serial_num_list = []
        # self.bad_sector_list = []
        # self.firm_ver_list = []
        # self.day_month_year_list = []
        # self.sec_min_hour_list = []

        filename_list = []

        for serial_num, firm_ver, day_month_year, sec_min_hour, bad \
                in zip(self.serial_num_list, self.firm_ver_list, self.day_month_year_list, self.sec_min_hour_list, self.bad_sector_list):

            print(serial_num, firm_ver, day_month_year, sec_min_hour, bad)
            filename = '%s_%s_%s_%s_%s' % (serial_num, firm_ver, day_month_year, sec_min_hour, bad)
            print("filename = ", filename)
            filename_list.append(filename)

        self.filename_list = filename_list

    def read_hw_info(self):
        self.yes_data_port_list = []
        self.no_data_port_list = []

        for current_cell_port in self.port_list:

            usart = serial.Serial(current_cell_port, BAUDRATE)
            sum_data = cell_info.check_cell_has_data(usart)
            if sum_data:
                print("Read GPS, IMU data from", current_cell_port)
                serial_number, firm_ver = cell_info.get_hw_info(usart)
                bad_sector_num = cell_info.get_cell_badblock_number(usart)
                day_month_year, sec_min_hour = cell_info.get_time_when_file_create()

                # 파일명 포맷
                # "시리얼번호_펌웨어 버전_스타트타임_badblock_개수.gp .imu"

                self.serial_num_list.append(serial_number)
                self.firm_ver_list.append(firm_ver)
                self.day_month_year_list.append(day_month_year)
                self.sec_min_hour_list.append(sec_min_hour)
                self.bad_sector_list.append(bad_sector_num)

                print("yes data port = ", current_cell_port)
                self.yes_data_port_list.append(current_cell_port)
            else:
                serial_number, firm_ver = cell_info.get_hw_info(usart)
                print("No data port :", current_cell_port)
                self.no_data_port_list.append(current_cell_port)
                self.no_data_serial_num_list.append(serial_number)
        print("yes data serial num list= ", self.serial_num_list)
        print("No data serial num list = ", self.no_data_serial_num_list)
        return self.serial_num_list, self.no_data_serial_num_list

    def make_gp_file(self, file_save_path):
        print(len(self.yes_data_port_list))
        for i in range(len(self.yes_data_port_list) - 1):
            file_save_path.append(file_save_path[0])
        print(file_save_path)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(partial(self.read_and_save_gps_data), self.yes_data_port_list,
                         file_save_path, self.filename_list)

    def make_imu_file(self, file_save_path):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(partial(self.read_and_save_imu_data), self.yes_data_port_list,
                         file_save_path, self.filename_list)

    @staticmethod
    def read_and_save_gps_data(port, file_save_path, filename):
        print(port + " Start reading GPS data")
        print(file_save_path)
        with serial.Serial(port, BAUDRATE, timeout=0.1) as ser, \
                open('%s/%s.gp' % (file_save_path, filename), mode='w+b') as f:

            gps = bytes.fromhex(SYSCOMMAND_OLD_UPLOAD_GPS_DATA)
            ser.write(gps)

            print("jaeuk =", filename)

            gps_data_reading_end_flag = 1
            while gps_data_reading_end_flag:
                data = ser.read(CELL_GPS_IMU_READ_CHUCK_SIZE)
                f.write(data)
                str_data = str(data)

                if (str_data.find(GPS_END_STR)) != -1:
                    print("Find GPSEND")
                    gps_data_reading_end_flag = 0
            print(port + " GPS data save is done")

    @staticmethod
    def read_and_save_imu_data(port, file_save_path, filename):
        print(port + " Start reading IMU data")
        print("jaeuk =", filename)

        with serial.Serial(port, BAUDRATE, timeout=0.1) as ser, \
                open('%s/%s.im' % (file_save_path, filename), mode='w+b') as f:
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
