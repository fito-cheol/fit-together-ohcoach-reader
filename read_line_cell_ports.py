import glob
import sys
import serial

# TODO 함수명에 동사 2개 연속되어서 쓰임
# TODO get_os_system_flag 라고 표시하고 os_system_flag이 뭔지 알려주는게 좋아보임
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

# TODO 함수설명과 함수명이랑 다름, 주석 없애고 함수명에 반영
# 운영체제에 따라서 출력 가능한 virtual port의 리스트를 모두 받아온다.
# TODO parameter로 위에 함수 결과값처럼 os_system_flag라고 쓰는 네이밍을 통일
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

# TODO 함수설명과 함수 명이 다름, 함수는 동사로 시작 할 것
# 포트가 정상적으로 열리는 지를 체크함, 열리는 상태이면 append
# 정상적이지 않으면 error 리턴
def port_normal_open_check(ports):
    # TODO result 대신에 어떤 결과값이 들어갈지 명시
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
# Ex : 두 번째 라인에 cell 3개만 있는 상태면 windows에서 COM3, COM4, COM6 처럼
# 이름을 리턴
# TODO parameter로 result라는 이름을 쓰면 안됨
# TODO parameter로 위에 함수 결과값처럼 os_system_flag라고 쓰는 네이밍을 통일
def get_cell_ports_from_hub_mcu(os, hub_port, result):
    if os == 1:
        start_index = result.index(hub_port)
        # TODO result 대신에 어떤 결과값이 들어갈지 명시
        result = result[start_index+1:start_index+7]
    elif os == 2:
        print("linux")
    elif os == 3:
        start_index = result.index(hub_port)
        result = result[start_index + 1:start_index + 7]
    else:
        raise EnvironmentError('Unsupported platform')

    return result

# TODO 함수명에 설명이 더 필요함 어떤 것을 리턴하는지
def read_ports(hub_port_name):
    os_system_flag = get_check_os()
    print(os_system_flag)
    print(hub_port_name)
    print("Read all cell ports")
    ports = get_cells_name(os_system_flag)
    result = port_normal_open_check(ports)
    final_result = get_cell_ports_from_hub_mcu(os_system_flag, hub_port_name, result)

    return final_result
