import aiohttp
import asyncio, os
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
    if os.path.isfile(outfile):
        print('yay')
        return

    try:
         open(outfile,"w")
    except:
        return 
    soup = await get_soup(session,url)
    if (soup != None):        
        # Look up the beautifulsoup documentation to see what you can do with this soup object
    
        # go to the next sibling
        #print (result.next_sibling)
        ALLOWED = "ABCDEFGHIJKLMNOPQRSTUVWXYZ ".lower()
        txt = soup.text
        txt=txt.lower().replace('\n'," ")
        filtered_txt=""
        for i in range(len(txt)):
            if txt[i] in ALLOWED:
                filtered_txt += txt[i]
            else:
                filtered_txt += " "

        filtered_txt = " ".join(filtered_txt.split()[100:]) #first 100 words are usually noisy
        filtered_txt = filtered_txt[:filtered_txt.index("retrieved from http")]
        l = open(outfile,"w")
        l.write(filtered_txt)
        l.close()

# basically our main function, we have to put it in async so we can go faster
async def scrape(outfiles, links):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10**9)) as session:
        # we make an array of all the tasks 
        tasks = []
        for i in range(len(links)):   
            tasks.append(process_url(session,links[i], outfiles[i]))

        # Note that at this point, not all the functions in tasks have returned yet. Hence we wait for it
        # by calling asyncio.gather
        # If process_url returns something then results will contain all the return values 
        
        results = await asyncio.gather(*tasks)
    
# Actually call do_stuff
def go(BASE_TOPIC):
    BASE_URL = 'https://en.wikipedia.org/wiki/'
    todo = []
    SCRAPE_URLS = []
    OUT_FILES = []
    inFile = BASE_TOPIC + ".txt"
    k = open(inFile, "r")
    try:
        os.mkdir(BASE_TOPIC)
    except:
        pass
    while True:
        l = k.readline()
        if l == "":
            break
        else:
            article_name = l.split('/')[-1].replace('\n','')
            if article_name == "":
                continue
            SCRAPE_URLS.append(BASE_URL+article_name)
            OUT_FILES.append(BASE_TOPIC+"/"+article_name+".txt")

    asyncio.run(scrape(OUT_FILES, SCRAPE_URLS))
DONE = ['Mathematics', 'Geography' ,'History', 'Geography', 'Arts','Philosophy_and_religion','Everyday_life',\
                  'Society_and_social_sciences','Biological_and_health_sciences','Physical_sciences',\
              'Technology']
Categories = ['Physical_sciences'] #math already done

for category in Categories:
    go(category)
