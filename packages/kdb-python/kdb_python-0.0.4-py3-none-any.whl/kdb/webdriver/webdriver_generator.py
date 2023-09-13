import logging
import os
import random
import time

from appium import webdriver
# Options are only available since client version 2.3.0
# If you use an older client then switch to desired_capabilities
# instead: https://github.com/appium/python-client/pull/720
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from selenium.common.exceptions import InvalidArgumentException, TimeoutException
from selenium.webdriver import Proxy
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.ie.options import Options as IEOptions, ElementScrollBehavior
from selenium.webdriver.ie.webdriver import WebDriver as IEDriver

import kdb
from kdb import FolderSettings
from kdb.common.config_parser import ConfigParser
from kdb.common.constants import ErrorMessage
from kdb.common.mobile_manager import MobileManager, get_device_info
from kdb.common.utils import DeviceType, WebDriverUtil, OS, CommandLine, FileUtil
from kdb.config import proxy_list
from kdb.config.settings import ChromeSettings, FirefoxSettings, DriverSettings, IESettings


def _create_proxy(proxy_name):
    """
    create a Proxy from config
    """
    # get a proxy from config
    proxy_config = proxy_list.PROXYS.get(str(proxy_name).lower())
    if proxy_name is None or proxy_config is None:
        raise Exception("No proxy is found for %s" % proxy_name)

    host = proxy_config.get('proxy')
    proxy = {'proxyType': 'manual', 'ftpProxy': host, 'httpProxy': host, 'sslProxy': host}

    if proxy_config.get('username') is not None and proxy_config.get('password') is not None:
        proxy['socksProxy'] = host
        proxy['username'] = proxy_config.get('username')
        proxy['password'] = proxy_config.get('password')

    return Proxy(proxy)


_CHROME_ALIAS = {"ch", "chrome"}
_FIREFOX_ALIAS = {"ff", "firefox"}
_IE_ALIAS = {"ie", "internetexplorer"}


def _create_chrome_driver(proxy_name=None, private_mode=False):
    # 1. create chromeOption
    chrome_options = ChromeOptions()
    # 2. set ChromeOption attribute from config (e.g. proxy, --maximize, etc)
    chrome_options.add_argument('start-maximized')
    # chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument('headless')
    if private_mode:
        chrome_options.add_argument('incognito')
    # 3. add proxy
    if proxy_name is not None:
        proxy = _create_proxy(proxy_name)  # todo proxy sẽ dc set ở ChromeOption
    # 4. create ChromeService
    service = ChromeService(executable_path=ChromeSettings.DRIVER_PATH,
                            log_output=os.path.join(FolderSettings.LOG_DIR, ChromeSettings.DRIVER_NAME + ".log"))
    # 5. create ChromeDriver
    chrome_driver = ChromeDriver(service=service, options=chrome_options)

    return chrome_driver


def _create_firefox_driver(proxy_name=None, private_mode=False):
    # create options instance
    options = FirefoxOptions()
    # set browser mode
    if private_mode:
        options.add_argument('-private')
    # set log level
    # options.log.level = 'trace'
    # convert options to desired_capabilities
    desired_capabilities = options.to_capabilities()
    # set proxy
    if proxy_name is not None:
        proxy = _create_proxy(proxy_name)
        proxy.add_to_capabilities(desired_capabilities)

    return FirefoxDriver(executable_path=FirefoxSettings.DRIVER_PATH, desired_capabilities=desired_capabilities,
                         log_path=os.path.join(FolderSettings.LOG_DIR, FirefoxSettings.DRIVER_NAME + ".log"))


def check_ie_running():
    """
    Check just run single IE instance on a VM
    :return:
    """
    if not OS.is_window_platform():
        raise OSError("The current operating system doesn't support to run with the internet explorer")
    current_time = time.time()
    # check file is exit but ie driver is not running
    is_running = CommandLine.check_port_running(IESettings.RUNNING_PORT)
    if is_running is False:
        # random a number
        time.sleep(random.uniform(1, 5))
        # check ie running
        data_check_again = CommandLine.check_port_running(IESettings.RUNNING_PORT)
        # run ie driver if ie not running
        if data_check_again is False:
            # create log file to make browser is running
            ConfigParser(IESettings.IE_LOG_FILE).write("time", time.time(), override=True,
                                                       create_if_file_not_exists=True)
            return True
    while int(time.time() - current_time) < IESettings.CHECK_PORT_TIME_OUT:
        if not os.path.exists(IESettings.IE_LOG_FILE):
            # check ie running
            is_running = CommandLine.check_port_running(IESettings.RUNNING_PORT)
            if is_running is False:
                # random a number
                time.sleep(random.uniform(1, 5))
                # check ie running
                data_check_again = CommandLine.check_port_running(IESettings.RUNNING_PORT)
                if data_check_again is False:
                    # create log file to make browser is running
                    ConfigParser(IESettings.IE_LOG_FILE).write("time", time.time(), override=True,
                                                               create_if_file_not_exists=True)
                    return True
            else:
                # This block code use for case run test in folder
                # get pid number
                pid = CommandLine.get_pid_by_port(IESettings.RUNNING_PORT)
                # kill process
                CommandLine.kill_process_by_pid(pid)
        time.sleep(random.uniform(1, 3))
    raise TimeoutException(
        "Out of time to check port is running. Port %s is running by other process" % IESettings.RUNNING_PORT)


