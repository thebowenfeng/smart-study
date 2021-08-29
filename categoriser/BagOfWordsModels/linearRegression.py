# Linear regression model
from torch.utils.data import Dataset, DataLoader
import torch
import torch.nn as nn
import random
import os
import numpy as np

# Data loading
device = 'cpu' # feels bad man 
random.seed(42069666)
class WikiDataset(Dataset):
    def __init__(self, setting):
        self.FOLDERS = ['History', 'Geography', 'Arts', 'Philosophy_and_religion','Everyday_life',\
                  'Society_and_social_sciences','Biological_and_health_sciences', 'Physical_sciences',\
              'Technology', 'Mathematics']
        self.MAP = {}
        self.CORPUS_FILE = "corpus.txt"
        self.SPLIT = np.array([0, 0.7,0.85,1])
        self.DIM = 0
        self.fileList = []
        self.setting = setting # one of 0,1,2 for train, test val
        for i in range(len(self.FOLDERS)):
            self.MAP[self.FOLDERS[i]] = i
        
        for folder in self.FOLDERS:
            for file in os.listdir(folder):
                self.fileList.append((self.MAP[folder], os.path.join(folder, file)))
        random.shuffle(self.fileList)
        self.SPLIT = [int(c) for c in self.SPLIT * len(self.fileList)]
        
        k = open(self.CORPUS_FILE,"r")
        while True:
            line = k.readline()
            if len(line.split()) == 2:
                self.DIM += 1
            else:
                break
    def __len__(self):
        return self.SPLIT[self.setting+1] - self.SPLIT[self.setting]

    def bag_transform(self, bag):
        return bag/sum(bag)
    def __getitem__(self, idx):
        # we use log bag of words due to zipfian nature
        idx += self.SPLIT[self.setting]
        k = open(self.fileList[idx][1], "r")
        bag = np.zeros(self.DIM)

        while True:
            l = k.readline().split()
            if len(l) <= 1:
                break
            bag[int(l[0])] = float(l[1])
        return torch.tensor(self.bag_transform(bag)).float(), self.fileList[idx][0]


train_set = WikiDataset(0)
train_loader = DataLoader(train_set, batch_size=32, shuffle=True)

val_set = WikiDataset(1)
val_loader = DataLoader(val_set, batch_size = 1, shuffle=True)

# Model
class LinearRegression(nn.Module):

    def __init__(self):
        super(LinearRegression, self).__init__()
        self.stack = nn.Sequential(
            nn.Linear(train_set.DIM, 10),
            nn.Softmax()
            #nn.Sigmoid() # stuff can in reality belong to multiple classes
        )

    def forward(self, x):
        return self.stack(x)

# Train & Test Loops

def trainloop(dataloader, model, loss_fn, optimizer):
    current = 0
    total_loss = 0
    for batch, (X,y) in enumerate(dataloader):
        X=X.to(device)
        y=y.to(device)
        pred = model(X)
        #print(pred)
        loss = loss_fn(pred, y)
        current += len(X)
        total_loss += loss.item()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if batch % 30 == 0:
            print(f"Processed {current} examples, cumulative batch loss={total_loss}")
    print(f"Finished epoch, cumulative loss = {total_loss}")

def testloop(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    test_loss, correct = 0,0
    with torch.no_grad():
        for X,y in dataloader:
            X=X.to(device)
            y=y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred,y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    print(f"Testset: Correct: {correct}/{size}. Cumulative Loss={test_loss}")
        
# Actual Training
epochs = 10 # all you need
lr = 0.1
model = LinearRegression().to(device) #yolo
loss = nn.CrossEntropyLoss()
optim = torch.optim.AdamW(model.parameters(), lr = lr, weight_decay = 0.01)


print(model)
for i in range(epochs):
    print(f"Epoch {i}")
    trainloop(train_loader, model, loss, optim)
    testloop(val_loader, model, loss)

# Test set
test_loader = DataLoader(WikiDataset(2), batch_size=32)
testloop(test_loader, model, loss)

# Export

#import torch.onnx as onnx
#onnx.export(model, train_set.__getitem__(0)[0], 'regression.onnx')

def export_np(Wfile, bfile):
    # write to file as np float32 binary
    [W,b] = list(model.parameters())
    W = np.array(torch.tensor(W))
    b = np.array(torch.tensor(b))
    W.tofile(Wfile)
    b.tofile(bfile)

export_np("weights2.txt","biases2.txt")
