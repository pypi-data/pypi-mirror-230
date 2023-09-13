import kdb
from kdb import report
from kdb.common.utils import DeviceType
from kdb.webdriver import kdb_driver


def click_test():
    report.add_comment("Test click")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # TODO click an element in viewport
    report.add_comment(">>> IN VIEWPORT")
    # click to the "Contact us" link
    kdb_driver.click("xpath=//div[@id='contact-link']/a")
    # verify text to confirm click success
    kdb_driver.verify_text_on_page('Customer service - Contact us')
    kdb_driver.screen_shot()

    # TODO click an element out of viewport
    report.add_comment(">>> OUT OF VIEWPORT")
    # load home page
    kdb_driver.open_url('http://automationpractice.com/index.php')
    # click to the "submitNewsletter" button
    kdb_driver.click("xpath=//button[@name='submitNewsletter']", timeout=5)
    # verify text to confirm click success
    kdb_driver.verify_text_on_page('Newsletter : Invalid email address.')
    kdb_driver.screen_shot()

    # TODO click an element in iframe
    report.add_comment(">>> IN IFRAME")
    if DeviceType.is_android(kdb.BROWSER):  # android
        # click the "PrestaShop" link inside iframe
        kdb_driver.click("xpath=//a[contains(@class, '_3-8_ lfloat')]", extra_time=1)
        # switch to fb window
        kdb_driver.windows.next()
        # verify text to confirm click success
        kdb_driver.verify_url_contains('facebook.com/prestashop')
        kdb_driver.screen_shot()
    else:
        # todo
        pass

    # close browser
    kdb_driver.close_browser()
