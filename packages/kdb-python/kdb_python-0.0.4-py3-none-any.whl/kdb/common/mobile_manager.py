import logging
import time
from random import random

from selenium.common.exceptions import TimeoutException, SessionNotCreatedException, InvalidArgumentException

from kdb import APPIUM_LOCK_FILE
from kdb.common.constants import ErrorMessage, AppiumCommand
from kdb.common.ssh_connection import SSH
from kdb.common.utils import DeviceType
from kdb.config import device_list
from kdb.config.settings import MobileSettings

_ssh = SSH(MobileSettings.HOST, MobileSettings.USERNAME, MobileSettings.PASSWORD)


def execute_ssh_command(command, new_connection=False, print_command=True):
    """
    Execute a command in server
    """
    if new_connection:
        new_ssh = SSH(MobileSettings.HOST, MobileSettings.USERNAME, MobileSettings.PASSWORD)
        return new_ssh.execute_command(command, print_command)
    else:
        return _ssh.execute_command(command, print_command)


def get_device_info(device_name):
    """
    Get the device(s) information from configuration file
    """
    device_name = str(device_name).lower()
    is_group = False

    if DeviceType.is_android(device_name):
        # android
        if DeviceType.ANDROID == device_name:
            is_group = True
            # android group
            # shuffling device_list.ANDROID
            return is_group, dict(sorted(device_list.ANDROID.items(), key=lambda x: random()))
        else:
            if device_list.ANDROID.get(device_name) is not None:
                return is_group, device_list.ANDROID.get(device_name)
            else:
                raise InvalidArgumentException(ErrorMessage.DEVICE_NOT_FOUND % device_name)

    elif DeviceType.is_ios(device_name):
        # ios
        if DeviceType.IOS == device_name:
            # ios group
            is_group = True
            # shuffling device_list.IOS
            return is_group, dict(sorted(device_list.IOS.items(), key=lambda x: random()))
        else:
            # ios device
            if device_list.IOS.get(device_name) is not None:
                return is_group, device_list.IOS.get(device_name)
            else:
                raise InvalidArgumentException(ErrorMessage.DEVICE_NOT_FOUND % device_name)
    else:
        # raise exception
        raise InvalidArgumentException(ErrorMessage.DEVICE_NOT_FOUND % device_name)


def check_free_port(device_alias, device_info):
    """
    Check device's Appium port is running or not. In Simulator case, return False if we have one simulator running.
    """
    if DeviceType.is_simulator(device_alias):
        simulator_ports = ""
        for device_key, device_value in device_list.SIMULATOR.items():
            simulator_ports += "," + str()
            result = execute_ssh_command(
                AppiumCommand.GET_PROCESS_ID_BY_PORT % ("appium", device_value.get('appiumPort')), print_command=False)
            if len(result) > 0:
                return False
        else:
            return True
    else:
        # is_ios or is_android
        result = execute_ssh_command(AppiumCommand.GET_PROCESS_ID_BY_PORT % ("appium", device_info.get('appiumPort')),
                                     print_command=False)
        return len(result) == 0


def kill_process(app_name, port):
    """
    Kill the processes on MAC machine
    """
    # get process id by port
    process_ids = execute_ssh_command(AppiumCommand.GET_PROCESS_ID_BY_PORT % (app_name, port))
    # stop by process id
    for process_id in process_ids:
        process_id = str(process_id).replace("\r\n", "")
        if process_id.strip() != '':
            execute_ssh_command(AppiumCommand.KILL_PROCESS % process_id)


def create_log_file(start_time):
    """
    Create a .lock file in server machine (MAC machine) that used to indicate when the appium can be started.
    We only start appium if file not exists
    """
    while int(time.time()) - start_time < MobileSettings.FIND_DEVICE_TIME_OUT:
        # comm_res is true if lock file is not exists and it is created successfully, otherwise false
        comm_res = str(execute_ssh_command(AppiumCommand.CREATE_LOCK_FILE_IF_NOT_EXISTS % (
            APPIUM_LOCK_FILE, AppiumCommand.SERVER_TIME_FORMAT, APPIUM_LOCK_FILE), print_command=False)[0])
        # created lock file successful
        if "true" in comm_res:
            logging.info(">>> Create lock file (%s) successful." % APPIUM_LOCK_FILE)
            return True
        else:
            # read first line in lock file
            data_lines = execute_ssh_command(AppiumCommand.GET_DATA_LINES_FROM_FILE % (1, APPIUM_LOCK_FILE),
                                             print_command=False)
            lock_file_time = int(data_lines[0])
            # get current time in server (MAC) machine
            server_time = int(execute_ssh_command(AppiumCommand.GET_SERVER_TIME, print_command=False)[0])
            # force remove lock file if it created more than 30 minutes ago
            if server_time - lock_file_time > MobileSettings.FIND_DEVICE_TIME_OUT:
                # remove lock file
                logging.info(">>> Force remove lock file because it created more than 30 minutes ago.")
                execute_ssh_command(AppiumCommand.REMOVE_FILE % APPIUM_LOCK_FILE)
        time.sleep(MobileSettings.CREATE_LOCK_FILE_INTERVAL_DELAY)
    # create lock file time out
    raise TimeoutException(
        ErrorMessage.CREATE_LOCK_FILE_TIMEOUT % (APPIUM_LOCK_FILE, MobileSettings.FIND_DEVICE_TIME_OUT))


