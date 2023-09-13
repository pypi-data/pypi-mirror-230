class TestStatus:
    PASSED = "passed"
    FAILED = "failed"
    SKIP = "skip"
    WARN = "warn"


class InfoMessage:
    ACTION_SUCCESS = "%s successfully."


class ErrorMessage:
    INVALID_ARGUMENT = "The %s argument is invalid."
    START_APPIUM_ERROR = "Can't start appium server with port %s."
    FIND_DEVICE_TIMEOUT = "Not found free device on %d seconds."
    CREATE_LOCK_FILE_TIMEOUT = "Can not create %s file on %d seconds."
    DEVICE_NOT_FOUND = "The %s device is not found."


class AppiumCommand:
    __APPIUM_ANDROID_PARAM = ' -bp %d --chromedriver-port %d --suppress-adb-kill-server --enable-heapdump --relaxed-security'
    START_APPIUM_ANDROID = '/usr/local/bin/node /usr/local/bin/appium -a %s -p %d' + __APPIUM_ANDROID_PARAM

    __APPIUM_IOS_PARAM = ' --webkit-debug-proxy-port %d --webdriveragent-port %d --tmp %s --enable-heapdump --relaxed-security'
    START_APPIUM_IOS = '/usr/local/bin/node /usr/local/bin/appium -a %s -p %d' + __APPIUM_IOS_PARAM

    START_WEBKIT_COMMAND = "/usr/local/bin/ios_webkit_debug_proxy -c %s:%d -d"
    GET_PROCESS_ID_BY_PORT = "ps -ef | grep %s | grep -v grep | grep %d | awk '{print $2}'"
    KILL_PROCESS = "kill -9 %s"

    SERVER_TIME_FORMAT = "%Y%m%d%H%M%S"
    CREATE_LOCK_FILE_IF_NOT_EXISTS = "[ ! -f %s ] && echo `date +%s` > %s && echo 'true' || echo 'false'"
    REMOVE_FILE = "rm %s"
    GET_SERVER_TIME = "echo `date +%s`" % SERVER_TIME_FORMAT
    GET_DATA_LINES_FROM_FILE = "head -%d %s"
