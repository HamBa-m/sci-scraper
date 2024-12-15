# code to prompt LLaMa model API
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

papers_plmr = pd.read_excel("PLMR_conference_papers_2018_2024.xlsx")
print("PLMR papers shape:", papers_plmr.shape)
papers_ijcai = pd.read_excel("IJCAI_conference_papers_2018_2024.xlsx")
print("IJCAI papers shape:", papers_ijcai.shape)

# merge the two dataframes
papers = pd.concat([papers_ijcai, papers_plmr], ignore_index=True)
# merge URL and Link columns in one column
papers['URL'] = papers['URL'].fillna(papers['Link'])
papers = papers.drop(columns=['Link'])
# drop duplicates
papers = papers.drop_duplicates(subset=['Title'])
papers = papers.reset_index(drop=True)

# add a boolean column to the dataframe
papers['is_relevent'] = None

# get the list of abstracts
abstracts = papers['Abstract'].tolist()
    
# loop through the abstracts and prompt the model
i = 0
for abs in tqdm.tqdm(abstracts, total=len(abstracts), desc="Prompting Phi model"):
    prompt = '''<|system|>
    You are a helpful assistant who only answers by "YES" or "NO" or "I DON'T KNOW".<|end|>
    <|user|>
    {}\n
    tell me if this abstract discusses adversarial attacks on multi agent deep reinforcement learning? yes or no or you don't know?<|end|>
    <|assistant|>'''.format(abs)
    response_text = prompt_model(prompt)
    response_text = response_text.lower().replace(".", "").strip()

    papers.iloc[i, papers.columns.get_loc('is_relevent')] = 1 if response_text == "yes" else 0
    i += 1
    
    # add time delay to avoid exceeding the API rate limit
    time.sleep(0.5)
    
# save the dataframe to a new xlsx file
papers.to_excel("conference_papers_with_adversarial_attacks_column.xlsx", index=False)