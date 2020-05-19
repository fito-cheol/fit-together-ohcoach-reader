import os
import pprint

from common.ohcoach_reader_constants import *
from module.Docking import Docking


class UserInterface:

    def __init__(self):
        self.docking = Docking()
        self.file_save_path = []

    def get_file_data_path(self, path, name):
        create_dir_if_not_exists(path, name)
        self.file_save_path.append(path + name)
        print(self.file_save_path)
        return self.file_save_path

    def processing_dock(self, file_save_path, line_process_index):
        each_lines_is_data_serial_num = self.docking.processing_dock(file_save_path, line_process_index)
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

    # UI 에서 받아온 파일 저장 경로(path)를 여기서 넘겨준다.
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







