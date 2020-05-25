import os
import pprint

from .common.ohcoach_reader_constants import *
from .module.Docking import Docking


class UserInterface:

    def __init__(self):
        self.docking = Docking()
        self._file_save_path = os.path.dirname(os.path.abspath(__file__)) + '/data'
        create_dir_if_not_exists(self._file_save_path)

    def get_file_data_path(self):
        return self._file_save_path

    def set_file_save_path(self, dir_path):
        create_dir_if_not_exists(dir_path)
        self._file_save_path = dir_path

    def processing_dock(self, line_process_index):
        self.docking.processing_dock(self._file_save_path, line_process_index)
        '''
              문제2
              CLBX-24434를 읽었었는데 결과값으로 5가 나왔음 시리얼번호가 맞는지 확인  
              
        '''

    # TODO 실제로 돌려보기전에 어떤 값이 return이 될지 예상할 수 있도록 주석이 필요
    def get_open_closed_serial(self):
        return self.docking.open_closed_serial_per_line

    def off_dock(self):
        self.docking.off_dock()


# TODO 사용자가 지정한 directory를 쓸거라 필요없어질 Method
def create_dir_if_not_exists(dir_path):
    print("Check data directory")
    print(dir_path)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)


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



