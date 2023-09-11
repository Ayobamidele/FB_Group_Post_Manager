import pyautogui
import time
import webbrowser



def comment_on_post(post_url, comment):
	# Open a new browser window and navigate to the Facebook login page
	webbrowser.open("https://www.facebook.com/login")
	time.sleep(5)

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

