#!/usr/bin/pythonimport
def getCost(weight):    #returns cost of load for input weight
    maxload = 10000    #the maximum load of the washing machine in g
    fullcost = 1    #the cost of 1 wash
    pfilled = 0.9    #at minimal how full the washing machine should be to wash
    cost = round(weight/(pfilled*maxload)*fullcost,2)
    return '$%f' %(cost)

#from getWeight import getWeight
#dout = 5
#pdsck = 6
#weight = getWeight(dout, pdsck)
#cost = getCost(weight)
#print cost
