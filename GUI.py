#import raspi/python functions
import RPi.GPIO as GPIO
import time

#import 1D functions
from weigh import weighingScale
from weigh import getCost
#from soap import giveSoap    #dispenses soap when cup is detected
from account import createUser, getUsers, verify, putData, getData
from database import initMachines, clearMachines, putState, getState, getMachine, getDoor, getWash

#import kivy functions
from kivy.app import App
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
from kivy.uix.image import Image

#set GPIO pins
GPIO.setmode(GPIO.BCM)
dout = 5
pdsck = 6
sonar = 0 #change
motor = 0 #change
GPIO.setup(sonar, GPIO.IN)
GPIO.setup(motor, GPIO.OUT)

#fixed global variables/objects
numOfMachines = 3
timeOut = 2*60*60    #maximum time laundry can be left in machines before wash starts
washTime = 40*60    #the hostel washing machine takes about 40mins for a wash
maxLoad = 10   #maximum laundry load of washing machine in kg
fullCost = 1.0    #cost of one wash in $
pfilled = 0.9    #approximately how full the washing machine should be to wash, also used for calculating cost
ws = weighingScale(dout, pdsck, maxLoad)

#variable global variables
globalWeight = 0
globalCost = 0
globalMachine = 0
globalState = 0
screenStart = 0


#placeholder functions TO BE REPLACED WITH ACTUAL CODE
#class weighingScale(object):
#    def tareScale(self): #Tares the load cell
#        return 'Please place laundry on the weighing scale'
#    def getWeight(self): #gets the weight of clothes
#        weight = ((time.time())/60)%10 #replace with actual weight code
#        return weight
#ws = weighingScale()


