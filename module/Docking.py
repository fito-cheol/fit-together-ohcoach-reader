import time, serial
import concurrent.futures
from functools import partial

from ..common.ohcoach_reader_constants import *
from ..helper.cell_port import get_hub_com_port
from ..helper import cell_info, cell_port
from ..module.CellLine import CellLine


class Docking:

    def __init__(self):
        self.open_closed_serial_per_line = [[[] for col in range(2)] for row in range(6)]
        self.hub_mcu_port = get_hub_com_port(TARGET_PORT_VENDOR_ID)
        self.transmit_command_to_hub_mcu(CELL_INIT_COMMAND)
        print("Hub port = ", self.hub_mcu_port)

        self.cell_line_list = []
        for i in range(TOTAL_DECK_LINE_NUMBER):
            self.cell_line_list.append(CellLine(line_number=i))

    def transmit_command_to_hub_mcu(self, command):
        self.hub_mcu_uart = serial.Serial(self.hub_mcu_port, BAUDRATE)
        # EXECUTE CELL INIT
        hub = bytes.fromhex(command)
        self.hub_mcu_uart.write(hub)
        if command == CELL_OFF_COMMAND:
            print("Close all port...")
            in_bin = self.hub_mcu_uart.read(10)
            print(in_bin)
        elif command == CELL_INIT_COMMAND:
            in_bin = self.hub_mcu_uart.read(27)
        else:
            in_bin = self.hub_mcu_uart.read(23)

        print(in_bin.decode('utf-8'))
        self.hub_mcu_uart.close()

    def yes_no_data_port_list(self):
        return

    def processing_dock(self, file_save_path, line_process_index):
        print("processing_dock = ", file_save_path)
        if (line_process_index + 1):
            print("True")
            cell_line = self.cell_line_list[line_process_index]
            print(cell_line)
            print("Waiting for Line Change")
            time.sleep(CELL_LINE_CHANGE_TIME)

            self.transmit_command_to_hub_mcu(cell_line.start_read_command)

            print("Cell booting, Opening port ....")
            time.sleep(CELL_BOOT_COM_PORT_OPEN_TIME)
            cell_line.port_list = cell_port.read_ports_compatible_os_system(self.hub_mcu_port)

            # 각각의 셀이 gps/imu 데이터가 있는지 없는지 체크한 다음
            # 데이터가 있으면 cell 정보를 파일명으로 쓰기 위한 데이터를 만든다.
            serial_num_list, no_data_serial_num_list = cell_line.read_hw_info()

            cell_line.make_filename()
            print("Main filename = ", cell_line.filename_list)
            start = time.time()
            print("---------------------Save GPS data---------------------")
            cell_line.make_gp_file(file_save_path)

            print("---------------------Save IMU data---------------------")
            cell_line.make_imu_file(file_save_path)
            print("Code execution time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
            self.open_closed_serial_per_line[line_process_index] = \
                [serial_num_list, no_data_serial_num_list]
            print("processing_dock", self.open_closed_serial_per_line)
        else:
            print("False")
            for cell_line in self.cell_line_list:
                print(self.cell_line_list.index(cell_line))
                print("Waiting for Line Change")
                time.sleep(CELL_LINE_CHANGE_TIME)

                self.transmit_command_to_hub_mcu(cell_line.start_read_command)

                print("Cell booting, Opening port ....")
                time.sleep(CELL_BOOT_COM_PORT_OPEN_TIME)
                cell_line.port_list = cell_port.read_ports_compatible_os_system(self.hub_mcu_port)

                # 각각의 셀이 gps/imu 데이터가 있는지 없는지 체크한 다음
                # 데이터가 있으면 cell 정보를 파일명으로 쓰기 위한 데이터를 만든다.
                serial_num_list, no_data_serial_num_list = cell_line.read_hw_info()

                cell_line.make_filename()
                print("Main filename = ", cell_line.filename_list)
                start = time.time()
                print("---------------------Save GPS data---------------------")
                cell_line.make_gp_file(file_save_path)

                print("---------------------Save IMU data---------------------")
                cell_line.make_imu_file(file_save_path)
                print("Code execution time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
                self.open_closed_serial_per_line[self.cell_line_list.index(cell_line)] = \
                    [serial_num_list, no_data_serial_num_list]
            print("processing_dock", self.open_closed_serial_per_line)


    def off_dock(self):
        self.transmit_command_to_hub_mcu(CELL_OFF_COMMAND)
