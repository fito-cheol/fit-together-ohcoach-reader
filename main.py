import os
import pprint

from .common.ohcoach_reader_constants import *
from .module.Docking import Docking


class UserInterface:

    def __init__(self):
        self.docking = Docking()
        self.file_save_path = []

    # TODO parameter가 2개일 필요 없음 1개 쓸 것
    # TODO return 값이 필요없는 함수
    def get_file_data_path(self, path, name):
        create_dir_if_not_exists(path, name)
        self.file_save_path.append(path + name)
        print(self.file_save_path)
        return self.file_save_path

    # TODO file_save_path를 받는 이유가 없음
    # TODO processing_dock은 return 값이 있을거라고 명시되어 있지 않지만 값을 return함
    #      기능이 한 함수에 여러개가 들어가있으므로 분리할 것 - processing_dock, get_dock_status
    def processing_dock(self, file_save_path, line_process_index):
        each_lines_is_data_serial_num = self.docking.processing_dock(file_save_path, line_process_index)
        # TODO 읽은 line과 안 읽은 line의 결과 값의 형식이 다름
        #
        '''
         2번 줄만 읽었을 때 결과
         
                1번        2번        3번     4번     5번      6번
              [[0, 0], [['5'], []], [0, 0], [0, 0], [0, 0], [0, 0]]
              
              문제1 
              읽지 않은 line(Default)은 int, 
              읽은 line은 string list or empty list
              
              문제2
              CLBX-24434를 읽었었는데 결과값으로 5가 나왔음 시리얼번호가 맞는지 확인  
              
        '''
        # TODO 실제로 돌려보기전에 어떤 값이 return이 될지 예상할 수 있도록 주석이 필요
        # TODO each_lines_is_data_serial_num이라는 이름은
        #      is~~가 들어가기 때문에 boolean값을 return할것으로 예상되지만 그렇지 않음
        #      주석 먼저 달고나서 그에 맞게 이름을 고칠 필요가 있음
        return each_lines_is_data_serial_num

    def off_dock(self):
        self.docking.off_dock()


# TODO 사용자가 지정한 directory를 쓸거라 필요없어질 Method
def create_dir_if_not_exists(path, name):
    print("Check data directory")
    print(path + name)
    if not os.path.isdir(path + name):
        os.mkdir(path + name)


if __name__ == '__main__':
    objectUI = UserInterface()


    # 지정된 line만 processing 한다.
    # line_process_index = 0~5 (line 1~6)
    # line_process_index = -1 이면 전체 line processing
    line_process_index = -1

    # path = PATH_FROM_UI -> PATH_FROM_UI = C:/~/
    path = ''
    file_save_path = objectUI.get_file_data_path(path, NAME_DATA_SAVE_DIR)

    '''
    each_lines_is_data_serial_num 예시
    
    each_lines_is_data_serial_num = 
    Line 1(총 6개 cell 중 4개 yes data 2개 no data) = [[['24348', '65507', '65500', '3'], ['65507', '3']],
    Line 2(총 3개 중 3개 yes data) = [['26323', '14392', '13875'], []], 
    Line 3 = [[], []],
    Line 4 = [[], []],
    Line 5 = [[], []],
    Line 6 = [[], []]]
    
    
    '''
    each_lines_is_data_serial_num = objectUI.processing_dock(file_save_path, line_process_index)
    pprint.pprint(each_lines_is_data_serial_num)

    objectUI.off_dock()







