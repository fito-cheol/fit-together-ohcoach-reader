import glob
import sys
import serial
import serial.tools.list_ports

# WINDOWS = 1, LINUX & CYGWIN = 2, macOS = 3
def get_os_system_flag():
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


# 운영체제에 따라서 출력 가능한 virtual port의 리스트를 모두 받아온다.
def get_os_system_port_list(os_system_flag):
    if os_system_flag == 1:
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif os_system_flag == 2:
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif os_system_flag == 3:
        ports = glob.glob('/dev/cu.*')
    else:
        raise EnvironmentError('Unsupported platform')

    return ports

# 포트가 정상적으로 열리는 지를 체크함, 열리는 상태이면 append
# 정상적이지 않으면 error 리턴
def is_port_open(ports):
    open_done_port = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            open_done_port.append(port)
        except (OSError, serial.SerialException):
            pass
    return open_done_port


# 허브 포트의 위치를 기준으로 라인에 있는 open 가능한 port의 이름을 리턴
# Ex : 두 번째 라인에 cell 3개만 있는 상태면 windows에서 COM3, COM4, COM6 처럼
# 이름을 리턴
def get_cell_ports_from_hub_mcu(os_system_flag, hub_port, open_done_port):
    print("getcell", hub_port)
    print("getcell open done", open_done_port)
    if os_system_flag == 1:
        start_index = open_done_port.index(hub_port)
        cell_ports_base_on_hub_port = open_done_port[start_index+1:start_index+7]
    elif os_system_flag == 2:
        print("linux")
    elif os_system_flag == 3:
        start_index = open_done_port.index(hub_port)
        cell_ports_base_on_hub_port = open_done_port[start_index + 1:start_index + 7]
    else:
        raise EnvironmentError('Unsupported platform')

    return cell_ports_base_on_hub_port

def read_ports_compatible_os_system(hub_port_name):
    os_system_flag = get_os_system_flag()
    print(os_system_flag)
    print(hub_port_name)
    print("Read all cell ports")
    ports = get_os_system_port_list(os_system_flag)
    open_done_port = is_port_open(ports)
    cell_ports_base_on_hub_port = get_cell_ports_from_hub_mcu(os_system_flag, hub_port_name, open_done_port)

    return cell_ports_base_on_hub_port

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

