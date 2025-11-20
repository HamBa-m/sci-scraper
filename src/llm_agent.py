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
        dataframe.to_excel("./results/filtered_papers.xlsx", index=False)
        logging.info("Filtered papers saved to ./results/filtered_papers.xlsx.")