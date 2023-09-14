import json
import os
from datetime import datetime
from facebook_scraper import get_posts
from dotenv import load_dotenv
from post_decider import get_post_category
import requests

load_dotenv()

class DateTimeEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.isoformat()
		return super(DateTimeEncoder, self).default(obj)


def send_to_telegram(message, file=False,filepath="attachment.json"):
	apiToken = os.getenv("token")
	chatID = os.getenv("chatID")
	if not(file):
		apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

		try:
			response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
			print(json.dumps(response.json(), indent=4))
		except Exception as e:
			print(e)
	else:
		apiURL2 = f'https://api.telegram.org/bot{apiToken}/sendDocument?chat_id={chatID}&caption={message}'

		files = {
			'document' : open(f'{filepath}' )
			}
		try:
			response = requests.post(
				apiURL2, 
				files=files
			)
			print(json.dumps(response.json(), indent=4))
		except Exception as e:
			print(e)

def remove_single_quotes(data):
	if isinstance(data, dict):
		return {remove_single_quotes(key): remove_single_quotes(value) for key, value in data.items()}
	elif isinstance(data, list):
		return [remove_single_quotes(element) for element in data]
	elif isinstance(data, str):
		return data.replace("'", "")
	else:
		return data

def process_json(file_path):
	with open(file_path, 'r') as f:
		data = json.load(f)

	data = remove_single_quotes(data)

	with open(file_path, 'w') as f:
		json.dump(data, f, indent=6)


def save_dict_as_json(data_dict):
	# Ensure the directory exists
	# folder_name = "results"
	# os.makedirs(folder_name, exist_ok=True)

	# Create the full file path
	file_path = os.path.join("data.json")

	# Check if the file exists
	if not os.path.exists(file_path):
		# Create a new file
		open(file_path, "w").close()

	# Write the dictionary to the file in JSON format with an indent of 4
	with open(file_path, "w") as f:
		json.dump(data_dict, f, indent=4, cls=DateTimeEncoder)


def save_defaultdict_as_json(data_dict, file_name):
	# Convert the defaultdict to a normal dictionary
	normal_dict = dict(data_dict)

	# Load the existing data from the file, if any
	try:
		with open(file_name, "r") as f:
			existing_data = json.load(f)
	except (FileNotFoundError, json.JSONDecodeError):
		existing_data = {}

	# Merge the existing data with the new data
	merged_data = {**existing_data, **normal_dict}

	# Open the file in write mode
	with open(file_name, "w") as f:
		# Write the merged dictionary to the file in JSON format
		json.dump(merged_data, f, indent=4)


def get_group_post(group_id: int):
	result = []
	for post in get_posts(group_id, pages=10 ,cookies=r"fb_cookies_ayo.json"):
		result.append(post)
	save_dict_as_json(result)
	with open("data.json", "r") as f:
		data = json.load(f)
	return data


def search_json_files(
	data,
	specific_datetime,
	keys=["header", "name", "text", "post_text", "shared_text", "original_text"],
):
	
	# Convert string to datetime object
	specific_datetime = datetime.strptime(specific_datetime, "%Y-%m-%dT%H:%M:%S")

	# Initialize the results list
	results = []

	# Initialize an empty dictionary for the last post
	last_post = {}

	# Search for the keywords in the values of the specified keys
	for item in data:
		# Convert post time to datetime object
		# post_time = item['time']
		post_time = datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%S")

		# Check if post time is after the specific datetime
		if post_time > specific_datetime:
			values = []

			# Iterate over the keys to search for
			for key in keys:
				# Check if the key is in the dictionary and if the value is not an empty string or None
				if key in item and item[key] not in ["", None]:
					# Add the value to the list
					values.append(item[key])

			# Convert the list to a string, checking for None values
			values_str = ", ".join(
				[str(value) for value in values if value is not None]
			)

			# Create a dictionary with the values string and other information
			new_dict = {
				"values_str": values_str,
				"post_id": item.get("post_id", ""),
				"time": item.get("time", ""),
				"post_url": item.get("post_url", ""),
			}

			# Add the new dictionary to the result list
			results.append(new_dict)

			# Update last post if it's later than the current last post
			if not last_post or post_time > datetime.strptime(
				last_post["time"], "%Y-%m-%dT%H:%M:%S"
			):
				last_post = item
	return results, last_post.get("time", specific_datetime.strftime('%Y-%m-%dT%H:%M:%S'))


def process_intents(list_of_dicts):
	# Iterate over the list of dictionaries
	for dict_ in list_of_dicts:
		# Try to get the 'values_str' key
		values_str = dict_.get("values_str", None)

		# If 'values_str' exists, call the 'get_post_category' function and create a new 'intent' key
		if values_str is not None:
			try:
				dict_["intent"] = get_post_category(values_str)
			except Exception as e:
				print(e, dict_)
				dict_["intent"] = 'no interest'


	# Load existing data from the JSON file
	try:
		with open("output.json", "r") as f:
			existing_data = json.load(f)
	except FileNotFoundError:
		existing_data = []

	# Append new data to existing data
	existing_data.extend(list_of_dicts)

	# Save the modified list of dictionaries to the JSON file
	with open("output.json", "w") as f:
		json.dump(existing_data, f, indent=6)


