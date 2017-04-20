'''To run on computer:
    Comment out the following:
        import RPi.GPIO as GPIO
        from weigh import weighingScale
        from soap import Dispenser
        GPIO.setmode(GPIO.BCM)
        ws = weighingScale(dout, pdsck, maxLoad)
    in weigh.py, comment out:
        from HX711 import HX711
    Uncomment all functions under placeholder functions
'''

#import raspi/python functions
import RPi.GPIO as GPIO
import time

#import 1D functions
from weigh import weighingScale
from weigh import getCost
from soap import Dispenser
from account import createUser, getUsers, verify, putData, getData
from database import initMachines, clearMachines, putState, getState, getMachine, getDoor, getWash

#import kivy functions
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

#Configure window size to pi screen size for testing on computer
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

#Setup font
from kivy.core.text import LabelBase  
LabelBase.register(name='HVD',fn_regular="fonts/HVD_Poster.ttf")


#set GPIO pins
GPIO.setmode(GPIO.BCM)
dout = 5
pdsck = 6

#fixed global variables/objects
numOfMachines = 3
timeOut = 2*60*60    #maximum time laundry can be left in machines before wash starts
washTime = 40*60    #the hostel washing machine takes about 40mins for a wash
maxLoad = 10   #maximum laundry load of washing machine in kg
fullCost = 1.0    #cost of one wash in $
pfilled = 0.9    #approximately how full the washing machine should be to wash, also used for calculating cost
ws = weighingScale(dout, pdsck, maxLoad)

#variable global variables
globalWeight = 0    #weight of laundry
globalCost = 0    #cost of wash
globalMachine = 0    #washing machine number
globalState = 0    #0 if insufficient load to wash, 1 if sufficient, used to pass strings for collection


#placeholder functions
#class weighingScale(object):
#    def tareScale(self): #Tares the load cell
#        return 'Please place laundry on the weighing scale'
#    def getWeight(self): #gets the weight of clothes
#        weight = ((time.time())/60)%10    #gives a variable weight based on time
#        return weight
#ws = weighingScale()
#
#def Dispenser():
#    return True

#Kivy custom widgets/functions, standardise look across app
def resetVar():    #resets all variable global variables
    global globalWeight
    global globalCost
    global globalMachine
    global globalState
    globalWeight = 0
    globalCost = 0
    globalMachine = 0
    globalState = 0

class MyLabel(Label):    #creates personalised label function
    def __init__(self,**kwargs):
        Label.__init__(self,**kwargs)
        self.font_name='HVD'
        self.color=(0,0,0,1)
        self.halign='center'

class MyScreen(Screen):    #creates personalised screen function
    def __init__(self,**kwargs):
        Screen.__init__(self,**kwargs)
        self.layout=FloatLayout() #set layout
        self.add_widget(self.layout)
        self.background=Image(source='icons/background2.jpg')
        self.layout.add_widget(self.background)

class LeftLabel(MyLabel):
    def __init__(self,**kwargs):
        MyLabel.__init__(self,**kwargs)
        self.pos_hint={'center_x':0.28,'center_y':0.55}
        self.font_size=40
        self.color=(1,1,1,1)

class RightLabel(MyLabel):
    def __init__(self,**kwargs):
        MyLabel.__init__(self,**kwargs)
        self.pos_hint={'center_x':0.72,'center_y':0.55}
        self.font_size=40
        self.color=(1,1,1,1)

class HomeButton(ButtonBehavior,Image):    #creates personalised home button by giving button behavior to an image
    def __init__(self,**kwargs):
        Image.__init__(self,**kwargs)
        ButtonBehavior.__init__(self,**kwargs)
        self.source='icons/home.png'
        self.pos=(10,10)
        self.size_hint=(0.09,0.15)

class BackButton(ButtonBehavior,Image):    #creates personalised back button
    def __init__(self,**kwargs):
        Image.__init__(self,**kwargs)
        ButtonBehavior.__init__(self,**kwargs)
        self.source='icons/back.png'
        self.pos=(800-10-self.width,10)
        self.size_hint=(0.09,0.15)

class LeftButton(ButtonBehavior,Image):
    def __init__(self,**kwargs):
        Image.__init__(self,**kwargs)
        ButtonBehavior.__init__(self,**kwargs)
        self.source='icons/button1.png'
        self.pos_hint={'center_x':0.28,'center_y':0.55}
        self.size_hint=(0.35,0.25)

