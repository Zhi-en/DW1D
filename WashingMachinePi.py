import RPi.GPIO as GPIO
from database import putState, getState

GPIO.setmode(GPIO.BCM)

class WashingMachine:
    def __init__(self, machine, openlight, closelight, washlight, doorbutton, washbutton):
        self.machine = machine
        self.openlight = openlight
        self.closelight = closelight
        self.washlight = washlight
        self.doorbutton = doorbutton
        self.washbutton = washbutton
        GPIO.setup(self.openlight, GPIO.OUT)
        GPIO.setup(self.closelight, GPIO.OUT)
        GPIO.setup(self.washlight, GPIO.OUT)
        GPIO.setup(self.doorbutton, GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.washbutton, GPIO.IN, GPIO.PUD_DOWN)
    def main(self):
        if getState(self.machine, 'door') != 0:
            GPIO.output(self.closelight, 0)
            GPIO.output(self.openlight, 1)
        elif getState(self.machine, 'state') == -1:
            GPIO.output(self.washlight, 1)
        if GPIO.input(self.doorbutton):
            putState(self.machine, door = 0)
        if GPIO.input(self.washbutton):
            putState(self.machine, state = -2)


#machine1 = WashingMachine(1,18,23,24,25,12)
#machine2 = WashingMachine(2,16,20,21,26,19)
#machine3 = WashingMachine(3,13,6,5,22,27)
#while True:
#    machine1.main()
#    machine2.main()
#    machine3.main()