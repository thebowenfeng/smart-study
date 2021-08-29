import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#output_file = "C:/Users/junhu/Desktop/Machine Learning/Study concentration/Model Construction/Weight outputs/benchmark_results_svm.txt" 
output_file = "benchmark_results.txt"
#output_file = 'benchmark_naive_embedding_regression2.txt'
#output_file = 'benchmark_svmgood_results.txt'
#output_file = 'svmgood_biases.txt'
#output_file = 'benchmark_naive_sentenceaveraged_embedding_regression.txt'
#output_file = 'sentence_logistic_regression.txt'
ground_truth = "benchmark.txt"
classes = ['History', 'Geography', 'Arts', 'Philosophy_and_religion','Everyday_life',\
                  'Society_and_social_sciences','Biological_and_health_sciences', 'Physical_sciences',\
              'Technology', 'Mathematics']
num_classes = len(classes)
k = open(output_file, "r")
k2 = open(ground_truth, "r")
results = k.read().split('\n')
categories = np.zeros((num_classes,4)) #top 2 and >= 0, top 2, >= 0, neither
freq = np.zeros((num_classes))
ans = []
top_class_scores = []
correct_class_scores = []
t2_class_scores = [] # If the model is right what kinds of scores does it output
results_matrix = np.zeros((num_classes, num_classes)) #[correct][predicted]
mistake_relevant_for_irrelevant = 0
if "Test" not in results[-1]:
    results.pop()

weak_correct = 0
metric_2_correct = 0
derp = 0
while True:
    txt = k2.readline().split()
    if len(txt) < 2:
        break
    ans.append(classes.index(txt[0]))

for i in results:
    [casenum, weights] = i.split(':')
    casenum = int(casenum.split()[1])
    #print(weights)
    weights = np.fromstring(weights, dtype=float, sep=' ')
    weights/=weights.sum()
    results_matrix[ans[casenum]][weights.argmax()] += 1

    top2 = weights[ans[casenum]] >= sorted(weights)[-2]
    criteria2 = weights[ans[casenum]] - weights.max() >= -0.1
    high_confidence = weights[ans[casenum]] >= -0.05
    if weights[ans[casenum]] <= 0:
        if weights[4] > 0:
            mistake_relevant_for_irrelevant += 1
    if top2 and high_confidence:
        categories[ans[casenum]][0]+=1
    elif top2:
        categories[ans[casenum]][1]+=1
    elif high_confidence:
        categories[ans[casenum]][2]+=1
    else:
        categories[ans[casenum]][3]+=1

    if high_confidence and criteria2:
        metric_2_correct += 2

    if top2 and weights[ans[casenum]] < 0.001:
        derp += 1

    weak_correct += top2

    if top2:
        t2_class_scores.append(weights[ans[casenum]])

    freq[ans[casenum]] += 1
    top_class_scores.append(weights.max())
    correct_class_scores.append(weights[ans[casenum]])

for i in range(num_classes):
    categories[i] /= freq[i]

"""
print(derp)
sns.heatmap(results_matrix, annot=True)
plt.show()
sns.heatmap(categories, annot=True)
plt.show()
plt.hist(t2_class_scores, bins=30)
plt.show()
plt.hist(correct_class_scores, bins=30)
plt.show()
print(mistake_relevant_for_irrelevant, weak_correct)
cleaned = list(filter(lambda x: not np.isnan(x), t2_class_scores))
print(np.std(cleaned), np.mean(cleaned))

#for SVM:
cleaned = np.array(cleaned)
cleaned = np.log(cleaned+1)
print(len(cleaned))
plt.hist(cleaned, bins=30)
plt.show()
"""
from scipy import stats
import seaborn as sns
stats.probplot(t2_class_scores, plot=sns.mpl.pyplot)
plt.show()
