# #import raspi/python functions
#import RPi.GPIO as GPIO
#import time
#
# #import 1D functions
#from weigh import getWeight    #gets weight of laundry
#from weigh import getCost    #gets cost of wash
#from weigh import getMachine    #gets optimal washing machine to use, automatically updates washing machine weight data
#from soap import giveSoap    #dispenses soap when cup is detected
#from firebase import getData    #gets machineNum, weight from firebase in the form (userid)
#from firebase import putData    #puts data on firebase in the form (userid, contact = str, machineNum = int, weight = int)
#from firebase import getState    #gets the state of any washing machine in the form (machineNum, 'door'/'state'/'weight')
#from firebase import getCloseDoor    #if any door has been opened for >2mins, gets the machine number else returns None
#from firebase import putState    #puts the state of any washing machine in the form (machineNum, door = 'open'/'closed', state = 'pooling'/'washing'/'collecting', weight = float)


#import kivy functions
from kivy.app import App
#kivy.require("1.8.0")
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from functools import partial

# #set GPIO pins
#GPIO.setmode(GPIO.BCM)
#dout = 5
#pdsck = 6
#sonar = 0 #change
#motor = 0 #change
#GPIO.setup(dout, GPIO.IN)
#GPIO.setup(pdsck, GPIO.OUT)
#GPIO.setup(sonar, GPIO.IN)
#GPIO.setup(motor, GPIO.OUT)
#
# #set global variables
#maxLoad = 10000    #maximum laundry load of washing machine in g
#fullCost = 1.0    #cost of one wash in $


#placeholder functions
def getWeight():
    weight = raw_input('weight:')
    return weight


#Shared kivy classes
class HomeButton(Button):
    pass

class BackButton(Button):
    pass

class LeftButton(Button):
    pass

class RightButton(Button):
    pass

class LoginLayout(GridLayout):
    pass

#Screen classes
class ScreenManagement(ScreenManager):
    pass
            
class WelcomeScreen(Screen):
#    def __init__(self, **kwargs):
#        super(WelcomeScreen, self).__init__(**kwargs)
#        Clock.schedule_interval(self.closeDoor, 10)
#    def closeDoor(self):
#        return getCloseDoor    #idk what it will return if getCloseDoor is None
    pass

class WashOrCollectScreen(Screen):
    pass

class PoolOrPrivateScreen(Screen):
    pass

class WeighScreen(Screen):
    def __init__(self, **kwargs):
        super(WeighScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.weight, 1)
    def weight(self, instance):
        self.weight = getWeight()
        if self.weight.isdigit():
            #self.button disable
            pass
    
    def build(self):        
        Wtbtn = Button(text="Weigh", on_press=self.getWeight, font_size=24)
        layout.add_widget(Wtbtn)
    
    
    
    # name='weigh'
    # id=weigh
    # 
    # Label(       
    # font_size=40
    # pos_hint: {'center_x'= 0.5, 'center_y'=0.6}
    # )
    # 
    # WS = Button(
    # text='Proceed'
    # font_size=40
    # color=(0,1,0,1)
    # pos_hint={'center_x'=0.5, 'center_y'=0.3}
    # size_hint=0.3, 0.2
    # button_instance.bind(on_press=partial
    # on_press=app.root.current = 'washlogin'
    # )
    # HomeButton
    # BackButton=
    # on_press= app.root.current = 'poolorprivate'
    pass

class WashLoginScreen(Screen):
    pass

class WashScreen(Screen):
    pass

class CollectLoginScreen(Screen):
    pass

class CollectScreen(Screen):
    pass

class CloseDoorScreen(Screen):
    pass

#import kivy code from kv file
main = Builder.load_file("main.kv")

class MainApp(App):
    def build(self):
        return main

if __name__ == "__main__":
    MainApp().run()