def _create_ie_driver(proxy_name=None, private_mode=False):
    """
    Create a IE driver
    We need to config as link: https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver#Required Configuration
    """
    check_ie_running()
    # create IEOption
    ie_options = IEOptions()
    # Forces launching Internet Explorer using the CreateProcess API. If this option is not specified,
    # IE is launched using the IELaunchURL, if it is available. For IE 8 and above,
    # this option requires the TabProcGrowth registry value to be set to 0.
    ie_options.force_create_process_api = True
    # private mode
    if private_mode:
        # This is only valid when used with the force_create_process_api
        ie_options.add_argument('-private')
    # clean all data history, cookies........
    ie_options.ensure_clean_session = True
    # use native events
    ie_options.native_events = True
    ie_options.element_scroll_behavior = ElementScrollBehavior.TOP
    # Require that the IE window have focus before performing any user interaction operations (mouse or keyboard events)
    ie_options.require_window_focus = True
    # no use ignore_protected_mode_settings: https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities#webdriver-1
    # ie_options.ignore_protected_mode_settings = True

    # Indicates whether to skip the check that the browser's zoom level is set to 100%.
    ie_options.ignore_zoom_level = True
    # TODO: persistent_hover not effect/work
    # Persistent hovering is achieved by continuously firing mouse over events at the last location
    # the mouse cursor has been moved to.
    ie_options.persistent_hover = True
    # parse option to Capabilities using to add proxy
    ie_capabilities = ie_options.to_capabilities()
    # set proxy
    if proxy_name is not None:
        proxy = _create_proxy(proxy_name)
        proxy.add_to_capabilities(ie_capabilities)
    return IEDriver(executable_path=IESettings.DRIVER_PATH, capabilities=ie_capabilities, port=IESettings.RUNNING_PORT,
                    service_log_path=os.path.join(FolderSettings.LOG_DIR, IESettings.DRIVER_NAME + ".log"))


def _create_android_driver(driver_name, app_path=None, full_reset=False, custom_opts=None):
    if kdb.ENV == 'dev':
        # get device info from config file
        is_group, device_info = get_device_info(driver_name)
        device_info = device_info['android_emulator-5555']
    else:
        if not OS.is_mac_platform():
            # Android only run on MAC machine
            raise InvalidArgumentException(
                "The %s driver is only run on MAC machine. Please check your server's OS." % driver_name)
        device_info = MobileManager.start_appium_server(driver_name)
        # remove lock file
        MobileManager.remove_lock_file()

    #
    options = UiAutomator2Options()
    options.automation_name = 'uiautomator2'  # uiautomator2 for Android; XCUITest for iOS
    options.platformName = 'android',  # iOS, Android
    # UDID of the device to be tested. Could ve retrieved from adb devices -l output.
    # If unset then the driver will try to use the first connected device.
    # Always set this capability if you run parallel tests.
    options.udid = device_info.get('udid')
    # The name of Android emulator to run the test on.
    # The names of currently installed emulators could be listed using avdmanager list avd command.
    # If the emulator with the given name is not running then it is going to be started before a test
    options.avd = device_info.get('avd')
    # The platform version of an emulator or a real device.
    # This capability is used for device autodetection if udid is not provided
    options.platformVersion = device_info.get('platformVersion')
    # The name of the device under test (actually, it is not used to select a device under test).
    # Consider setting udid for real devices and avd for emulators instead
    options.deviceName = device_info.get('deviceName')
    options.newCommandTimeout = DriverSettings.DRIVER_NEW_COMMAND_TIMEOUT
    options.chromeDriverPort = device_info.get('chromeDriverPort')
    # fullRest uninstalls the app. fullReset is generally used when you have newer versions of the app coming in fairly quickly.
    # So with fullReset, you will always uninstall the app and then automatically install the new version.
    options.fullReset = full_reset
    options.noReset = not full_reset  # noReset just clears the app data, such as its cache
    # Enforces the server to dump the actual XML page source into the log if any error happens.
    options.printPageSourceOnFindFailure = True  # false by default.
    options.skipDeviceInitialization = True
    # options.enforceAppInstall = True
    # Do not provide both app and browserName capabilities at once.
    if app_path is None:
        options.browserName = 'chrome'
        logging.info("Starting Chrome browser on %s..." % device_info.get('deviceName'))
    else:
        options.app = FileUtil.get_absolute_path(app_path)
        logging.info("Starting App on %s..." % device_info.get('deviceName'))

    if custom_opts is not None:
        options.load_capabilities(custom_opts)
    return webdriver.Remote(device_info.get('hubURL'), options=options)