#Kivy custom widgets/functions, standardise look across app
def resetVar():
    global globalWeight
    global globalCost
    global globalMachine
    global globalState
    globalWeight = 0    #weight of laundry
    globalCost = 0    #cost of wash
    globalMachine = 0    #washing machine number
    globalState = 0    #0 if insufficient load to wash, 1 if sufficient

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
        self.layout=FloatLayout(on_touch_down=self.nextscreen) #touch screen to go to wash or collect screen
        self.add_widget(self.layout)
        self.ml=Label(text='Welcome to Laundry Pool',font_size=50,color=(0,1,0,1))
        self.layout.add_widget(self.ml)
        self.close=Label(text='',font_size=20)    #tells user to close an open laundry door if any door is left open
        self.layout.add_widget(self.close)
        self.sl=Label(text='click anywhere on screen to continue',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'top':0.7})
        self.layout.add_widget(self.sl)
    def on_pre_enter(self):
        resetVar()
        Clock.schedule_interval(self.checks,10)
    def on_pre_leave(self):
        Clock.unschedule(self.checks)
    def nextscreen(self,*args): #function to go to next screen
        self.manager.current = 'washorcollect'
    def checks(self,instance): #checks if all doors are closed (if not, go to the close door screen) and pooling time does not exceed timeOut
        if getWash(timeOut)!=None:
            putState(getWash(timeOut),state=-1)
        if getDoor()!=None:
            return self.door(instance)
        else:
            return self.closed(instance)
    def door(self,instance):
        self.ml.text=''
        self.sl.text=''
        self.close.text='Please close the door of Washing Machine %d'%(getDoor())
        self.layout.on_touch_down=self.closed
    def closed(self,instance):
        self.close.text=''
        self.ml.text='Welcome to Laundry Pool'
        self.sl.text='click anywhere on screen to continue'
        self.layout.on_touch_down=self.nextscreen

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
    def on_enter(self):
        Clock.schedule_once(self.home,60)    #returns to home screen if left on this screen for too long
    def on_pre_leave(self):
        Clock.unschedule(self.home)
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
    def on_enter(self):
        Clock.schedule_once(self.home,60)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
    def pool(self,instance):
        self.manager.current='weigh'
    def private(self,instance):
        global globalWeight
        globalWeight=maxLoad
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
        Clock.schedule_once(self.home,2*60)
    def on_pre_leave(self):
        Clock.unschedule(self.weigh)
        Clock.unschedule(self.home)
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
        self.fail=Label(text='',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'center_y':0.7}) #Label that appears when wrong userid/password is input
        self.layout.add_widget(self.fail)
        self.ul=Label(text='Student ID',pos_hint={'center_x':0.3,'center_y':0.54})
        self.layout.add_widget(self.ul)
        self.ut=TextInput(pos_hint={'center_x':0.7,'center_y':0.54},size_hint=(0.4,0.08),multiline=False,write_tab=False,on_text_validate=self.login) #write_tab and on_text_validate enable use of tab to go to next text field and enter to return a function
        self.ut.focus=True
        self.layout.add_widget(self.ut)
        self.pl=Label(text='Password',pos_hint={'center_x':0.3,'center_y':0.46})
        self.layout.add_widget(self.pl)
        self.pt=TextInput(pos_hint={'center_x':0.7,'center_y':0.46},size_hint=(0.4,0.08),multiline=False,write_tab=False,on_text_validate=self.login,password=True)
        self.layout.add_widget(self.pt)
        self.lb=Button(text='Login',pos_hint={'center_x':0.7,'center_y':0.25},size_hint=(0.2,0.1),on_press=self.login)
        self.layout.add_widget(self.lb)
        self.sb=Button(text='Sign up',pos_hint={'center_x':0.3,'center_y':0.25},size_hint=(0.2,0.1),on_press=self.signup)
        self.layout.add_widget(self.sb)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
    def on_pre_enter(self):
        global globalCost
        global globalMachine
        global globalState
        globalCost=getCost(globalWeight,maxLoad,fullCost,pfilled)
        globalState,globalMachine = getMachine(globalWeight,maxLoad,pfilled)
        if type(globalMachine) is int:
            self.costl.text='Cost is $%.2f' %(globalCost)
        else:
            self.costl.text=str(globalMachine)
            self.lb.disabled=True
            self.sb.disabled=True
            self.ut.disabled=True
            self.pt.disabled=True
    def on_enter(self):
        Clock.schedule_once(self.home,60)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
    def on_leave(self):
        self.costl.text=''
        self.ut.text=''
        self.pt.text=''
        self.fail.text=''
        self.lb.disabled=False
        self.ut.disabled=False
        self.pt.disabled=False
    def login(self,instance):
        if verify(self.ut.text,self.pt.text):
            weight,machineid,endtime=getData(self.ut.text,['weight','machineid','endtime'])
            timing,studentid=getState(globalMachine,['state','studentid'])
            if weight==None:
                weight=[globalWeight]
                machineid=[globalMachine]
                if timing==0:
                    endtime=[time.time()+washTime+timeOut]
                else:
                    endtime=[timing+washTime+timeOut]
            else:
                weight+=[globalWeight]
                machineid+=[globalMachine]
                if timing==0:
                    endtime+=[time.time()+washTime+timeOut]
                else:
                    endtime+=[timing+washTime+timeOut]
            if studentid==None:
                studentid=[self.ut.text]
            else:
                studentid+=[self.ut.text]
            putData(self.ut.text,weight=weight,machineid=machineid,endtime=endtime,debt=globalCost)
            if globalState==-1:
                putState(globalMachine,door=1,state=-1,weight=globalWeight,studentid=studentid)
            elif getState(globalMachine,'state')==0:
                putState(globalMachine,door=1,state=time.time(),weight=globalWeight,studentid=studentid)
            else:
                putState(globalMachine,door=1,weight=globalWeight,studentid=studentid)
            self.manager.current='wash'
        else:
            self.ut.text=''
            self.pt.text=''
            self.fail.text='Incorrect User ID or Password'
    def signup(self,instance):
        self.manager.current='signup'
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
    def on_enter(self):
        Clock.schedule_once(self.home,30)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
    def on_leave(self):
        self.washl.text=''
    def home(self,instance):
        self.manager.current='welcome'

class CollectLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(CollectLoginScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.fail=Label(text='',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'center_y':0.8})
        self.layout.add_widget(self.fail)
        self.ul=Label(text='Student ID',pos_hint={'center_x':0.3,'center_y':0.54})
        self.layout.add_widget(self.ul)
        self.ut=TextInput(pos_hint={'center_x':0.7,'center_y':0.54},size_hint=(0.4,0.08),multiline=False,write_tab=False,on_text_validate=self.login)
        self.ut.focus=True
        self.layout.add_widget(self.ut)
        self.pl=Label(text='Password',pos_hint={'center_x':0.3,'center_y':0.46})
        self.layout.add_widget(self.pl)
        self.pt=TextInput(pos_hint={'center_x':0.7,'center_y':0.46},size_hint=(0.4,0.08),multiline=False,write_tab=False,on_text_validate=self.login,password=True)
        self.layout.add_widget(self.pt)
        self.lb=Button(text='Login', pos_hint={'center_x':0.5,'center_y':0.25},size_hint=(0.2,0.1),on_press=self.login)
        self.layout.add_widget(self.lb)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
    def on_enter(self):
        Clock.schedule_once(self.home,60)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
    def on_leave(self):
        self.ut.text=''
        self.pt.text=''
        self.fail.text=''
    def login(self,instance):
        if verify(self.ut.text,self.pt.text):
            weight,machineid,endtime=getData(self.ut.text,['weight','machineid','endtime'])
            timing,studentid=getState(globalMachine,['state','studentid'])
            if weight==None:
                global globalState
                globalState='You do not have any laundry to collect'
                self.manager.current='nocollect'
                return None
            else:
                machinels=[]
                for machine in range(len(machineid)):
                    if getState(machineid[machine],'state')==-2:
                        machinels.append(machine)
                if machinels==[]:
                    global globalState
                    globalState='Your laundry is not ready for collection'
                    self.manager.current='nocollect'
                    return None
                weightls=[]
                machineidls=[]
                for machine in sorted(machinels,reverse=True):
                    weightls.append(weight.pop(machine))
                    machineidls.append(machineid.pop(machine))
                    endtime.pop(machine)
                putData(self.ut.text,machineid=machineid,weight=weight,endtime=endtime,pmstate='clear')
                for machine in range(len(machineidls)):
                    studentid=getState(machineidls[machine],'studentid')
                    try:
                        studentid.remove(self.ut.text)
                    except ValueError:
                        pass
                    if getState(machineidls[machine],'weight')-weightls[machine]<0.001:
                        putState(machineidls[machine],door=1,state=0,weight=-weightls[machine],studentid=studentid)
                    else:
                        putState(machineidls[machine],door=1,weight=-weightls[machine],studentid=studentid)
                global globalMachine
                globalMachine = list(set(machineidls))
                self.manager.current='collect'
        else:
            self.ut.text=''
            self.pt.text=''
            self.fail.text='Incorrect User ID or Password'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='washorcollect'

class CollectScreen(Screen):
    def __init__(self, **kwargs):
        super(CollectScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.collect=Label(text='',font_size=20) #tells user which washing machine to take laundry from
        self.layout.add_widget(self.collect)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back,disabled=True)
        self.layout.add_widget(self.backb)
    def on_pre_enter(self):
        if len(globalMachine)>1:
            machine=', '.join(str(i) for i in globalMachine)
            machine='s '+machine
        else:
            machine=' %d' %(globalMachine[0])
        self.collect.text='Please collect your laundry from Washing Machine%s' %(machine)
    def on_enter(self):
        Clock.schedule_once(self.home, 30)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
    def on_leave(self):
        self.collect.text=''
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='collectlogin'

class NoCollectScreen(Screen):
    def __init__(self, **kwargs):
        super(NoCollectScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.collect=Label(text='',font_size=20)
        self.layout.add_widget(self.collect)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back,disabled=True)
        self.layout.add_widget(self.backb)
    def on_enter(self):
        Clock.schedule_once(self.home,30)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
    def on_pre_enter(self):
        self.collect.text=globalState
    def on_leave(self):
        self.collect.text=''
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='collectlogin'

