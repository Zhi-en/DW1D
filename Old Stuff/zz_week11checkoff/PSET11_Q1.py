# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 12:29:22 2017

@author: TABLET0007
"""

from kivy.app import App
from kivy.uix.label import Label

class MyApp(App):
    def __init__(self,**kwargs):
        self.text1 = 'I love programmin'
        self.text2 = 'it is fun to program.'
        App.__init__(self,**kwargs)
        
    def build(self):
        self.main_label = Label(text=self.text1,font_size = 72, on_touch_down = self.alternate)
        return self.main_label
        
    def alternate(self,instance,touch):
        if self.main_label.text == self.text1:
            self.main_label.text = self.text2
        elif self.main_label.text == self.text2:
            self.main_label.text = self.text1
        return self.main_label
        
if __name__ == '__main__':
    MyApp().run()