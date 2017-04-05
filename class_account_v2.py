#Requires weight, fee, and machineid
#weight = weight of laundry
#fee = how much person has to pay
#machineid = which washing machine person is assigned to


class account(object):
    def __init__(self,name,contact,balance=0):
        self.name = name
        self.info = {"contact":contact,"machineid":None, "time":None, "weight":None}
        self.balance = balance
    
    def charge(self,value):
        self.balance += value
        
    def wash(self,weight,fee,machineid):
        self.charge(fee)
        self.info["machineid"] = machineid
        self.info["weight"] = weight

        
        
    
        