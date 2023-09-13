from kdb import report
from kdb.webdriver import kdb_driver


def close_browser_test():
    report.add_comment("Test close browser")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')
    # verify title
    kdb_driver.verify_title("My Store", timeout=5)
    # close browser
    kdb_driver.close_browser()
    # thrown exception when execute a api after close browser
    try:
        kdb_driver.verify_title("Women - My Store", log=False)
        assert False
    except:
        assert True
