#ladidaaaaa
#heloooooooo change no 2
#3

from firebase import firebase

#database
url = "https://rasppi2-efc3c.firebaseio.com/" # URL to Firebase database
token = "96ph75e8wFRh1pS2IjkowbVP9onHN5YZl6g23jnN" # unique token used for authentication

firebase = firebase.FirebaseApplication(url, token)

class account(object):
    pass

class washMachine(object):
    def __init__(self, id):
        self.id = id
        self.lockstate = False
    def wash(self):
        #directly manipulate database
        print 'id: %d \nWashing...' %(self.id)
    def lock(self):
        #directly manipulate database
        print 'id: %d \nLocking...' %(self.id)
    def unlock(self):
        #directly manipulate database
        print 'id: %d \nUnlocking' %(self.id)
        pass

def UI():
    pass

def main():
    account = {}
    machine = {}

    
    

    
main()

def updateData(name, info):
    pass # update the database