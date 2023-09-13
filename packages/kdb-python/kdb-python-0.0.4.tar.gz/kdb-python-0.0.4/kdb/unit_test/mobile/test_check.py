from kdb import report
from kdb.webdriver import kdb_driver


def check_uncheck_and_verify_state_test():
    report.add_comment("Test check ON for radio/checkbox, uncheck for checkbox only and verify radio/checkbox state")
    kdb_driver.start_browser()

    # TODO radio
    report.add_comment(">>> Radio")
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php?controller=authentication')
    # update text to create email
    kdb_driver.update_text("xpath=//input[@id='email_create']", "truc.nguyen@mail.com.vn")
    # click to button submit
    kdb_driver.click("xpath=//button[@id='SubmitCreate']")
    # verifying "Your personal information" is displayed
    kdb_driver.verify_text_on_page("Your personal information")

    # execute script to show web element
    kdb_driver.execute_script("$('div.radio input').css('opacity', 1)")
    # verify the radio is not check
    kdb_driver.verify_state("id=id_gender1", checked=False, timeout=3, extra_time=1)
    kdb_driver.verify_state("id=id_gender2", checked=False, timeout=3)
    kdb_driver.screen_shot()
    # check to the radio Mr
    kdb_driver.check("id=id_gender1", timeout=5)
    # verify radio is checked Mr
    kdb_driver.verify_state("id=id_gender1", checked=True, timeout=3)
    # verify radio is not checked Mrs
    kdb_driver.verify_state("id=id_gender2", checked=False, timeout=2)
    kdb_driver.screen_shot()
    # check to the radio Mrs
    kdb_driver.check("id=id_gender2", extra_time=1)
    # verify radio is checked Mrs
    kdb_driver.verify_state("id=id_gender2", checked=True, timeout=3)
    kdb_driver.verify_state("id=id_gender1", checked=False, timeout=2)
    kdb_driver.screen_shot()

    # TODO checkbox
    report.add_comment(">>> Test check for checkbox")
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php?id_category=3&controller=category')
    # verify a text on page
    kdb_driver.verify_text_on_page("Showing 1 - 7 of 7 items")
    # open catalog
    kdb_driver.click("xpath=//div[@id='layered_block_left']/p")
    # check and verify with checkbox
    # execute script to show web element
    kdb_driver.execute_script(
        "$('div.checker input').css({'opacity': '1','filter': 'alpha(opacity=1)','-moz-opacity': '1'})")
    # verify checkbox is not check
    kdb_driver.verify_state("id=layered_category_4", checked=False, extra_time=1)

    # checkbox is in viewport

    # check ON checkbox
    kdb_driver.check("id=layered_category_4")
    # verify a text on page
    kdb_driver.verify_text_on_page("Showing 1 - 2 of 2 items")
    # verify checkbox is checked
    kdb_driver.verify_state("id=layered_category_4", checked=True, timeout=5)
    kdb_driver.screen_shot()

    # UNCHECK checkbox
    # execute script to show web element
    kdb_driver.execute_script(
        "$('div.checker input').css({'opacity': '1','filter': 'alpha(opacity=1)','-moz-opacity': '1'})")
    kdb_driver.uncheck("id=layered_category_4")
    # verify a text on page
    kdb_driver.verify_text_on_page("Showing 1 - 7 of 7 items")
    # verify checkbox is unchecked
    kdb_driver.verify_state("id=layered_category_4", checked=False, timeout=5)
    kdb_driver.screen_shot()

    # checkbox is out of viewport

    # check ON checkbox
    # execute script to show web element
    kdb_driver.execute_script(
        "$('div.checker input').css({'opacity': '1','filter': 'alpha(opacity=1)','-moz-opacity': '1'})")
    # verify checkbox is unchecked
    kdb_driver.verify_state("id=layered_manufacturer_1", checked=False, timeout=5, extra_time=1)
    # check
    kdb_driver.check("id=layered_manufacturer_1")
    # verify url
    kdb_driver.verify_url_contains("manufacturer-fashion_manufacturer")
    # verify checkbox is checked
    kdb_driver.verify_state("id=layered_manufacturer_1", checked=True, timeout=5)
    kdb_driver.screen_shot()

    # UNCHECK checkbox
    # execute script to show web element
    kdb_driver.execute_script(
        "$('div.checker input').css({'opacity': '1','filter': 'alpha(opacity=1)','-moz-opacity': '1'})")
    kdb_driver.uncheck("id=layered_manufacturer_1")
    # verify url
    kdb_driver.verify_url_contains("manufacturer-fashion_manufacturer", reverse=True)
    # verify checkbox is unchecked
    kdb_driver.verify_state("id=layered_manufacturer_1", checked=False, timeout=5)
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
