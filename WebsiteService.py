from WebsiteModel import Website

from bs4 import BeautifulSoup
import main
import bs4
import re
import re
import dateparser
from dateparser.search import search_dates
from datetime import datetime,timedelta
from WebsiteModel import InternalWebsite

EN_MINUTES_BEFORE = re.compile(
    r"\b\d+\s*(?:minute|minutes|min|mins)\s+ago\b|\b\d+\s*m\s+ago\b",
    re.IGNORECASE
)

GR_MINUTES_BEFORE = re.compile(
    r"\bπριν(?:\s+από|\s+απο)?\s+\d+\s+λεπ(?:τό|το|τά|τα)\b",
    re.IGNORECASE
)

# To detect relative datetime used in news posts
def contains_exact_minutes_before(text: str) -> bool:
    is_english_relative_time = EN_MINUTES_BEFORE.search(text) is not None
    is_greek_relative_time = GR_MINUTES_BEFORE.search(text) is not None
    return is_english_relative_time or is_greek_relative_time

# Change date syntax from dd.mm.yy to dd/mm/yy so that the parser can find it
def changeDateSyntax(text: str) -> str:
    pattern = r'\b\d{2}\.\d{2}\.(?:\d{2}|\d{4})\b' # changes both yy and yyyy date formats
    return re.sub(pattern, lambda m: m.group().replace('.', '/'), text)

# Check if there is a new Post by checking dates of the page
def findRecentPostDate(internal_website: InternalWebsite):
    text = internal_website.soup

    #  Replace date characters that dateparser cannot read
    text = changeDateSyntax(text=text)

    #  Get dates of the html file
    html_dates = search_dates(text, settings= {'SKIP_TOKENS': ['|']})
    html_absolute_date: datetime.datetime

    # Return if no dates where found
    if(html_dates is None or len(html_dates) == 0):
        return None
    
    absolute_post_dates = []

    # Iterate through dates found
    for date in html_dates:

        # Iterate through the tuple date where it contains a date text value and a datetime value
        for d in date:
            # If it's text date value then save it and continue
            if isinstance(d, str):
                date_text = d
                continue

            # Create a lambda func that will check if text date value is an absolute value with date and time
            is_absolute_datetime = lambda text: (
                dateparser.parse(
                    text,
                    languages=["en", "el"],
                    settings={
                        "PARSERS": ["absolute-time"],
                        "STRICT_PARSING": True
                    }
                ) is not None
                and re.search(
                    r"\b\d{1,2}[:.]\d{2}(?:[:.]\d{2})?\b|\b\d{1,2}\s?(am|pm|πμ|μμ)\b", 
                    text,
                    re.IGNORECASE
                ) is not None
            )

            # Get datetime value
            html_absolute_date = d
                
            # Will save the dates found in the html

            # Find if it's a post datetime value. 
            if is_absolute_datetime(date_text) or contains_exact_minutes_before(date_text) :
                absolute_post_dates.append(html_absolute_date)

    latest_before_now: datetime.datetime = None
    if absolute_post_dates is not None and len(absolute_post_dates) != 0:
        try:
            latest_before_now = max(d for d in absolute_post_dates if d <= datetime.now() + timedelta(minutes = 1)) # Todo: must check also timezones that are diferent from my country
        except ValueError:
            latest_before_now = None
    
                # if internal_website.main_website.last_post_date.

    return latest_before_now
            


def find_internal_url_posted_datetime(internal_website: InternalWebsite):        

    soup_text = ""
    soup = internal_website.soup
    # print(soup.text +"\n")
    # Every time variable s is the text bettween 2 html tags 
    soup_text_list = []

    for s in soup.strings:
        text: bs4.element.NavigableString = s

        # Adding a space so the strings don't run together.
        soup_text_list.append(text)
    
    internal_website.soup = " ".join(soup_text_list)

    
    # print(internal_website.soup )
    url_most_recent_date = findRecentPostDate(internal_website)

    print("FOUND POSTED TIME FOR URL: " + internal_website.url + " DATETIME: " + str(url_most_recent_date))
    # print(url_most_recent_date)
    return url_most_recent_date



