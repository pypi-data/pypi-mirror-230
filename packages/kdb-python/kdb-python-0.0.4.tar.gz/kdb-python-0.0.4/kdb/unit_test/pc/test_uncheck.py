import kdb
from kdb import report
from kdb.webdriver import kdb_driver


def test_uncheck():
    report.add_comment("Test uncheck for checkbox")
    kdb_driver.start_browser(kdb.BROWSER)
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php?id_category=3&controller=category')
    # check and verify with checkbox
    report.add_comment("Test check for checkbox")
    # execute script to show web element
    kdb_driver.execute_script(
        "$('div.checker input').css({'opacity': '1','filter': 'alpha(opacity=1)','-moz-opacity': '1'})")
    # verify checkbox is not check
    kdb_driver.verify_state("id=layered_category_4", checked=False, timeout=10)
    # check to checkbox
    kdb_driver.check("id=layered_category_4")
    kdb_driver.screen_shot()
    # verify checkbox is checked
    kdb_driver.verify_state("id=layered_category_4", checked=True, timeout=10)
    kdb_driver.screen_shot()
    # check to checkbox
    kdb_driver.uncheck("id=layered_category_4")
    # verify checkbox is not check
    kdb_driver.verify_state("id=layered_category_4", checked=False, timeout=10)
    kdb_driver.screen_shot()
    kdb_driver.close_browser()
