from dataclasses import dataclass, field
from selenium.webdriver.remote.webdriver import WebDriver
from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException


@dataclass
class Web_Driver_Service:
    web_driver: WebDriver = field(init=False)
    opened_pages_count: int = 0

    def __post_init__(self):
        self.web_driver = self.__create_web_driver()

    def get_html(self, url: str):
        counter = 0
        had_exception = False

        while True:
            if self.opened_pages_count >= 50 or had_exception:
                try:
                    self.web_driver.quit()
                except Exception:
                    pass
                self.web_driver = self.__create_web_driver()
                had_exception = False

            try:
                # clear browser cache before each request
                self.web_driver.execute_cdp_cmd("Network.clearBrowserCache", {})

                self.web_driver.get(url)

                WebDriverWait(self.web_driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )

                self.opened_pages_count += 1
                return self.web_driver.page_source

            except WebDriverException:
                counter += 1
                had_exception = True

                if counter == 3:
                    try:
                        self.web_driver.quit()
                    except Exception:
                        pass
                    raise WebDriverException(
                        "Something is wrong: driver cannot connect to browser"
                    )

    def __create_web_driver(self):
        driver = Driver(
            uc=True,
            browser="chrome",
            chromium_arg="--disable-application-cache,--disk-cache-size=0,--media-cache-size=0,--incognito",
        )

        driver.set_page_load_timeout(30)

        # Enable Network domain first
        driver.execute_cdp_cmd("Network.enable", {})

        # Disable normal browser cache
        driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})

        # Bypass service worker cache too
        driver.execute_cdp_cmd("Network.setBypassServiceWorker", {"bypass": True})

        self.opened_pages_count = 0
        return driver