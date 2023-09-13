from kdb import report
from kdb.webdriver import kdb_driver


def execute_script_test():
    report.add_comment("Test execute javascript")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php')
    kdb_driver.screen_shot()

    # execute javascript command
    kdb_driver.execute_script(
        "window.location = 'http://automationpractice.com/index.php?id_product=1&controller=product';")
    # verify text to confirm execute success
    kdb_driver.verify_text_on_page('Fashion has been creating well-designed collections since 2010')
    kdb_driver.screen_shot()

    # execute javascript command
    result = kdb_driver.execute_script("return 123;")
    # verify text to confirm execute success
    assert result == 123

    # close browser
    kdb_driver.close_browser()
