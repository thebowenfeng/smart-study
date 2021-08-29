# input: paragraph of text
# output: category

import numpy as np
from nltk.stem.porter import PorterStemmer
import os
from tqdm import tqdm

# definitsions
class SentenceVote:

    def __init__(self):
        CORPUS_FILE = "corpus.txt"
        self.CLASSES = ['History', 'Geography', 'Arts', 'Philosophy_and_religion','Everyday_life',\
                  'Society_and_social_sciences','Biological_and_health_sciences', 'Physical_sciences',\
              'Technology', 'Mathematics']
        self.corpus = {}
        self.cnt = 0
        k1 = open(CORPUS_FILE,"r")
        while True:
            r = k1.readline().replace('\n',"")
            if r =="":
                break
            word = r.split()[0]
            self.corpus[word] = self.cnt
            self.cnt += 1
        self.precomp()
    
    def preprocess(self, txt, sparse=False):
        txt = txt.lower()
        ALLOWED = "abcdefghijklmnopqrstuvwxyz "
        stemmer = PorterStemmer()
        cleaned = ""
        for i in range(len(txt)):
            if txt[i] in ALLOWED:
                cleaned += txt[i]
            else:
                cleaned += " "
        cleaned = [stemmer.stem(c) for c in cleaned.split()]

        if not sparse:
            bag = [0.0]*self.cnt
            for word in cleaned:
                res = self.corpus.get(word, -1)
                if res == -1:
                    continue
                bag[res] += 1.0
        else:
            bag = []
            for word in cleaned:
                res = self.corpus.get(word, -1)
                if res == -1:
                    continue
                bag.append(res)
                
        return np.array(bag)

    def science_arts_split(self, classId):
        if classId < 4 or classId == 5:
            return 0 #arts
        if classId >= 6:
            return 1 #science
        if classId == 4:
            return 2 #everyday life
        
    def bag_transforms(self, bag):
        #print(bag.max())
        if bag.sum() != 0:
            return bag/bag.sum() # normalise
        return bag

    def precomp(self):
        # can be overriden
        WEIGHTS_FILE = "weights2.txt"
        BIAS_FILE = "biases2.txt"
        self.W = np.fromfile(WEIGHTS_FILE, dtype=np.float32)
        self.b = np.fromfile(BIAS_FILE, dtype=np.float32)
        self.W = np.reshape(self.W, (len(self.CLASSES), self.cnt))
        
    def predict(self, bag):
        # to be overriden
        return np.matmul(self.W, bag) + self.b

    def test_sentence(self, txt=""):
        if txt == "": txt = input() #user test
        res = np.zeros(10)
        sparse_bag = self.preprocess(txt, sparse=True)
        for ind in sparse_bag:
            res += self.W[:, ind]
        res /= len(sparse_bag)
        return res+self.b

    def test(self, txt):
        txt = txt.split(' ') 
        vote = np.zeros(10)
        WORDS_PER_SENTENCE = 15
        pt = 0
        while pt < len(txt):
            sentence = ' '.join(txt[pt:pt+WORDS_PER_SENTENCE])
            if len(sentence) >= WORDS_PER_SENTENCE*2: 
                #print(sentence)
                res = self.test_sentence(sentence)

                # check consistency
                good = True
                for i in range(10):
                    if res[i] != res[i] or abs(res[i]) == np.inf:
                        good = False

                if good and res.argmax() >= -2:
                    vote[res.argmax()] += 1
                    
            pt += int(WORDS_PER_SENTENCE*0.75)
        #print(res)
        return vote
        

    def write_bag(self, file, bag, overwrite=False):
        if os.path.isdir(file) and not overwrite:
            return
        bag.tofile(file)
    
    def eval(self, outfile="benchmark_results.txt", top=2, idle=False, raw_txt = True):
        file = open("benchmark.txt","r").read().split('\n')
        BENCHMARK_BINARIES = "benchmark_binaries"
        try: checkpoint = open(outfile,"r").read()
        except: checkpoint = ""
        cases = 0
        correct = 0
        it = range(len(file))
        if not idle:
            it = tqdm(it)
        for testId in it:
            try: [ans, url] = file[testId].split()
            except: continue

            txt_file_name = "benchmark/test"+str(testId)+".txt"
            outfile_string = "Test "+str(testId)+": "
            try:
                raw_txt = open(txt_file_name, "r").read()
                if len(raw_txt) <= 10:
                    continue
                res = self.test(raw_txt)
                test_stat = self.test_sentence(raw_txt)
            except FileNotFoundError:
                continue
            cases += 1
            #print(ans, url)
            if cases % 50 == 0 and idle:
                 print(f"Processed {cases} Cases")
            
            correct_label = self.CLASSES.index(ans)
            # Metrics:
            # We consider a result correct if it exceeds 0 and falls in the top 2 confidences
            # Optional: CHeck for seperation but meh

            # Check exact category score
            sorted_res = sorted(res)
            test_stat = test_stat[correct_label]
            if res[correct_label] >= sorted_res[-top] and test_stat > -2:
                correct += 1
            
            checkpoint += outfile_string + " ".join([str(c) for c in res])+"\n"
        print(f"{correct}/{cases} correct")
        #output_file = open(outfile,"w")
        #output_file.write(checkpoint)
        #output_file.close()

#SentenceVote().eval(outfile = "sentence_logistic_regression.txt", idle=True)