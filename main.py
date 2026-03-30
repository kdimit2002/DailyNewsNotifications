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



debug = 0 

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

    for url in urls: # Must read each time from 
        
        # Todo If website already exists get the newest links only
        if not WebsiteRepository.exists_by_url(url) :
            # website: Website = Website(url = url,soup = soup)
            website: MainWebsite = MainWebsite(url = url)
            WebsiteRepository.save(website.to_json(), website)
        else:
            website: MainWebsite = WebsiteRepository.get_by_url(url=url)
        website_list.append(website)

    # Driver that recives data from browser for each website and url
    web_driver = Web_Driver_Service()
    while True:
        time.sleep(0.1)
        # Iterate over each website
        for website in website_list:

            # Find the internal urls for a website we are searching 
            internal_urls: set[str] = website.find_links_to_check(web_driver)

            # Make a list to store each internal url's datetime
            urls_posted_dates: list[datetime.datetime] = []

            # Iterate over each internal url of the website
            for url in internal_urls:
               print("new url!")
               url = "https://www.ant1live.com/"+ url[1:]
               internal_website = InternalWebsite(url=url, main_website=website, web_driver=web_driver) # Create an object that stores info for internal urls sites

               # Find posted time of internal site/url   
               posted_time = WebsiteService.find_internal_url_posted_datetime(internal_website) # CHECK THIS

               # If posted time was found for the url add it to the list    
               if posted_time is not None:
                    print(posted_time)
                    urls_posted_dates.append(posted_time)

               # Clean internal's website object from memory  
               del internal_website

            

            if urls_posted_dates is None or len(urls_posted_dates) == 0:
                # send email
                continue
            
            # Todo: Check whether to use <= from now or < or something else
            latest_before_now = max(d for d in urls_posted_dates if d < datetime.datetime.now()) # Todo: must check also timezones that are diferent from my country

            # Remove from links history those that hold datetime that is equal to now in order to check it again later
            website.internal_links_history = [d for d in urls_posted_dates if d != datetime.datetime.now()] 

            if website.last_post_date is not None and website.last_post_date < latest_before_now : 
                 # Todo: notify code
                print(f"notify for website: {website.url} time: {latest_before_now:%H:%M}\n{urls_posted_dates}")
            website.last_post_date = latest_before_now
    
        debug = 1





def main1():
    inputUrls()


if __name__ == "__main__":
    main()