from ntptime import time
import firebase

url = 'https://laundry-pool.firebaseio.com/'
token = 'TVEKlcgHcA5QTWOrESZI8aocvLTwUX58BTjhHN1v'
firebase = firebase.FirebaseApplication(url, token)

'''Legend:
    machine: machine number
    door: 0 is closed, 1 is input time openned
    state: 0 is empty, -1 is washing, -2 is collecting, for pooling: time first user placed laundry in
    weight: float value
    studentid: list of users with laundry in machine
'''


def initMachines(number):    #creates the specified number of machines on firebase
    for machine in range(number + 1)[1:]:
        putState(machine, door = 0, state = 0, studentid = 'clear', weight = 'clear')
        firebase.put('/washingmachine/%d/' %(machine), 'id', machine)


def clearMachines():    #removes all machines from firebase
    for machine in firebase.get('/washingmachine/')[1:]:
        firebase.put('/washingmachine/', str(machine['id']), None)


def putState(machine, door = None, state = None, weight = None, studentid = None):    #changes the attributes of the machines on firebase
    if door != None:
        if door == 0:    #0 is the command that door is closed
            firebase.put('/washingmachine/%d/' %(machine), 'door', door)
        elif door == 1:    #1 is the command that door is opened and puts time of openning
            firebase.put('/washingmachine/%d/' %(machine), 'door', time())
    if state != None:
        firebase.put('/washingmachine/%d/' %(machine), 'state', state)
    if weight != None:
        try:    #accumulates weight if the type is correct, else clears all the weight
            weight += getState(machine, 'weight')
            firebase.put('/washingmachine/%d/' %(machine), 'weight', weight)
        except TypeError:
            firebase.put('/washingmachine/%d/' %(machine), 'weight', 0.0)
    if studentid != None:
        if studentid == 'clear':    #clears the list of studentids
            firebase.put('/washingmachine/%d/' %(machine), 'studentid', None)
        else:    #puts studentid list
            firebase.put('/washingmachine/%d/' %(machine), 'studentid', studentid)


def getState(machine, item):    #gets the attributes of the machines from firebase
    if type(item) is list:    #allows multiple values to be retrieved as a tuple
        outp = []
        for items in item:
            outp.append(firebase.get('/washingmachine/%d/%s' %(machine, items)))
        return tuple(outp)
    else:
        return firebase.get('/washingmachine/%d/%s' %(machine, item))

    
def getDoor():
    for machine in firebase.get('/washingmachine/')[1:]:
        if machine['door'] != 0:
            if time() - machine['door'] > 2*60:    #if door is left open for > 2 minutes, informs user to close door
                return machine['id']


def getWash(timeOut):
    for machine in firebase.get('/washingmachine/')[1:]:
        if machine['state'] > 0:
            if time() - machine['state'] > timeOut:    #if the laundry has been left in washing machine for too long, retrieves the washing machine number
                return machine['id']

def getMachine(weight, maxLoad, pfilled):    #optimises machine to place laundry in by prioritising waiting time of users given several conditions
    idls = []
    weightls = []
    timels = []
    removels = []
    for machine in firebase.get('/washingmachine/')[1:]:    #gets all the machines and their current laundry weights and time since first user placed laundry inside
        if machine['state'] >= 0:
            idls.append(machine['id'])
            weightls.append(machine['weight'])
            if machine['state'] == 0:
                timels.append(0)
            else:
                timels.append(time() - machine['state'])
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
        return 0, 'All washing machines are full\nSorry for the inconvenience caused'    #if all options removed due to overloading, no machines available
    for machine in range(len(idls)):
        if weightls[machine] != 0 and weightls[machine] + weight < 0.6*maxLoad:    #if final load of at least 2 people's laundry is < 2/3 of maxLoad, place in that machine
            return 0, idls[machine]
    for machine in range(len(idls)):
        if weightls[machine] + weight > (2*pfilled - 1)*maxLoad:    #if biggest final load is > 2pfilled - 1 of maxLoad, place in that machine and wash (equivalent losses to earnings of firt if statement better than starting a new machine)
            return -1, idls[machine]
    if weightls[-1] == 0:    #if there are empty machines, place laundry in them
        return 0, idls[-1]
    else:    #if really no choice, just wash the longest waiting load
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