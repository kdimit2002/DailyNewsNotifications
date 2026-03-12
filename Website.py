import datetime
from bs4 import BeautifulSoup
from dataclasses import field, dataclass, asdict

@dataclass
class Website:
    url: str = field(init=False)
    soup: BeautifulSoup = field(init=False)
    internal_links: list[str] = field(init=False)
    static_link_removal_threshold: datetime.datetime = field(init=False)

    def __init__(self, url, soup):
        self.url = url
        self.soup = soup
        self.internal_links = []
        self.static_link_removal_threshold = datetime.datetime() 
        self.internal_links = self.find_internal_links(soup)
        self.static_link_removal_threshold = self.find_static_links_removal_threshold()


# create a file that contains the website's links and will be checked in along with it's future state
# to identify links that are permanent in the website
# ATTENTION: REMOVE ALL EXTERNAL LINKS

def find_internal_links(self, soup):
    link_list =[]
    for href in soup.find_all('a', href=True):
        if href.startswith("http://", "https://", "mailto:", "tel:", "javascript:", "#") :
            print(href['href'])
            link_list.append(href['href'])
    return link_list


def find_static_links_removal_threshold(self):
    return datetime.datetime.now() + datetime.timedelta(days=3)



def to_json(self):
    data = asdict(self)
    data["soup"] = None
    data["static_link_removal_threshold"] = data["static_link_removal_threshold"].isoformat()
    return data