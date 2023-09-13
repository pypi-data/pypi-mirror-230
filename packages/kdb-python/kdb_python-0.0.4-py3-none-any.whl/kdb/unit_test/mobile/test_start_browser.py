import kdb
from kdb import report
from kdb.common.utils import DeviceType
from kdb.webdriver import kdb_driver

# script to verify private mode
script_verify_private_mode = """
    function detectPrivateMode(cb) {
        var db,
        on = cb.bind(null, true),
        off = cb.bind(null, false)

        function tryls() {
            try {
                localStorage.length ? off() : (localStorage.x = 1, localStorage.removeItem("x"), off());
            } catch (e) {
                // Safari only enables cookie in private mode
                // if cookie is disabled then all client side storage is disabled
                // if all client side storage is disabled, then there is no point
                // in using private mode
                navigator.cookieEnabled ? on() : off();
            }
        }

        // Blink (chrome & opera)
        window.webkitRequestFileSystem ? webkitRequestFileSystem(0, 0, off, on)
        // FF
        : "MozAppearance" in document.documentElement.style ? (db = indexedDB.open("test"), db.onerror = on, db.onsuccess = off)
        // Safari
        : /constructor/i.test(window.HTMLElement) || window.safari ? tryls()
        // IE10+ & edge
        : !window.indexedDB && (window.PointerEvent || window.MSPointerEvent) ? on()
        // Rest
        : off()
    }
    detectPrivateMode(function (isPrivateMode) {
        var sTop = document.getElementById('search_query_top');
        if (sTop) {
            sTop.value = isPrivateMode;
        }
        var sG = document.getElementById('lst-ib');
        if (sG) {
            sG.value = isPrivateMode;
        }
    })
    """


def start_browser_test():
    report.add_comment("Start browser testing")

    # TODO start browser with default params
    report.add_comment(">>> Start browser with default parameters")
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('http://automationpractice.com/index.php')
    if DeviceType.is_android(kdb.BROWSER):  # android
        # verify Chrome started as default
        assert kdb_driver.execute_script(
            "return /android/i.test(navigator.userAgent || navigator.vendor || window.opera)") is True
    else:  # iOS or simulator
        # verify IE started as default
        assert kdb_driver.execute_script(
            'return /iPad|iPhone|iPod/.test(navigator.userAgent || navigator.vendor || window.opera) && !window.MSStream') is True
    kdb_driver.close_browser()

    # TODO start browser with browser name
    report.add_comment(">>> Start browser with a given name")
    # android
    if DeviceType.is_android(kdb.BROWSER):
        kdb_driver.start_browser('android')
        # load page for test
        kdb_driver.open_url('https://www.google.com/')
        # verify Chrome started as default
        assert kdb_driver.execute_script(
            "return /android/i.test(navigator.userAgent || navigator.vendor || window.opera)") is True
    # iOS or simulator
    else:
        kdb_driver.start_browser('ios')
        # load page for test
        kdb_driver.open_url('http://automationpractice.com/index.php')
        # verify Chrome started as default
        assert kdb_driver.execute_script(
            "return /iPad|iPhone|iPod/.test(navigator.userAgent || navigator.vendor || window.opera) && !window.MSStream") is True
    # close browser
    kdb_driver.close_browser()

    # TODO start browser with private_mode
    report.add_comment(">>> Private mode is NOT support in mobile")
