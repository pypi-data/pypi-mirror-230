import kdb
from kdb import report
from kdb.common.utils import DeviceType
from kdb.webdriver import kdb_driver


def press_keys_test():
    report.add_comment("Test press keys keyword/api")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')
    # focus to input search
    kdb_driver.click('id=search_query_top')
    # input search
    kdb_driver.press_keys('shirts')
    # take screenshot
    kdb_driver.screen_shot()
    # press enter
    kdb_driver.press_keys(kdb_driver.keys.ENTER)
    # verify shirts show on page
    kdb_driver.verify_text_on_page('"shirts"')
    # take screenshot
    kdb_driver.screen_shot()

    if DeviceType.is_android(kdb.BROWSER):  # android
        # copy value in input search
        kdb_driver.press_keys((kdb_driver.keys.CONTROL, 'a'), 'id=search_query_top', timeout=10)
        kdb_driver.press_keys((kdb_driver.keys.CONTROL, 'c'))
        # paste value to newsletter
        kdb_driver.press_keys((kdb_driver.keys.CONTROL, 'v'), 'id=newsletter-input')
    else:
        # TODO
        # copy value in input search
        kdb_driver.press_keys((kdb_driver.keys.COMMAND, 'a'), 'id=search_query_top', timeout=10)
        kdb_driver.press_keys((kdb_driver.keys.COMMAND, 'c'))
        # paste value to newsletter
        kdb_driver.press_keys((kdb_driver.keys.COMMAND, 'v'), 'id=newsletter-input')
    # press enter
    kdb_driver.press_keys(kdb_driver.keys.ENTER)
    # verify text on page
    kdb_driver.verify_text_on_page("Newsletter : Invalid email address.")

    # input search
    kdb_driver.press_keys('TRUC_NGUYEN', 'id=search_query_top')
    # press keys
    kdb_driver.press_keys(kdb_driver.keys.LEFT)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_LEFT)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD0)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD1)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD2)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD3)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD4)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD5)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD6)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD7)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD8)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD9)
    kdb_driver.press_keys(kdb_driver.keys.DELETE, extra_time=1)
    kdb_driver.press_keys(kdb_driver.keys.HOME)
    kdb_driver.press_keys(kdb_driver.keys.RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.SEMICOLON)
    kdb_driver.press_keys(kdb_driver.keys.EQUALS)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.SPACE)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.BACKSPACE)
    kdb_driver.press_keys(kdb_driver.keys.BACK_SPACE)
    kdb_driver.press_keys(kdb_driver.keys.END)
    kdb_driver.press_keys(kdb_driver.keys.MULTIPLY)
    kdb_driver.press_keys(kdb_driver.keys.ADD)
    kdb_driver.press_keys(kdb_driver.keys.SEPARATOR)
    kdb_driver.press_keys(kdb_driver.keys.SUBTRACT)
    kdb_driver.press_keys(kdb_driver.keys.DECIMAL)
    kdb_driver.press_keys(kdb_driver.keys.DIVIDE)

    kdb_driver.press_keys(kdb_driver.keys.ENTER)
    # verify text on page
    kdb_driver.verify_text_on_page("T;=R UNGUY0123456789N*+,-./")
    # verify url after search
    kdb_driver.verify_url_contains("T%3B%3DR+UNGUY0123456789N*%2B%2C-.%2F")
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
