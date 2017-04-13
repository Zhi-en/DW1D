#!/usr/bin/pythonimport
from HX711 import HX711
from time import sleep
#from firebase import getState
#from firebase import putState

class weighingScale(object):
    def __init__(self,dout,pdsck):
        self.hx=HX711(dout,pdsck)
    def tareScale(self):
        offset = 8920000    #max offset allowed incase there is already laundry on the scale
        ref = 300    #calibrated to return weight in grams
        self.hx.set_reading_format("LSB", "MSB")    #reading settings according to hx711 docs
        self.hx.set_reference_unit(ref)    #divides reading by ref, calibrated to return weight in grams
        self.hx.reset()    #powers down and up, online sources say it is good practice to do so often
        self.hx.tare()    #zeros the weighing scale
#        print self.hx.OFFSET
        if self.hx.OFFSET >= offset:    #incase users place their laundry on the scale before it is ready to weigh
            return 'Please remove all items from weighing scale'
        else:
            sleep(1)    #gives time for all weight to be removed before retaring to give an accurate tare
            self.hx.tare()
            return 'Please place laundry on the weighing scale'
    def getWeight(self):
        minweight = 1000    #min weight needed to prevent 0 return when user takes time to place laundry on weighing scale
        weight = self.hx.get_weight(10)
        self.hx.reset
        if weight < minweight:
            return 'Please place laundry on the weighing scale'
        else:
            return weight/1000.0
    def offScale(self):
        self.hx.power_down()


def getCost(weight, maxLoad, fullCost):    #returns cost of load for input weight
    pfilled = 0.9    #at minimal how full the washing machine should be to wash
    cost = round(weight/(pfilled*maxLoad)*fullCost,2)
    if cost > fullCost:
        cost = fullCost
    return cost

def getMachine(weight):
    pass


#import RPi.GPIO as GPIO
#dout = 5
#pdsck = 6
#scale = weighingScale(dout, pdsck)
#print scale.tareScale()
#while True:
#    try:
#        weight = scale.getWeight()
#        print weight
#        if type(weight) is str:
#            continue
#        cost = getCost(weight,10,1)
#        print cost
#    except (KeyboardInterrupt, SystemExit):
#        GPIO.cleanup()
