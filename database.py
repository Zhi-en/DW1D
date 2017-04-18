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


url = 'https://laundry-pool.firebaseio.com/'
token = 'TVEKlcgHcA5QTWOrESZI8aocvLTwUX58BTjhHN1v'
firebase = FirebaseApplication(url, token)

'''Legend:
    machine: machine number
    door: 0 is closed, 1 is input time openned
    state: 0 is empty, -1 is washing, -2 is collecting, for pooling: time first user placed laundry in
    weight: float value
'''


def initMachines(number):
    for machine in range(number + 1)[1:]:
        putState(machine, door = 0, state = 0, studentid = 'clear', weight = 'clear')
        firebase.put('/washingmachine/%d/' %(machine), 'id', machine)


def clearMachines():
    for machine in firebase.get('/washingmachine/')[1:]:
        firebase.put('/washingmachine/', str(machine['id']), None)


def putState(machine, door = None, state = None, weight = None, studentid = None):
    if door != None:
        if door == 0:
            firebase.put('/washingmachine/%d/' %(machine), 'door', door)
        elif door == 1:
            firebase.put('/washingmachine/%d/' %(machine), 'door', time.time())
    if state != None:
        firebase.put('/washingmachine/%d/' %(machine), 'state', state)
    if weight != None:
        try:
            weight += getState(machine, 'weight')
            firebase.put('/washingmachine/%d/' %(machine), 'weight', weight)
        except TypeError:
            firebase.put('/washingmachine/%d/' %(machine), 'weight', 0.0)
    if studentid != None:
        if studentid == 'clear':
            firebase.put('/washingmachine/%d/' %(machine), 'studentid', None)
        else:
            firebase.put('/washingmachine/%d/' %(machine), 'studentid', studentid)


def getState(machine, item):
    return firebase.get('/washingmachine/%d/%s' %(machine, item))

    
def getDoor():
    for machine in firebase.get('/washingmachine/')[1:]:
        if machine['door'] != 0:
            if time.time() - machine['door'] > 2*60:    #if door is left open for > 2 minutes, informs user to close door
                return machine['id']


def getWash(timeOut):
    for machine in firebase.get('/washingmachine/')[1:]:
        if machine['state'] > 0:
            if time.time() - machine['state'] > timeOut:
                return machine['id']

def getMachine(weight, maxLoad, pfilled):    #to further improve, should incorporate time factor
    idls = []
    weightls = []
    timels = []
    removels = []
    for machine in firebase.get('/washingmachine/')[1:]:
        if machine['state'] >= 0:
            idls.append(machine['id'])
            weightls.append(machine['weight'])
            if machine['state'] == 0:
                timels.append(0)
            else:
                timels.append(time.time() - machine['state'])
    if idls == []:
        return 0, 'All washing machines are full\nSorry for the inconvenience caused'    #if all washing machines in washing/collecting state
    timels, weightls, idls = zip(*sorted(zip(timels, weightls, idls), reverse = True))    #sorts lists based on time in laundry
    timels, weightls, idls = list(timels), list(weightls), list(idls)    #converts tuples back to strings
    for machine in range(len(idls)):
        if weightls[machine] + weight > maxLoad:    #removes options that give an overloaded washing machine
            removels.append(machine)
        elif weightls[machine] + weight > pfilled*maxLoad:    #if sufficiently filled, use this
            return -1, idls[machine]
    if removels != []:
        for machine in sorted(removels, reverse = True):
            timels.remove(timels[machine])
            weightls.remove(weightls[machine])
            idls.remove(idls[machine])
    if idls == []:
        return 0, 'All washing machines are full\nSorry for the inconvenience caused'    #if all options removed due to overloading, all are full
    for machine in range(len(idls)):
        if weightls[machine] != 0 and weightls[machine] + weight < 0.6*maxLoad:    #if lightest final load of at least 2 people's laundry is < 2/3 of maxLoad, place in that machine
            return 0, idls[machine]
    for machine in range(len(idls)):
        if weightls[machine] + weight > (2*pfilled - 1)*maxLoad:    #if biggest final load is > 2pfilled - 1 of maxLoad, place in that machine and wash (equivalent losses to earnings of firt if statement better than starting a new machine)
            return -1, idls[machine]
    if weightls[-1] == 0:    #if there are empty machines, place laundry in them
        return 0, idls[-1]
    else:    #if really no choice, just wash the biggest load
        return -1, idls[0]
        

#initMachines(3)
#putState(1, door = 1)
#while True:
#    if getDoor() != None:
#        print getDoor()
#        break
#    else:
#        print 'None'
#putState(2, state = 2, weight = 10)
#print getState(2, 'state')
#print getState(2, 'weight')
#initMachines(3)