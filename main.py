import os
import pprint

from .module.Docking import Docking


class UserInterface:

    def __init__(self):
        self.docking = Docking()
        self._file_save_path = 'data'
        self.create_dir_if_not_exists(self._file_save_path)

    def get_file_data_path(self):
        return self._file_save_path

    def set_file_save_path(self, dir_path):

        self.create_dir_if_not_exists(dir_path)
        self._file_save_path = dir_path

    '''
        지정된 line만 processing 한다.
        line_process_index = 0~5 (line 1~6)
        line_process_index = -1 이면 전체 line processing
    '''
    def processing_dock(self, line_process_index):
        self.docking.processing_dock(self._file_save_path, line_process_index)

    def get_open_closed_serial(self):
        return self.docking.open_closed_serial_per_line

    def off_dock(self):
        self.docking.off_dock()

    @staticmethod
    def create_dir_if_not_exists(dir_path):
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)


if __name__ == '__main__':
    objectUI = UserInterface()

    line_process_index = -1

    objectUI.processing_dock(line_process_index)
    each_lines_is_data_serial_num = objectUI.get_open_closed_serial()
    pprint.pprint(each_lines_is_data_serial_num)

    objectUI.off_dock()



