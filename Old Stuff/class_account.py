from firebase import firebase
import time

url = 'https://laundry-pool.firebaseio.com/' # URL to Firebase database
token = 'TVEKlcgHcA5QTWOrESZI8aocvLTwUX58BTjhHN1v' # unique token used for authentication

# Create a firebase object by specifying the URL of the database and its secret token.
# The firebase object has functions put and get, that allows user to put data onto 
# the database and also retrieve data from the database.
firebase = firebase.FirebaseApplication(url, token)

print "Reading from my database."
print firebase.get('/Name') # get the value from the node age

class account(object):
    def __init__(self,name,contact,balance=0):
        self.name = name
        self.info = {"contact":contact,"machineid":None, "time":None, "weight":None}
        self.balance = balance
    
    def withdraw(self,value):
        if value > self.balance:
            self.insufficientFunds()
            return False
        else:
            self.balance -= value
            return True
    
    def insufficientFunds(self):
        print "Insufficient Funds" #Popup Display on LCD
        
    
    def topup(self,value):
        self.balance += value

        
    def wash(self,weight,fee,machineid):
#==============================================================================
#         fee = calcFee(weight)               #from main
#         machineid = findMachine(weight)     #from main
#==============================================================================
        success = self.withdraw(fee)
        if success:              #successful withdrawal
            self.info["machineid"] = machineid
            self.info["weight"] = weight

            return success

        
        
    
        