class RightButton(ButtonBehavior,Image):
    def __init__(self,**kwargs):
        Image.__init__(self,**kwargs)
        ButtonBehavior.__init__(self,**kwargs)
        self.source='icons/button1.png'
        self.pos_hint={'center_x':0.72,'center_y':0.55}
        self.size_hint=(0.35,0.25)

class MyButton(ButtonBehavior,Image):    #creates personalised button
    def __init__(self,**kwargs):
        Image.__init__(self,**kwargs)
        ButtonBehavior.__init__(self,**kwargs)
        self.source='icons/button2.png'
        self.size_hint=(0.3,0.2)

#Kivy screen classes
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)    #initialise the attributes of the parent class
        self.layout=FloatLayout(on_touch_down=self.nextscreen)    #touch screen to go to next screen
        self.add_widget(self.layout)
        background=Image(source='icons/background1.jpg')
        ml=MyLabel(text='Laundry Pool',font_size=70,pos_hint={'center_x':0.33,'center_y':0.75})
        self.sl=MyLabel(text='<touch screen to start>',font_size=20,pos_hint={'center_x':0.33,'center_y':0.6})
        self.close=MyLabel(text='',font_size=30,pos_hint={'center_x':0.33,'center_y':0.5})    #tells user to close an open laundry door if any door is left open
        self.layout.add_widget(background)
        self.layout.add_widget(ml)
        self.layout.add_widget(self.sl)
        self.layout.add_widget(self.close)
    def on_pre_enter(self):
        resetVar()
        Clock.schedule_interval(self.checks,10)    #runes check every 10 seconds
        Clock.schedule_interval(self.flash,1)    #flashes the label <touch screen to start> every second
    def on_pre_leave(self):
        Clock.unschedule(self.checks)
        Clock.unschedule(self.flash)
    def nextscreen(self,*args):    #function to go to next screen
        self.manager.current = 'washorcollect'
    def checks(self,instance):    #checks if all doors are closed (if not, go to the close door screen) and checks if pooling time does not exceed timeOut (start wash once exceeds)
        if getWash(timeOut)!=None:
            putState(getWash(timeOut),state=-1)
        if getDoor()!=None:
            return self.door(instance)
        else:
            return self.closed(instance)
    def flash(self,instance):
        if self.sl.color==[0,0,0,0]:    #if transparent, make it opaque
            self.sl.color=(0,0,0,1)
        else:
            self.sl.color=(0,0,0,0)    #last digit 0 makes it transparent
    def door(self,instance):
        Clock.unschedule(self.flash)    #if door is not closed, stoped flashing <touch screen to start> and hides it
        self.sl.color=(0,0,0,0)
        self.close.text='Please close the door of\nWashing Machine %d'%(getDoor())    #displays which washing machine's door to close
        self.layout.on_touch_down=self.closed
    def closed(self,instance):
        Clock.schedule_interval(self.flash,1)    #once door is closed, retarts flashing <touch screen to start>
        self.close.text=''
        self.layout.on_touch_down=self.nextscreen

class WashOrCollectScreen(MyScreen):    #prompt the user to wash or collect
    def __init__(self, **kwargs):
        super(WashOrCollectScreen, self).__init__(**kwargs)
        lb=LeftButton(on_press=self.wash)    #adding the custom buttons and labels for them
        ll=LeftLabel(text='Wash')
        rb=RightButton(on_press=self.collect)
        rl=RightLabel(text='Collect')
        homeb=HomeButton(on_press=self.home)
        backb=BackButton(on_press=self.back)
        self.layout.add_widget(lb)
        self.layout.add_widget(ll)
        self.layout.add_widget(rb)
        self.layout.add_widget(rl)
        self.layout.add_widget(homeb)
        self.layout.add_widget(backb)
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

