#from HX711 import HX711
from time import sleep


class weighingScale(object):
    def __init__(self,dout,pdsck,maxLoad):
        self.hx=HX711(dout,pdsck)
        self.maxLoad = maxLoad
    def tareScale(self):
        offset = 8900000    #max offset allowed incase there is already laundry on the scale (calculated by adding about 700g*280 to offset without weight)
        ref = 280    #calibrated to return weight in grams
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
        minweight = 500    #min weight of 500g needed for readings to start
        weight = self.hx.get_weight(10)    #returns the average of 10 readings
        self.hx.reset()
        if weight < minweight:
            return 'Please place laundry on the weighing scale'
        elif weight > self.maxLoad*1000:    #prevents overloading the washing machine
            return 'Your laundry load is too heavy, please wash in 2 loads'
        else:
            return weight/1000.0
    def offScale(self):
        self.hx.power_down()


def getCost(weight, maxLoad, fullCost, pfilled):    #returns cost of load for input weight calculated proportionally by weight where pfilled*maxLoad is fullcost since hitting that weight starts wash
    cost = round(weight/(pfilled*maxLoad)*fullCost,2)
    if cost > fullCost:
        cost = fullCost
    return cost


#import RPi.GPIO as GPIO
#dout = 5
#pdsck = 6
#scale = weighingScale(dout, pdsck, 10)
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
