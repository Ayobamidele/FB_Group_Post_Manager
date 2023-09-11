from EdgeGPT.EdgeUtils import Query, Cookie
from pathlib import Path


def get_post_category(prompt):
    Cookie.dir_path = Path("./bing_cookies_ayo.json")
    decider = f"""
	Please return one of the following responses based on the intent you infer from the text below: 

	- If the intent is to buy a real estate or property, return 'buy'.
	- If the intent is to sell a real estate or property, return 'sell'.
	- If the intent is to rent a real estate property, return 'rent'.
	- If there is no intent to buy, sell or rent a real estate property, return 'no interest'.

	Here is the text:{prompt}
	"""
    q = Query(
        prompt=decider,
        style="precise",  # or: 'balanced', 'precise'
        cookie_files=Cookie.dir_path,
    )
    return q.output
