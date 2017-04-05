#Requires function to tell user door is open when door is open for >= 1min

import time


class WashingMachine(object):
    def __init__(self,machineid):
        self.machineid = machineid
        self.weight = 0
        self.OCstate = "Closed"
        self.PWCstate = "Pooling"
        self.startTime = 0
           
    def doorOpen(self):
        self.OCstate = "Open"
        self.startTime = time.time()
    
    def doorClose(self):
        self.OCstate = "Closed"
        
    def startWash(self):
        self.PWCstate = "Wash"
    
    def endWash(self):
        self.PWCstate = "Collect"
    
    def addWeight(self,weight):
        self.weight += weight
    
    def minusWeight(self,weight):
        self.weight -= weight
        if self.weight<=0:
            self.weight = 0
            self.PWCstate = "Pooling"
        
    def DoorTime(self):
        currentTime - time.time()
        if currentTime - startTime > 60 and self.OCstate == "Open":
            #door is open function
            pass
        
        

        
        
    
        