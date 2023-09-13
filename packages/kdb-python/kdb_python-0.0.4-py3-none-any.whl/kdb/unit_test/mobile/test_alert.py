from kdb import report
from kdb.webdriver import kdb_driver


def alert_tests():
    report.add_comment("Test alert")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php')
    kdb_driver.screen_shot()

    # TODO: get, verify alert text and accept
    # execute js to show alert
    kdb_driver.execute_script("alert('Alert text')")
    # get text in alert
    text_alert = kdb_driver.alert.get_text()
    # verify alert text
    kdb_driver.alert.verify_text_alert(text_alert)
    # accept alert
    kdb_driver.alert.accept()
    kdb_driver.screen_shot()

    # TODO: dismiss alert
    # execute js to show alert
    kdb_driver.execute_script("alert('Alert text')")
    # dismiss alert
    kdb_driver.alert.dismiss()
    kdb_driver.screen_shot()

    # TODO: get, verify confirm text and accept
    # execute js to show confirm alert
    kdb_driver.execute_script("""
        if(confirm('Are you want to navigate to Sign-in page?') == true){
            document.location = 'http://automationpractice.com/index.php?controller=authentication&back=my-account'
        }
    """)
    # get text in confirm alert
    text_confirm = kdb_driver.alert.get_text()
    # verify confirm alert text
    kdb_driver.alert.verify_text_alert(text_confirm)
    kdb_driver.alert.verify_text_alert('truc_nguyen', reverse=True, timeout=0)
    # accept confirm alert
    kdb_driver.alert.accept()
    # verify Sign-in is displayed
    kdb_driver.verify_title('Login - My Store')
    kdb_driver.screen_shot()

    # TODO: verify text and dismiss confirm
    # execute js to show confirm alert
    kdb_driver.execute_script("""
        if(confirm('Click Cancel to navigate to Home page') == false){
            document.location = 'http://automationpractice.com/index.php'
        }
    """)
    # verify confirm alert text
    kdb_driver.alert.verify_text_alert('Click Cancel to navigate to Home page')
    kdb_driver.alert.verify_text_alert(text_confirm, reverse=True, timeout=0)
    # dismiss confirm alert
    kdb_driver.alert.dismiss()
    # verify Sign-in is displayed
    kdb_driver.verify_title('My Store')
    kdb_driver.screen_shot()

    # TODO: get, verify prompt text and accept
    # execute js to show prompt alert
    kdb_driver.execute_script("document.location = prompt('Where the page you want to navigate?', "
                               "'http://automationpractice.com/index.php?controller=authentication&back=my-account')")
    # get text in prompt alert
    text_prompt = kdb_driver.alert.get_text()
    # verify prompt alert text
    kdb_driver.alert.verify_text_alert(text_prompt)
    kdb_driver.alert.verify_text_alert('truc_nguyen', reverse=True, timeout=0)
    # accept prompt alert
    kdb_driver.alert.accept()
    # verify Sign-in is displayed
    kdb_driver.verify_title('Login - My Store')
    kdb_driver.screen_shot()

    # TODO: send text and dismiss prompt
    # execute js to show prompt alert
    kdb_driver.execute_script("document.location = prompt('Where the page you want to navigate?', "
                               "'http://automationpractice.com/index.php?controller=authentication&back=my-account')")
    # send_keys to prompt alert
    kdb_driver.alert.send_keys('http://automationpractice.com/index.php')
    # accept prompt alert
    kdb_driver.alert.accept()
    # verify Home page is displayed
    kdb_driver.verify_title('My Store')
    kdb_driver.screen_shot()

    # TODO: send text and dismiss prompt
    # execute js to show prompt alert
    kdb_driver.execute_script("document.location = prompt('Where the page you want to navigate?', "
                               "'http://automationpractice.com/index.php?controller=authentication&back=my-account')")
    # send_keys to alert
    kdb_driver.alert.send_keys('http://automationpractice.com/index.php')
    # dismiss prompt alert
    kdb_driver.alert.dismiss()
    # verify Error page is displayed
    kdb_driver.verify_url_contains('automationpractice.com/null')
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
