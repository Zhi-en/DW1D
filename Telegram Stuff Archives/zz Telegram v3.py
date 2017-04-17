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
#Regular Expression
import re

fburl = 'https://laundry-pool.firebaseio.com/' # URL to Firebase database
fbtoken = 'TVEKlcgHcA5QTWOrESZI8aocvLTwUX58BTjhHN1v' # unique token used for authentication
firebase = firebase.FirebaseApplication(fburl, fbtoken)


# Bot Key (get from bot_father)
API_KEY = '351253681:AAH5UPmKm6StPZrPF1VfYU7PeHf8FGxTSK8'
botURL = "https://api.telegram.org/bot{}/".format(API_KEY)


def on_get_msg(msg):
    """Called when a message is received, sends a greeting & custom keyboard"""
    
    # telepot.glace() lets us grab the important info we need to handle 
    # requests to the bot from a user
    content_type, chat_type, chat_id = telepot.glance(msg)
    
    # We print this out for logging purposes:
    print('{}\t{}\t{}'.format(content_type, chat_type, chat_id))
    
    # Prepare a reponse for the user:
    # We create an inline keyboard as a reply. For info, see:
    # https://core.telegram.org/bots#inline-keyboards-and-on-the-fly-updating
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Check Laundry Status',
                              callback_data='press')]])
                              
    
    # Send the response
    bot.sendMessage(chat_id, 
                    'Hello, what can I do for you?',
                    reply_markup=keyboard)
    return

def on_callback_query(msg):
    """Called when user taps a button on the custom keyboard"""
    
    # Grab some of the info we need to respond when the user presses buttons
    # on the keyboard we sent to them in on_get_msg()
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    
    # Asks user for student ID, then checks firebase for time left.
    # For help on the .format() method below, see: https://pyformat.info/
    reply = "Can I have your student/staff ID?"
    bot.sendMessage(from_id, reply)
    
    
    
    #status,time = get_washInfo()
    bot.sendMessage(from_id, time)
    
    '''reply_str = 'Try this one:\n' + \
        '"{title}" by {spkr} on {date} ({dur}):\n{link}'.format(**locals())
    
    # Send the reply string. Since answerCallbackQuery() only flashes a 
    # notification to the user, we send them a message too.
    bot.answerCallbackQuery(query_id, text=link)
    bot.sendMessage(from_id, reply_str)'''
    
    # Then we print this line for logging purposes
    print('Response sent for {}'.format(query_id))


def replyCheck(msg):
    ID = msg["text"]
    """Called when a message is received, checks to see if to send greeting or send time"""
    state = re.match(r'[\d\s]{7}', msg["text"])
    if state!= None:
        get_washInfo(ID)
    else:
        on_get_msg(msg)

def get_washInfo(studentid):
    machineid = firebase.get('/Accounts/%s/machineid' %(studentid)) 
    
    print machineid


if __name__ == '__main__':
    # Bot setup stuff
    #load_results_pool()
    bot = telepot.Bot(API_KEY)

    bot.message_loop({'chat': replyCheck,
                    'callback_query': on_callback_query})
    print('Now listening...')
    #ID = queryID()
    
    # Main loop
    while True:
        print('Fetching updates...')
        time.sleep(10)
        