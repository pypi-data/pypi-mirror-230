from kdb import report
from kdb.webdriver import kdb_driver


def browser_navigation_test():
    report.add_comment("Test browser navigation")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php')
    # click a CATEGORIES
    kdb_driver.click("xpath=//div[@id='block_top_menu']/div")
    # click a Contact us
    kdb_driver.click("xpath=//div[@id='contact-link']/a")
    kdb_driver.verify_title("Contact us - My Store")
    kdb_driver.screen_shot()

    # TODO back()
    kdb_driver.back()
    # verify the title in current page is "My Store"
    kdb_driver.verify_title("My Store")
    kdb_driver.screen_shot()

    # TODO forward()
    kdb_driver.forward()
    kdb_driver.verify_title("Contact us - My Store")
    kdb_driver.screen_shot()

    # TODO refresh()
    # switch to login page
    kdb_driver.click("xpath=//a[@class='login']")
    # click to submit button to get error message
    kdb_driver.click("xpath=//button[@id='SubmitCreate']")
    # verify text on page
    kdb_driver.verify_text_on_page('Invalid email address')
    kdb_driver.refresh()
    # verify text not on page after refresh
    kdb_driver.verify_text_on_page('Invalid email address', reverse=True, timeout=5)
    kdb_driver.screen_shot()

    # TODO back() 2nd times
    kdb_driver.back()
    kdb_driver.back()
    # verify the title in current page is "My Store"
    kdb_driver.verify_title("My Store")
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
