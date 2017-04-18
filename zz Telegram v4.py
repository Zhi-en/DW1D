# Modules needed for running Telegram bot:
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# Modules needed to open and access info from websites:
import requests
from bs4 import BeautifulSoup
# Modules for processing that info:
import time
from random import randint
# Config for bot to run
import config
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
    #print msg
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
    #Returns an array of the machines used
    machineid = firebase.get('/Accounts/%s/machineid' %(userID))
    
    #For our reference here in python
    print "Washing Machines used: %r" %(machineid)
    
    #Checks if entered user ID has any washes
    if machineid != None:        
        #Gets the chat ID from firebase
        chatIDcheck = firebase.get('/Accounts/%s/chatID' %(userID))
        
        #If it doesn't exist, add it to firebase
        if chatIDcheck == None:
            chatIDcheck = chatID
            firebase.put('Accounts/%s/' %(userID),'chatID',chatID)
            
        #Checks if user matches the chat ID  
        #Matches: Sends reply  
        if chatIDcheck == chatID:
            #Prints for our reference
            print "Replying to %r's query"%(chatID)
            reply0 = 'Hello %s! Here are your current washes' %(name)
            bot.sendMessage(chatID,reply0)
            
            if len(machineid) == 1:
                reply1 = makeReply(userID,machineid,0)
                bot.sendMessage(chatID,reply1)
            else:
                for i in range(len(machineid)):
                    reply0 = 'Load %d:\n' %(i+1)
                    reply1 = makeReply(userID,machineid,i)
                    reply = reply0 + reply1
                    bot.sendMessage(chatID,reply)
        #Does not match: ask user to enter own ID (the userid tagged to chatid)
        else:
            #Prints for our reference
            print "%r did not enter id tagged to him."%(chatID)
            reply = "Sorry, please enter your own ID."
            bot.sendMessage(chatID,reply)
            
    #If no machines under current user, returns an error message
    else:
        userIDcheck = firebase.get('/Accounts/%s' %(userID))
        #checks if entered userID exists in database
        if userIDcheck == None:
            #Prints for our reference
            print "Invalid ID entered"
            reply = "Sorry, this ID is not registered. Please create and account."
        else:
            #Prints for our reference
            print "%r is not washing any laundry."%(chatID)
            reply = "Sorry %s, you are currently not washing any laundry :(" %(name)
        bot.sendMessage(chatID,reply)

def makeReply(userID,machineid,i):
    """Called when creating a reply to the user, returns information in a string"""
    status = get_machineInfo(machineid[i]) #get machine status
    time = get_time(userID,i) #get time remaining
    reply2 = 'Currently %s in Washing Machine %d' %(status,machineid[i])
    reply3 = 'Estimated time left: %r' %(time)
    
    if time == 0:
        reply = reply2 + '\n' + '\n'
    else:
        reply = reply2 + '\n' + reply3  + '\n'
    return reply

def get_machineInfo(machineid):
    """Called when makeReply is getting washInfo, to get information on washing machine"""
    #Gets state of washing machine
    status = firebase.get('/washingmachine/%r/state' %(machineid))
    print "Machine %r status: %r" %(machineid,status) #for reference
    if status > 0:
        status = 'pooling'
    elif status == -1:
        status = 'washing'
    elif status == -2:
        status = '* ready for collection *'
    else:
        status = 'Machine not in use'
    return status

def get_time(userID,i):
    """Called when makeReply is getting washInfo, to get information on time remaining"""
    endTimeList = firebase.get('/Accounts/%s/endtime' %(str(userID)))
    currentTime = time.time()
    #If endtime is not logged returns error
    if endTimeList == None:
        return None
    else:
        iTime = endTimeList[i]
        diff = iTime - currentTime
        if diff > 0:
            return formatTime(diff)
        else:
            return 0

def formatTime(time):
    """Called when get_time is formatting time to a string"""
    if time > 3600:
        hours = time/3600
        minutes = (time%3600)/60
        #seconds = (time%3600)%60
        return "%d Hours and %02d Minutes" %(hours,minutes)
    elif time > 60:
        minutes = time/60
        seconds = time%60
        return "%d Minutes and %02d Seconds" %(minutes,seconds)
    else:
        seconds = time
        return "%02d Seconds" %(seconds)
    
def checkMachines():
    """Called when periodically by main() to check washing machine states"""
    #Repeats for all 3 Washing Machines (wm)
    for i in range (3):
        #Gets state of wm
        wm = firebase.get('/washingmachine/%s/state'%(str(i+1)))
        #If wash is ready for collection
        if wm == -2:
            #Gets Users assigned to this wm
            users = firebase.get('/washingmachine/%s/studentid'%(str(i+1)))
            #For all assgined users
            for j in users:
                #Get their chatID and pmState
                ID = firebase.get('/Accounts/%s/chatID' %(str(j)))
                pmState = firebase.get('/Accounts/%s/pmstate' %(str(j)))
                #If pmState does not exist, add it
                if pmState == None:
                    firebase.put('/Accounts/%s/' %(str(j)),"pmstate",1)
                    pmState = 0
                #change pmState to 0 after 15mins
                elif pmState < 90:
                    pmState += 1
                    firebase.put('/Accounts/%s/' %(str(j)),"pmstate",pmState)
                else:
                    pmState = 0
                    firebase.put('/Accounts/%s/' %(str(j)),"pmstate",pmState)
                #If chatID exists and pmState = 0, pm the user
                if ID != None and pmState == 1: 
                    #Prints message for our reference
                    print "Messenging user: %r"%(ID)
                    #PMs user 
                    reply = "Hello! Your laundry in washing machine %r is now ready for collection!"%(i+1)
                    bot.sendMessage(ID,reply)
    
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
        checkMachines()
        time.sleep(10)
    