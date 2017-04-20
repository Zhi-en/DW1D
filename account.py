import firebase

url = 'https://laundry-pool.firebaseio.com/' # URL to Firebase database
token = 'TVEKlcgHcA5QTWOrESZI8aocvLTwUX58BTjhHN1v' # unique token used for authentication
firebase = firebase.FirebaseApplication(url, token)

'''Legend:
    Requires studentid,password,phonenumber
    weight = list containing weight of laundry
    machineid = list containing which washing machine user has clothes in
    endtime = list containing estimated time of completion of wash
    debt = accumulated debt of users
    pmstate = for telegrambot to use as timer for pm-ing users every 15min once laundry is ready for collection
'''
 
def createUser(studentid,password,phone):    #creates a user together with the required attributes
    firebase.put('/Accounts/%s/' %(studentid), 'studentid', studentid)
    firebase.put('/Accounts/%s/' %(studentid), 'password', password)
    firebase.put('/Accounts/%s/' %(studentid), 'phonenumber', phone)
    putData(studentid, debt = 'clear')  

def getUsers():    #returns a list of userids
    return firebase.get('/Accounts/').keys()

def resetUsers(studentid = None):    #resets the attributes of users
    if studentid == None:    #if no user input, resets all users
        for studentid in firebase.get('/Accounts/').keys():
            putData(studentid, weight = 'clear', machineid = 'clear', endtime = 'clear', debt = 'clear')
    elif type(studentid) is not list:    #converts inputs to list if not list
        studentid = [studentid]
    for student in studentid:    #clears all users in list
        putData(student, weight = 'clear', machineid = 'clear', endtime = 'clear', debt = 'clear')

def delUsers(studentid = None):    #deletes users
    if studentid == None:    #if no user inpit, deletes all users
        firebase.put('/Accounts/', '', None)
    elif type(studentid) is not list:    #converts input to list if not list
        studentid = [studentid]
    for student in studentid:    #deletes all users in list
        firebase.put('/Accounts/', str(student), None)

def verify(studentid, password):    #checks if userid and password matches
    return getData(studentid, 'password') == password

def putData(studentid, weight = None, machineid = None, endtime = None, debt = None, pmstate = None):    #changes the attributes of users on firebase
    if weight != None:
        if type(weight) is str:    #removes weight attribute (used for command 'clear')
            firebase.put('/Accounts/%s/' %(studentid), 'weight', None)
        else:    #puts weight list
            firebase.put('/Accounts/%s/' %(studentid), 'weight', weight)
    if machineid != None:
        if type(machineid) is str:    #removes machineid attribute
            firebase.put('/Accounts/%s/' %(studentid), 'machineid', None)
        else:    #puts machineid list
            firebase.put('/Accounts/%s/' %(studentid), 'machineid', machineid)
    if endtime != None:
        if type(endtime) is str:    #removes endtime list
            firebase.put('/Accounts/%s/' %(studentid), 'endtime', None)
        else:    #puts endtime list
            firebase.put('/Accounts/%s/' %(studentid), 'endtime', endtime)
    if debt != None:
        try:    #accumulates debt if the type is correct, else resets debt
            debt += getData(studentid, 'debt')
            firebase.put('/Accounts/%s/' %(studentid), 'debt', debt)
        except TypeError:
            firebase.put('/Accounts/%s/' %(studentid), 'debt', 0)
    if pmstate != None:
        if type(pmstate) is str:    #removes pmstate attribute
            firebase.put('/Accounts/%s/' %(studentid), 'pmstate', None)
        else:    #puts pmstate
            firebase.put('/Accounts/%s/' %(studentid), 'pmstate', pmstate)

def getData(studentid, item):    #gets the attributs of users from firebase
    if type(item) is list:    #allows multiple values to be retrieved as a tuple
        outp = []
        for items in item:
            outp.append(firebase.get('/Accounts/%s/%s' %(studentid, items)))
        return tuple(outp)
    else:
        return firebase.get('/Accounts/%s/%s' %(studentid, item))