from huggingface_hub import InferenceClient
import pandas as pd
import time
import tqdm
import os
import json
import logging

# Load configurations from JSON file
current_dir = os.path.dirname(__file__)
config_file = os.path.join(current_dir, 'config.json')
with open(config_file, 'r') as f:
    config = json.load(f)

################
class AgentLLM:
    def __init__(self, api_key = config['api_key'], model_url = config['model_url']):
        self.client = InferenceClient(model=model_url, token=api_key)

    def prompt_model(self, prompt):
        try:
            response = self.client.text_generation(prompt, return_full_text=False)
            return response
        except Exception as err:
            logging.error(f"Error occurred while prompting model: {err}")
            raise SystemExit(err)

    def filter_papers(self, dataframe):
        dataframe['is_relevent'] = pd.Series(dtype='int64')
        dataframe['Verdict'] = pd.Series(dtype='str')
        abstracts = dataframe['Abstract'].tolist()
        for i, abs in tqdm.tqdm(enumerate(abstracts), total=len(abstracts), desc="Prompting Phi model"):
            title = dataframe.iloc[i]['Title']
            abstract = abs
            prompt = '''<|system|>
            You are a helpful assistant. Your only valid responses are: "YES", "NO", or "I DON'T KNOW".
            <|end|>
            <|user|>
                Title: {0}
                Abstract: {1}
                Based on this abstract and title, does it discuss adversarial attacks and/or defenses on multi-agent reinforcement learning (MARL) algorithms? Ensure that the abstract specifically references a MARL or Game Theory algorithm. Answer "YES", "NO", or "I DON'T KNOW". Make sure it is in the following format:
                is_relevant: <YES | NO | I DON'T KNOW>
                explanation: <brief explanation of your decision>
            <|end|>
            <|assistant|>
            '''.format(title, abstract)
            
            response_text = self.prompt_model(prompt)
            is_relevant = response_text.split('is_relevant: ')[1].split('explanation: ')[0].strip().lower()
            verdict = response_text.split('explanation: ')[1].strip()
            
            if is_relevant == "yes":
                dataframe.loc[i, 'is_relevent'] = 1
            else:
                dataframe.loc[i, 'is_relevent'] = 0
            
            dataframe.loc[i, 'Verdict'] = verdict
                
            logging.info(f"Processed paper {title} with response: {is_relevant}, and explanation: {verdict}")
            
            time.sleep(0.5)
        # # drop the rows that are not relevant
        # dataframe = dataframe[dataframe['is_relevent'] == 1]
        # dataframe.drop(columns=['is_relevent'], inplace=True)
        
        return dataframe

    def save_results(self, dataframe):
        dataframe.to_excel("./results/filtred_papers.xlsx", index=False)
        logging.info("Filtered papers saved to ./results/filtred_papers.xlsx.")


    def classify_papers(self, dataframe):
        # add the 12 columns to the dataframe
        classes = ['Attack', 'Defense', 'Robustness', 'Training', 'Testing', 'Competitive', 'Cooperative', 'AttackAgainstCommunication', 'BlackBox', 'WhiteBox', 'GreyBox', 'Comments']
        for col in classes:
            dataframe[col] = None

        # get the list of abstracts
        abstracts = dataframe['Abstract'].tolist()
        
        # loop through the abstracts and prompt the model
        for i, abs in tqdm.tqdm(enumerate(abstracts), total=len(abstracts), desc="Prompting Phi model"):
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

            response_text = self.prompt_model(prompt)
            
            # remove '''json from the response_text
            if response_text.startswith("```json"):
                response_text = response_text[7:len(response_text)-3]
            # convert the response_text to a dictionary
            response_dict = json.loads(response_text)
            
            # update the dataframe with the response_dict values
            for key, value in response_dict.items():
                dataframe.loc[i, key] = value
                
            logging.info(f"Processed paper {dataframe.iloc[i]['Title']} with response: {response_dict}")
            
            # add time delay to avoid exceeding the API rate limit
            time.sleep(0.5)
        
        return dataframe