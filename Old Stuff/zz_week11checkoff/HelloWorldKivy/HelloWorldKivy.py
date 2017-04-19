# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 12:29:22 2017

@author: TABLET0007
"""

from kivy.app import App
from kivy.uix.label import Label

class MyApp(App):

    def build(self):
        return Label(text='Hello world')

if __name__ == '__main__':
    MyApp().run()
