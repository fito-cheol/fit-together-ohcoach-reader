import glob
import sys
import serial


# WINDOWS = 1, LINUX & CYGWIN = 2, macOS = 3
def get_check_os():
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
def get_cells_name(os):
    if os == 1:
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif os == 2:
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif os == 3:
        ports = glob.glob('/dev/cu.*')
    else:
        raise EnvironmentError('Unsupported platform')

    return ports


# 포트가 정상적으로 열리는 지를 체크함, 열리는 상태이면 append
# 정상적이지 않으면 error 리턴
def port_normal_open_check(ports):
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# 허브 포트의 위치를 기준으로 라인에 있는 open 가능한 port의 이름을 리턴
# jaeuk :
# Ex : 두 번째 라인에 cell 3개만 있는 상태면 windows에서 COM3, COM4, COM6 처럼
# 이름을 리턴
def get_cell_ports_from_hub_mcu(os, hub_port, result):
    if os == 1:
        start_index = result.index(hub_port)
        result = result[start_index+1:start_index+7]
    elif os == 2:
        print("linux")
    elif os == 3:
        start_index = result.index(hub_port)
        result = result[start_index + 1:start_index + 7]
    else:
        raise EnvironmentError('Unsupported platform')

    return result


def read_ports(hub_port_name):
    os_system_flag = get_check_os()
    print(os_system_flag)
    print(hub_port_name)
    print("Read all cell ports")
    ports = get_cells_name(os_system_flag)
    result = port_normal_open_check(ports)
    final_result = get_cell_ports_from_hub_mcu(os_system_flag, hub_port_name, result)

    return final_result
