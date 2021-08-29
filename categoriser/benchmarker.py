from googlesearch import search
import random
# to search

l = open("testcases4.txt","w")

CLASSES = ['History', 'Geography', 'Arts', 'Philosophy_and_religion','Everyday_life',\
                  'Society_and_social_sciences','Biological_and_health_sciences', 'Physical_sciences',\
              'Technology', 'Mathematics']


for class_name in CLASSES:
    # select 30 topics from the list of wikipedia pages
    topics = list(map(lambda x: x.split('/')[-1].replace('_',' '), open(class_name+".txt","r").read().split('\n')))
    random.shuffle(topics)
    ALLOWED = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    ALLOWED = ALLOWED + ALLOWED.lower()
    NUM_TOPICS = 10
    for i in range(NUM_TOPICS):
        #tune pause = 0.1 to avoid HTTP 429 too many requests
        #for 1 topic pause = 0.1 takes 20s, pause = 2 takes 43s
        for j in search(topics[i], tld="com.au", num=15, stop=15, pause=2):
            if 'wikipedia' not in j:
                l.write(class_name + " " + j + "\n")

l.close()
