import RPi.GPIO as GPIO
import time
from database import putState, getState
from account import putData, getData
import urllib2

washTime = 40*60    #the hostel washing machine takes about 40mins for a wash

GPIO.setmode(GPIO.BCM)

class WashingMachine:
    def __init__(self, machine, openlight, closelight, washlight, doorbutton, washbutton):
        self.machine = machine    #machineid
        self.openlight = openlight    #Green LED pin, lights up when door is open
        self.closelight = closelight    #Red LED pin, lights up when door is closed
        self.washlight = washlight    #Amber LED pin, lights up when laundry is being washed
        self.doorbutton = doorbutton    #Door button pin, pressed when user closes the foor
        self.washbutton = washbutton    #Wash button pin, pressed when washing machine has finished its wash
        self.washing = False    #state of washing, True if washing, False if not washing
        GPIO.setup(self.openlight, GPIO.OUT)
        GPIO.setup(self.closelight, GPIO.OUT)
        GPIO.setup(self.washlight, GPIO.OUT)
        GPIO.setup(self.doorbutton, GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.washbutton, GPIO.IN, GPIO.PUD_DOWN)
    def main(self):
        if GPIO.input(self.doorbutton):    #if door closed button is pressed, switches off green LED and switches on red LED
            GPIO.output(self.openlight, 0)
            GPIO.output(self.closelight, 1)
            putState(self.machine, door = 0)
        if GPIO.input(self.washbutton) and GPIO.input(self.washlight):    #if it was washing finished washing button is pressed, switches off amber LED and informs firebase wash is done
            GPIO.output(self.washlight, 0)
            putState(self.machine, state = -2)
            self.washing = False
        if not self.washing:    #if its not washing, it will check firebase if door should open
            if getState(self.machine, 'door') != 0:
                GPIO.output(self.closelight, 0)
                GPIO.output(self.openlight, 1)
            else:    #check firebase if washing should begin and updates wash time to users
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

#create 3 washing machines on 1 pi
machine1 = WashingMachine(1,18,23,24,25,12)
machine2 = WashingMachine(2,16,20,21,26,19)
machine3 = WashingMachine(3,13,6,5,22,27)
try:
    while True:    #runs the 3 machines alternatingly
        try:
            machine1.main()
            machine2.main()
            machine3.main()
        except urllib2.HTTPError:
            continue    #prevents error when unable to retrieve info from firebase
except KeyboardInterrupt:
    GPIO.cleanup()