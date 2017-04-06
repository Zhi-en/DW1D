from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ToggleButtonBehavior



class MyLabel(Label):
    def __init__(self,**kwargs):
        Label.__init__(self,**kwargs)
        self.bind(size=self.setter('text_size'))
        self.padding=(20,20)
        self.font_size=24
        self.halign='center'
        self.valign='middle'

class ledApp(App):

    def build(self):
        layout= GridLayout(cols=2,row_force_default=True, row_default_height=40)
        
        yellow=MyLabel(text="Yellow LED",width=150)
        layout.add_widget(yellow)
        
        self.yellowbtn = ToggleButton(text="off", on_press=self.yPress,state = 'normal', font_size=24)
        layout.add_widget(self.yellowbtn)
        
        red=MyLabel(text="Red LED",width=150)
        layout.add_widget(red)
        
        self.redbtn = ToggleButton(text="off", on_press=self.rPress,state = 'normal', font_size=24)
        layout.add_widget(self.redbtn)
        
        exit = Button(text="Exit", on_press=self.quit_app, font_size=24)
        layout.add_widget(exit)
        
        return layout
        
    def yPress(self,value):
        if self.yellowbtn.text == "off":
            self.yellowbtn.text ="on"
            self.yellowbtn.state = 'down'
        
        else:
            self.yellowbtn.text ="off"
            self.yellowbtn.state = 'normal'
    
    def rPress(self,value):
        if self.redbtn.text == "off":
            self.redbtn.text ="on"
            self.redbtn.state = 'down'
        
        else:
            self.redbtn.text ="off"
            self.redbtn.state = 'normal'
            
    def quit_app(self, value):
        App.get_running_app().stop()
        exit()
        
        
        

if __name__ == '__main__':
    ledApp().run()
