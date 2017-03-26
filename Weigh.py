#!/usr/bin/pythonimport
from HX711 import HX711
from time import sleep
from firebase import getState
from firebase import putState

def getWeight(dout, pdsck):
    offset = 8378000    #max offset allowed incase there is already laundry on the scale
    ref = 300    #calibrated to return weight in grams
    minweight = 500    #min weight needed to prevent 0 return when user takes time to place laundry on weighing scale
    delta = 20    #allowable difference in value range to ensure stable weight returned
    hx = HX711(dout, pdsck)
    hx.set_reading_format("LSB", "MSB")    #reading settings according to hx711 docs
    hx.set_reference_unit(ref)    #divides reading by ref, calibrated to return weight in grams
    hx.reset()    #powers down and up, online sources say it is good practice to do so often
    hx.tare()    #zeros the weighing scale
    #print hx.OFFSET
    if hx.OFFSET >= offset:    #incase users place their laundry on the scale before it is ready to weigh
        print 'Please remove all items from weighing scale'
        while hx.OFFSET >= offset:
            hx.tare()
            #print hx.OFFSET
            hx.reset()
            sleep(0.2)
        sleep(1)    #give time for all weight to be fully removed before zeroing again
        hx.tare()
    print 'Please place your laundry on the weighing scale'
    weight = [0 for i in range(5)]
    count = 0
    while True:
        weight[count] = hx.get_weight(10)
        #print weight
        count += 1
        if count == 5:
            count = 0
        if sum(weight)/5 >= minweight:
            if max(weight) - min(weight) <= delta:
                hx.power_down()
                return sum(weight)/5
        hx.reset()
        sleep(0.2)


def getCost(weight, maxLoad, fullCost):    #returns cost of load for input weight
    pfilled = 0.9    #at minimal how full the washing machine should be to wash
    cost = round(weight/(pfilled*maxLoad)*fullCost,2)
    if cost > fullCost:
        cost = fullCost
    print 'Cost is $%.2f' %(cost)
    return cost

def getMachine(weight):
    pass

#from cleanAndExit import CleanAndExit
#while True:
#    try:
#        dout = 5
#        pdsck = 6
#        weight = getWeight(dout, pdsck)
#        print weight
#        cost = getCost(weight)
#        print '$.2f' %(cost)
#    except (KeyboardInterrupt, SystemExit):
#        cleanAndExit()
