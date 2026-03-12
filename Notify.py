from bs4 import BeautifulSoup
import main
import bs4
import re
import re
import dateparser
from dateparser.search import search_dates
import datetime


EN_MINUTES_BEFORE = re.compile(
    r"\b\d+\s*(?:minute|minutes|min|mins)\s+ago\b|\b\d+\s*m\s+ago\b",
    re.IGNORECASE
)

GR_MINUTES_BEFORE = re.compile(
    r"\bπριν(?:\s+από|\s+απο)?\s+\d+\s+λεπ(?:τό|το|τά|τα)\b",
    re.IGNORECASE
)

def contains_exact_minutes_before(text):
    return any(p.search(text) for p in EN_MINUTES_BEFORE + GR_MINUTES_BEFORE)

# Change date syntax from dd.mm.yy to dd/mm/yy so that the parser can find it
def changeDateSyntax(text: str) -> str:
    pattern = r'\b\d{2}\.\d{2}\.(?:\d{2}|\d{4})\b' # changes both yy and yyyy date formats
    return re.sub(pattern, lambda m: m.group().replace('.', '/'), text)


def isPostDateTime(dt: datetime.datetime):
    now = datetime.datetime.now()
    return not (dt.hour == now.hour and dt.minute == now.minute) # or ("00" in dt.hour and "00" in dt.hour and "00" in dt.hour)

# Check if there is a new Post by checking dates of the page
def findRecentPostDate(text):
    text = changeDateSyntax(text=text)
    dates= {}
    dateTimes = search_dates(text, settings= {'SKIP_TOKENS': ['|']})
    absoluteDateTime: datetime.datetime
    if(dateTimes is None):
        return None
    for dateAndTime in dateTimes:
        for d in dateAndTime:
            if isinstance(d, str):
                textPhrase = d
                continue

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



            absoluteDateTime = d
            
            # if absoluteDateTime.strftime("%H") == 
            if isPostDateTime(absoluteDateTime) and (is_absolute_datetime(textPhrase) or contains_exact_minutes_before(textPhrase)) :
            # if "00" not in absoluteDateTime.strftime("%H"):
            #     breakpoint()
                dates[textPhrase] = absoluteDateTime
    return dates
            


def findImportandKeywords(soup: BeautifulSoup):        
    # Search by text with the help of lambda function
    soup_text = ""
    print(soup.text +"\n")
    # we will search the tag with in which text is same as given text
    for s in soup.strings:
        text: bs4.element.NavigableString = s

        # Add a space before each start of a new text bettween elements 
        soup_text = soup_text + " " + text

    
    print(soup_text)
    print(findRecentPostDate(soup_text))
    



