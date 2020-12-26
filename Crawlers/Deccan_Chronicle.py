## It is a crawler for a news website : Deccan Chronicle.

#%% Imports
""" Importing the Required Packages """
from requests_html import HTMLSession # extract the information from the website 
from bs4 import BeautifulSoup # pulling data out of HTML and XML files
from dateparser import parse # parse a date from the given string
from urllib.parse import urljoin #combining the components to a url string and convert a relative URL to an absolute url (base_url)
import pandas as pd # storing the data in dataframe

#%% Section Links

session = HTMLSession() # to initialize the GET requests

base_url = 'https://www.deccanchronicle.com/'

"""
As there are many sections on the website such as nation, world, technology, etc. Therefore, 
here we first find out all the sections in the news. 
"""
def get_section_links(retry = 3):
    r = session.get(base_url, timeout = 180) # storing the response for base_url
    soup = BeautifulSoup(r.content, 'lxml') #parsing the response using 'lxml' parser
    section_links = [urljoin(base_url,x.attrs['href']) for x in  soup.find('ul',{'class':'nav'}).find_all('a')] #combining the relative urls of every sections with base_url
    """ ignoring the urls as it shows the brief of all the news present in each section and 
    also some irrelevant urls
    """
    ignore_url = ['https://www.deccanchronicle.com/nation','https://www.deccanchronicle.com/world','https://www.deccanchronicle.com/just-in',
                  'https://www.deccanchronicle.com/south','https://www.deccanchronicle.com/entertainment',
                  'https://www.deccanchronicle.com/sports','https://www.deccanchronicle.com/technology',
                  'https://www.deccanchronicle.com/lifestyle','https://www.deccanchronicle.com/galleries',
                  'https://www.deccanchronicle.com/business','https://www.deccanchronicle.com/opinion',
                  'https://www.deccanchronicle.com/sunday-chronicle','https://www.deccanchronicle.com/play-games',
                  'https://www.deccanchronicle.com/daily-astroguide','https://www.deccanchronicle.com/videos']
    section_links = list(filter(lambda x: not x.startswith('https://www.deccanchronicle.com/tabloid/'),section_links))
    section_links = list(filter(lambda x: x not in ignore_url, section_links))
    return section_links

#%% Article Links

"""
Now after extracting the sections from the website we'll further continue to find out articles in 
each section. We find all the articles from respective sections. Article links here are found by 
checking the date. i.e. here we check the date first and according to it the article links are 
updated in the data from following pages in every section.
"""
def get_article_links(url, retry = 3):
    try:
        i = 1
        article_links = []
        while True:
            page_url = url + '?pg=' + str(i)  # as the next page in each section shows '?pg=' in common we'll paginate according to this page_url
            r = session.get(page_url, timeout=180) # storing the response for every page_url
            soup = BeautifulSoup(r.content, 'lxml')
            articles = soup.find('div',{'class':'storyList'}).find_all('div',{'class':'SunChNewListing'}) #finding all the articles present on each page
            i += 1 #increment the page_url
            last_pg = False
            print(page_url)
            
            """ for every article in articles we'll check the date and append the article_links
            """
            for article in articles:
                try:
                    date = parse(article.find('span',{'class':'SunChDt2'}).text) # find out the date
                    title = article.find('h3',{'class':'SunChroListH3'}).text.strip() # find out the title
                    link = urljoin(base_url,article.find('a').attrs['href']) #find out the link 
                    if date > upto: 
                        article_links.append(link) # if the article date is greater than the latest date (i.e. upto) then it will append the articles in article_links
                    elif date == upto:
                        if title not in titles:
                            article_links.append(link) # if the article date is equal to the latest date (i.e. upto) then we'll find the titles of the articles and if title is not present than it will append the articles in article_links
                    else:
                        last_pg = True # if both the above condition doesn't satisfy it will break the loop and return the stored article_links
                        break
                except Exception as e:
                    print(e)
            if last_pg: # after satisying the above for loop i.e. after the date check it will stop the pagination and return the article_links
                break       
        return article_links
    except Exception as e:
        print(url, e)
            
"""
We find out the required data here i.e. the titles, published date, description and link 
of each article.
"""
def get_article(url, retry = 3): 
    r = session.get(url, timeout = 180)
    soup = BeautifulSoup(r.content, 'lxml')
    row = {}
    row['title'] = soup.find('h1',{'class':'headline'}).text.strip()
    row['link'] = url
    row['pubDate'] = parse(soup.find('div',{'class':'pubStamp'}).find('div',{'class':'col-sm-5'}).text.replace('Published ',''))
    row['description'] = "\n".join([p.text.strip() for p in  soup.find('div',{'class':'story-body'}).find_all('p')])
    return row

#%% Calling the functions
# Section Links
section_links = get_section_links()

# Article Links
article_links = []
titles = []
upto = parse('30 Nov 2020') # latest date when the data is updated
for url in section_links:
    article_links.extend(get_article_links(url))
    
#Removing duplicates
article_links = list(set(article_links))  

# Articles
articles = []
for url in article_links:
    articles.append(get_article(url))

# Converting the data in a dataframe and storing it in a csv format
df = pd.DataFrame(articles)
df.to_csv("deccanchronicle.csv")