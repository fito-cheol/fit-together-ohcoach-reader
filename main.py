import os
import serial

from helper import cell_info, cell_port

from ohcoach_reader_constants import *
from module.Docking import Docking


class UserInterface:

    def __init__(self):
        create_dir_if_not_exists(PATH_DATA_SAVE_DIR)
        self.docking = Docking()

    def processing_dock(self):
        self.docking.processing_dock()

    def off_dock(self):
        self.docking.off_dock()


# TODO 사용자가 지정한 directory를 쓸거라 필요없어질 Method
def create_dir_if_not_exists(directory):
    print("Check data directory")

    if not os.path.isdir(directory):
        os.mkdir(directory)


if __name__ == '__main__':
    objectUI = UserInterface()

    is_processing = True

    objectUI.find_dock()

    if is_processing:
        objectUI.processing_dock()
    else:
        objectUI.off_dock()







