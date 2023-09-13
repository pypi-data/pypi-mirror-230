ANDROID = {
    'android_emulator-5554': {
        'avd': 'Pixel_4_API_30',
        'udid': '',
        'platformVersion': '11.0',
        'deviceName': 'Pixel 4 API 30',
        'appiumPort': 8010,
        'bootstrapPort': 8011,
        'chromeDriverPort': 8012,
        'mjpegServerPort': 8013,
        'hubURL': 'http://localhost:4723'
    },
    'android_emulator-5555': {
        'avd': 'Pixel_3a_API_34_extension_level_7_x86_64',
        'udid': '',
        'platformVersion': '11.0',
        'deviceName': 'Nexus 5X API 30',
        'appiumPort': 8010,
        'bootstrapPort': 8011,
        'chromeDriverPort': 8012,
        'mjpegServerPort': 8013,
        'hubURL': 'http://localhost:4723'
    },
    # 'android_htc_one': {
    #     'udid': 'HT364W908169',
    #     'platformVersion': '5.0',
    #     'deviceName': 'HTC One',
    #     'appiumPort': 8020,
    #     'bootstrapPort': 8021,
    #     'chromeDriverPort': 8022,
    #     'mjpegServerPort': 8023,
    #     'hubURL': 'http://192.168.1.104:8020'
    # },
}

SIMULATOR = {
    'simulator_iphone_x': {
        'udid': '0760F589-5F15-4B62-A49B-431C3924AAD4',
        'platformVersion': '12.0',
        'deviceName': 'iPhone X',
        'appiumPort': 9010,
        'webkitDebugProxyPort': 9011,
        'wdaLocalPort': 9012,
        'hubURL': 'http://192.168.1.104:9010',
        'tmpDir': '/Users/user/Tmp/appium_iOS_9010'
    },
    'simulator_iphone_xs': {
        'udid': '389E5726-1ABC-479A-B9E8-6A6C5F185200',
        'platformVersion': '12.0',
        'deviceName': 'iPhone XS',
        'appiumPort': 9020,
        'webkitDebugProxyPort': 9021,
        'wdaLocalPort': 9022,
        'hubURL': 'http://192.168.1.104:9020',
        'tmpDir': '/Users/user/Tmp/appium_iOS_9020'
    },
}

IOS = SIMULATOR
