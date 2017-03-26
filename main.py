#!/usr/bin/pythonimport

#import functions
import RPi.GPIO as GPIO
from cleanAndExit import cleanAndExit
from weigh import getWeight    #gets weight of laundry
from weigh import getCost    #gets cost of wash
from weigh import getMachine    #gets optimal washing machine to use, automatically updates washing machine weight data
from soap import giveSoap    #dispenses soap when cup is detected
from firebase import getData    #gets machineNum, weight from firebase in the form (userid)
from firebase import putData    #puts data on firebase in the form (userid, contact = str, machineNum = int, weight = int)
from firebase import getState    #gets the state of any washing machine in the form (machineNum, 'door'/'state'/'weight')
from firebase import putState    #puts the state of any washing machine in the form (machineNum, door = 'open'/'closed', state = 'pooling'/'washing'/'collecting', weight = float)
import time

#set GPIO pins
GPIO.setmode(GPIO.BCM)
dout = 5
pdsck = 6
sonar = 0 #change
motor = 0 #change
GPIO.setup(dout, GPIO.IN)
GPIO.setup(pdsck, GPIO.OUT)
GPIO.setup(sonar, GPIO.IN)
GPIO.setup(motor, GPIO.OUT)

#set global variables
NumofMachines = 3
maxLoad = 10000    #maximum laundry load of washing machine in g
fullCost = 1.0    #cost of one wash in $
openTime = -1

try:
    while True:
        if time.time() - openTime > 60 and openTime != -1:   #There should be a better way of ensuring all washing machine doors are closed properly
            allClosed = True
            for i in range(NumofMachines):
                if getState(i, 'door') == 'open':
                    print 'Please Close the door of Washing Machine %d' %(i)
                    allClosed = False
            if allClosed:
                openTime = -1
        washOrCollect = raw_input('Wash or Collect')
        if washOrCollect == 'Collect':
            user = raw_input('UserID')
            machineNum, weight = getData(user)
            if machineNum == 0:
                print 'You do not have any laundry to collect'
                time.sleep(10)
                continue
            putData(user, machineNum = 0, weight = 0)
            print 'Collect laundry from Washing Machine %d' %(machineNum)
            weight = getState(machineNum, 'weight') - weight
            if weight == 0:
                putState(machineNum, door = 'open', state = 'collecting', weight = weight)
            else:
                putState(machineNum, door = 'open', weight = weight)
            openTime = time.time()
            continue
        elif washOrCollect == 'Wash':
            poolOrPrivate = raw_input('Pool or Private')
            if poolOrPrivate == 'Private':
                weight = maxLoad
            elif poolOrPrivate == 'Pool':
                weight = getWeight()
            cost = getCost(weight, maxLoad, fullCost)
            machineNum, state = getMachine(weight)
            user = raw_input('UserID')
            #add in some check if user not in database to add new account
            putData(user, machineNum = machineNum, weight = weight)    #assumes user is not washing multiple loads or it will override
            if state == 'washing':
                giveSoap()
            print 'Please put laundry in Washing Machine %d' %(machineNum)
            putState(machineNum, door = 'open', state = state)
            
            
except (KeyboardInterrupt, SystemExit):
    cleanAndExit()