#!/usr/bin/pythonimport
from cleanAndExit import cleanAndExit
from weigh import getWeight    #gets weight of laundry
from weigh import getCost    #gets cost of wash
from weigh import getMachine    #gets optimal washing machine to use
from soap import giveSoap    #dispenses soap when cup is detected
from firebase import userData    #checks/upload user data to firebase
from firebase import machineState    #checks/changes the state of any washing machine
import time

NumofMachines = 3

try:
    while True:
        if time.time() - openTime > 60 and openTime != -1:
            allClosed = True
            for i in range(NumofMachines):
                if machineState(i) == 'Open':
                    print 'Please Close the door of Washing Machine %d' %(i)
                    allClosed = False
            if allClosed:
                openTime = -1
        washOrCollect = raw_input('Wash or Collect')
        if washOrCollect == 'Collect':
            user = raw_input('User')
            machineNum = userData('something')    #checks the id, returns None if no laundry else returns machine number
            print 'Collect laundry from Washing Machine %d' %(machineNum)
            machineState('Open', machineNum)    #im using these functions very loosely since they arent defined
            openTime = time.time()
            continue
        elif washOrCollect == 'Wash':
            poolOrPrivate = raw_input('Pool or Private')
            if poolOrPrivate == 'Private':
                user = raw_input('User')
                print 'Cost is $1'
                for i in range(NumofMachines):
                    if machineState(i) == 'Empty':
                        machineNum = i
                        break
                giveSoap()
                print 'Place laundry in Washing Machine %d' %(machineNum)
                machineState('Open', machineNum)
                openTime = time.time()
                continue
            elif poolOrPrivate == 'Pool':
                weight = getWeight()
                cost = getCost(weight)
                machineNum = getMachine(weight)
                print 'The Cost is %f' %(cost)
                user = raw_input('User')
                
                
        
        
        
        
except (KeyboardInterrupt, SystemExit):
    cleanAndExit()