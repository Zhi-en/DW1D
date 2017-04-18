from firebase import firebase
from libdw import sm
import getCost #import getCost(weight)
import getWeight #import getWeight(dout, pdsck) << whats this?
import accountClass

#database
url = "https://rasppi2-efc3c.firebaseio.com/" # URL to Firebase database
token = "96ph75e8wFRh1pS2IjkowbVP9onHN5YZl6g23jnN" # unique token used for authentication

firebase = firebase.FirebaseApplication(url, token)
status = firebase.get('/washingMachine/status')  ##On/Off trigger for main code, stored on firebase (boolean value)

maxWeight = 10 #kg Max weight (for private wash calculations)

#Function for GUI page 1: takes in user input(login details), returns True or False
def GUI_1():
    
    #user input here (idk how to do this sorry ><)
    
    currentUser = #call user tagged to the accountClass
    
    if(#login details + enter pressed): 
        return True
    else:
        return False
               


#Function for GUI page 2: takes in user input, returns 1 or 2 (Private or Pool), if no input, return 3
def GUI_2():
    
    #user input here
    
    if(#pool button selected): #Pool button pressed
        return 1
    elif(#private button selected):  #Private button pressed
        return 2
    else:
        return 3
    
#Function that determines which machine to put the clothes in, returns the machineID
def findMachine(weight):
    #code
    return machineID
               
    
class mainPi(sm.SM):
    startState = 0
    #state 0 - GUI page 1: takes in user input, returns 1 or 2(Private or Pool)
    #state 1 - Pool Wash
    #state 2 - Private Wash
    #state 3 - Check if previous wash(es) are done
    
    def getNextValues(self,state): 
        if state == 0:
            login = GUI_1() #True or False
            if login:
                next_state = GUI_2()
            else:
                next_state = 3 #no login detected so go check wash status
        
        elif state == 1:
            weight = getWeight() #whats the arguments here??
            cost = getCost(weight)
            machineid = findMachine(weight)
            success = currentUser.wash(weight,cost,machineID) #Updates account information, returns True or False Value (successful deduction or not)
            if success: #sucessful deduction
                wash() #calls wash function

            else: #failed to deduct
                currentUser.insufficientFunds()
            
            next_state = 0
            
            
        elif state == 2:
            weight = maxWeight
            cost = getCost(weight)
            machineid = findMachine(weight)
            success = currentUser.wash(weight,cost,machineID)
            
            if success: 
                wash ()
            else: 
                currentUser.insufficientFunds()
            
            next_state = 0
            
        
        elif state == 3:
            #checks previous washes
            #if any are finished
            #calls contact user function
            
      
      

activate = mainPi()
activate.start()
            
while (status): #status should be True until want to turn code off
    activate.step()
    
    
    
    
    
    
    
    
    
    