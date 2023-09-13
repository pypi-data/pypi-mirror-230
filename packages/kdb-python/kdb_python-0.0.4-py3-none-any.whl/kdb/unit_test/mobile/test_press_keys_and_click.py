import kdb
from kdb import report
from kdb.common.utils import DeviceType
from kdb.webdriver import kdb_driver


def press_keys_and_click_test():
    report.add_comment("Test press keys and click keyword/api")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')
    # verify curent title
    kdb_driver.verify_title("My Store")
    # take screenshot
    kdb_driver.screen_shot()
    # Ctrl + click to "Contact us" link
    if DeviceType.is_android(kdb.BROWSER):  # android
        kdb_driver.press_keys_and_click(kdb_driver.keys.CONTROL, 'id=contact-link', timeout=5)
    else:
        kdb_driver.press_keys_and_click(kdb_driver.keys.COMMAND, 'id=contact-link', timeout=5)

    # switch to the tab which open in above step
    kdb_driver.windows.next()
    # verify curent title
    kdb_driver.verify_title("Contact us - My Store")
    # take screenshot
    kdb_driver.screen_shot()
    # Ctrl + click to "Sign in" link
    if DeviceType.is_android(kdb.BROWSER):  # android
        kdb_driver.press_keys_and_click(kdb_driver.keys.CONTROL, 'xpath=//*[@class="login"]', extra_time=2)
    else:
        kdb_driver.press_keys_and_click(kdb_driver.keys.COMMAND, 'xpath=//*[@class="login"]', extra_time=2)

    # switch to the tab which open in above step
    kdb_driver.windows.next()
    # verify curent title
    kdb_driver.verify_title("Login - My Store")
    # take screenshot
    kdb_driver.screen_shot()

    # Ctrl + click to invalid element
    try:
        if DeviceType.is_android(kdb.BROWSER):  # android
            kdb_driver.press_keys_and_click(kdb_driver.keys.CONTROL, 'xpath=//*[@class="invalid-locator"]', timeout=1,
                                            log=False)
        else:
            kdb_driver.press_keys_and_click(kdb_driver.keys.COMMAND, 'xpath=//*[@class="invalid-locator"]', timeout=1,
                                            log=False)
        assert False
    except:
        assert True

    # close browser
    kdb_driver.close_browser()
