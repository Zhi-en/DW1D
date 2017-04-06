##import raspi/python functions
#import RPi.GPIO as GPIO
import time
#
##import 1D functions
#from weigh import getWeight, getCost, getMachine    #gets weight of laundry, cost of wash and optimal washing machine to use, automatically updates washing machine weight data
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
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

##set GPIO pins
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
##set global variables
#maxLoad = 10000    #maximum laundry load of washing machine in g
#fullCost = 1.0    #cost of one wash in $


#placeholder functions
def startWeigh():
    instr = raw_input('Please place your laundry on the weighing scale/Please remove all items from weighing scale')
    global globalWeight
    if instr = 'Please place your laundry on the weighing scale':
        globalWeight = 0, instr
    elif instr = 'Please remove all items from weighing scale':
        globalWeight = -1, instr

def getWeight():
    instr = raw_input('stabalised?(y/n)')
    weight = raw_input('weight:')
    if instr = 'y':
        instr = 1
    elif instr = 'n':
        instr = 0
    global globalWeight
    globalWeight = instr, weight

def verify(userID,password):
    if userID == 'pi' and password == 'Sutd1234':
        return True
    else:
        return False

def doorOpen():
    if time.time()-startTime > 120:
        return True, 1
    else:
        return False, 0

#Kivy shared GUI classes
class HomeButton(Button):
    def __init__(self,**kwargs):
        Button.__init__(self,**kwargs)
        self.text='Home'
        self.font_size=20
        self.pos_hint={'left':0,'bottom':0}
        self.size_hint=(0.2,0.1)
        
class BackButton(Button):
    def __init__(self,**kwargs):
        Button.__init__(self,**kwargs)
        self.text='Back'
        self.font_size=20
        self.pos_hint={'right':1,'bottom':0}
        self.size_hint=(0.2,0.1)

class LeftButton(Button):
    def __init__(self,**kwargs):
        Button.__init__(self,**kwargs)
        self.font_size=40
        self.color=(0,1,0,1)
        self.pos_hint={'center_x':0.25,'center_y':0.5}
        self.size_hint=(0.3,0.2)

class RightButton(Button):
    def __init__(self,**kwargs):
        Button.__init__(self,**kwargs)
        self.font_size=40
        self.color=(0,1,0,1)
        self.pos_hint={'center_x':0.75,'center_y':0.5}
        self.size_hint=(0.3,0.2)

#Kivy screen classes
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.closeDoor, 10)
        self.layout=FloatLayout(on_touch_down=self.next)
        self.add_widget(self.layout)
        self.ml=Label(text='Welcome to Laundry Pool',font_size=50,color=(0,1,0,1))
        self.layout.add_widget(self.ml)
        self.sl=Label(text='click anywhere on screen to continue',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'top':0.7})
        self.layout.add_widget(self.sl)
    def next(self, instance, value):
        self.manager.current='washorcollect'
    def closeDoor(self, instance):
        if doorOpen()[0]:
            global globalMachine
            globalMachine = doorOpen()[1]
            self.manager.current='closedoor'

