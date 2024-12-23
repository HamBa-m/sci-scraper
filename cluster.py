import pandas as pd

# read the classifed papers xlsx file
papers = pd.read_excel("results/classified_conference_papers.xlsx")

X = papers[['Attack', 'Defense', 'Robustness', 'Training', 'Testing', 'Competitive', 'Cooperative', 'AttackAgainstCommunication', 'BlackBox', 'WhiteBox', 'GreyBox']]
# generate dendrogram with paper titles in indexes
import scipy.cluster.hierarchy as shc
import matplotlib.pyplot as plt

# Set the index of X to the paper titles
X.index = papers['Title']

plt.figure(figsize=(10, 7))
plt.title("Dendrograms")
dend = shc.dendrogram(shc.linkage(X, method='ward', optimal_ordering=True), labels=X.index, orientation='right')
# truncate the labels to the first 20 characters
ax = plt.gca()
ax.set_yticklabels([label.get_text()[:20] for label in ax.get_yticklabels()])
# tight layout
plt.tight_layout()
plt.show()

# 