class MobileManager:
    mobile_port = 0
    is_created_lock_file = False

    @staticmethod
    def start_appium_server(device_name):
        # get time start
        start_time = int(time.time())
        # create lock file
        created_lock_file = create_log_file(start_time)
        # update create log file flag
        if created_lock_file:
            MobileManager.is_created_lock_file = True
        # get device info from config file
        is_group, device_info = get_device_info(device_name)
        # find a device until time out
        while True:
            if created_lock_file:
                # checking whether the given device name is group or single device
                if is_group:
                    # running on a group device
                    for device_alias, device_value in device_info.items():
                        # device_alias: is key (device_name) in device_list.py
                        result = start_appium(device_alias, device_value)
                        if result is not None:
                            return result
                else:
                    # running a single device
                    result = start_appium(device_name, device_info)
                    if result is not None:
                        return result
                # find interval delay
                time.sleep(MobileSettings.FIND_DEVICE_INTERVAL_DELAY)
            # return loop when time out
            if int(time.time()) - start_time > MobileSettings.FIND_DEVICE_TIME_OUT:
                # remove lock file
                MobileManager.remove_lock_file()
                # find devices time out
                raise TimeoutException(ErrorMessage.FIND_DEVICE_TIMEOUT % MobileSettings.FIND_DEVICE_TIME_OUT)

    @staticmethod
    def remove_lock_file():
        if MobileManager.is_created_lock_file:
            execute_ssh_command(AppiumCommand.REMOVE_FILE % APPIUM_LOCK_FILE)
            MobileManager.is_created_lock_file = False

    @staticmethod
    def set_mobile_port(mobile_port: int):
        MobileManager.mobile_port = mobile_port

    @staticmethod
    def close_mobile_port():
        if MobileManager.mobile_port != 0:
            kill_process("appium", MobileManager.mobile_port)
            MobileManager.mobile_port = 0


def start_appium(device_alias, device_info):
    is_free_port = check_free_port(device_alias, device_info)
    if is_free_port:
        # start appium
        if DeviceType.is_android(device_alias):
            start_server_android(device_info)
        else:
            start_server_ios(device_info, device_alias)
        # make sure appium server is started by checking port
        if not check_free_port(device_alias, device_info):
            # store the started appium port that will be closed at the end test
            MobileManager.set_mobile_port(int(device_info.get('appiumPort')))
            logging.info(">>> %s device is started: %s" % (device_alias, str(device_info)))
            return device_info
        else:
            raise SessionNotCreatedException(ErrorMessage.START_APPIUM_ERROR % str(device_info.get('appiumPort')))
    else:
        # this case handle running a folder
        if MobileManager.mobile_port == int(device_info.get('appiumPort')):
            logging.warning(
                ">>> Only one device will be run on a session. But also we now have a device (%s) is started before. "
                "So this will be used to run this test script "
                "but also we must restart the Appium server before using." % str(device_info))
            logging.info("Restarting the Appium server...")
            MobileManager.close_mobile_port()
            return start_appium(device_alias, device_info)


def start_server_android(device_info):
    appium_port = device_info.get('appiumPort')
    bootstrap_port = device_info.get('bootstrapPort')
    chrome_driver_port = device_info.get('chromeDriverPort')

    logging.info(">>> Starting Appium server with port: " + str(appium_port))
    # start appium server
    execute_ssh_command(
        AppiumCommand.START_APPIUM_ANDROID % (MobileSettings.HOST, appium_port, bootstrap_port, chrome_driver_port),
        True)


def start_server_ios(device_info, device_name):
    udid = device_info.get('udid')
    appium_port = device_info.get('appiumPort')
    # todo is only necessary for Appium below version 1.15.
    webkit_debug_proxy_port = device_info.get('webkitDebugProxyPort')
    wda_port = device_info.get('wdaLocalPort')
    tmp = device_info.get('tmpDir')

    if not DeviceType.is_simulator(device_name):
        # stop process id by webkit port(webkit_debug_proxy_port)
        kill_process("webkit", webkit_debug_proxy_port)
        # START Webkit Debug Proxy # todo
        # https://appium.io/docs/en/writing-running-appium/web/hybrid/#execution-against-an-ios-real-device
        # ios-webkit-debugger-proxy is only necessary for Appium below version 1.15.
        logging.info(">>> Starting Webkit Debug Proxy with port: " + str(webkit_debug_proxy_port))
        execute_ssh_command(AppiumCommand.START_WEBKIT_COMMAND % (udid, webkit_debug_proxy_port), True)

    logging.info(">>> Starting Appium server with port: " + str(appium_port))
    # start appium server
    execute_ssh_command(
        AppiumCommand.START_APPIUM_IOS % (MobileSettings.HOST, appium_port, webkit_debug_proxy_port, wda_port, tmp),
        True)
