from kdb import report
from kdb.webdriver import kdb_driver


def select_test():
    first_product_locator = "xpath=//ul[contains(@class, 'product_list')]/li[1]/div/div[2]/h5/a"
    report.add_comment("Test select")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php?id_category=3&controller=category')
    # verify
    kdb_driver.verify_element_attribute(first_product_locator, 'innerHTML', 'Faded Short Sleeve T-shirts',
                                        check_contains=True)

    # select by index
    kdb_driver.select("id=selectProductSort", index=2)
    # verify
    kdb_driver.verify_element_attribute(first_product_locator, 'innerHTML', 'Printed Chiffon Dress',
                                        check_contains=True)
    kdb_driver.screen_shot()

    # select by option value
    kdb_driver.select("id=selectProductSort", value="name:asc", timeout=5)
    # verify
    kdb_driver.verify_element_attribute(first_product_locator, 'innerHTML', 'Blouse', check_contains=True)
    kdb_driver.screen_shot()

    # select by text
    kdb_driver.select("id=selectProductSort", text="Reference: Highest first", extra_time=1, timeout=5)
    # verify
    kdb_driver.verify_element_attribute(first_product_locator, 'innerHTML', 'Faded Short Sleeve T-shirts',
                                        check_contains=True)
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
