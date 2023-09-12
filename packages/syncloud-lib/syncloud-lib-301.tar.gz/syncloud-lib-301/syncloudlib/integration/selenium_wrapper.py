import time

from syncloudlib.integration.screenshots import screenshots
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions


class SeleniumWrapper:
    def __init__(self, driver, ui_mode, screenshot_dir, app_domain, timeout):
        self.app_domain = app_domain
        self.screenshot_dir = screenshot_dir
        self.ui_mode = ui_mode
        self.driver = driver
        self.wait_driver = WebDriverWait(self.driver, timeout)

    def find_by_xpath(self, xpath):
        return self.find_by(By.XPATH, xpath)

    def find_by_name(self, name):
        return self.find_by(By.NAME, name)

    def find_by_id(self, field_id):
        return self.find_by(By.ID, field_id)

    def find_by_css(self, css):
        return self.find_by(By.CSS_SELECTOR, css)

    def find_by(self, by, value):
        self.wait_or_screenshot(expected_conditions.visibility_of_element_located((by, value)))
        return self.driver.find_element(by, value)

    def invisible_by(self, by, value):
        self.wait_or_screenshot(expected_conditions.invisibility_of_element_located((by, value)))

    def click_by(self, by, value):
        self.wait_or_screenshot(expected_conditions.element_to_be_clickable((by, value)))
        self.driver.find_element(by, value).click()

    def exists_by(self, by, value, timeout=10):
        driver = WebDriverWait(self.driver, timeout)
        cond = expected_conditions.visibility_of_element_located((by, value))
        try:
            driver.until(cond)
            return True
        except Exception as _:
            self.screenshot('exception', False)
            return False

    def wait_or_screenshot(self, method, throw=True):
        try:
            self.wait_driver.until(method)
            return True
        except Exception as e:
            self.screenshot('exception', throw)
            if throw:
                raise e
            else:
                return False

    def screenshot(self, name, throw=True):
        retries = 5
        retry = 0
        while True:
            try:
                screenshots(self.driver, self.screenshot_dir, '{}-{}'.format(name, self.ui_mode))
                break
            except Exception as e:
                if retry >= retries:
                    if throw:
                        raise
                    else:
                        return
                retry += 1
                time.sleep(1)
                print('retrying screenshot {0}'.format(retry))

    def open_app(self, path=''):
        self.driver.get("https://{0}{1}".format(self.app_domain, path))
