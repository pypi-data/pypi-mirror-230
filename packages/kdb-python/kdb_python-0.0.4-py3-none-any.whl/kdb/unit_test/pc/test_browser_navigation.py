from kdb import report
from kdb.unit_test.pc import login_unit_test_page
from kdb.webdriver import kdb_driver


def test_browser_nav():
    # start browser
    report.add_comment("Test browser navigation")
    # load page for test.
    login_unit_test_page()

    # click a left menu "Điện Gia Dụng"
    # href="https://tiki.vn/dien-gia-dung/c1882"
    kdb_driver.click("xpath=//a[@href='https://tiki.vn/dien-gia-dung/c1882']")
    kdb_driver.verify_text_on_page("Back to products")
    #  //a[@data-view-index='1']/span[@title='Điện Gia Dụng']
    kdb_driver.screen_shot()
    kdb_driver.back()
    kdb_driver.verify_url_contains("https://www.saucedemo.com/inventory.html")
    kdb_driver.screen_shot()
    kdb_driver.forward()
    kdb_driver.verify_text_on_page("Back to products")
    kdb_driver.screen_shot()


    kdb_driver.close_browser()
