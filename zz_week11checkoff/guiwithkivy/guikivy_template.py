from kivy.app import App 
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.label import Label 
from kivy.uix.togglebutton import ToggleButton
from firebase import firebase

token=None
url=None
firebase=firebase.FirebaseApplication(url,token)

class GuiKivy(App):

	def build(self):
		layout=None
		# add your widget to the layout

		return layout

	def updateStatus(self, instance):
		# use this callback to update firebase
		pass


GuiKivy().run()