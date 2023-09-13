from kdb import report
from kdb.webdriver import kdb_driver


def verify_url_contains_test():
    report.add_comment("Test verify url  contains a string or not")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # verify
    kdb_driver.verify_url_contains("automationpractice.com/index.php")
    # verify current url = http://automationpractice.com/index.php
    kdb_driver.verify_url_contains("http://automationpractice.com/index.php")
    kdb_driver.verify_url_contains("http://automationpractice.com/index.php", exactly=True)
    # verify current url != http://automationpractice.com/index.html
    kdb_driver.verify_url_contains("http://automationpractice.com/index.html", reverse=True, timeout=0)
    kdb_driver.verify_url_contains("http://automationpractice.com/index.html", exactly=True, reverse=True, timeout=0)
    kdb_driver.screen_shot()

    # click a Contact us
    kdb_driver.click("xpath=//div[@id='contact-link']/a")
    # verify current url contains "controller=contact"
    kdb_driver.verify_url_contains("controller=contact")
    kdb_driver.verify_url_contains("http://automationpractice.com/index.php?controller=contact", exactly=True)
    kdb_driver.screen_shot()

    # negative case
    try:
        kdb_driver.verify_url_contains("controller=invalid", log=False, timeout=2)
        assert False
    except:
        assert True
    try:
        kdb_driver.verify_url_contains("http://automationpractice.com/index.php", reverse=True, log=False, timeout=2)
        assert False
    except:
        assert True

    # close browser
    kdb_driver.close_browser()
