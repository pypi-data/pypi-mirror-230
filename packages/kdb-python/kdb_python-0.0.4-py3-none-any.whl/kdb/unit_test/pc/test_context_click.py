from kdb import report
from kdb.webdriver import kdb_driver


def context_click_test():
    report.add_comment("Test context click keyword/api")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')
    # context click to "Contact us" link
    kdb_driver.context_click('id=contact-link', extra_time=10)
    # todo verifying

    # take screenshot
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
