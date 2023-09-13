from kdb import report
from kdb.webdriver import kdb_driver


def login_unit_test_page():
    report.add_comment("Open Tiki.vn page")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://tiki.vn/')

    # update text
    # kdb_driver.update_text('id=user-name', 'standard_user')
    # kdb_driver.update_text('id=password', 'secret_sauce')
    # # click to the search button
    # kdb_driver.click('id=login-button')
    kdb_driver.verify_text_on_page('Sản phẩm bán chạy')