class PoolOrPrivateScreen(MyScreen):
    def __init__(self, **kwargs):
        super(PoolOrPrivateScreen, self).__init__(**kwargs)
        lb=LeftButton(on_press=self.pool)
        ll=LeftLabel(text='Pool')
        rb=RightButton(on_press=self.private)
        rl=RightLabel(text='Private')
        homeb=HomeButton(on_press=self.home)
        backb=BackButton(on_press=self.back)
        self.layout.add_widget(lb)
        self.layout.add_widget(ll)
        self.layout.add_widget(rb)
        self.layout.add_widget(rl)
        self.layout.add_widget(homeb)
        self.layout.add_widget(backb)
    def on_enter(self):
        Clock.schedule_once(self.home,60)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
    def pool(self,instance):
        self.manager.current='weigh'
    def private(self,instance):
        global globalWeight
        globalWeight=maxLoad    #private was is equivalent of washing maximum loads
        self.manager.current='washlogin'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='washorcollect'

class WeighScreen(MyScreen):
    def __init__(self, **kwargs):
        super(WeighScreen, self).__init__(**kwargs)        
        self.weightl=MyLabel(text='',font_size=25,pos_hint={'center_x':0.5,'center_y':0.8})    #displays weight/instructions for user
        self.proceedb=MyButton(on_press=self.proceed,disabled=True,pos_hint={'center_x':0.5,'center_y':0.33})    #continue to next screen, only enabled when there is weight measured
        proceedl=MyLabel(text='Proceed',font_size=25,pos_hint={'center_x':0.5,'center_y':0.33})
        proceedl.color=(1,1,1,1)
        homeb=HomeButton(on_press=self.home)
        backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.weightl)
        self.layout.add_widget(self.proceedb)
        self.layout.add_widget(proceedl)
        self.layout.add_widget(homeb)
        self.layout.add_widget(backb)
    def on_pre_enter(self):
        self.weightl.text=str(ws.tareScale())
    def on_enter(self):
        Clock.schedule_interval(self.weigh,0.1)    #calls functions to get weight every 0.1s
        Clock.schedule_once(self.home,2*60)
    def on_pre_leave(self):
        Clock.unschedule(self.weigh)
        Clock.unschedule(self.home)
    def on_leave(self):    #resets screen to original set-up
        self.weightl.text=''
        self.weightl.font_size=25
        self.proceedb.disabled=True
    def weigh(self,instance):
        if self.weightl.text=='Please remove all items from weighing scale':
            self.weightl.text=str(ws.tareScale())
        elif self.weightl.text=='Please place laundry on the weighing scale':
            weight = ws.getWeight()
            if type(weight) is float:
                self.weightl.font_size=50    #weight displays are larger than instructions
                self.weightl.text='Weight: %.2fkg'%(weight)
            else:
                self.weightl.text=str(weight)
        else:
            weight=ws.getWeight()
            if type(weight) is float:
                delta=0.5    #allowable difference in value range to ensure stable weight returned
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
                self.weightl.font_size=25    #if weight drops below 1kg, instructions are returned instead
                self.weightl.text=str(weight)
    def proceed(self,instance):
        self.manager.current='washlogin'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        resetVar()
        self.manager.current='poolorprivate'

