from dataclasses import dataclass, field
from selenium.webdriver.remote.webdriver import WebDriver
from seleniumbase import Driver

@dataclass
class Web_Driver:
    
    web_driver: WebDriver = field(default_factory=lambda: Driver(uc=True, browser="chrome"))
    opened_pages_count: int = 0

    
    def get_html(self,url: str):
        # Opens website humanly
        if self.opened_pages_count >= 30:
            self.web_driver.quit()
            self.web_driver = Driver(uc=True, browser="chrome")
            self.opened_pages_count = 0
        self.web_driver.get(url)
        self.opened_pages_count+=1

        # Get HTML
        html = self.web_driver.page_source
        return html
    
