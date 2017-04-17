#Requires studentid,phone,password
#weight = weight of laundry
#fee = how much person has to pay
#machineid = which washing machine person is assigned to

from firebase import firebase
import time

url = 'https://laundry-pool.firebaseio.com/' # URL to Firebase database
token = 'TVEKlcgHcA5QTWOrESZI8aocvLTwUX58BTjhHN1v' # unique token used for authentication
firebase = firebase.FirebaseApplication(url, token)

        
def createAccount(studentid,phone,password):
    weight = 0
    machineid = 0
    firebase.put('/Accounts/%s/' %(studentid), 'studentid', studentid)  
    firebase.put('/Accounts/%s/' %(studentid), 'phonenumber', phone)  
    firebase.put('/Accounts/%s/' %(studentid), 'password', password) 
    firebase.put('/Accounts/%s/' %(studentid), 'weight', weight) 
    firebase.put('/Accounts/%s/' %(studentid), 'machineid', machineid)  
    
studentid = 1001234
phone = 98765432
password = 1234

createAccount(studentid,phone,password)
    
        