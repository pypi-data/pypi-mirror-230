from kdb import report
from kdb.webdriver import kdb_driver


def element_attribute_test():
    attribute_value = 'text for set attribute'
    report.add_comment("Test get,set and verify attributes of element")
    # start browser
    kdb_driver.start_browser()
    # load url home page
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # TODO in viewport
    report.add_comment(">>> IN VIEWPORT")
    # verify element attribute before set attribute
    kdb_driver.verify_element_attribute("id=search_query_top", 'value', attribute_value, reverse=True, timeout=3)
    # set
    kdb_driver.set_element_attribute("id=search_query_top", 'value', attribute_value)
    kdb_driver.screen_shot()
    # verify
    kdb_driver.verify_element_attribute("id=search_query_top", 'value', attribute_value, timeout=3)
    kdb_driver.verify_element_attribute("id=search_query_top", 'name', 'search_query', timeout=2)
    kdb_driver.verify_element_attribute("id=search_query_top", 'name', 'ch_query', timeout=2, check_contains=True)
    kdb_driver.verify_element_attribute("id=search_query_top", 'placeholder', 'Search', timeout=2)
    # get
    autocomplete = kdb_driver.get_element_attribute("id=search_query_top", "autocomplete")
    # verify of get
    kdb_driver.verify_element_attribute("id=search_query_top", 'autocomplete', autocomplete, timeout=2)
    # verify before set
    kdb_driver.verify_element_attribute("id=search_query_top", 'custom-attr', 'truc.nguyen', timeout=1, reverse=True)
    # set
    kdb_driver.set_element_attribute("id=search_query_top", 'custom-attr', 'truc.nguyen', timeout=3)
    # verify
    kdb_driver.verify_element_attribute("id=search_query_top", 'custom-attr', 'truc.nguyen', timeout=2)
    kdb_driver.verify_element_attribute("id=search_query_top", 'custom-attr', 'truc', timeout=2, check_contains=True)
    # get
    custom = kdb_driver.get_element_attribute("id=search_query_top", "custom-attr")
    # verify of get
    kdb_driver.verify_element_attribute("id=search_query_top", 'custom-attr', custom, timeout=2)

    # TODO out of viewport
    report.add_comment(">>> OUT OF VIEWPORT")
    # verify element attribute before set attribute
    kdb_driver.verify_element_attribute("id=newsletter-input", 'value', attribute_value, reverse=True, timeout=2)
    kdb_driver.set_element_attribute("id=newsletter-input", 'value', attribute_value)
    kdb_driver.screen_shot()
    # verify element attribute after set attribute
    kdb_driver.verify_element_attribute("id=newsletter-input", 'value', attribute_value)
    kdb_driver.verify_element_attribute("id=newsletter-input", 'class', 'inputNew form-control grey newsletter-input')
    kdb_driver.verify_element_attribute("id=newsletter-input", 'type', 'text')
    kdb_driver.verify_element_attribute("id=newsletter-input", 'size', '18')
    # get element attribute after set attribute
    input_value = kdb_driver.get_element_attribute("id=newsletter-input", "value")
    # verify element attribute after get attribute
    kdb_driver.verify_element_attribute("id=newsletter-input", 'value', input_value)
    # verify before set
    kdb_driver.verify_element_attribute("id=newsletter-input", 'abc', input_value, reverse=True, timeout=2)
    # set an element attribute
    kdb_driver.set_element_attribute("id=newsletter-input", 'abc', "aaa")
    # verify
    kdb_driver.verify_element_attribute("id=newsletter-input", 'abc', input_value, reverse=True, timeout=2)
    kdb_driver.verify_element_attribute("id=newsletter-input", 'abc', 'aaa')
    kdb_driver.verify_element_attribute("id=newsletter-input", 'abc', 'a', check_contains=True)
    # get element attribute after set attribute
    abc = kdb_driver.get_element_attribute("id=newsletter-input", "abc")
    # verify
    kdb_driver.verify_element_attribute("id=newsletter-input", 'abc', abc, timeout=3)

    # close browser
    kdb_driver.close_browser()
