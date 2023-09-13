import kdb
from kdb import report
from kdb.common.utils import DeviceType
from kdb.webdriver import kdb_driver


def verify_text_on_page_test():
    report.add_comment("Test verify text on page")
    # start browser
    kdb_driver.start_browser()
    # loads login page in the current browser session.
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # verify text is displayed on web page
    kdb_driver.verify_text_on_page('Best Sellers')
    # verify text not displayed in web page
    kdb_driver.verify_text_on_page('This text not in page', reverse=True, timeout=2)
    # verify hidden text
    kdb_driver.verify_text_on_page('Product successfully added to your shopping cart', reverse=True, timeout=2)
    # verify text inside frame
    if DeviceType.is_android(kdb.BROWSER):  # android
        kdb_driver.verify_text_on_page('Be the first of your friends to like this')
    else:
        # todo
        pass

    # close browser
    kdb_driver.close_browser()
