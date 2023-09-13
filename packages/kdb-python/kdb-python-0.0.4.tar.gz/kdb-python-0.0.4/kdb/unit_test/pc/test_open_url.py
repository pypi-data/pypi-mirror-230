from kdb import report
from kdb.webdriver import kdb_driver


def open_url_test():
    report.add_comment("Open url http://automationpractice.com/index.php")
    # start browser
    kdb_driver.start_browser()

    # load page
    kdb_driver.open_url('http://automationpractice.com/index.php')
    # verify title
    kdb_driver.verify_title("My Store")
    kdb_driver.screen_shot()

    # load page
    kdb_driver.open_url('http://automationpractice.com/index.php?controller=contact')
    # verify title
    kdb_driver.verify_title("Contact us - My Store")
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
