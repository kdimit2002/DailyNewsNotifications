import os
import ProccessWebsitesLinks
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
import Notify
from seleniumbase import Driver
import WebsiteRepository
from WebsiteModel import Website

# await,celery etc..

def inputUrls() :
    redisConnection = redis.Redis().from_pool(WebsiteRepository.redisPool)
    url = input("Enter the website url: ")

    while url != "stop":           
        
        redisConnection.sadd("Websites", url)
        
        url = input("Enter the website url: ")


    # Close connection    
    redisConnection.close()



# Cleans css style elements in tags
def CleanSoup(content):
    for tags in content.find_all(): 
        for val in list(tags.attrs):
            del tags.attrs[val]
    return content


def createSoup(url):
#     """Returns true if the webpage was changed, otherwise false."""
#     headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
#     'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
#     response = requests.get(url, headers=headers)

    # 1. Μπαίνεις στο site "σαν άνθρωπος"
    driver = Driver(uc=True) 
    driver.get(url)

    # 2. Παίρνεις το HTML αφού έχει φορτώσει η σελίδα
    html = driver.page_source
        # processed_response_html = process_html(response.text)

    soup = BeautifulSoup(html, features="html.parser")
    
    # make the html look good
    soup.prettify()

    # remove script tags
    for s in soup.select('script'):
        s.extract()

    # remove meta tags 
    for s in soup.select('meta'):
        s.extract()

    for a in soup.find_all('a', href=True):
        print("Found the URL:", a['href'])

    driver.quit()
    # Return soup object
    return soup



def getUrls():
    redisConnection = redis.Redis().from_pool(WebsiteRepository.redisPool)
    urls = redisConnection.smembers("Websites")
    redisConnection.close()
    return urls




     
def main():
    inputUrls()
    urls = getUrls()
    print("Checking websites:")
    for url in urls:
        print(url)
    
    counter = 0
    for url in urls:
        counter+=1
        # s = requests.Session()
        # s.cookies.update({'__hs_opt_out': 'no'})
        # s.get(url)  # Automatically uses the session cookies
        soup = createSoup(url)

        website: Website = Website(url = url,soup = soup)
        WebsiteRepository.save(website.to_json(), url) # should replace this with name given by the user
        # ProccessWebsitesLinks.createFirstFile(soup)
        d = {}
        Notify.findImportandKeywords(soup)
        


        # ProccessWebsitesLinks.removeStaticLinks




def main1():
    inputUrls()


if __name__ == "__main__":
    main()