class WashLoginScreen(MyScreen):
    def __init__(self, **kwargs):
        super(WashLoginScreen, self).__init__(**kwargs)
        self.costl=MyLabel(text='',font_size=50,pos_hint={'center_x':0.5,'center_y':0.80})    #Label that displays costs to be paid
        self.fail=MyLabel(text='',font_size=25,pos_hint={'center_x':0.5,'center_y':0.65})    #Label that appears when wrong userid/password is input
        ul=MyLabel(text='Student ID',font_size=25,pos_hint={'center_x':0.3,'center_y':0.54})    #UserID and Password format
        self.ut=TextInput(pos_hint={'center_x':0.7,'center_y':0.54},size_hint=(0.4,0.07),multiline=False,write_tab=False,on_text_validate=self.login)    #write_tab and on_text_validate enable use of tab to go to next text field and enter to return a function
        pl=MyLabel(text='Password',font_size=25,pos_hint={'center_x':0.3,'center_y':0.46})
        self.pt=TextInput(pos_hint={'center_x':0.7,'center_y':0.46},size_hint=(0.4,0.07),multiline=False,write_tab=False,on_text_validate=self.login,password=True)
        self.lb=MyButton(pos_hint={'center_x':0.7,'center_y':0.25},on_press=self.login)    #login button
        ll=MyLabel(text='Login',font_size=25,pos_hint={'center_x':0.7,'center_y':0.25})
        ll.color=(1,1,1,1)
        self.sb=MyButton(pos_hint={'center_x':0.3,'center_y':0.25},on_press=self.signup)    #sign up button
        sl=MyLabel(text='Sign up',font_size=25,pos_hint={'center_x':0.3,'center_y':0.25})
        sl.color=(1,1,1,1)
        homeb=HomeButton(on_press=self.home)
        backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.costl)
        self.layout.add_widget(self.fail)
        self.layout.add_widget(ul)
        self.layout.add_widget(self.ut)
        self.ut.focus=True    #selects text field input
        self.layout.add_widget(pl)
        self.layout.add_widget(self.pt)
        self.layout.add_widget(self.lb)
        self.layout.add_widget(ll)
        self.layout.add_widget(self.sb)
        self.layout.add_widget(sl)
        self.layout.add_widget(homeb)
        self.layout.add_widget(backb)
    def on_pre_enter(self):
        global globalCost
        global globalMachine
        global globalState
        globalCost=getCost(globalWeight,maxLoad,fullCost,pfilled)    #calculates cost based on weight and weight-cost ratio
        globalState,globalMachine = getMachine(globalWeight,maxLoad,pfilled)    #determines which washing machine to use and if it should wash or wait for more laundry
        if type(globalMachine) is int:
            self.costl.text='Cost: $%.2f' %(globalCost)
        else:    #if all machines are full/used
            self.costl.font_size=30
            self.costl.text=str(globalMachine)
            self.lb.disabled=True    #disables the textfields and buttons
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
        self.costl.font_size=50
        self.lb.disabled=False
        self.sb.disabled=False
        self.ut.disabled=False
        self.pt.disabled=False
    def login(self,instance):
        if verify(self.ut.text,self.pt.text):    #if userID and passwords match
            weight,machineid,endtime=getData(self.ut.text,['weight','machineid','endtime'])    #gets current wash info of the user
            timing,studentid=getState(globalMachine,['state','studentid'])    #gets current userids and state of washing machine
            if weight==None:    #if user has no current washes
                weight=[globalWeight]
                machineid=[globalMachine]
                if timing==0:    #of no laudry in the machine, puts time of putting laundry
                    endtime=[time.time()+washTime+timeOut]
                else:    #uses the first user's time of putting laundry
                    endtime=[timing+washTime+timeOut]
            else:    #adds new wash info to current washes
                weight+=[globalWeight]
                machineid+=[globalMachine]
                if timing==0:
                    endtime+=[time.time()+washTime+timeOut]
                else:
                    endtime+=[timing+washTime+timeOut]
            if studentid==None:    #if machine is empty, create the user list
                studentid=[self.ut.text]
            else:    #add user info to user list
                studentid+=[self.ut.text]
            putData(self.ut.text,weight=weight,machineid=machineid,endtime=endtime,debt=globalCost,pmstate=0)    #updates users data to firebase
            if globalState==-1:    #if last user (washing machine starts wash immediately after this user), updates info accordingly
                putState(globalMachine,door=1,state=-1,weight=globalWeight,studentid=studentid)
            elif getState(globalMachine,'state')==0:    #if first user, puts time of putting laundry and updates info accordingly
                putState(globalMachine,door=1,state=time.time(),weight=globalWeight,studentid=studentid)
            else:    #if neither, keeps first user timing and updates rest of info accordingly
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

class WashScreen(MyScreen):
    def __init__(self, **kwargs):
        super(WashScreen, self).__init__(**kwargs)
        self.washl=MyLabel(text='',font_size=35)    #tells user which washing machine to place laundry in
        homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.washl)
        self.layout.add_widget(homeb)
        self.dispensed=False
    def on_pre_enter(self):
        if globalState==-1:    #last user, dispense soap
            self.washl.text='Please place your laundry\nin Washing Machine %d and\nCollect soap from the dispenser' %(globalMachine)
        else:
            self.washl.text='Please place your laundry\nin Washing Machine %d' %(globalMachine)
    def on_enter(self):
        Clock.schedule_once(self.home,60)
        if globalState==-1:
            Clock.schedule_once(self.dispense,1)
    def on_pre_leave(self):
        Clock.unschedule(self.home)
        Clock.unschedule(self.dispense)
    def on_leave(self):
        self.washl.text=''
    def dispense(self,instance):    #tries to dispense soap until soap is dispensed (runs every 1s)
        if not self.dispensed:
            self.dispensed=Dispenser()
    def home(self,instance):
        self.manager.current='welcome'

