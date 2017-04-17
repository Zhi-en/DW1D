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
    state: 0 is pooling, 1 is washing, 2 is collecting
    weight: float value
'''


def initMachines(number):
    for machine in range(number + 1)[1:]:
        putState(machine, door = 0, state = 0, weight = 0)
        firebase.put('/washingmachine/%d/' %(machine), 'id', machine)


def putState(machine, door = None, state = None, weight = None):
    if door != None:
        if door == 0:
            firebase.put('/washingmachine/%d/' %(machine), 'door', door)
        elif door == 1:
            firebase.put('/washingmachine/%d/' %(machine), 'door', time.time())
    if state != None:
        firebase.put('/washingmachine/%d/' %(machine), 'state', state)
    if weight != None:
        if type(weight) is float:
            weight += getState(machine, 'weight')
            firebase.put('/washingmachine/%d/' %(machine), 'weight', weight)
        else:
            firebase.put('/washingmachine/%d/' %(machine), 'weight', 0)


def getState(machine, item):
    return firebase.get('/washingmachine/%d/%s' %(machine, item))

    
def getDoor():
    for machine in firebase.get('/washingmachine/')[1:]:
        if machine['door'] != 0:
            if time.time() - machine['door'] > 2*60:    #if door is left open for > 2 minutes, informs user to close door
                return machine['id']


def getMachine(weight, maxLoad):    #to further improve, should incorporate time factor
    idls = []
    initialweight = []
    finalweight = []
    for machine in firebase.get('/washingmachine/')[1:]:
        if getState(machine['id'], 'state') == 0:
            idls.append(machine['id'])
            initialweight.append(machine['weight'])
            finalweight.append(machine['weight'] + weight)
    finalweight, initialweight, idls = zip(*sorted(zip(finalweight, initialweight, idls)))    #sorts lists based on final weights
    if finalweight[-1] > 0.85*maxLoad:    #if biggest final load is > 85% of maxLoad, place in that machine and wash
        for machine in range(len(idls))[::-1]:
            if finalweight[machine] < maxLoad:
                return 1, idls[machine]
        else:    #all the final weights exceed max load
            return 0, 'All washing machines are full\nSorry for the inconvenience caused'
    for machine in range(len(idls)):
        if initialweight[machine] != 0 and finalweight[machine] < 0.65*maxLoad:    #if lightest final load of at least 2 people's laundry is < 65% of maxLoad, place in that machine
            return 0, idls[machine]
    if finalweight[-1] > 0.75*maxLoad:    #if biggest final load is >75% of maxLoad, place in that machine and wash (greater losses but better than starting a new machine)
        return 1, idls[-1]
    elif initialweight[0] == 0:    #if there are empty machines, place laundry in them
        return 0, idls[0]
    else:    #if really no choice, just wash the biggest load
        return 1, idls[-1]
        

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