class WashOrCollectScreen(Screen):
    def __init__(self, **kwargs):
        super(WashOrCollectScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.lb=LeftButton(text='Wash',on_press=self.wash)
        self.layout.add_widget(self.lb)
        self.rb=RightButton(text='Collect',on_press=self.collect)
        self.layout.add_widget(self.rb)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
    def wash(self,instance):
        self.manager.current='poolorprivate'
    def collect(self,instance):
        self.manager.current='collectlogin'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='welcome'

class PoolOrPrivateScreen(Screen):
    def __init__(self, **kwargs):
        super(PoolOrPrivateScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.lb=LeftButton(text='Pool',on_press=self.pool)
        self.layout.add_widget(self.lb)
        self.rb=RightButton(text='Private',on_press=self.private)
        self.layout.add_widget(self.rb)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
    def pool(self,instance):
        startWeigh()
        self.manager.current='weigh'
    def private(self,instance):
        self.manager.current='washlogin'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='washorcollect'

class WeighScreen(Screen):
    def __init__(self, **kwargs):
        super(WeighScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.weigh,1)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.weightl=Label(text='',font_size=40,pos_hint={'center_x':0.5,'center_y':0.75},)
        self.layout.add_widget(self.weightl)
        self.proceed=Button(text='Proceed',pos_hint={'center_x':0.5,'center_y':0.25},size_hint=(0.3,0.2))
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
#    def weigh(self,instance):        #instead of generator can try using 2 functions: startWeigh and getWeight
#        global globalWeight
#        self.weightl.text=globalWeight[1]
#        if globalWeight[0]:
#            self.layout.add_widget(self.proceed)
#        else:
#            self.layout.remove_widget(self.proceed)
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='poolorprivate'

class WashLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(WashLoginScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.fail=Label(text='Incorrect User ID or Password',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'center_y':0.8},disabled=True,opacity=0)
        self.ul=Label(text='User ID',pos_hint={'center_x':0.25,'center_y':0.525})
        self.layout.add_widget(self.ul)
        self.ut=TextInput(pos_hint={'center_x':0.75,'center_y':0.525},size_hint=(0.5,0.05),multiline=False,write_tab=False,on_text_validate=self.login)
        self.ut.focus=True
        self.layout.add_widget(self.ut)
        self.pl=Label(text='Password',pos_hint={'center_x':0.25,'center_y':0.475})
        self.layout.add_widget(self.pl)
        self.pt=TextInput(pos_hint={'center_x':0.75,'center_y':0.475},size_hint=(0.5,0.05),multiline=False,write_tab=False,on_text_validate=self.login,password=True)
        self.layout.add_widget(self.pt)
        self.pb=Button(text='Login', pos_hint={'center_x':0.5,'center_y':0.25},size_hint=(0.2,0.1),on_press=self.login)
        self.layout.add_widget(self.pb)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
    def login(self,instance):
        if verify(self.ut.text, self.pt.text):    ######################################################################
            global globalWeight
            global globalCost
            global globalMachine
#            putWeight(globalWeight,id)
#            getCost()
#            getMachine()
#            OpenMachine()
#            UpdateMachineWeight()
            self.ut.text=''
            self.pt.text=''
            try:
                self.layout.remove_widget(self.fail)
            except:
                pass
            self.manager.current='wash'
        else:
            self.ut.text=''
            self.pt.text=''
            try:
                self.layout.add_widget(self.fail)
            except:
                pass
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='poolorprivate'

class WashScreen(Screen):
    def __init__(self, **kwargs):
        super(WashScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.wash=Label(text='Please place your laundry in Washing Machine ')
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
    def home(self,instance):
        self.manager.current='welcome'

class CollectLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(CollectLoginScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.fail=Label(text='Incorrect User ID or Password',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'center_y':0.8},disabled=True)
        self.ul=Label(text='User ID',pos_hint={'center_x':0.25,'center_y':0.525})
        self.layout.add_widget(self.ul)
        self.ut=TextInput(pos_hint={'center_x':0.75,'center_y':0.525},size_hint=(0.5,0.05),multiline=False,write_tab=False,on_text_validate=self.login)
        self.ut.focus=True
        self.layout.add_widget(self.ut)
        self.pl=Label(text='Password',pos_hint={'center_x':0.25,'center_y':0.475})
        self.layout.add_widget(self.pl)
        self.pt=TextInput(pos_hint={'center_x':0.75,'center_y':0.475},size_hint=(0.5,0.05),multiline=False,write_tab=False,on_text_validate=self.login,password=True)
        self.layout.add_widget(self.pt)
        self.lb=Button(text='Login', pos_hint={'center_x':0.5,'center_y':0.25},size_hint=(0.2,0.1),on_press=self.login)
        self.layout.add_widget(self.lb)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
    def login(self,instance):
        if verify(self.ut.text, self.pt.text):    ######################################################################
            global globalWeight
            global globalCost
            global globalMachine
#            putWeight(global weight)
#            getCost()
#            getMachine()
#            OpenMachine()
#            UpdateMachineWeight()
            self.ut.text=''
            self.pt.text=''
            try:
                self.layout.remove_widget(self.fail)
            except:
                pass
            self.manager.current='collect'
        else:
            self.ut.text=''
            self.pt.text=''
            try:
                self.layout.add_widget(self.fail)
            except:
                pass
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='washorcollect'

class CollectScreen(Screen):
    def __init__(self, **kwargs):
        super(CollectScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        global globalMachine
        self.collect=Label(text='Please collect your laundry from Washing Machine %d' %(globalMachine))
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back,disabled=True)
        self.layout.add_widget(self.backb)
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='collectlogin'

class CloseDoorScreen(Screen):
    def __init__(self, **kwargs):
        super(CloseDoorScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        global globalMachine
        self.close=Label(text='Please close the door of Washing Machine %d' %(globalMachine))
        self.layout.add_widget(self.close)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
    def home(self,instance):
        global startTime
        startTime = time.time()
        self.manager.current='welcome'

#Kivy main app
class SwitchScreenApp(App):
	def build(self):
            sm=ScreenManager(transition=FadeTransition())
            ws=WelcomeScreen(name='welcome')
            wcs=WashOrCollectScreen(name='washorcollect')
            pps=PoolOrPrivateScreen(name='poolorprivate')
            weighs=WeighScreen(name='weigh')
            wls=WashLoginScreen(name='washlogin')
            washs=WashScreen(name='wash')
            cls=CollectLoginScreen(name='collectlogin')
            cs=CollectScreen(name='collect')
            cds=CloseDoorScreen(name='closedoor')
            sm.add_widget(ws)
            sm.add_widget(wcs)
            sm.add_widget(pps)
            sm.add_widget(weighs)
            sm.add_widget(wls)
            sm.add_widget(washs)
            sm.add_widget(cls)
            sm.add_widget(cs)
            sm.add_widget(cds)
            sm.current='welcome'
            return sm

if __name__== '__main__':
    global startTime
    global globalWeight
    global globalCost
    global globalMachine
    startTime = time.time()
    globalWeight = (False, 0)
    globalCost = 0
    globalMachine = 0
    SwitchScreenApp().run()