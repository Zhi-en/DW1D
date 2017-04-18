import time
import json, urllib2


class FirebaseApplication():
	def __init__(self, url, token):
		self.url=url
		self.firebaseToken=token

	def put(self, root,node, data):
		json_url=self.url+root+node
		opener = urllib2.build_opener(urllib2.HTTPHandler)
		request = urllib2.Request(json_url+'.json?auth='+self.firebaseToken, 
			data=json.dumps(data))

		request.add_header('Content-Type', 'your/contenttype')
		request.get_method = lambda: 'PUT'
		result = opener.open(request)
		if result.getcode()==200:
			return "OK"
		else:
			return "ERROR"

	def post(self, newnode, data):
		json_url=self.url+newnode		
		opener = urllib2.build_opener(urllib2.HTTPHandler)
		request = urllib2.Request(json_url+'.json?auth='+self.firebaseToken, 
			data=json.dumps(data))

		request.add_header('Content-Type', 'your/contenttype')
		request.get_method = lambda: 'POST'
		result = opener.open(request)
		if result.getcode()==200:
			return "OK"
		else:
			return "ERROR"

	def get(self, node):
		json_url=self.url+node
		opener = urllib2.build_opener(urllib2.HTTPHandler)
		request = urllib2.Request(json_url+'.json?auth='+self.firebaseToken)
		request.get_method = lambda: 'GET'
		result = opener.open(request)
		return json.loads(result.read())

url = 'https://laundry-pool.firebaseio.com/' # URL to Firebase database
token = 'TVEKlcgHcA5QTWOrESZI8aocvLTwUX58BTjhHN1v' # unique token used for authentication
firebase = FirebaseApplication(url, token)

'''Legend:
    Requires studentid,phone,password
    weight = weight of laundry
    fee = how much person has to pay
    machineid = which washing machine person is assigned to
'''
 
def createUser(studentid,password,phone):
    firebase.put('/Accounts/%s/' %(studentid), 'studentid', studentid)
    firebase.put('/Accounts/%s/' %(studentid), 'password', password)
    firebase.put('/Accounts/%s/' %(studentid), 'phonenumber', phone)
    putData(studentid, debt = 'clear')  

def getUsers():
    return firebase.get('/Accounts/').keys()

def resetUsers(studentid = None):
    if studentid == None:
        for studentid in firebase.get('/Accounts/').keys():
            putData(studentid, weight = 'clear', machineid = 'clear', endtime = 'clear', debt = 'clear')
    else:
        putData(studentid, weight = 'clear', machineid = 'clear', endtime = 'clear', debt = 'clear')

def verify(studentid, password):
    return getData(studentid, 'password') == password

def putData(studentid, weight = None, machineid = None, endtime = None, debt = None, pmstate = None):
    if weight != None:
        if type(weight) is str:
            firebase.put('/Accounts/%s/' %(studentid), 'weight', None)
        else:
            firebase.put('/Accounts/%s/' %(studentid), 'weight', weight)
    if machineid != None:
        if type(machineid) is str:
            firebase.put('/Accounts/%s/' %(studentid), 'machineid', None)
        else:
            firebase.put('/Accounts/%s/' %(studentid), 'machineid', machineid)
    if endtime != None:
        if type(endtime) is str:
            firebase.put('/Accounts/%s/' %(studentid), 'endtime', None)
        else:
            firebase.put('/Accounts/%s/' %(studentid), 'endtime', endtime)
    if debt != None:
        try:
            debt += getData(studentid, 'debt')
            firebase.put('/Accounts/%s/' %(studentid), 'debt', debt)
        except TypeError:
            firebase.put('/Accounts/%s/' %(studentid), 'debt', 0)
    if pmstate != None:
        if type(pmstate) is str:
            firebase.put('/Accounts/%s/' %(studentid), 'pmstate', None)
        else:
            firebase.put('/Accounts/%s/' %(studentid), 'pmstate', pmstate)

def getData(studentid, item):
    if type(item) is list:
        outp = []
        for items in item:
            outp.append(firebase.get('/Accounts/%s/%s' %(studentid, items)))
        return tuple(outp)
    else:
        return firebase.get('/Accounts/%s/%s' %(studentid, item))


#studentid = '1001234'
#phone = 98765432
#password = '1234'
#createUser(studentid,password,phone)
#studentid = '1002175'
#phone = 92365431
#password = '1234'
#createUser(studentid,password,phone)