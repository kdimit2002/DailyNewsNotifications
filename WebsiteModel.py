import datetime
from bs4 import BeautifulSoup
from seleniumbase import Driver
from WebDriver import Web_Driver_Service
import copy

class Website:

    def __init__(self, url):
        self.url = url
        self.soup = None

    def createSoup(self, web_driver: Web_Driver_Service):

        # Get Html file
        html = web_driver.get_html(url = self.url)



        soup = BeautifulSoup(html, features="html.parser")
        
        # make the html look good
        soup.prettify()

        # remove script tags
        for s in soup.select('script'):
            s.extract()

        # remove meta tags 
        for s in soup.select('meta'):
            s.extract()

        # Return soup object
        return soup




class MainWebsite(Website):


    def __init__(self, url):
        self.id = None
        super().__init__(url)
        self.internal_links_history = None
        self.links_to_check = None
        self.last_post_date: datetime.datetime = None


    # TODO: Instead of using list I must change functionality to using sets
    def find_links_to_check(self, web_driver: Web_Driver_Service) -> set[str]:

        # Fetches html file
        self.soup = self.createSoup(web_driver = web_driver)

        # List that will contain all internal site links
        links_set = set()

        # Iterate through website href links
        for href in self.soup.find_all('a', href=True):
            # Find all internal links
            if ("https://" not in href['href'] and "http://" not in href['href']) and href['href'] != "#" and href['href'] != "/"   and "javascript:" not in  href['href']  and "tel:" not in href['href']:
                links_set.add(href['href'])

            # Remove links that have already been checked
            if  self.internal_links_history is not None: # When the Website object is first constructed we store all internal links
                links_set = links_set - self.internal_links_history

        self.__find_internal_links_history()
        self.links_to_check = links_set
        return links_set
    

    # Private method to avoid mistakes in usage
    def __find_internal_links_history(self):
        # Iterate through website href links
        if self.internal_links_history is None:
            self.internal_links_history = set()
        for href in self.soup.find_all('a', href=True):
            # Find all internal links
            if ("https://" not in href['href'] and "http://" not in href['href']) and href['href'] != "#" and href['href'] != "/"   and "javascript:" not in  href['href']  and "tel:" not in href['href']:
                self.internal_links_history.add(href['href'])
    

    # Serialize object to json
    def to_json(self):
        data = {}
        if id is not None:
            data["id"] = self.id
        data["url"] = self.url
        if self.last_post_date is not None:
            data["last_post_date"] = self.last_post_date.isoformat()      
        if self.internal_links_history is not None:    
            data["links_to_check"] = self.internal_links_history
        breakpoint()
        return data
    

    @classmethod
    def to_obj(cls, data: dict) -> "MainWebsite":
        """
        Create a MainWebsite object from Redis JSON.
        """
        website = cls(data["url"])

        if "id" in data:
            website.id = data["id"]

        if "internal_links_history" in data and data["internal_links_history"] is not None:
            website.internal_links_history = set(data["internal_links_history"])

        if "last_post_date" in data and data["last_post_date"] is not None:
            website.last_post_date = datetime.datetime.fromisoformat(data["last_post_date"])

        return website


class InternalWebsite(Website):

    def __init__(self, url: str, main_website: MainWebsite, web_driver : Web_Driver_Service):
        super().__init__(url)
        self.soup = self.createSoup(web_driver=web_driver)
        self.main_website: MainWebsite = main_website
        # if main_website.last_post_date is not None:
        #     print(self.url)




