import datetime
from bs4 import BeautifulSoup
from dataclasses import field, dataclass, asdict

class Website:

    def __init__(self, url, soup):
        self.id = None
        self.url = url
        self.soup = soup
        self.internal_links = self.find_internal_links(soup)
        self.last_checked = datetime.datetime.now()
        self.static_link_removal_threshold = self.find_static_links_removal_threshold()


    # create a file that contains the website's links and will be checked in along with it's future state
    # to identify links that are permanent in the website
    # ATTENTION: REMOVE ALL EXTERNAL LINKS

    def find_internal_links(self):
        link_list =[]
        for href in self.soup.find_all('a', href=True):
            if "https://" not in href['href'] and "http://" not in href['href'] :
                print(href['href'])
                link_list.append(href['href'])
        return link_list


    def find_static_links_removal_threshold(self):
        return datetime.datetime.now() + datetime.timedelta(days=3)



    def to_json(self):
        data = asdict(self)
        data["soup"] = None
        data["last_checked"] = data["last_checked"].isoformat()
        data["static_link_removal_threshold"] = data["static_link_removal_threshold"].isoformat()
        return data