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
    
    # Print this out for logging purposes:
    print('{}\t{}\t{}'.format(content_type, chat_type, chat_id))

    # Send the response
    welcomeMessage = 'Hello! Thank you for using LaundryPool. \n Please enter your Student/Staff ID to check on your wash status.'
    bot.sendMessage(chat_id,welcomeMessage)
    return


def replyCheck(msg):
    """Called when a message is received, checks to see if to send greeting or send wash info"""
    #extracts the chat ID and text from message
    name = msg["from"]["first_name"]
    chatID = msg["from"]["id"]
    userID = msg["text"]
    
    #Uses Regular Expressions to check for a 7 digit number
    #If it is, tries to get the informaiton from Firebase
    #If its not, sends welcome message
    state = re.match(r'[\d\s]{7}', userID)
    if state!= None:
        get_washInfo(userID,chatID,name)
    else:
        on_get_msg(msg)

def get_washInfo(userID,chatID,name):
    """Called when a user ID is received, accesses Firebase to get informaion"""
    machineid = firebase.get('/Accounts/%s/machineid' %(userID))
    print machineid
    if machineid != None:
        for i in range(len(machineid)):
            reply0 = 'Hello %s! Here are you current washes' %(name)
            reply1 = 'Load %d:' %(i+1)
            status,time = get_machineInfo(machineid[i])
            reply2 = 'Currently %s in Washing Machine %d' %(status,machineid[i])
            reply3 = 'Estimated time left: %s' %(time)
            reply = reply0 + '\n' +reply1 + '\n' + reply2 + '\n' + reply3 + '\n' + '\n'
            bot.sendMessage(chatID,reply)
    else:
        reply = "Sorry %s, you are currently not washing any laundry :(" %(name)
        bot.sendMessage(chatID,reply)

def get_machineInfo(machineid):
    status = 'Washing'
    time = '2 Hours'
    return status,time

    


if __name__ == '__main__':
    # Bot setup stuff
    #load_results_pool()
    bot = telepot.Bot(API_KEY)

    bot.message_loop({'chat': replyCheck})
    print('Now listening...')
    #ID = queryID()
    
    # Main loop
    while True:
        print('Fetching updates...')
        time.sleep(10)
        