# code adapted from: 
# http://telepot.readthedocs.io/en/latest/#quickly-glance-a-message

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

# Note: api-key is imported from external file
# If you want to use your own just replace config.key with a string containing 
# your API key
API_KEY = config.key

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
        [InlineKeyboardButton(text='Get me something to watch',
                              callback_data='press')]])
    
    # Send the response
    bot.sendMessage(chat_id, 
                    'Hello, what can I do for you today?',
                    reply_markup=keyboard)

def on_callback_query(msg):
    """Called when user taps a button on the custom keyboard"""
    
    # Grab some of the info we need to respond when the user presses buttons
    # on the keyboard we sent to them in on_get_msg()
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    
    # Get a random talk and grab info about it, then compose a reply string.
    # For help on the .format() method below, see: https://pyformat.info/
    title, spkr, date, dur, link = get_random_talk()
    reply_str = 'Try this one:\n' + \
        '"{title}" by {spkr} on {date} ({dur}):\n{link}'.format(**locals())
    
    # Send the reply string. Since answerCallbackQuery() only flashes a 
    # notification to the user, we send them a message too.
    bot.answerCallbackQuery(query_id, text=link)
    bot.sendMessage(from_id, reply_str)
    
    # Then we print this line for logging purposes
    print('Response sent for {}'.format(query_id))

def load_results_pool():
    """Creates a list of random talks (stored as dicts) as global 'talks'"""
    
    # We declare 'talks' a global so we can access this list easily from
    # other functions outside of load_results_pool()
    global talks
    
    # To grab and parse talks, first connect to the TED Talks page
    r = requests.get('https://www.ted.com/talks')
    
    # Use BeautifulSoup to parse the page so we can access data on it easily
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Shorthands
    # I made a bunch of shorthands so the code is easier to read.
    # Basically it compiles some maps some methods from BeautifulSoup to
    # more readable names.
    # For to understand how lamdba works, try typing this into Python:
    #   >>> foo = lambda x: x ** 2
    #   >>> foo(3)  # You should get 9
    p_s = lambda x: x.previous_sibling
    _get_speaker = lambda x: x.find(class_='talk-link__speaker').text
    _get_date = lambda x: ' '.join(x.find(class_='meta__item').text.split()[1:])
    # Note: p_s(p_s(x)) is equiv to x.previous_sibling.previous_sibling
    _get_duration = lambda x: p_s(p_s(x)).find(class_='thumb__duration').text
    _get_title = lambda x: ' '.join(x.a.text.split()).strip()
    _get_link = lambda x: 'https://www.ted.com' + x.a['href']

    # We use a list comprehension below to compile all the data we need about
    # each talk into a dictionary. Help on list comprehensions:
    # http://treyhunner.com/2015/12/python-list-comprehensions-now-in-color/
    # Basically: 
    #   squares = [x ** 3 for x in range(3)]
    # is shortform for:
    #   squares = []
    #   for x in range(3): squares.append(x ** 2)
    # Dictionary comprehensions are a thing too:
    #   cubes = {i: i ** 3 for i in range(3)}
    # is shortform for:
    #   cubes = {}
    #   for i in range(3): cibes[i] = i ** 3
    
    # Below, we take the list returned by soup.find_all() and for each x in it,
    # we call some of the lambda functions above on x and use that to write a
    # dictionary of info. In the end, we get a list of dicts containing talk 
    # info called 'talks'. Since we declared the name 'talks' as a global var, 
    # we can access this list from anywhere in the script.
    talks = [{'speaker': _get_speaker(x),
              'date': _get_date(x),
              'title': _get_title(x),
              'duration': _get_duration(x),
              'link': _get_link(x)}
             for x in soup.find_all('div', class_='media__message')]

def get_random_talk():
    """Called by callback query. Returns data from a random talk in 'talks'"""
    
    # We declare 'talks' global so Python knows when we say 'talks' within this
    # function, we're talking about the global 'talks' that we created using
    # load_results_pool()
    global talks
    
    # We use randint to get a random item index from the 'talks' list to select
    # a talk randomly.
    random_talk = talks[randint(0, len(talks) - 1)]
    
    # We break up the info into vars then return them. There are lazier ways
    # to do this too, like:
    #   return map(random_talk.get, random_talk.keys())
    # ...if you don't like typing.
    title = random_talk['title']
    spkr = random_talk['speaker']
    date = random_talk['date']
    dur = random_talk['duration']
    link = random_talk['link']
    
    return title, spkr, date, dur, link

if __name__ == '__main__':
    # Bot setup stuff
    load_results_pool()
    bot = telepot.Bot(API_KEY)
    bot.message_loop({'chat': on_get_msg,
                      'callback_query': on_callback_query})
    print('Now listening...')
    
    # Main loop
    while True:
        print('Fetching updates...')
        time.sleep(10)