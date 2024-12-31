# code to prompt Phi3.5 model API
from huggingface_hub import InferenceClient
import pandas as pd
import time
import tqdm

api_key = "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"
model_url = "microsoft/Phi-3-mini-4k-instruct"

client = InferenceClient(model=model_url, token=api_key)

# prompt the model
def prompt_model(prompt):
    try:
        response = client.text_generation(prompt, return_full_text=False)
        return response
    except Exception as err:
        raise SystemExit(err)

# read the conference papers xlsx file
# papers = pd.read_excel("./results/venues_results.xlsx")
papers = pd.read_csv("./results/scholar_results.csv")

# add a boolean column to the dataframe
papers['is_relevent'] = None

# get the list of abstracts
# abstracts = papers['Abstract'].tolist()
abstracts = papers['abstract'].tolist()
    
# loop through the abstracts and prompt the model
i = 0
for abs in tqdm.tqdm(abstracts, total=len(abstracts), desc="Prompting Phi model"):
    prompt = '''<|system|>
    You are a helpful assistant who only answers by "YES" or "NO" or "I DON'T KNOW".<|end|>
    <|user|>
    {}\n
    tell me if this abstract discuses adversarial attacks on multi agent deep reinforcement learning algorithms? answer yes or no or you don't know? it should be using some MARL algo<|end|>
    <|assistant|>'''.format(abs)
    response_text = prompt_model(prompt)
    response_text = response_text.lower().replace(".", "").strip()

    papers.iloc[i, papers.columns.get_loc('is_relevent')] = 1 if response_text == "yes" else 0
    i += 1
    
    # add time delay to avoid exceeding the API rate limit
    time.sleep(0.5)
    
# save the dataframe to a new xlsx file
papers.to_excel("./results/scholar_papers_with_adversarial_attacks_column.xlsx", index=False)

# filter the dataframe to get only the relevant papers
relevant_papers = papers[papers['is_relevent'] == 1]
print("Relevant papers shape:", relevant_papers.shape)

# save the relevant papers to a new xlsx file
# relevant_papers.to_excel("relevant_venues_papers.xlsx", index=False)
relevant_papers.to_excel("./results/relevant_scholar_papers.xlsx", index=False)