import aiohttp
import asyncio, os, random
from bs4 import BeautifulSoup

# Gets soup. Soup is an abstract representation of the HTML that has already been nicely parsed. 
# Has plenty of nice helper functions

OUTDIR = "Benchmark"
THRESHOLD = 100 #words per case
BASE_URL = 'https://en.wikipedia.org'
DONE = ['Mathematics','History', 'Geography','Physical_sciences', 'Arts','Philosophy_and_religion','Everyday_life']
Categories = ['Society_and_social_sciences','Biological_and_health_sciences',\
              'Technology'] #math already done

NUM_PGS = 100

def cleanText(txt):
    txt = txt.lower()
    ALLOWED = "ABCDEFGHIJKLMNOPQRSTUVWXYZ ".lower()
    processed_txt = ""
    for i in txt:
        if i not in ALLOWED:
            if len(processed_txt) and processed_txt[-1] != " ":
                processed_txt += " "
        else:
            processed_txt += i
    return processed_txt

async def get_soup(session,url):
    print("Retrieved",url)
    try:
        async with session.get(url) as req:
            if req.status == 200:
                return BeautifulSoup(await req.text(), 'html.parser')
            else:
                print('Error on', url )
    except:
        pass
    return None

async def process_url(session, semantic_class, url):
    soup = await get_soup(session,url)
    if (soup != None):        
        Paragraphs = list(map(lambda x: cleanText(str(x.text)), list(soup.find_all('p'))))
        random.shuffle(Paragraphs)
        num_cases = 8
        pt = 0
        out_txt = []
        while num_cases and pt != len(Paragraphs):
            out_txt.extend(Paragraphs[pt].split())
            pt += 1

            if len(out_txt) >= THRESHOLD:
                outfile = os.path.join(OUTDIR, str(len(os.listdir(OUTDIR)))+".txt")
                l = open(outfile,"w")
                l.write(semantic_class+"\n")
                #print(out_txt)
                l.write(" ".join(out_txt))
                l.close()
                out_txt = []
                num_cases -= 1


# basically our main function, we have to put it in async so we can go faster
async def scrape(category, num):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10**9)) as session:
        # we make an array of all the tasks 
        tasks = []
        pgs =[]
        k = open(category+".txt", "r")
        while True:
            line = k.readline()
            if "wiki" not in line:
                break
            else:
                line = line.replace('\n',"")
                pgs.append(BASE_URL + line)

        for i in range(num):
            link = pgs[random.randint(0, len(pgs)-1)]
            #print(i, link)
            soup = await get_soup(session, link)
            hreflist = list(soup.find_all('a'))
            #print(len(hreflist), type(hreflist[0]))
            wildLinks = list(filter(lambda x: "wiki" not in str(x.get('href')) and "http" in str(x.get('href')), hreflist))
            for j in range(5):
                tasks.append(process_url(session, category, str(wildLinks[random.randint(0, len(wildLinks)-1)].get('href'))))
        # Note that at this point, not all the functions in tasks have returned yet. Hence we wait for it
        # by calling asyncio.gather
        # If process_url returns something then results will contain all the return values 
        
        results = await asyncio.gather(*tasks)
    
# Actually call do_stuff

#kek idk what this does: https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())    
for category in Categories:
    print(category)
    asyncio.run(scrape(category, NUM_PGS))
