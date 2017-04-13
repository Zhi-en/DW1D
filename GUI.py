#import raspi/python functions
import RPi.GPIO as GPIO
import time

#import 1D functions
from weigh import weighingScale
from weigh import getCost, getMachine    #gets weight of laundry, cost of wash and optimal washing machine to use, automatically updates washing machine weight data
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

#set GPIO pins
GPIO.setmode(GPIO.BCM)
dout = 5
pdsck = 6
sonar = 0 #change
motor = 0 #change
GPIO.setup(sonar, GPIO.IN)
GPIO.setup(motor, GPIO.OUT)

#fixed global variables/objects
maxLoad = 10   #maximum laundry load of washing machine in kg
fullCost = 1.0    #cost of one wash in $
ws = weighingScale(dout, pdsck)

#variable global variables
globalWeight = 0
globalCost = 0
globalMachine = 0

#placeholder functions TO BE REPLACED WITH ACTUAL CODE
#class weighingScale(object):
#    def tareScale(self): #Tares the load cell
#        instr = raw_input('proceed? y/n: ')
#        if instr == 'n':
#            return 'Please remove all items from weighing scale'
#        elif instr == 'y':
#            return 'Please place laundry on the weighing scale'
#    def getWeight(self): #gets the weight of clothes
#        weight = ((startTime-time.time())/60)%10 #replace with actual weight code
#        return weight
#ws = weighingScale()

def getMachine(): #chooses the correct machine
    global globalMachine
    if globalWeight > 9:
        return 1
    elif globalWeight > 6:
        return 2
    else:
        return 3

def verify(userID,password): #verifys the authenticity of the customer and charges to his account
    if userID == 'pi' and password == 'Sutd1234':
        return True
    else:
        return False

def doorOpen(): #checks if the door is open
    pass

#Kivy custom widgets/functions, standardise look across app
def resetVar():
    global globalWeight
    global globalCost
    global globalMachine
    globalWeight = 0
    globalCost = 0
    globalMachine = 0

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

class LoginLayout(FloatLayout):
    pass


#Kivy screen classes
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)        
        self.layout=FloatLayout(on_touch_down=self.nextscreen) #touch screen to go to wash or collect screen
        self.add_widget(self.layout)
        self.ml=Label(text='Welcome to Laundry Pool',font_size=50,color=(0,1,0,1))
        self.layout.add_widget(self.ml)
        self.sl=Label(text='click anywhere on screen to continue',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'top':0.7})
        self.layout.add_widget(self.sl)
    def on_pre_enter(self):
        resetVar()
        Clock.schedule_interval(self.closeDoor, 10)
    def on_pre_leave(self):
        Clock.unschedule(self.closeDoor)
    def nextscreen(self, instance, value): #function to go to next screen
        self.manager.current = 'washorcollect'
    def closeDoor(self, instance): #checks if all doors are closed. if not, go to the close door screen
        if doorOpen()[0]:
            global globalMachine
            globalMachine = doorOpen()[1]
            self.manager.current='closedoor'

class WashOrCollectScreen(Screen): #prompt the user whether he/she wants to wash or collect
    def __init__(self, **kwargs):
        super(WashOrCollectScreen, self).__init__(**kwargs) #initialise the attributes of the parent class
        self.layout=FloatLayout() #set layout
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
        super(PoolOrPrivateScreen, self).__init__(**kwargs) #initialise the attributes of the parent class
        self.layout=FloatLayout() #set layout
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
        self.manager.current='weigh'
    def private(self,instance):
        global globalWeight
        globalWeight = maxLoad
        self.manager.current='washlogin'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='washorcollect'

