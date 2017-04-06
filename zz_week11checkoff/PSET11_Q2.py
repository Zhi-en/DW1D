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
        self.textSlide = 'slide me.'
        App.__init__(self,**kwargs)
        
    def build(self):
        self.main_label = Label(text=self.textSlide,font_size = 72, on_touch_move = self.detect)
        return self.main_label
        
    def alternate(self,instance,touch):
        if self.main_label.text == self.text1:
            self.main_label.text = self.text2
        elif self.main_label.text == self.text2:
            self.main_label.text = self.text1
        return self.main_label

    # def displacement(self, instance, touch):
    #     return (touch.dx**2 + touch.dy**2)**0.5

    def detect(self, instance, touch):
        if touch.dx < -40:
            instance.text = 'Left'
        if touch.dx > 40:
            instance.text = 'Right'
        if touch.dy < -40:
            instance.text = 'Down'
        if touch.dy > 40:
            instance.text = 'Up'
        return True
        
if __name__ == '__main__':
    MyApp().run()