def update_last_post_time(file_path, group_id, new_date):
	# Load the JSON data from the file
	with open(file_path, "r") as f:
		data = json.load(f)

	# Search for dictionaries with the specified group ID and update their last_post_time
	for item in data:
		if item.get("group_id") == group_id:
			if str(new_date):
				item["last_post_time"] = new_date

	# Save the updated data back to the file
	with open(file_path, "w") as f:
		json.dump(data, f, indent=4)


def send_sell_posts(sell_list):
	sell_message = f"""
				Hey, there,
				There are {len(sell_list)} posts that show an intent to sell some real estate property.

				"""

	for i, post in enumerate(sell_list, 1):
		current_post = f"\n{i}. {post.get('post_url', 'No URL provided')}\n"
		sell_message += current_post

	send_to_telegram(sell_message)
	return True


def filter_other_dicts(list_of_dicts):
	# create an empty list to store the filtered dicts
	filtered_list = []
	# loop through each dict in the list
	for dict in list_of_dicts:
	# check if the dict has a key called "intent"
		if "intent" in dict:
			# check if the value of "intent" is not "no interest"
			if dict["intent"] != "no interest":
			# append the dict to the filtered list
				filtered_list.append(dict)
		# return the filtered list
	return filtered_list


def send_other_posts(other_list):
	
	sell_message = f"""
				Hey, there,
				There are {len(other_list)} posts that show an intent of some what interest in some real estate property.

				"""

	for i, post in enumerate(other_list, 1):
		current_post = f"\n{i}. {post.get('post_url', 'No URL provided')}\n"
		sell_message += current_post

	send_to_telegram(sell_message, file=True,filepath="other-posts.json")
	return True


def write_to_output(list1, list2, file):
	# Check if both lists are empty
	if not list1 and not list2:
		return(False, "Both lists are empty. No data to write to the JSON file.")

	# Combine the two lists
	combined_list = list1 + list2

	# Write the combined list to a JSON file
	with open(file, 'w') as f:
		json.dump(combined_list, f, indent=6)
	return(True, "Json file Ready to be Sent")


def categorize_intents_and_send_notifications():
	# Initialize lists for each category
	sell_list = []
	buy_list = []
	rent_list = []
	other_list = []

	# Load the JSON file
	with open('output.json', 'r') as f:
		data = json.load(f)

	# Iterate over the list of dictionaries in the JSON data
	for post in data:
		# Get the 'intent' key
		intent = post.get('intent', None)

		# Add the dictionary to the appropriate list based on the intent
		if intent == 'sell':
			sell_list.append(post)
		elif intent == 'buy':
			buy_list.append(post)
		elif intent == 'rent':
			rent_list.append(post)
		else:
			other_list.append(post)
	
	# Send sell message to telegram
	send_sell_posts(sell_list)

	# Send buy and rent file to telegram with message
	write_to_output(buy_list, rent_list,"attachment.json")
	send_to_telegram("""
						Hey there,
				  			Here are the Facebook posts with rent and buy intent in the json file.
				  		Bye.
					""",file=True)
	
	# Process other list
	filtered_other_dicts = filter_other_dicts(other_list)

	# Create th json file for other list
	write_to_output(filtered_other_dicts, [],"other-posts.json")

	# Send the other list
	send_sell_posts(filtered_other_dicts)

	return True


def clear_json_files(json_files):
	# Loop through the list and open each file in write mode
	for file in json_files:
		with open(file, "w") as f:
			# Write an empty list to the file with indentation of 4
			json.dump([], f, indent=6)
			print("Cleared ", file)
	return True




def main():
	# Set the file path to 'groups.json'
	file_path = "groups.json"

	# Load the JSON data from the file
	with open(file_path, "r") as f:
		data = json.load(f)

	# Iterate over all dictionaries in the list
	for item in data:
		# Check if the dictionary has a 'group_id' key
		if "group_id" in item:
			# Get the group ID
			group_id = item["group_id"]

			# Get the last post time
			group_last_post_time = item["last_post_time"]

			# Try to get the post but send notification to Telegraam if an error occurs 
			# try:
			# Use the get_group_post function to get the group posts
			data = get_group_post(group_id)

			# Search the JSON file to get te most recent posts using datetime_treshold and return last post time
			datetime_threshold = group_last_post_time
			results, last_post_time = search_json_files(data, datetime_threshold)

			# Process the Intents of post
			process_intents(results)

			#Removes any single quotes from code
			process_json('output.json')

			# Categorize intents and Send notification of results
			categorize_intents_and_send_notifications()
			
			# Update last post time
			update_last_post_time(file_path, group_id, last_post_time)
			
			# Clear the json files for a new group
			json_files_to_clear = ["output.json","other-posts.json", "data.json", "attachment.json"]
			clear_json_files(json_files_to_clear)
			# except Exception as e:
				# send_to_telegram(f"There seems to be an error with Group - {group_id} while scraping fro this time threshold - {group_last_post_time}.Please, try to fix before next cycle. \n Heres the error message: {e}")

	print("Done!")



# Run the code

if __name__ == '__main__':
	main()
	