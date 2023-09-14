import os
from dotenv import load_dotenv
import google.generativeai as palm
from google.api_core import retry

load_dotenv()


palm.configure(api_key=os.getenv('api-token'))


defaults = {
  'model': 'models/text-bison-001',
  'temperature': 0.1,
  'candidate_count': 1,
  'top_k': 40,
  'top_p': 0.95,
  'max_output_tokens': 1024,
  'stop_sequences': [],
  'safety_settings': [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},{"category":"HARM_CATEGORY_TOXICITY","threshold":1},{"category":"HARM_CATEGORY_VIOLENCE","threshold":2},{"category":"HARM_CATEGORY_SEXUAL","threshold":2},{"category":"HARM_CATEGORY_MEDICAL","threshold":2},{"category":"HARM_CATEGORY_DANGEROUS","threshold":2}],
}


@retry.Retry()
def get_post_category(prompt):
	decider = f"""
	Please return one of the following responses based on the intent you infer from the text below: respond in JSON

	- If the intent is to buy a real estate or property, return 'buy'.
	- If the intent is to sell a real estate or property, return 'sell'.
	- If the intent is to rent a real estate property, return 'rent'.
	- If there is no intent to buy, sell or rent a real estate property, return 'no interest'.

	Here is the text:{prompt}
	"""
	response = palm.generate_text(**defaults ,prompt=decider)
	return response.result


# print(get_post_category("I'm thinking of going home and selling my house off call for info 0993890223"))