from kdb import report
from kdb.webdriver import kdb_driver


def is_display_test():
    report.add_comment("Test is display")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # TODO element is NOT displayed/ is hidden
    # verify an element is not display
    is_displayed = kdb_driver.is_displayed('xpath=//div[@id="categories_block_left"]/div', reverse=True, timeout=5)
    assert is_displayed is True
    is_displayed = kdb_driver.is_displayed('xpath=//div[@id="categories_block_left"]/div', timeout=2)
    assert is_displayed is False
    # take screenshot
    kdb_driver.screen_shot()

    # TODO element is displayed
    # check a web element is display
    is_displayed = kdb_driver.is_displayed("xpath=//button[@name='submitNewsletter']")
    assert is_displayed is True
    is_displayed = kdb_driver.is_displayed("xpath=//button[@name='submitNewsletter']", timeout=1, reverse=True)
    assert is_displayed is False

    # TODO element not exists
    is_displayed = kdb_driver.is_displayed("id=not-exist", timeout=2, reverse=True)
    assert is_displayed is True
    is_displayed = kdb_driver.is_displayed("id=not-exist", timeout=1)
    assert is_displayed is False
    # take screenshot
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
