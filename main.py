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

redisPool = redis.ConnectionPool(host='localhost', port=6379, retry=Retry(ExponentialBackoff(cap=10, base=1), 25), retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError], health_check_interval=1, decode_responses=True)

# await,celery etc..

def inputUrls() :
    redisConnection = redis.Redis().from_pool(redisPool)
    url = input("Enter the website url: ")

    while url != "stop":           
        
        redisConnection.sadd("Websites", url)
        
        url = input("Enter the website url: ")


    # Close connection    
    redisConnection.close()



def printHtml():
    """Returns true if the webpage was changed, otherwise false."""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
    response = requests.get(URL_TO_MONITOR, headers=headers)

    # create the previous_content.txt if it doesn't exist
    if not os.path.exists("previous_content.txt"):
        open("previous_content.txt", 'w+').close()
    
    filehandle = open("previous_content.txt", 'r')
    previous_response_html = filehandle.read() 
    filehandle.close()

    findLinksToCheck(response.text)
    # findStaticLinks(response.text)
    
    # print(response.text)
    processed_response_html = process_html(response.text)
    # print(processed_response_html)
  



# Cleans css style elements in tags
def CleanSoup(content):
    for tags in content.find_all(): 
        for val in list(tags.attrs):
            del tags.attrs[val]
    return content


def createSoup(url):
    """Returns true if the webpage was changed, otherwise false."""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
    response = requests.get(url, headers=headers)

    # processed_response_html = process_html(response.text)

    soup = BeautifulSoup(response.text, features="html.parser")
    
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

    #  DONT USE THIS IF YOU WANT TO ITERATE AMONG HREF LINKS
    # CleanSoup(soup)

   
    # # create the previous_content.txt if it doesn't exist
    # if not os.path.exists("html.txt"):
    #     open("html.txt", 'w+').close()
    # try:
    #     with open('html.txt', 'w') as f:
    #         f.write(str(soup).replace('\r', ''))
    # except IOError as e:
    #     # Must inform with email 
    #     print("Oops! There is an error when trying to write to the file html.txt, Line 116",e.errno,e)

    # Return soup object
    return soup



def getUrls():
    redisConnection = redis.Redis().from_pool(redisPool)
    urls = redisConnection.smembers("Websites")
    redisConnection.close()
    return urls




     
def main():
    inputUrls()
    urls = getUrls()
    for url in urls:
        print(url)
    
    counter = 0
    for url in urls:
        print("URLSSS" + url)
        counter+=counter
        soup = createSoup(url)
        breakpoint()
        ProccessWebsitesLinks.createFirstFile(soup)

        # ProccessWebsitesLinks.removeStaticLinks




def main1():
    inputUrls()


if __name__ == "__main__":
    main()