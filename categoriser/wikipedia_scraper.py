import aiohttp
import asyncio
from bs4 import BeautifulSoup

# Gets soup. Soup is an abstract representation of the HTML that has already been nicely parsed. 
# Has plenty of nice helper functions
async def get_soup(session,url):
    print("Retrieved",url)
    async with session.get(url) as req:
        if req.status == 200:
            return BeautifulSoup(await req.text(), 'html.parser')
    return None

async def process_url(session,url,outfile):
    soup = await get_soup(session,url)
    if (soup != None):        
        # Look up the beautifulsoup documentation to see what you can do with this soup object
    
        # go to the next sibling
        #print (result.next_sibling)
        l = open(outfile,"w")
        for link in soup.find_all('a'):
            ref = link.get('href')
            if type(ref) != str:
                continue
    
            if "File" not in ref and "Vital_articles" not in ref and "#" not in ref:
                #if "Template" in ref:
                #    break
                l.write(ref+"\n")
        l.close()
        # I am pretty sure a lot of times you want the .text attribute too
# basically our main function, we have to put it in async so we can go faster
async def scrape(outfiles, links):
    async with aiohttp.ClientSession() as session:
        # we make an array of all the tasks 
        tasks = []
        for i in range(len(links)):   
            tasks.append(process_url(session,links[i], outfiles[i]))

        # Note that at this point, not all the functions in tasks have returned yet. Hence we wait for it
        # by calling asyncio.gather
        # If process_url returns something then results will contain all the return values 
        
        results = await asyncio.gather(*tasks)
    
# Actually call do_stuff

Categories = ['History', 'Geography', 'Arts', 'Philosophy_and_religion','Everyday_life',\
              	'Society_and_social_sciences','Biological_and_health_sciences', 'Physical_sciences',\
              'Technology', 'Mathematics']

BASE_URL = 'https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/'
SCRAPE_URLS = [BASE_URL+c for c in Categories]
OUT_FILES = [c+".txt" for c in Categories]

asyncio.run(scrape(OUT_FILES, SCRAPE_URLS))

