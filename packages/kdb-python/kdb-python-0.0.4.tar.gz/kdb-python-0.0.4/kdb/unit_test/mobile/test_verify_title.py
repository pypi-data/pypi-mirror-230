from kdb import report
from kdb.webdriver import kdb_driver


def verify_title_test():
    report.add_comment("Test verify title")
    # start browser
    kdb_driver.start_browser()
    # loads page
    kdb_driver.open_url('http://automationpractice.com/index.php')
    # Verify title is My Store
    kdb_driver.verify_title('My Store')
    # Verify title is not Women - My Store
    kdb_driver.verify_title('Women - My Store', reverse=True, timeout=2)
    kdb_driver.screen_shot()

    # click a Contact us
    kdb_driver.click("xpath=//div[@id='contact-link']/a")
    # Verify title is Women - My Store
    kdb_driver.verify_title("Contact us - My Store")
    # Verify title is not My Store
    kdb_driver.verify_title('My Store', reverse=True, timeout=2)
    kdb_driver.screen_shot()
    kdb_driver.close_browser()