class CollectLoginScreen(MyScreen):
    def __init__(self, **kwargs):
        super(CollectLoginScreen, self).__init__(**kwargs)
        self.fail=MyLabel(text='',font_size=25,pos_hint={'center_x':0.5,'center_y':0.65})
        ul=MyLabel(text='Student ID',font_size=25,pos_hint={'center_x':0.3,'center_y':0.54})
        self.ut=TextInput(pos_hint={'center_x':0.7,'center_y':0.54},size_hint=(0.4,0.07),multiline=False,write_tab=False,on_text_validate=self.login)
        pl=MyLabel(text='Password',font_size=25,pos_hint={'center_x':0.3,'center_y':0.46})
        self.pt=TextInput(pos_hint={'center_x':0.7,'center_y':0.46},size_hint=(0.4,0.07),multiline=False,write_tab=False,on_text_validate=self.login,password=True)
        lb=MyButton(pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.login)
        ll=MyLabel(text='Login',font_size=25,pos_hint={'center_x':0.5,'center_y':0.25})
        ll.color=(1,1,1,1)
        backb=BackButton(on_press=self.back)
        homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.fail)
        self.layout.add_widget(ul)
        self.layout.add_widget(self.ut)
        self.ut.focus=True
        self.layout.add_widget(pl)
        self.layout.add_widget(self.pt)
        self.layout.add_widget(lb)
        self.layout.add_widget(ll)
        self.layout.add_widget(homeb)
        self.layout.add_widget(backb)
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
            if weight==None:    #if wash info is empty
                global globalState
                globalState='You do not have any laundry to collect'
                self.manager.current='nocollect'
                return None
            else:
                machinels=[]
                for machine in range(len(machineid)):
                    if getState(machineid[machine],'state')==-2:
                        machinels.append(machine)
                if machinels==[]:    #if none of the washing machines the user has laundry in is ready
                    global globalState
                    globalState='Your laundry is not ready for collection'
                    self.manager.current='nocollect'
                    return None
                weightls=[]
                machineidls=[]
                for machine in sorted(machinels,reverse=True):    #removed ready wash data and puts it into new lists
                    weightls.append(weight.pop(machine))
                    machineidls.append(machineid.pop(machine))
                    endtime.pop(machine)
                putData(self.ut.text,machineid=machineid,weight=weight,endtime=endtime)    #returns not ready wash data back to firebase
                for machine in range(len(machineidls)):    #uses ready wash data to update washing machine status
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
                globalMachine = list(set(machineidls))    #puts list of washing machines with user's laundry ready for collection
                self.manager.current='collect'
        else:
            self.ut.text=''
            self.pt.text=''
            self.fail.text='Incorrect User ID or Password'
    def home(self,instance):
        self.manager.current='welcome'
    def back(self,instance):
        self.manager.current='washorcollect'

class CollectScreen(MyScreen):
    def __init__(self, **kwargs):
        super(CollectScreen, self).__init__(**kwargs)
        self.collect=MyLabel(text='',font_size=35)    #tells user which washing machine to take laundry from
        homeb=HomeButton(on_press=self.home)
        self.layout.add_widget(self.collect)
        self.layout.add_widget(homeb)
    def on_pre_enter(self):
        if len(globalMachine)>1:    #adds an s and commas for more than 1 machine
            machine=', '.join(str(i) for i in globalMachine)
            machine='s '+machine
        else:
            machine=' %d' %(globalMachine[0])
        self.collect.text='Please collect your laundry from\nWashing Machine%s' %(machine)
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

class NoCollectScreen(MyScreen):
    def __init__(self, **kwargs):
        super(NoCollectScreen, self).__init__(**kwargs)
        self.collect=MyLabel(text='',font_size=35)    #tells user why there is no laundry to collect
        homeb=HomeButton(on_press=self.home)
        backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.collect)
        self.layout.add_widget(homeb)
        self.layout.add_widget(backb)
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

