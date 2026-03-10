
import os
from bs4 import BeautifulSoup
import requests
import datetime
# Importing libraries
import time
import hashlib
from urllib.request import urlopen, Request
import main
import redis

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

# create a file that contains the website's links and will be checked in along with it's future state
# to identify links that are permanent in the website
# ATTENTION: REMOVE ALL EXTERNAL LINKS
@staticmethod
def createFirstFile(soup):
    checkOn = datetime.datetime.now() + datetime.timedelta(minutes=3)
    redisConnection = redis.Redis().from_pool(main.redisPool)
    linkList =[]
    for a in soup.find_all('a', href=True):
        if "https://" not in a['href'] and "http://" not in a['href'] :
            print(a['href'])
            linkList.append(a['href'])
        # redisConnection.json().set("websiteLink",'$',a['href'])
        # redisConnection.json().set("Website_Links",'$',a['href'])

    diction = {}
    diction["links"] = linkList
    redisConnection.json().set("Website_Internal_Links",'$',diction)
    diction["checkOn"] = json_serial(checkOn)
    redisConnection.json().set("First_Website_Internal_Links",'$',diction)
    redisConnection.close()


# @staticmethod
# def createFirstFile(soup, firstFilename):
#     try:
#         checkOn = datetime.datetime.now() + datetime.timedelta(minutes=3)''
#         f = open(firstFilename, 'w+')
#         f.write(f"Check on: {checkOn}\n")
#         for a in soup.find_all('a', href=True):
#             f.write(f"Found the URL: {a['href']}\n")
#     except IOError as e:
#         # Must inform with email 
#         print("Oops! There is an error when trying to write/open the file: ",firstFilename,e.errno,e)
#     finally:
#         f.close()
        





# Write down the links of the html page for the first time
@staticmethod
def findLinksToCheck(soup, filename):
    # soup = BeautifulSoup(string, features="html.parser")
        
    # # make the html look good
    # soup.prettify()

    # # remove script tags
    # for s in soup.select('script'):
    #     s.extract()

    redisConnection = redis.Redis().from_pool(main.redisPool)
    
    createFirstFile(soup)


    # # create a file that contains websites links and will be checked in along with it's future state of links
    # # to identify links that are permanent in the website
    # if not os.path.exists(filename):
    #     try:
    #         f = open(filename, 'w+')
    #         f.write(f"Check on: {checkOn}\n")
    #         for a in soup.find_all('a', href=True):
    #             f.write(f"Found the URL: {a['href']}\n")
    #     except IOError as e:
    #         # Must inform with email 
    #         print("Oops! There is an error when trying to write/open to the file: ",filename,e.errno,e)
    #     finally:
    #         f.close
    
    # Create the file that stores all the href links of the site 

    try:
        if not os.path.exists(filename):
            open(filename, 'w+').close()

        with open(filename, 'w') as f:
            for a in soup.find_all('a', href=True):
                f.write(f"Found the URL: {a['href']}\n")

    except IOError as e:
        # Must inform with email 
        print(f"Oops! There was an error when trying to write/open the file: ", filename,e.errno,e)
    finally:
        f.close()



# Inspect lines that has before hours, dates and more



###########  Todo: this w


# Function is going to be called after 3 days to remove static links 
# in order to minimize the set of links to check
@staticmethod
def removeStaticLinks(filename):
    firstFilename = "first_" + filename
    links = []
    dynamicLinks = []
    found = False

    firstLine = True

    try:
        # File must exist
        with open(filename, 'r') as fr:
            last_urls = fr.readlines()
            with open(firstFilename, 'r') as first_fr:
                first_urls = fr.readlines()
                for line in last_urls:
                    if firstLine:
                        firstLine = False
                        continue
                    # present at the end of each line
                    for link in links:
                        if link in line:
                            found = True
                    if not found:
                        dynamicLinks.append(line)
                    found = False
    except IOError as e:
        # Must inform with email 
        print("Oops! There is an error when trying to read either: ",filename,firstFilename,e.errno,e)

    try:
        with open('links.txt', 'w') as f:
            for dynamicLink in dynamicLinks:
                f.write(f"{dynamicLink}\n")
    except IOError as e:
        # Must inform with email 
        print("Oops! There is an error when trying to write to the file links.txt, Line 154",e.errno,e)

    