def _create_ios_driver(driver_name, app_path=None, full_reset=False):
    if not OS.is_mac_platform():
        # iOS only run on MAC machine
        raise InvalidArgumentException(
            "The %s driver is only run on MAC machine. Please check your server's OS." % driver_name)
    device_info = MobileManager.start_appium_server(driver_name)
    # remove lock file
    MobileManager.remove_lock_file()

    logging.info("Starting Safari browser on %s..." % device_info.get('deviceName'))
    #
    desired_caps = {"automationName": "xcuitest",  # case-insensitively
                    "platformName": "iOS",
                    # platformVersion: This capability is used for device autodetection if udid is not provided
                    "platformVersion": device_info.get('platformVersion'),
                    # Consider setting udid for real devices and use this one for Simulator selection instead
                    "deviceName": device_info.get('deviceName'),
                    "udid": device_info.get('udid'),
                    "newCommandTimeout": DriverSettings.DRIVER_NEW_COMMAND_TIMEOUT,
                    "wdaLocalPort": device_info.get('wdaLocalPort'),
                    # todo: webkitDebugProxyPort is only necessary for Appium below version 1.15.
                    "webkitDebugProxyPort": device_info.get('webkitDebugProxyPort'),  # todo
                    "clearSystemFiles": True,  # Delete any generated files at the end of a session. Default to false.
                    "shouldUseSingletonTestManager": False,
                    # Get JSON source from WDA and transform it to XML on the Appium server side. Defaults to false
                    'useJSONSource': True,
                    'preventWDAAttachments': True,
                    'fullReset': full_reset,
                    'sendKeyStrategy': 'oneByOne',
                    # simulator caps
                    "shutdownOtherSimulators": True, 'safariAllowPopups': True,
                    'safariIgnoreFraudWarning': True,
                    'safariOpenLinksInBackground': True, 'reduceMotion': True,
                    # todo
                    # 'useNewWDA': True,  # useNewWDA: Real devices require WebDriverAgent client to run for as long as possible without reinstall/restart
                    # 'nativeWebTap': True,
                    # 'showXcodeLog': True,
                    }

    if app_path is None:
        desired_caps['browserName'] = 'safari'
    else:
        desired_caps['app'] = FileUtil.get_absolute_path(app_path)

    return webdriver.Remote(device_info.get('hubURL'), desired_caps)


def create_driver(driver_name="chrome", proxy_name=None, private_mode=False, app_path=None, full_reset=False):
    """
    create a webdriver
    :param driver_name:
    :param proxy_name:
    :param private_mode:
    :param app_path:
    :param full_reset:
    :return: WebDriver
    """
    driver_name = str(driver_name).lower().strip()
    # create web driver depend driver_name
    if driver_name in _CHROME_ALIAS:
        driver = _create_chrome_driver(proxy_name, private_mode)
    elif driver_name in _FIREFOX_ALIAS:
        driver = _create_firefox_driver(proxy_name, private_mode)
    elif driver_name in _IE_ALIAS:
        driver = _create_ie_driver(proxy_name, private_mode)
    elif DeviceType.is_android(driver_name):
        driver = _create_android_driver(driver_name, app_path=app_path, full_reset=full_reset)
    elif DeviceType.is_ios(driver_name):
        driver = _create_ios_driver(driver_name, app_path=app_path, full_reset=full_reset)
    else:
        # the driver name invalid
        raise InvalidArgumentException(ErrorMessage.INVALID_ARGUMENT % "driver_name")

    if driver is not None:
        # make maximize window for PC only
        if not WebDriverUtil.is_mobile(driver):
            driver.maximize_window()
            driver.set_page_load_timeout(DriverSettings.DRIVER_SET_PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(DriverSettings.DRIVER_SET_SCRIPT_TIMEOUT)
        # add timeout
        # driver.implicitly_wait(DriverSettings.DRIVER_IMPLICITLY_WAIT)
        # use IMPLICITLY_WAIT to find element in actions instead
    return driver
