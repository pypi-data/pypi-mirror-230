from kdb import report
from kdb.common.utils import TimeUtil
from kdb.webdriver import kdb_driver


def login_test():
    report.add_comment("Open chrome browser & login")
    # start browser
    kdb_driver.start_browser('chrome')
    kdb_driver.open_url('https://vietbank.vnpaytest.vn/Account/Login')
    kdb_driver.screen_shot()
    kdb_driver.update_text('id=login-username', 'trucnt')
    kdb_driver.update_text("id=login-password", 'Vnpay@123')
    kdb_driver.click('id=btn-login')
    report.add_comment("Verifying the home page after login successfully")
    kdb_driver.verify_title('Home Page - VIETBANK')
    kdb_driver.verify_text_on_page('VIETBANK - CN HO CHI MINH')
    kdb_driver.screen_shot()


def update_configuration_test():
    report.add_comment("Update a configuration")
    # click config menu
    kdb_driver.click('xpath=//li[@id="64"]/a')
    # verify the configuration page
    kdb_driver.verify_title('Configuration MB Manager - VIETBANK')
    kdb_driver.screen_shot()
    kdb_driver.select('xpath=//select[@ng-model="PerPageItems"]', '50')
    kdb_driver.screen_shot()
    kdb_driver.update_text('id=code', 'AUTOMATION-TEST')
    kdb_driver.click('xpath=//a[@ng-click="Search()"]')
    kdb_driver.screen_shot()
    kdb_driver.click('xpath=//a[@ng-href="/Configuration/Edit/AUTOMATION-TEST?f=64&c=64"]')
    kdb_driver.set_global_var('autotest', kdb_driver.random.random_text(5))
    kdb_driver.update_text('id=value', kdb_driver.get_global_var('autotest'))
    kdb_driver.screen_shot()
    kdb_driver.click('id=create')
    kdb_driver.alert.accept()
    kdb_driver.verify_title('Configuration MB Manager - VIETBANK')
    kdb_driver.screen_shot()
    # search AUTOMATION-TEST config name
    report.add_comment("Verifying update configuration successfully")
    kdb_driver.update_text('id=code', 'AUTOMATION-TEST')
    kdb_driver.click('xpath=//a[@ng-click="Search()"]')
    kdb_driver.verify_text_on_page(kdb_driver.get_global_var('autotest'))
    kdb_driver.screen_shot(extra_time=2)
