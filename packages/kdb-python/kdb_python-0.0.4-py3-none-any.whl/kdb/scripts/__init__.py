from selenium.common.exceptions import InvalidArgumentException

from kdb.common.profiles import Profiles
from kdb.common.utils import WebDriverUtil
from kdb.webdriver import kdb_driver


class BaseAPI:
    def __init__(self, profile: Profiles):
        self._profile = profile
        self._host = profile.get('host')
        self._request_data = {}
        self._headers = {'content-type': 'application/json'}
        self._response = None
        self._response_keys_success = None
        self._response_keys_default = None

    def _execute(self, data: dict, headers: dict = None, override_profile_data: dict = None, **kwargs):
        if override_profile_data is not None:
            self._request_data.update(override_profile_data)
        if data is not None:
            self._request_data.update(data)
        if headers is not None:
            self._headers.update(headers)
        self._response = kdb_driver.requests.post(self._host, json=self._request_data,
                                                  headers=self._headers, **kwargs)
        # response = self._response.json()
        # if '00' == response.get('code'):
        #     self.verify_response_success_keys()
        # else:
        #     self.verify_response_keys()
        self.verify_response_keys()
        return self._response

    def verify_response(self, json_path_expressions, value_expected):
        return kdb_driver.json_path.verify_value(self._response.text, json_path_expressions, value_expected)

    def verify_response_keys(self, keys: set = None, expressions=None):
        if self._response_keys_default is None or type(self._response_keys_default) != set:
            raise InvalidArgumentException(f"API's response_keys_default is invalid. {self._response_keys_default}")
        if keys is not None:
            self._response_keys_default |= keys
        if expressions is None:
            kdb_driver.json_path.verify_keys(self._response.json(), self._response_keys_default)
        else:
            data = kdb_driver.json_path.get(self._response.json(), expressions, log=False)
            kdb_driver.json_path.verify_keys(data, self._response_keys_default)

    def verify_response_success_keys(self, keys: set = None, expressions=None):
        if self._response_keys_success is None or type(self._response_keys_success) != set:
            raise InvalidArgumentException(f"API's response_keys_success is invalid. {self._response_keys_success}")
        self._response_keys_success |= self._response_keys_default
        if keys is not None:
            self._response_keys_success |= keys
        if expressions is None:
            kdb_driver.json_path.verify_keys(self._response.json(), self._response_keys_success)
        else:
            data = kdb_driver.json_path.get(self._response.json(), expressions, log=False)
            kdb_driver.json_path.verify_keys(data, self._response_keys_success)

    def get_response_json(self):
        return self._response.json()

    def get_request_json(self):
        return self._request_data

    def get_request_param(self, key: str):
        return self._request_data[key]

    def store_response_to_temp_file(self):
        pass


class BasePageObject:

    def __init__(self):
        # page url
        self._page_url = None
        # page title
        self._page_title = None

    def load_page(self):
        """
        Loads the page in the current browser session.
        """
        kdb_driver.open_url(self._page_url)

    def verify_title(self):
        """
        Verifying the title of page
        """
        kdb_driver.verify_title(self._page_title)

    def verify_url(self):
        """
        Verifying the URL of page
        """
        kdb_driver.verify_url_contains(self._page_url, exactly=True)


class MobileAppPageObject:

    def __init__(self):
        assert kdb_driver._driver
        self._activity = None
        self._is_android = WebDriverUtil.is_android_app(kdb_driver._driver)

    def wait_page_loaded(self):
        """
        Waiting for the activity is loaded
        """
        if self._is_android:
            kdb_driver.verify_activity(self._activity)
        else:  # todo ios
            pass
