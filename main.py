import os
from bs4 import BeautifulSoup
import redis
import requests
import datetime
# Importing libraries
import time
import hashlib
from urllib.request import urlopen, Request
from redis.retry import Retry
from redis.exceptions import (TimeoutError, ConnectionError)
from redis.backoff import ExponentialBackoff
import WebsiteService
from seleniumbase import Driver
import WebsiteRepository
from WebsiteModel import MainWebsite, InternalWebsite
from WebDriver import Web_Driver_Service

# Note: better to have a func waiting an api response when a url is added


# await,celery etc..

def inputUrls() :
    # redisConnection = redis.Redis().from_pool(WebsiteRepository.redis_pool)
    url = input("Enter the website url: ")

    while url != "stop":           
        
        WebsiteRepository.redis_client.sadd("Websites", url)
        
        url = input("Enter the website url: ")


    # Close connection    
    # redisConnection.close()



# Cleans css style elements in tags
def CleanSoup(content):
    for tags in content.find_all(): 
        for val in list(tags.attrs):
            del tags.attrs[val]
    return content


# def createSoup(url):
# #     """Returns true if the webpage was changed, otherwise false."""
# #     headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
# #     'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
# #     response = requests.get(url, headers=headers)

#     # 1. Μπαίνεις στο site "σαν άνθρωπος"
#     driver = Driver(uc=True) 
#     driver.get(url)

#     # 2. Παίρνεις το HTML αφού έχει φορτώσει η σελίδα
#     html = driver.page_source
#         # processed_response_html = process_html(response.text)

#     soup = BeautifulSoup(html, features="html.parser")
    
#     # make the html look good
#     soup.prettify()

#     # remove script tags
#     for s in soup.select('script'):
#         s.extract()

#     # remove meta tags 
#     for s in soup.select('meta'):
#         s.extract()

#     for a in soup.find_all('a', href=True):
#         print("Found the URL:", a['href'])

#     driver.quit()
#     # Return soup object
#     return soup



def getUrls():
    # redisConnection = redis.Redis().from_pool(WebsiteRepository.redisPool)
    urls = WebsiteRepository.redis_client.smembers("Websites")
    # redisConnection.close()
    return urls




     
def main():
    inputUrls()
    urls = getUrls()
    for url in urls:
        print(url)
    
    website_list = []
    counter = 0
    for url in urls: # Must read each time from 
        counter+=1
        # s = requests.Session()
        # s.cookies.update({'__hs_opt_out': 'no'})
        # s.get(url)  # Automatically uses the session cookies
        # soup = createSoup(url)

        # Todo If website already exists get the newest links only
        if not WebsiteRepository.exists_by_url(url) :
            # website: Website = Website(url = url,soup = soup)
            website: MainWebsite = MainWebsite(url = url)
            WebsiteRepository.save(website.to_json(), website)
            website_list.append(website)
        else:
            pass

    web_driver = Web_Driver_Service()
    while True:
        time.sleep(2)
        for website in website_list:
            # website.createSoup()
            internal_urls: list[str] = website.find_links_to_check(web_driver)

            del website.soup
            website_posted_dates: list[datetime.datetime] = []

            for url in internal_urls:
               url = website.url + url[1:]
               internal_website = InternalWebsite(url=url, main_website=website, web_driver=web_driver)

               posted_time = WebsiteService.find_internal_url_posted_datetime(internal_website) # CHECK THIS
               if posted_time is not None:
                    website_posted_dates.append(posted_time)

               # Clean in-website internal site object from memory  
               del internal_website

            if website_posted_dates is None or len(website_posted_dates) == 0:
                # send email
                continue
            
            latest_before_now = max(d for d in website_posted_dates if d < datetime.datetime.now()) # Todo: must check also timezones that are diferent from my country

            if website.last_post_date is not None and website.last_post_date <= latest_before_now :
                 # Todo: notify code
                print(f"notify for website: {website.url} time: {website.last_post_date:%H:%M}\n{website_posted_dates}")
            website.last_post_date = latest_before_now

            
        # ProccessWebsitesLinks.createFirstFile(soup)

        


        # ProccessWebsitesLinks.removeStaticLinks




def main1():
    inputUrls()


if __name__ == "__main__":
    main()