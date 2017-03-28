#v5.2 
#added PID

import math
import libdw.util as util
import libdw.sm as sm
import libdw.gfx as gfx
from soar.io import io
import time
import sys

class PID(object): #needs import time
    def __init__(self, Kp = 1, Ki = 0, Kd = 0, min_output = 0, max_output = 1, integrator_min = -sys.maxint, integrator_max = sys.maxint,  derivativeN = 5, backCalc = False, backCalcCoeff = 0.0):
        self.Kp = Kp #Proportional constant
        self.Ki = Ki #Integral Constant
        self.Kd = Kd #Derivative Constant

        self.I_val = 0.0
        self.integrator_min = integrator_min
        self.integrator_max = integrator_max
        self.min_output = min_output
        self.max_output = max_output
        self.prevError = None
        self.prevTime = time.time()
        self.clamped = False
        
        self.derivIdx = 0
        self.derivN = derivativeN #num of derivatives to average. Increase value to reduce derivative noise. Not too much to reduce derivative dead time.
        self.derivVals = [0 for i in range(derivativeN)]

        #not implemented yet
        self.backCalc = backCalc
        self.backCalcCoeff = backCalcCoeff
        self.prevOut = None

    def __call__(self, x):
        #calculate dt = time since previous output measurement
        timeNow = time.clock() #get the time once to prevent waiting for execution time
        dt = timeNow - self.prevTime
        self.prevTime = timeNow #save current time as previous time for next reading
        
        #calculate error and P value
        error = self.setpoint - x
        self.P_val = self.Kp * error
        
        #clamp the I value
        if self.clamped == False:
            if self.I_val < self.integrator_max and self.I_val > self.integrator_min:
                self.I_val += self.Ki * error * dt

        #reduce the integral using back calculation if signal is clamp
        if self.backCalc == True and self.clamped == True:
            self.I_val += self.Ki * (error - (self.backCalcCoeff * self.backCalcLevel)) * dt
        
        #Calculate the moving average of the derivatives to reduce sensor noise.
        if self.prevError != None:
            self.derivVals[self.derivIdx] = (error - self.prevError) / dt
        self.D_val = self.Kd * reduce(lambda x, y: x + y, self.derivVals)/float(self.derivN)
        self.derivIdx = (self.derivIdx + 1) % self.derivN #advance the index of the list
        error = self.prevError

        output = self.I_val + self.P_val + self.D_val
        self.prevOut = output
        
        #clamp the output signal to the expected output range
        if output > self.max_output:
            self.clamped = True
            output = self.max_output
            self.backCalcLevel = output - self.prevOut
        if output < self.min_output:
            self.clamped = True
            output = self.min_output
            self.backCalcLevel = output - self.prevOut
        else:
            self.clamped = False

        return output

    def set_setpoint(self, setpoint):
        self.setpoint = setpoint

class MySMClass(sm.SM):
    startState=0
    
    def __init__(self):
        self.wallFollower = PID(Kp = 1, Ki = 0, Kd = 0.4, min_output = -0.5, max_output = 0.5, integrator_min = -0.05, integrator_max = 0.05,  derivativeN = 3, backCalc = False, backCalcCoeff = 0.0)
        self.wallFollower.set_setpoint(0.3)
        
    def getNextValues(self, state, inp):
        print "#########   %d    #########" %(state)
        print inp.sonars# list
        print inp.odometry.theta
        a =0.6
        if state == 0:   #Nothing nearby -> move straight
            if inp.sonars[2] > a*0.52 and inp.sonars[1] > a*0.42 and inp.sonars[3] > a*0.42:
                speed = 0.1
                rotate = 0
                next_state = 0
            elif inp.sonars[2] <a*0.55:    #front obstacle
                speed = 0
                rotate = 0.3
                next_state = 0
            elif inp.sonars[2] > a*0.5:
                speed = 0.1
                rotate = 0
                next_state = 1
            else:                       #side obstacle
                speed = 0#0.2
                rotate = 0#-0.2
                next_state = 1
        elif state == 1:                #side obstacle detected
            if inp.sonars[2] > 0.35:
                speed = 0.1
                rotate = self.wallFollower(inp.sonars[3])
                print 'rotation speed: ' + str(rotate)
                next_state = 1
            else:
                speed = 0.1
                rotate = 0.4
                next_state = 2
            '''
            if inp.sonars[1]< a*0.42:      #too close to left
                speed = 0.1
                rotate = -0.3
                next_state = 1
            elif inp.sonars[3] <a*0.42:    #too close to right
                speed = 0.1
                rotate = 0.3
                next_state = 1
            else:
                speed = 0
                rotate = 0
                next_state = 2
                '''
        elif state == 2:                
            if inp.sonars[4]< a*0.3:      
                speed = 0#0.2
                rotate = 0.3
                next_state = 2
            elif inp.sonars[0]< a*0.3:  
                speed = 0#0.2
                rotate = -0.3
                next_state = 2
            else:
                speed = 0.1
                rotate = 0
                next_state = 3

        elif state == 3:
            if inp.sonars[2] > a*0.5 and a*0.71 > inp.sonars[1] > a*0.42 and a*0.71 > inp.sonars[3] > a*0.42:
                speed = 0.1
                rotate = 0
                next_state = 3
            elif inp.sonars[2] <a*0.5:    #front obstacle
                speed = 0
                rotate = 0.3
                next_state = 3
            elif inp.sonars[2] > a*0.5 and inp.sonars[3]>a*0.71: #turning open corners
                speed = 0.1
                rotate = -0.2
                next_state = 3
            elif inp.sonars[2] > a*0.5 and inp.sonars[1] > a*0.71 and inp.sonars[3] > a*0.71:
                speed = 0.1
                rotate = 0
                next_state = 3
            else:                   
                speed = 0.1
                rotate = 0#-0.2
                next_state = 1

        return (next_state, io.Action(fvel = speed, rvel = rotate)) #(state, io.Action(fvel = 0.05, rvel = 0.05))

mySM = MySMClass()
mySM.name = 'brainSM'
mySM.start()

######################################################################
###
###          Brain methods
###
######################################################################

def plotSonar(sonarNum):
    robot.gfx.addDynamicPlotFunction(y=('sonar'+str(sonarNum),
                                        lambda: 
                                        io.SensorInput().sonars[sonarNum]))

# this function is called when the brain is (re)loaded
def setup():
    robot.gfx = gfx.RobotGraphics(drawSlimeTrail=False, # slime trails
                                  sonarMonitor=False) # sonar monitor widget
    
    # set robot's behavior
    robot.behavior = mySM

# this function is called when the start button is pushed
def brainStart():
    robot.behavior.start(traceTasks = robot.gfx.tasks())

# this function is called 10 times per second
def step():
    inp = io.SensorInput()
    # print inp.sonars[3]
    robot.behavior.step(inp).execute()
    io.done(robot.behavior.isDone())

# called when the stop button is pushed
def brainStop():
    pass

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
