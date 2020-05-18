import time, serial
import concurrent.futures
from functools import partial

from common.ohcoach_reader_constants import *
from helper.cell_port import get_hub_com_port
from helper import cell_info, cell_port
from module.CellLine import CellLine


class Docking:

    def __init__(self):
        self.hub_mcu_port = get_hub_com_port(TARGET_PORT_VENDOR_ID)
        self.transmit_command_to_hub_mcu(CELL_INIT_COMMAND)
        print("Hub port = ", self.hub_mcu_port)
        self.hub_mcu_uart = serial.Serial(self.hub_mcu_port , BAUDRATE)

        self.cell_line_list = []
        for i in range(TOTAL_DECK_LINE_NUMBER):
            self.cell_line_list.append(CellLine(i))

    def transmit_command_to_hub_mcu(self, command):

        # EXECUTE CELL INIT
        hub = bytes.fromhex(command)
        self.hub_mcu_uart.write(hub)
        if command == CELL_OFF_COMMAND:
            print("Close all port...")
            in_bin = self.hub_mcu_uart.read(10)
            in_bin = in_bin.decode()
            print(in_bin)
        elif command == CELL_INIT_COMMAND:
            in_bin = self.hub_mcu_uart.read(27)
        else:
            in_bin = self.hub_mcu_uart.read(23)

        print(in_bin.decode('utf-8'))

    def processing_dock(self):

        for cell_line in self.cell_line_list:
            print("Waiting for Line Change")
            time.sleep(CELL_LINE_CHANGE_TIME)

            self.transmit_command_to_hub_mcu(cell_line.start_read_command)

            print("Cell booting, Opening port ....")
            time.sleep(CELL_BOOT_COM_PORT_OPEN_TIME)

            # TODO 한줄로 합치기
            list_ports = cell_port.read_ports_compatible_os_system(self.hub_mcu_port)
            cell_line.port_list = list_ports
            print(list_ports)

            cell_line.read_hw_info()

            # TODO makefilename CellLine에서 가져와서 쓰기
            cell_line.make_filename()
            print("Main filename = ", cell_line.filename_list)

            print("---------------------Save GPS data---------------------")
            cell_line.make_gp_file()

            print("---------------------Save IMU data---------------------")
            cell_line.make_imu_file()

    def off_dock(self):
        self.transmit_command_to_hub_mcu(CELL_OFF_COMMAND)
