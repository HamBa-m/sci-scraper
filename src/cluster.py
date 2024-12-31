import pandas as pd

# read the classifed papers xlsx file
papers = pd.read_excel("./results/merged_papers.xlsx")

X = papers[['Attack', 'Defense', 'Robustness', 'Training', 'Testing', 'Competitive', 'Cooperative', 'AttackAgainstCommunication', 'BlackBox', 'WhiteBox', 'GreyBox']]
# generate dendrogram with paper titles in indexes
import scipy.cluster.hierarchy as shc
import matplotlib.pyplot as plt

# Set the index of X to the paper titles
X.index = papers['Title']

# plt.figure(figsize=(10, 7))
# plt.title("Dendrograms")
# dend = shc.dendrogram(shc.linkage(X, method='ward', optimal_ordering=True), labels=X.index, orientation='right')
# # truncate the labels to the first 20 characters
# ax = plt.gca()
# ax.set_yticklabels([label.get_text()[:70] for label in ax.get_yticklabels()])
# # tight layout
# plt.tight_layout()
# plt.show()

# get 4 clusters
from sklearn.cluster import AgglomerativeClustering
cluster = AgglomerativeClustering(n_clusters=4, affinity='euclidean', linkage='ward')
papers['Cluster'] = cluster.fit_predict(X)
papers.to_excel("./results/clustered_papers.xlsx")

# divide the dataframe into dataframes based on the clusters
clusters = {}
for i in range(4):
    clusters[i] = papers[papers['Cluster'] == i]
    
# code to prompt Phi3.5 model API
from huggingface_hub import InferenceClient

api_key = "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"
model_url = "microsoft/Phi-3-mini-4k-instruct"

client = InferenceClient(model=model_url, token=api_key)

# prompt the model
def prompt_model(prompt):
    try:
        response = client.text_generation(prompt, max_new_tokens=512)
        return response
    except Exception as err:
        raise SystemExit(err)

for i in range(4):
    prompt = '''<|system|>
    I have a topic that contains the following documents: 
    {0}

    Based on the information above, extract a short but highly descriptive topic label of at most 5 words. Make sure it is in the following format:
    topic: <topic label>
    topic explanation: <topic explanation>
    <|end|>
    <|assistant|>'''.format(clusters[i]['Abstract'])

    response_text = prompt_model(prompt)
    print(response_text)
    # extract the topic label
    topic_label = response_text.split('topic: ')[1].strip()
    topic_explanation = response_text.split('topic explanation: ')[1].strip()
    print(topic_label)
    # map the topic label to the cluster
    clusters[i]['Topic'] = topic_label
    clusters[i]['Topic Explanation'] = topic_explanation
    
# add the topic labels to the original papers dataframe
papers = pd.concat([clusters[0], clusters[1], clusters[2], clusters[3]])

# save the clustered papers with the topic labels
papers.to_excel("./results/clustered_papers_with_topic.xlsx")