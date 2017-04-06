from firebase import firebase
import time
import hashlib, uuid #password hashing

token = 'yMZCCFRTqpn1A09FKehU6h0fzptu54M9uUc0Y0yM'
url = 'https://dwwk11-194f2.firebaseio.com/'

# Create a firebase object by specifying the URL of the database and its secret token.
# The firebase object has functions put and get, that allows user to put data onto 
# the database and also retrieve data from the database.
myFireBase = firebase.FirebaseApplication(url, token)

class DBIO(object):
    def validLocation(self, location):
        location = str(location)
        for char in location:
            if not char.isalnum() and char is not '/':
                return False
            else:
                return True

    def parseLocation(self, location):
        if self.validLocation(location):
            location = str(location) #convert to string
            if location[0] != '/': #if the first character is missing a slash, add it in
                location = '/' + location
            if location[-1] == '/': #if the location string has a terminating slash, delete it
                location = location[:-1]
            #search for the last slash in the string
            idx = 1
            for char in location:
                if char == '/':
                    lastSlash = idx
                idx += 1
            #split the location into subdir and containing directory
            subdir = location[lastSlash:]
            location = location [:lastSlash]
            if location[-1] == '/':
                location = location[:-1]
            return location, subdir

    def writeDataToLocation(self, data, check, location):
        parsedLocation = self.parseLocation(location)
        if check(data):
            print 'Writing data:    %s\nTo location:     %s\nSubdirectory:    %s' %(data, parsedLocation[0], parsedLocation[1])
            # myFireBase.put(parsedLocation[0], parsedLocation[1], data)
            print 'Upload complete.'

class UsersIO(DBIO):
    def __init__(self, directory):
        self._usernameMinLength = 8
        self._passwordMinLength = 10
        if super(UsersIO, self).validLocation(directory):
            self.directory = directory
        else:
            raise ValueError('Unexpected directory format')
        if self.directory[-1] != '/':
            self.directory += '/'
        print 'Initialised directory to %s' %(self.directory)
        
    def isValidUsername(self, username):
        username = str(username)
        if username.isalnum() and len(username) >= self._usernameMinLength:
            return True
        else: 
            print 'Username "%s" is not valid. Username must be longer than 8 characters, no spaces and alphanumeric.' %(username)
            return False
    
    def createUser(self, new_user, password, balance, infoDict):
        if not self.isValidUsername(new_user):
            print 'Username is invalid.'
            return None
        if new_user in myFireBase.get(self.directory):
            print 'Username already taken.'
        else: #create the user
            location = self.directory + str(new_user)
            location = super(UsersIO, self).parseLocation(location)
            myFireBase.put(location[0], location[1], {'hash' : self.hashPassword(password)})
            myFireBase.put(location[0], location[1], {'balance' : balance})
            myFireBase.put(location[0], location[1], {'info': infoDict})
    
    def isValidPassword(self, password):
        password = str(password)
        if len(password) >= self._passwordMinLength:
            return True
        else:
            return False

    def hashPassword(self, password):
        salt = hashlib.md5(password).hexdigest()
        saltyPass = password + salt + 'laundry2017Pool!'
        return hashlib.sha512(saltyPass).hexdigest()
    
    def lookupUserPassHash(self, username):
        myFireBase.get(self.directory + '/' + str(username))

    def verifyUser(self, username, password):
        return self.hashPassword(password) == self.lookupUserPassHash(password)

# DBIO().writeDataToLocation('this is some datamuahahahahahah', returntrue, 'test/asdf')
# UsersIO('/test/users').createUser('asdasdfffasdf')

class WashMachineIO(object):
    def __init__(self, directory, nWashMachines):
        self.directory = directory
        self.nWashMachines = nWashMachines
        self.defaults = {'doorOpen': False, 'washing' : False, 'weight': 0.0}
        for id in range(nWashMachines):
            if id not in myFireBase.get(self.directory):
                for node, data in self.defaults.iteritems():
                    myFireBase.put(self.directory, node, data)
    def wash(self, id):
        #directly manipulate database
        print 'id: %d \nWashing...' %(self.id)
    def lock(self):
        #directly manipulate database
        print 'id: %d \nLocking...' %(self.id)
    def unlock(self):
        #directly manipulate database
        print 'id: %d \nUnlocking' %(self.id)
        pass