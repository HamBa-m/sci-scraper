# code to prompt Phi3.5 model API
from huggingface_hub import InferenceClient
import pandas as pd
import time
import tqdm
import json

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

# read the relevant papers xlsx file
# papers = pd.read_excel("./results/relevant_conference_papers.xlsx")
papers = pd.read_excel("./results/relevant_scholar_papers.xlsx")

# add the 12 columns to the dataframe
classes = ['Attack', 'Defense', 'Robustness', 'Training', 'Testing', 'Competitive', 'Cooperative', 'AttackAgainstCommunication', 'BlackBox', 'WhiteBox', 'GreyBox', 'Comments']
for col in classes:
    papers[col] = None

# get the list of abstracts
# abstracts = papers['Abstract'].tolist()
abstracts = papers['abstract'].tolist()
    
# loop through the abstracts and prompt the model
i = 0
for abs in tqdm.tqdm(abstracts, total=len(abstracts), desc="Prompting Phi model"):
    prompt = '''<|system|>
    You are a helpful assistant who analyzes research paper abstracts and generates a JSON object with specific binary indicators or textual comments. Each key in the JSON corresponds to the described dimensions.

    ### Instructions:
    1. **Attack**: Does the abstract primarily discuss an attack approach? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    2. **Defense**: Does the abstract focus on defense mechanisms? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    3. **Robustness**: Is the focus on improving robustness? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    4. **Training**: Does the abstract emphasize training-time aspects? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    5. **Testing**: Is the focus on testing-time aspects? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    6. **Competitive**: Is the multi-agent RL setting competitive? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    7. **Cooperative**: Is the multi-agent RL setting cooperative? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    8. **AttackAgainstCommunication**: Does the abstract discuss attacks targeting communication in multi-agent RL? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    9. **BlackBox**: Does the method treat the system as a black box? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    10. **WhiteBox**: Does the method have full access to the system's internal details? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    11. **GreyBox**: Does the method have partial access to the system's details? (YES -> 1, NO -> 0, I DON'T KNOW -> 0)
    12. **Comments**: Provide a brief sentence summarizing any unique aspects or focus of the abstract.

    ### Abstract:
    {}

    ### Output:
    Return the output strictly in the following JSON format:
    {{
        "Attack": X,
        "Defense": X,
        "Robustness": X,
        "Training": X,
        "Testing": X,
        "Competitive": X,
        "Cooperative": X,
        "AttackAgainstCommunication": X,
        "BlackBox": X,
        "WhiteBox": X,
        "GreyBox": X,
        "Comments": "Your short summary or observation."
    }}<|end|>
    <|assistant|>'''.format(abs)

    response_text = prompt_model(prompt)
    
    # remove '''json from the response_text
    if response_text.startswith("```json"):
        response_text = response_text[7:len(response_text)-3]
    # convert the response_text to a dictionary
    response_dict = json.loads(response_text)
    
    # update the dataframe with the response_dict values
    for key, value in response_dict.items():
        papers.iloc[i, papers.columns.get_loc(key)] = value
    i += 1
    
    # add time delay to avoid exceeding the API rate limit
    time.sleep(0.5)
    
# save the dataframe to a new xlsx file
# papers.to_excel("./results/classified_conference_papers.xlsx", index=False)
papers.to_excel("./results/classified_scholar_papers.xlsx", index=False)