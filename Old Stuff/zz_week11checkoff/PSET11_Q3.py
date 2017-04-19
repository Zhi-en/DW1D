from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button 

class MyLabel(Label):
    def __init__(self, text,**kwargs):
        super(MyLabel, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        self.padding=(20,20)
        self.text = text
        self.font_size = 24
        self.padding = (20, 20)
        self.halign = 'center'
        self.valign = 'middle'

class Investment(App):

    def build(self):
        layout= GridLayout(cols=2)

        l1=MyLabel(text="Investment Amount", font_size=24, halign='left', valign='middle')
        layout.add_widget(l1) 
        self.textInput1 = TextInput(font_size = 24)
        layout.add_widget(self.textInput1)

        l2=MyLabel(text="Years", font_size=24, halign='left', valign='middle')
        layout.add_widget(l2) 
        self.textInput2 = TextInput(font_size = 24)
        layout.add_widget(self.textInput2)

        l3=MyLabel(text="Monthly Interest Rate", font_size=24, halign='left', valign='middle')
        layout.add_widget(l3) 
        self.textInput3 = TextInput(font_size = 24)
        layout.add_widget(self.textInput3)

        btn = Button(text="Calculate", on_press=self.calculate, font_size=24)
        layout.add_widget(btn)
        self.result = MyLabel(text="blah", font_size=24, halign='left', valign='middle')
        layout.add_widget(self.result)
        return layout

    def calculate(self, instance):
        inv_amt = float(self.textInput1.text)
        years = float(self.textInput2.text)
        mth_int_rate = float(self.textInput3.text)
        self.result.text = str(inv_amt * (1.0 + mth_int_rate/1200.0) ** (years * 12))

if __name__ == '__main__':
    Investment().run()
