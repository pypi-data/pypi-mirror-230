from kdb import report
from kdb.webdriver import kdb_driver


def update_text_test():
    report.add_comment("Test function update text")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # TODO in viewport
    report.add_comment(">>> IN VIEWPORT")
    # update text
    kdb_driver.update_text('id=search_query_top', 'shirts')
    # click to the search button
    kdb_driver.click('xpath=//button[@name="submit_search"]')
    # verify result
    kdb_driver.verify_text_on_page("Showing 1 - 1 of 1 item")
    kdb_driver.screen_shot()
    # with slow
    kdb_driver.update_text('id=search_query_top', 'shirts slow', slow=True, timeout=5)
    # verify
    kdb_driver.verify_element_attribute('id=search_query_top', 'value', 'shirts slow', timeout=2)
    kdb_driver.screen_shot()
    # with slow and extra time
    kdb_driver.update_text('id=search_query_top', 'shirts slow extra', slow=True, timeout=5, extra_time=1)
    # verify
    kdb_driver.verify_element_attribute('id=search_query_top', 'value', 'shirts slow extra', timeout=2)
    kdb_driver.screen_shot()
    # # with decrypt todo later
    # kdb_driver.update_text('id=search_query_top', 'shirts slow extra', decrypt=True, timeout=5)

    # TODO out of viewport
    report.add_comment(">>> OUT OF VIEWPORT")
    # update text
    kdb_driver.update_text('id=newsletter-input', 'invalid-email', timeout=5)
    # verify attribute
    kdb_driver.verify_element_attribute('id=newsletter-input', 'value', 'invalid-email', timeout=2)
    kdb_driver.screen_shot()
    # click to submit button
    kdb_driver.click('xpath=//button[@name="submitNewsletter"]')
    # verify result
    kdb_driver.verify_text_on_page(" Newsletter : Invalid email address.")
    kdb_driver.screen_shot()
    # close browser
    kdb_driver.close_browser()
