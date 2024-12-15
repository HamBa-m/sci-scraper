# code to prompt LLaMa model API
import requests
import json

api_key = "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"
model_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# prompt the model
def prompt_model(prompt):
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"inputs": prompt}
        response = requests.post(model_url, headers=headers, json=data)
        response.raise_for_status()
        response_text = response.json()[0]['generated_text'].strip()
        return response_text
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
# prompt the model with a given prompt
prompt = "Develop the following text: 'A new study finds that the best way to live a long life is to eat a lot of fruits and vegetables.'"

response = prompt_model(prompt)
print(response)