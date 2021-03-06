#!/usr/bin/env python
# encoding: utf-8
"""
ohcoach_reader_constants.py
"""
NAME_DATA_SAVE_DIR = "gps_imu_data"
GPS_END_STR = "GPSEND"
IMU_END_STR = "IMUEND"

CELL_INIT_COMMAND = "43 45 4C 4C 5F 45 4E 5F 49 4E 49 54 0D 0A"
CELL_OFF_COMMAND = "43 45 4C 4C 5F 4F 46 46 0D 0A"
CELL_GPS_IMU_READ_CHUCK_SIZE = 2048
CELL_IMU_CAL_RESP_SIZE = 128
CELL_LINE_CHANGE_TIME = 1
CELL_BOOT_COM_PORT_OPEN_TIME = 12
BAUDRATE = 230400
TARGET_PORT_VENDOR_ID = 1155

SYSCOMMAND_CELL_POWER_ON = ""
SYSCOMMAND_CELL_POWER_OFF = ""
SYSCOMMAND_HW_INFORMATION = "AC C0 01 10 7D"
SYSCOMMAND_HW_INFORMATION_RESP_SIZE = 23
SYSCMD_GET_BADBLOCK_NUMBER = "AC C0 01 D6 BB"
SYSCMD_GET_BADBLOCK_NUMBER_RESP_SIZE = 6
SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_SIZE = "AC C0 01 11 7C"
SYSCOMMAND_UPLOAD_TOTAL_GPS_AND_IMU_RESP_SIZE = 9
SYSCOMMAND_SET_READ_IMU_CAL = "AC C0 01 24 49"
SYSCOMMAND_OLD_UPLOAD_GPS_DATA = "AC C0 02 E0 00 8E"
SYSCOMMAND_OLD_UPLOAD_IMU_DATA = "AC C0 01 E1 8C"
SYSCOMMAND_ERASE_NAND_FLASH = "AC C0 01 15 78"
SYSCMD_CELL_POWER_OFF = "AC C0 01 17 7A"

TOTAL_DECK_LINE_NUMBER = 6

START_READ_WHOLE_CELL_DATA = ["43 45 4C 4C 31 5F 4F 4E 0D 0A", "43 45 4C 4C 32 5F 4F 4E 0D 0A", "43 45 4C 4C 33 5F 4F 4E 0D 0A",
                              "43 45 4C 4C 34 5F 4F 4E 0D 0A", "43 45 4C 4C 35 5F 4F 4E 0D 0A", "43 45 4C 4C 36 5F 4F 4E 0D 0A"]