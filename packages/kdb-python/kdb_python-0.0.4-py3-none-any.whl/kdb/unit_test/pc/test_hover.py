from kdb import report
from kdb.webdriver import kdb_driver


def hover_test():
    report.add_comment("Hover to a web element")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # TODO out of viewport
    report.add_comment(">>> OUT OF VIEWPORT")
    # hover to web element
    kdb_driver.hover("xpath=//*[@id='homefeatured']/li[7]/div")
    # screen shot
    kdb_driver.screen_shot()
    # click to the button More
    kdb_driver.click("xpath=//*[@id='homefeatured']/li[7]/div/div[2]/div[2]/a[2]")
    # verify text after click
    kdb_driver.verify_text_on_page('Printed chiffon knee length dress with tank straps. Deep v-neckline.')
    # screen shot
    kdb_driver.screen_shot()

    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # TODO in viewport
    report.add_comment(">>> IN VIEWPORT")
    # hover to web element
    kdb_driver.hover("xpath=//*[@id='homefeatured']/li[1]/div", extra_time=1)
    # screen shot
    kdb_driver.screen_shot()
    # verify text before click
    kdb_driver.verify_text_on_page('Product successfully added to your shopping cart', reverse=True, timeout=2)
    kdb_driver.verify_text_on_page('There is 1 item in your cart.', reverse=True, timeout=2)
    # click to the Add to cart button
    kdb_driver.click("xpath=//*[@id='homefeatured']/li[1]/div/div[2]/div[2]/a[1]")
    # verify text after click
    kdb_driver.verify_text_on_page('Product successfully added to your shopping cart')
    kdb_driver.verify_text_on_page('There is 1 item in your cart.')
    # screen shot
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
