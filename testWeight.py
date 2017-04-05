#import kivy functions
from kivy.app import App
#kivy.require("1.8.0")
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from functools import partial
from kivy.uix.boxlayout import BoxLayout

def getWeight():
    weight = raw_input('weight:')
    return weight
    
class MyLabel(Label):
    def __init__(self,**kwargs):
        Label.__init__(self,**kwargs)
        self.bind(size=self.setter('text_size'))
        self.padding=(20,20)
        
class WeighScreen(Screen):
    def __init__(self, **kwargs):
        #Screen.__init__(self, **kwargs)
        super(WeighScreen, self).__init__(**kwargs)
        #Clock.schedule_interval(self.weight, 1)
        self.layout= BoxLayout(cols=2,default_height=40)    
        self.add_widget(self.layout) 
        
        self.weighlabel=MyLabel(text="Weight?",font_size=24,halign='center',valign='middle')
        self.layout.add_widget(self.weighlabel)
           
        Wtbtn = Button(text="Weigh", on_press=self.weight, font_size=24)
        self.layout.add_widget(Wtbtn)
        
        return
        

    def weight(self, instance):
        self.weight = getWeight()
        self.weighlabel.text = '%s kg'%(self.weight)
        if self.weight.isdigit():
            #self.button disable
            pass
    
        
        
        

class TestApp(App):
    def build(self):
            sm=ScreenManager()
            ws=WeighScreen(name='Weigh')
            sm.add_widget(ws)
            sm.current='Weigh'
            return sm
        
TestApp().run()