class SignUpScreen(Screen):
    def __init__(self, **kwargs):
        super(SignUpScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.fail=Label(text='',font_size=20,color=(1,0,0,1),pos_hint={'center_x':0.5,'center_y':0.8})
        self.layout.add_widget(self.fail)
        self.cl=Label(text='Handphone Number',pos_hint={'center_x':0.3,'center_y':0.62})
        self.layout.add_widget(self.cl)
        self.ct=TextInput(pos_hint={'center_x':0.7,'center_y':0.62},size_hint=(0.4,0.08),multiline=False,write_tab=False,on_text_validate=self.signup)
        self.ct.focus=True
        self.layout.add_widget(self.ct)
        self.ul=Label(text='Student ID',pos_hint={'center_x':0.3,'center_y':0.54})
        self.layout.add_widget(self.ul)
        self.ut=TextInput(pos_hint={'center_x':0.7,'center_y':0.54},size_hint=(0.4,0.08),multiline=False,write_tab=False,on_text_validate=self.signup)
        self.layout.add_widget(self.ut)
        self.pl=Label(text='Password',pos_hint={'center_x':0.3,'center_y':0.46})
        self.layout.add_widget(self.pl)
        self.pt=TextInput(pos_hint={'center_x':0.7,'center_y':0.46},size_hint=(0.4,0.08),multiline=False,write_tab=False,on_text_validate=self.signup,password=True)
        self.layout.add_widget(self.pt)
        self.cpl=Label(text='Re-type Password',pos_hint={'center_x':0.3,'center_y':0.38})
        self.layout.add_widget(self.cpl)
        self.cpt=TextInput(pos_hint={'center_x':0.7,'center_y':0.38},size_hint=(0.4,0.08),multiline=False,write_tab=False,on_text_validate=self.signup,password=True)
        self.layout.add_widget(self.cpt)
        self.sb=Button(text='Sign up', pos_hint={'center_x':0.5,'center_y':0.25},size_hint=(0.2,0.1),on_press=self.signup)
        self.layout.add_widget(self.sb)
        self.homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.homeb)
        self.backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.backb)
    def on_enter(self):
        Clock.schedule_once(self.home, 2*60)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
    def on_leave(self):
        self.ct.text=''
        self.ut.text=''
        self.pt.text=''
        self.cpt.text=''
        self.fail.text=''
    def signup(self,instance):
        if self.ut.text in getUsers():
            self.fail.text='Student ID already in use, please choose another'
            self.ut.text=''
            self.ut.focus=True
        elif self.pt.text!=self.cpt.text:
            self.fail.text='Passwords do not match'
            self.pt.text=''
            self.cpt.text=''
            self.pt.focus=True
        elif not (self.ct.text.isdigit() and len(self.ct.text)==8):
            self.fail.text='Invalid Handphone Number'
            self.ct.focus=True
        elif self.ct.text=='':
            self.fail.text='Please key in your Handphone Number\nso we can contact you for laundry collection'
            self.ct.focus=True
        elif self.ut.text=='':
            self.fail.text='Please key in your User ID'
            self.ut.focus=True
        elif self.pt.text=='':
            self.fail.text='Please key in your password'
            self.pt.focus=True
        else:
            createUser(self.ut.text,self.pt.text,int(self.ct.text))
            timing,studentid=getState(globalMachine,['state','studentid'])
            weight=[globalWeight]
            machineid=[globalMachine]
            if timing==0:
                endtime=[time.time()+washTime+timeOut]
            else:
                endtime=[timing+washTime+timeOut]
            if studentid==None:
                studentid=[self.ut.text]
            else:
                studentid+=[self.ut.text]
            putData(self.ut.text,weight=weight,machineid=machineid,endtime=endtime,debt=globalCost)
            if globalState==-1:
                putState(globalMachine,door=1,state=-1,weight=globalWeight,studentid=studentid)
            elif getState(globalMachine,'state')==0:
                putState(globalMachine,door=1,state=time.time(),weight=globalWeight,studentid=studentid)
            else:
                putState(globalMachine,door=1,weight=globalWeight,studentid=studentid)
            self.manager.current='contactbot'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='washlogin'

class ContactBotScreen(Screen):
    def __init__(self, **kwargs):
        super(ContactBotScreen, self).__init__(**kwargs)
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.ml=Label(text='To receive notifications when laundry is ready for collection\nplease start chat with SUTD_LaundryPool on Telegram',font_size=30)
        self.layout.add_widget(self.ml)
        self.pb=Button(text='Proceed', pos_hint={'center_x':0.5,'center_y':0.25},size_hint=(0.2,0.1),on_press=self.proceed)
        self.layout.add_widget(self.pb)
    def on_enter(self):
        Clock.schedule_once(self.proceed, 60)
    def on_pre_leave(self):
        Clock.unschedule(self.proceed)
    def proceed(self,instance):
        self.manager.current='wash'

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
            ncs=NoCollectScreen(name='nocollect')
            sus=SignUpScreen(name='signup')
            cbs=ContactBotScreen(name='contactbot')
            sm.add_widget(ws)
            sm.add_widget(wcs)
            sm.add_widget(pps)
            sm.add_widget(weighs)
            sm.add_widget(wls)
            sm.add_widget(washs)
            sm.add_widget(cls)
            sm.add_widget(cs)
            sm.add_widget(ncs)
            sm.add_widget(sus)
            sm.add_widget(cbs)
            sm.current='welcome'
            return sm

if __name__== '__main__':
#    initMachines(numOfMachines)
    SwitchScreenApp().run()
#    clearMachines()
    