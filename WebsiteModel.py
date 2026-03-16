import datetime
from bs4 import BeautifulSoup
from seleniumbase import Driver
from WebDriver import Web_Driver_Service
import copy

class Website:

    # def __init__(self, url, soup):
    #     self.id = None
    #     self.url = url
    #     self.soup = soup
    #     self.internal_links = self.find_internal_links(soup) # Each time we will only newest links   set(newstlinks) - set(oldlinks)
    #     self.last_checked = datetime.datetime.now()

    def __init__(self, url):
        self.url = url
        self.soup = None



    # create a file that contains the website's links and will be checked in along with it's future state
    # to identify links that are permanent in the website
    # ATTENTION: REMOVE ALL EXTERNAL LINKS

    def createSoup(self, web_driver: Web_Driver_Service):

        # # Get Html file
        # html = self.driver.page_source
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

        # for a in soup.find_all('a', href=True):
        #     print("Found the URL:", a['href'])

        # Return soup object
        return soup




class MainWebsite(Website):


    def __init__(self, url):
        self.id = None
        super().__init__(url)
        # self.internal_links_history = self.__find_internal_links_history() # Each time we will only newest links   set(newstlinks) - set(oldlinks)
        self.internal_links_history: set[str] = None
        self.links_to_check = None
        self.last_post_date: datetime.datetime
        self.last_post_date =  None



    # create a file that contains the website's links and will be checked in along with it's future state
    # to identify links that are permanent in the website
    # ATTENTION: REMOVE ALL EXTERNAL LINKS


    # TODO: Instead of using list I must change functionality to using sets
    def find_links_to_check(self, web_driver: Web_Driver_Service) -> list[str]:
        self.soup = self.createSoup(web_driver= web_driver)
        link_list = []
        # Iterate through website href links
        for href in self.soup.find_all('a', href=True):
            # Find all internal links
            if ("https://" not in href['href'] and "http://" not in href['href']) and href['href'] != "#" and href['href'] != "/"   and "javascript:" not in  href['href']  and "tel:" not in href['href']:
                link_list.append(href['href'])
            # Remove links that have already been checked
            if  self.internal_links_history is not None: # When the Website object is first constructed we store all internal links
                link_list = list(set(link_list) - self.internal_links_history)
        self.__find_internal_links_history()
        self.links_to_check = link_list
        return link_list
    

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
        data["url"] = self.url
        if self.last_post_date is not None:
            data["last_post_date"] = self.last_post_date.isoformat()      
        if self.links_to_check is not None:    
            data["links_to_check"] = self.links_to_check
        return data
    


class InternalWebsite(Website):

    def __init__(self, url: str, main_website: MainWebsite, web_driver : Web_Driver_Service):
        super().__init__(url)
        self.soup = self.createSoup(web_driver=web_driver)
        self.main_website: MainWebsite = main_website



