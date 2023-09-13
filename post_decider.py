import os
from dotenv import load_dotenv
import google.generativeai as palm
from google.api_core import retry

load_dotenv()


palm.configure(api_key=os.getenv('api-token'))


@retry.Retry()
def generate_text(*args, **kwargs):
    return palm.generate_text(*args, **kwargs)

models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name


@retry.Retry()
def get_post_category(prompt):
    decider = f"""
	Please return one of the following responses based on the intent you infer from the text below: 

	- If the intent is to buy a real estate or property, return 'buy'.
	- If the intent is to sell a real estate or property, return 'sell'.
	- If the intent is to rent a real estate property, return 'rent'.
	- If there is no intent to buy, sell or rent a real estate property, return 'no interest'.

	Here is the text:{prompt}
	"""
    response = palm.generate_text(prompt=decider)
    return response.result


# print(get_post_category("I'm thinking of going home and selling my house off call for info 0993890223"))