from kdb import report
from kdb.unit_test.pc.page_object.signup import Signup
from kdb.webdriver import kdb_driver


def check_uncheck_and_verify_state_test():
    report.add_comment("Test check ON for radio/checkbox, uncheck for checkbox only and verify radio/checkbox state")
    kdb_driver.start_browser()

    # TODO radio
    report.add_comment(">>> Radio")
    # load page for test.
    kdb_driver.open_url('https://automationexercise.com/signup')

    signup_page = Signup()
    signup_page.input_name("trucnt").input_email("trucnt88@gmail.com").click_signup()

    signup_page.set_mr().verify_mr(True).verify_mrs(False)
    kdb_driver.screen_shot()
    signup_page.set_mrs().verify_mrs(True).verify_mr(False)
    kdb_driver.screen_shot()

    # TODO checkbox
    report.add_comment(">>> Test check for checkbox")
    signup_page.verify_newsletter(False).verify_optin(False)
    kdb_driver.screen_shot()
    signup_page.set_newsletter().verify_newsletter(True)
    signup_page.set_optin().verify_optin(True)
    kdb_driver.screen_shot()

    # UNCHECK checkbox
    signup_page.unset_newsletter().verify_newsletter(False)
    signup_page.unset_optin().verify_optin(False)
    kdb_driver.screen_shot()

    # checkbox is out of viewport
    # check ON checkbox
    # UNCHECK checkbox

    # close browser
    kdb_driver.close_browser()
