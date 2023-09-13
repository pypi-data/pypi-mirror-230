import kdb
from kdb import report
from kdb.webdriver import kdb_driver


def test_verify_element_attribute():
    # start browser
    report.add_comment("Test get attribute element")
    kdb_driver.start_browser(kdb.BROWSER)
    # load url home page
    kdb_driver.open_url('http://automationpractice.com/index.php')
    kdb_driver.set_element_attribute("id=newsletter-input", 'value', "text for set attribute")
    kdb_driver.screen_shot()
    kdb_driver.verify_element_attribute("id=newsletter-input", 'value', "text for set attribute")
    input_value = kdb_driver.get_element_attribute("id=newsletter-input", "value")
    kdb_driver.verify_element_attribute("id=newsletter-input", 'value', input_value, extra_time=5)

    kdb_driver.set_element_attribute("id=newsletter-input", 'value', "text for set attribute set again")
    kdb_driver.screen_shot()
    kdb_driver.verify_element_attribute("id=newsletter-input", 'value', input_value, reverse=True, timeout=5)

    kdb_driver.close_browser()
