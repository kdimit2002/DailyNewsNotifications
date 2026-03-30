from dataclasses import dataclass, field
from selenium.webdriver.remote.webdriver import WebDriver
from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException


@dataclass
class Web_Driver_Service:
    
    web_driver: WebDriver = field(default_factory=lambda: Driver(uc=True, browser="chrome"))
    opened_pages_count: int = 0

    
    def get_html(self,url: str):
        # Opens website humanly
        if self.opened_pages_count >= 50:
            self.web_driver.quit()
            self.web_driver = self.__create_web_driver()
        try:
            self.web_driver.get(url)

            # Wait up to 10 seoconds until page is ready to be retrieved
            WebDriverWait(self.web_driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            self.opened_pages_count+=1

            # Get HTML
            html = self.web_driver.page_source
        except WebDriverException:
            breakpoint()

        return html
    

    def __create_web_driver(self):
        driver = Driver(uc=True, browser="chrome")
        # Raises timeout exception if initializing fails
        driver.set_page_load_timeout(30)
        self.opened_pages_count = 0
        return driver
    
