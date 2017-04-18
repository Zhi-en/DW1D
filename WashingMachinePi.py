import RPi.GPIO as GPIO
import time
from database import putState, getState
from account import putData, getData

washTime = 40*60    #the hostel washing machine takes about 40mins for a wash

GPIO.setmode(GPIO.BCM)

class WashingMachine:
    def __init__(self, machine, openlight, closelight, washlight, doorbutton, washbutton):
        self.machine = machine
        self.openlight = openlight
        self.closelight = closelight
        self.washlight = washlight
        self.doorbutton = doorbutton
        self.washbutton = washbutton
        self.washing = False
        GPIO.setup(self.openlight, GPIO.OUT)
        GPIO.setup(self.closelight, GPIO.OUT)
        GPIO.setup(self.washlight, GPIO.OUT)
        GPIO.setup(self.doorbutton, GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.washbutton, GPIO.IN, GPIO.PUD_DOWN)
    def main(self):
        if GPIO.input(self.doorbutton):
            GPIO.output(self.openlight, 0)
            GPIO.output(self.closelight, 1)
            putState(self.machine, door = 0)
        if GPIO.input(self.washbutton):
            GPIO.output(self.washlight, 0)
            putState(self.machine, state = -2)
            self.washing = False
        if not self.washing:
            if getState(self.machine, 'door') != 0:
                GPIO.output(self.closelight, 0)
                GPIO.output(self.openlight, 1)
            else:
                GPIO.output(self.openlight, 0)
                GPIO.output(self.closelight, 1)
                if getState(self.machine, 'state') == -1:
                    GPIO.output(self.washlight, 1)
                    for student in getState(self.machine, 'studentid'):
                        machineid, endtime = getData(student, ['machineid','endtime'])
                        for machine in range(len(machineid)):
                            if machineid[machine] == self.machine:
                                endtime[machine]=time.time()+washTime
                        putData(student,endtime=endtime)
                        self.washing = True


machine1 = WashingMachine(1,18,23,24,25,12)
machine2 = WashingMachine(2,16,20,21,26,19)
machine3 = WashingMachine(3,13,6,5,22,27)
try:
    while True:
        machine1.main()
        machine2.main()
        machine3.main()
except KeyboardInterrupt:
    GPIO.cleanup()