class SignUpScreen(MyScreen):
    def __init__(self, **kwargs):
        super(SignUpScreen, self).__init__(**kwargs)
        self.fail=MyLabel(text='',font_size=25,pos_hint={'center_x':0.5,'center_y':0.75})
        self.fail.color=(1,0,0,1)
        cl=MyLabel(text='Handphone Number',font_size=25,pos_hint={'center_x':0.3,'center_y':0.62})
        self.ct=TextInput(pos_hint={'center_x':0.7,'center_y':0.62},size_hint=(0.4,0.07),multiline=False,write_tab=False,on_text_validate=self.signup)
        ul=MyLabel(text='Student ID',font_size=25,pos_hint={'center_x':0.3,'center_y':0.54})
        self.ut=TextInput(pos_hint={'center_x':0.7,'center_y':0.54},size_hint=(0.4,0.07),multiline=False,write_tab=False,on_text_validate=self.signup)
        pl=MyLabel(text='Password',font_size=25,pos_hint={'center_x':0.3,'center_y':0.46})
        self.pt=TextInput(pos_hint={'center_x':0.7,'center_y':0.46},size_hint=(0.4,0.07),multiline=False,write_tab=False,on_text_validate=self.signup,password=True)
        cpl=MyLabel(text='Re-type Password',font_size=25,pos_hint={'center_x':0.3,'center_y':0.38})
        self.cpt=TextInput(pos_hint={'center_x':0.7,'center_y':0.38},size_hint=(0.4,0.07),multiline=False,write_tab=False,on_text_validate=self.signup,password=True)
        sb=MyButton(on_press=self.signup,pos_hint={'center_x':0.5,'center_y':0.25})
        sl=MyLabel(text='Sign up',font_size=25,pos_hint={'center_x':0.5,'center_y':0.25})
        sl.color=(1,1,1,1)
        homeb=HomeButton(on_press=self.home)
        backb=BackButton(on_press=self.back)
        self.layout.add_widget(self.fail)
        self.layout.add_widget(cl)
        self.layout.add_widget(self.ct)
        self.ct.focus=True
        self.layout.add_widget(ul)
        self.layout.add_widget(self.ut)
        self.layout.add_widget(pl)
        self.layout.add_widget(self.pt)
        self.layout.add_widget(cpl)
        self.layout.add_widget(self.cpt)
        self.layout.add_widget(sb)
        self.layout.add_widget(sl)
        self.layout.add_widget(homeb)
        self.layout.add_widget(backb)
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
        if not (self.ut.text.isdigit() and len(self.ut.text)==7):    #checks validity of student ID
            self.fail.text='Invalid Student ID'
            self.ut.text=''
            self.ut.focus=True
        elif self.ut.text in getUsers():    #checks if student ID is already in system
            self.fail.text='Student ID already in use, please choose another'
            self.ut.text=''
            self.ut.focus=True
        elif self.pt.text!=self.cpt.text:    #checks for matching passwords
            self.fail.text='Passwords do not match'
            self.pt.text=''
            self.cpt.text=''
            self.pt.focus=True
        elif not (self.ct.text.isdigit() and len(self.ct.text)==8):    #checks validity of hp number
            self.fail.text='Invalid Handphone Number'
            self.ct.focus=True
        elif self.ct.text=='':    #checks for empty fields
            self.fail.text='Please key in your Handphone Number\nso we can contact you for laundry collection'
            self.ct.focus=True
        elif self.ut.text=='':
            self.fail.text='Please key in your User ID'
            self.ut.focus=True
        elif self.pt.text=='':
            self.fail.text='Please key in your password'
            self.pt.focus=True
        else:
            createUser(self.ut.text,self.pt.text,int(self.ct.text))    #creates the user on firebase
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

class ContactBotScreen(MyScreen):    #tells user to add the laundry pool bot on telegram
    def __init__(self, **kwargs):
        super(ContactBotScreen, self).__init__(**kwargs)
        ml=MyLabel(text='To receive notifications when\nlaundry is ready for collection\nplease start chat with\nSUTD_LaundryPool on Telegram',font_size=25,pos_hint={'center_x':0.5,'center_y':0.7})
        pb=MyButton(on_press=self.proceed,pos_hint={'center_x':0.5,'center_y':0.33})
        pl=MyLabel(text='Proceed',font_size=25,pos_hint={'center_x':0.5,'center_y':0.33})
        pl.color=(1,1,1,1)
        self.layout.add_widget(ml)
        self.layout.add_widget(pb)
        self.layout.add_widget(pl)
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
    