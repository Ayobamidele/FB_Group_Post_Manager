import pyautogui
import time
import webbrowser
import json


# Open a new browser window and navigate to the Facebook login page
webbrowser.open("https://www.facebook.com/login")
time.sleep(5)


def comment_on_post(post_url, comment):	
	time.sleep(5)
	# Navigate to the post URL
	pyautogui.hotkey("ctrl", "l")
	pyautogui.typewrite(post_url)
	pyautogui.press("enter")
	time.sleep(5)

	# Find the comment box using image recognition and click on it
	comment_box = pyautogui.locateOnScreen("comment_box.png")
	if comment_box:
		print("seen")
		pyautogui.click(comment_box)
		pyautogui.typewrite(comment)
		pyautogui.press("enter")


def extract_intent_and_url(json_files):
	# Get all the data from the json files and put them together in a list
	data = []
	for file in json_files:
		with open(file, 'r') as f:
			data_ = json.load(f)
			if data_:
				data.extend(data_)
	
	# Check if there any data in the list befrore commenting
	if data:
		for item in data:
			intent = item.get('intent')
			url = item.get('post_url')

			if intent == "buy":
				comment_on_post(url,"Message for Buy posts.")
			elif intent == "rent":
				comment_on_post(url,"Message for Rent posts.")
