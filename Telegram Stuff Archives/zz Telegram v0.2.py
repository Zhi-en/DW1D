# Modules needed for running Telegram bot:
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# Modules needed to open and access info from websites:
import json
import requests
from bs4 import BeautifulSoup
# Modules for processing that info:
import time
from random import randint
# Config for bot to run
import config
from pprint import pprint
# Firebase stuff
from firebase import firebase

fburl = 'https://laundry-pool.firebaseio.com/' # URL to Firebase database
fbtoken = 'TVEKlcgHcA5QTWOrESZI8aocvLTwUX58BTjhHN1v' # unique token used for authentication
firebase = firebase.FirebaseApplication(fburl, fbtoken)


# Bot Key (get from bot_father)
API_KEY = '351253681:AAH5UPmKm6StPZrPF1VfYU7PeHf8FGxTSK8'
botURL = "https://api.telegram.org/bot{}/".format(API_KEY)

'''Functions for text responses'''
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = botURL + "getUpdates"
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    url = botURL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)
    
    
'''offsets parameter to only get most recent message'''
def get_updates(offset=None):
    url = botURL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

'''calculates the highest ID of all the updates'''    
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)
    


if __name__ == '__main__':
    last_update_id = None
    bot = telepot.Bot(API_KEY)
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            #
        print('Fetching updates...')
        time.sleep(10)