class WeighScreen(Screen):
    def __init__(self, **kwargs):
        super(WeighScreen, self).__init__(**kwargs)        
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.weightl=Label(text='',font_size=40,pos_hint={'center_x':0.5,'center_y':0.75}) #Label displays weight/instructions for user
        self.layout.add_widget(self.weightl)
        self.proceedb=Button(text='Proceed',pos_hint={'center_x':0.5,'center_y':0.25},size_hint=(0.3,0.2),on_press=self.proceed,disabled=True) #Button to continue to next screen, only activated there is a weight measured
        self.layout.add_widget(self.proceedb)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
    def on_pre_enter(self):
        self.weightl.text=str(ws.tareScale())
    def on_enter(self):
        Clock.schedule_interval(self.weigh,0.1)
    def on_pre_leave(self):
        Clock.unschedule(self.weigh)
    def on_leave(self):
        self.weightl.text=''
        self.proceedb.disabled=True
    def weigh(self,instance):
        if self.weightl.text=='Please remove all items from weighing scale':
            self.weightl.text=str(ws.tareScale())
        elif self.weightl.text=='Please place laundry on the weighing scale':
            weight = ws.getWeight()
            if type(weight) is float:
                self.weightl.text='Weight: %.2fkg'%(weight)
            else:
                self.weightl.text=str(weight)
        else:
            weight=ws.getWeight()
            if type(weight) is float:
                delta=100    #allowable difference in value range to ensure stable weight returned
                weightls=[0 for i in range(5)]
                count=0
                weightls[count]=weight
                self.weightl.text='Weight: %.2fkg'%(weightls[count])
                count+=1
                if count==5:
                    count=0
                if max(weightls)-min(weightls)<=delta:
                    global globalWeight
                    globalWeight = weight
                    self.proceedb.disabled=False
            else:
                self.weightl.text=str(weight)
    def proceed(self,instance):
        self.manager.current='washlogin'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        resetVar()
        self.manager.current='poolorprivate'

class WashLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(WashLoginScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.costl=Label(text='',font_size=30,pos_hint={'center_x':0.5,'center_y':0.85}) #Label that displays costs to be paid
        self.layout.add_widget(self.costl)
        self.fail=Label(text='Incorrect User ID or Password',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'center_y':0.7},disabled=True) #Label that appears when wrong userid/password is input
        self.layout.add_widget(self.fail)
        self.ul=Label(text='User ID',pos_hint={'center_x':0.25,'center_y':0.525})
        self.layout.add_widget(self.ul)
        self.ut=TextInput(pos_hint={'center_x':0.75,'center_y':0.525},size_hint=(0.5,0.05),multiline=False,write_tab=False,on_text_validate=self.login) #write_tab and on_text_validate enable use of tab to go to next text field and enter to return a function
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
    def on_pre_enter(self):
        global globalCost
        global globalMachine
        globalCost = getCost(globalWeight,maxLoad,fullCost)
        globalMachine = getMachine()
        self.costl.text='Cost is $%.2f' %(globalCost)
    def on_pre_leave(self):
        #add in all firebase functions here
        pass
    def on_leave(self):
        self.costl.text=''
        self.ut.text=''
        self.pt.text=''
        self.fail.disabled=True
    def login(self,instance):
        if verify(self.ut.text, self.pt.text):
            self.manager.current='wash'
        else:
            self.ut.text=''
            self.pt.text=''
            self.fail.disabled=False
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='poolorprivate'

class WashScreen(Screen):
    def __init__(self, **kwargs):
        super(WashScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.washl=Label(text='',font_size=30) #tells user which washing machine to place laundry in
        self.layout.add_widget(self.washl)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
    def on_pre_enter(self):
        self.washl.text='Please place your laundry in Washing Machine %d' %(globalMachine)
    def on_leave(self):
        self.washl.text=''
    def home(self,instance):
        self.manager.current='welcome'

class CollectLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(CollectLoginScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.fail=Label(text='Incorrect User ID or Password',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'center_y':0.8},disabled=True)
        self.layout.add_widget(self.fail)
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
    def on_pre_leave(self):
        #get the washing machine number here and update the washing machine state(open and minus from weight)
        pass
    def on_leave(self):
        self.ut.text=''
        self.pt.text=''
        self.fail.disabled=True
    def login(self,instance):
        if verify(self.ut.text, self.pt.text):
            self.manager.current='collect'
        else:
            self.ut.text=''
            self.pt.text=''
            self.fail.disabled=False
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
        self.collect=Label(text='',font_size=20) #tells user which washing machine to take laundry from
        self.layout.add_widget(self.collect)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back,disabled=True)
        self.layout.add_widget(self.backb)
    def on_pre_enter(self):
        self.collect.text='Please collect your laundry from Washing Machine %d' %(globalMachine)
    def on_leave(self):
        self.collect.text=''
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
        self.close=Label(text='',font_size=20) #tells user to close an open laundry door if any door is left open
        self.layout.add_widget(self.close)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
    def on_pre_enter(self):
        self.close.text='Please close the door of Washing Machine %d'%(globalMachine)
    def on_leave(self):
        self.close.text=''
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
    startTime = time.time()
    SwitchScreenApp().run()