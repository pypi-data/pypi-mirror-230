from kdb import report
from kdb.webdriver import kdb_driver


def window_test():
    report.add_comment("Test window")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # This is test step fail
    try:
        kdb_driver.windows.next(timeout=5, log=False)
        assert False
    except:
        assert True
    # move to previous window and get message error
    try:
        kdb_driver.windows.previous(timeout=3, log=False)
        assert False
    except:
        assert True
    # open new tab
    kdb_driver.execute_script("window.open('http://automationpractice.com/index.php?id_product=1&controller=product')")
    # move to next window
    kdb_driver.windows.next()
    # verify text on new window
    kdb_driver.verify_title("Faded Short Sleeve T-shirts - My Store")
    kdb_driver.screen_shot()

    # move to previous window
    kdb_driver.windows.previous()
    # verify text on page
    kdb_driver.verify_title("My Store")
    kdb_driver.screen_shot()

    # open new tab
    kdb_driver.execute_script("window.open('http://automationpractice.com/index.php?id_product=3&controller=product')")
    # move to last tab
    kdb_driver.windows.next()
    kdb_driver.screen_shot()

    kdb_driver.windows.next()
    # verify text on new window
    kdb_driver.verify_title("Printed Dress - My Store")
    kdb_driver.screen_shot()

    # move to main tab
    kdb_driver.windows.main()
    # verify text in main tab
    kdb_driver.verify_title("My Store")
    kdb_driver.screen_shot()
    # move to previous window and get message error
    try:
        kdb_driver.windows.previous(timeout=3, log=False)
        assert False
    except:
        assert True

    # switch to a window
    kdb_driver.windows.switch_window("Faded Short Sleeve T-shirts - My Store")
    # verify text after switch
    kdb_driver.verify_text_on_page("demo_1")
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
