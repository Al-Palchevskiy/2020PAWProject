
"""
Authors:        Kevin Ta & Al Palchevskiy
Date:           2020 Aug 20
Purpose:        This code starts serrial communication with Roboteq motor controller, and sends initial configuration settings.
                Next two bluetooth connections are started on separate threads.
                In an infinite loop hall sensor reading are retrived from each bluetooth connection and converted into speed commands for each wheel.
                Then speed commands get sent to the motor controller.

"""


# IMPORTED LIBRARIES

import os
import datetime, time
import math
import sys
import serial

#import numpy as np
#import pandas as pd

from multiprocessing import Queue
from threading import Thread

# DEFINITIONS

RESPONSE_TIME = 0.020 # (s) Roboteq's response time for serial commands is 16ms

dir_path = os.path.dirname(os.path.realpath(__file__))  # Current file directory
WHEEL_DIAMETER = 0.61   # (m)
WHEEL_BASE = 0.52       # (m)

MAX_SPEED = 6 # (km/h)
MAX_ACCELERATION = 1000 # (dRPM/s)
MIN_ACCELERATION = 200
DEFAULT_ACCELERATION = 1000
MAX_POWER = 100 # (%)
MIN_POWER = 25

MAX_RPM = MAX_SPEED*1000/60/(math.pi*WHEEL_DIAMETER) # Covert km/h to m/min to rev/min

# note: self calibrationg code might be a good idea
DEAD_ZONE_MIN = -150
DEAD_ZONE_MAX = 150

MAX_HALL_VALUE = 3000 # 3000 is max output out of 4096 resolution max
MIN_HALL_VALUE = -3000


# CUSTOM LIBRARIES

# Include subdirectories for libraries
# TODO: Reorganize file structure to have all libraries in shared folder
sys.path.insert(0, os.path.join(dir_path, 'WheelModule'))
sys.path.insert(0, os.path.join(dir_path, 'FrameModule'))

from WheelDAQLib import ClWheelDataParsing
from FrameDAQLib import ClFrameDataParsing

# DICTIONARIES

# Python dictionaries storing name of data source, bluetooth address, data storage path, and the recorded data
Left = {'Name': 'Left', 'Address': '98:D3:51:FD:AD:F5', 'motorChannel' : 1, 'Placement': 'Left', 'Device': 'Module',
        'AccPath': os.path.join('IMU Data', '{} leftAcc.csv'.format(
            datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))),
        'GyroPath': os.path.join('IMU Data', '{} leftGyro.csv'.format(
            datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))),
        'Path': '',
        #~ 'DisplayData-IMU_6': np.zeros((7, 2000)),
        'Queue': Queue(),
        'RunMarker': Queue()
        }

Right = {'Name': 'Right', 'Address': '98:D3:81:FD:48:C9', 'motorChannel' : 2, 'Placement': 'Right', 'Device': 'Module',
         'AccPath': os.path.join('IMU Data', '{} rightAcc.csv'.format(
             datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))),
         'GyroPath': os.path.join('IMU Data', '{} rightGyro.csv'.format(
             datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))),
         'Path': '',
         #~ 'DisplayData-IMU_6': np.zeros((7, 2000)),
         'Queue': Queue(),
         'RunMarker': Queue()
         }

RaspberryPi = {'Name': 'Frame', 'Address': 'B8:27:EB:A3:ED:6F', 'Host': '', 'Port': 65432,
               'Placement': 'Middle', 'Device': 'Module',
               'Path': '',
               'ProximityPath': '',
               #~ 'DisplayData-IMU_6': np.zeros((10, 1800)),
               #~ 'DisplayData-IMU_9': np.zeros((13, 600)),
               'Queue': Queue(),
               'RunMarker': Queue()
               }


# Dictionary associating measurement descriptions to array space
IMUDataDict = {'X Acceleration (m/s^2)': 1, 'Y Acceleration (m/s^2)': 2, 'Z Acceleration (m/s^2)': 3,
               'X Angular Velocity (rad/s)': 4, 'Y Angular Velocity (rad/s)': 5, 'Z Angular Velocity (rad/s)': 6,
               'Pitch (deg)': 7, 'Roll (deg)': 8, 'Heading (deg)': 9,
               'X Magnetometer': 10, 'Y Magnetometer': 11, 'Z Magnetometer': 12,
               'Proximity (cm)': 1}

# CLASSES

class Control():
    """
    Class for running all module data acquisition (ClWheelDataParsing, ClFrameDataParsing).
    """

    def __init__(self, sources):
        """
        Purpose:    Initialize class with sub-class structures and initial variables. Creates a parsing class
                    for every passed data source.
        Passed:     Sources of data (Left Wheel, Right Wheel, Raspberry Pi, Left Phone, Right Phone, Frame Phone)
        """
        self.ser = serial.Serial(port = '/dev/serial0', baudrate = 115200, timeout = 0)
        time.sleep(2)
        
        print ("Initializing motor controller")
        commandsList = []
        commandsList.append ('^ECHOF 1') #turn echo off
        commandsList.append ('^MMOD 1 1') #mode 1 closed loop speed, mode 5 closed loop torque
        commandsList.append ('^MMOD 2 1')
        commandsList.append ('^MAC 1 {}'.format(DEFAULT_ACCELERATION)) #set default acceleration rate
        commandsList.append ('^MAC 2 {}'.format(DEFAULT_ACCELERATION))
        commandsList.append ('^MDEC 1 100') #set deceleration to 1deg/s
        commandsList.append ('^MDEC 2 100')
        commandsList.append ('^MXPF 1 {}'.format(MAX_POWER)) #set power limit to 100% forward
        #~ commandsList.append ('^MXPR 1 {}'.format(MIN_POWER)) #set power limit to 100% reverse
        commandsList.append ('^MXPF 2 {}'.format(MAX_POWER))
        #~ commandsList.append ('^MXPR 2 {}'.format(MIN_POWER))
        commandsList.append ('^RWD 500') #set watchdog timeout to 500ms
        commandsList.append('!EX') #Emergency Stop, turn off regen for both motors (coast mode)
        commandsList.append ('!S 1 0') #set motors speed to zero
        commandsList.append ('!S 2 0')

        self.sendCommandsList(commandsList);

        self.sources = sources  # Make globally set source dictionaries available to class
        self.instDAQLoop = {}  # Initialize dictionary containing data acquisition
        self.activeSensors = [] # Initialize active sensor list
        threads = {}

        # Initialize every passed data module, starts bluetooth connections on separate threads
        for dataSource in self.sources:
            self.instDAQLoop[dataSource['Name']] = ClWheelDataParsing(dataSource)
            threads[dataSource['Name']] = Thread(target=self.instDAQLoop[dataSource['Name']].fnRun)
            threads[dataSource['Name']].start()
            
        # Loop while waiting for the bluetooth buffer to clear
        while (not self.instDAQLoop['Left'].clearedBuffer or not self.instDAQLoop['Right'].clearedBuffer):
            time.sleep(1)


    def fnStart(self):
        """
        Purpose:    Runs each data acquisition loop in a separate thread.
                    Runs QT update display.
                    Dumps data in csv file when complete.
        Passed:     None
        """
        
        # note: code can be optimized here, also might be a good idea to not send less repeat commands
        
        offsetLeft = self.instDAQLoop['Left'].hallData[-1]
        offsetRight = self.instDAQLoop['Right'].hallData[-1]
        
        print ("Printing received data")
        safe = True
        rpmLeftOld = 0
        rpmRightOld = 0
        
        while safe:
            commandsList = []
            safe = self.saftyCheck()
            
            #fliping the signs because hall sensor are installed backwards (flip left to right)
            hallDataLeft = -(self.instDAQLoop['Left'].hallData[-1] - offsetLeft)
            hallDataRight = -(self.instDAQLoop['Right'].hallData[-1] - offsetRight)

            #~ rpmLeft = 0 #turn off the speed commands for this wheel
            rpmLeft = self.calcRPM(hallDataLeft)
            accelLeft = self.calcAccel(hallDataLeft)
            powerLeft = self.calcPower(hallDataLeft)
            
            #~ rpmRight = 0 #turn off the speed commands this wheel
            rpmRight = self.calcRPM(hallDataRight)
            accelRight = self.calcAccel(hallDataRight)
            powerRight = self.calcPower(hallDataRight)
            
            # instead of decelaration, switching to coast mode
            if rpmLeft < rpmLeftOld:
                rpmLeft = 0
            if rpmRight < rpmRightOld:
                rpmRight = 0
            
            # when rpm is less the 0 (going backwards) enable coast mode
            if rpmLeft <= 0 and rpmRight <= 0:
                commandsList.append('!EX')
            else:
                commandsList.append('!MG')
            
            commandsList.append ('!S 1 {:<4}'.format(rpmLeft))
            commandsList.append ('!S 2 {:<4}'.format(rpmRight))
            
            # additional commands to adjust the power/torque ramp up
            #~ if rpmLeft > 0:
                #~ commandsList.append ('^AC 1 {}'.format(accelLeft))
                #~ commandsList.append ('^MXPF 1 {}'.format(powerLeft))
            #~ if rpmRight > 0:
                #~ commandsList.append ('^AC 2 {}'.format(accelRight))
                #~ commandsList.append ('^MXPF 2 {}'.format(powerRight))
                
            print('{} Left {:<5} Right {:<5}'.format(commandsList, hallDataLeft, hallDataRight))
            
            self.sendCommandsList(commandsList);
            
            rpmLeftOld = rpmRight
            rpmRightOld = rpmLeft
            
                
        print("Loss of input, ending program")
    
    def calcRPM (self, hallValue):
        if hallValue > DEAD_ZONE_MIN and hallValue < DEAD_ZONE_MAX:
            rpm = 0
        else:
            rpm = int(MAX_RPM*(hallValue/MAX_HALL_VALUE))
        return rpm
        
    def calcAccel (self, hallValue):
        if hallValue > DEAD_ZONE_MIN and hallValue < DEAD_ZONE_MAX:
            accel = MIN_ACCELERATION
        else:
            accel = abs(int(MIN_ACCELERATION+(MAX_ACCELERATION-MIN_ACCELERATION)*(hallValue/MAX_HALL_VALUE)))
        return accel
        
    def calcPower (self, hallValue):
        if hallValue > DEAD_ZONE_MIN and hallValue < DEAD_ZONE_MAX:
            powerPercent = MIN_POWER
        else:
            powerPercent = (int(MIN_POWER+(MAX_POWER-MIN_POWER)*(hallValue/MAX_HALL_VALUE)))
        return powerPercent
        
    def saftyCheck (self):
        """
        checks if the values are updating
        """
        checks = 1
        while self.instDAQLoop['Left'].hallData[-1] == self.instDAQLoop['Left'].hallData[-1 -checks]:
            checks = checks + 1
            if checks == 100:
                return False
        checks = 1
        while self.instDAQLoop['Right'].hallData[-1] == self.instDAQLoop['Right'].hallData[-1 -checks]:
            checks = checks + 1
            if checks == 100:
                return False
        return True
        
    def sendCommandsList (self, commandsList):
        """
        takes a list of commands and sends them over serial with delay between each command.
        Each command is ended with "\r" character, confirmation reply is read and not stored.
        """
        
        for command in commandsList:
            time.sleep(RESPONSE_TIME)
            #~ print ('{}'.format(command))
            self.ser.write((command + '\r').encode())
            self.readSerialReply()
            
    def readSerialReply (self):
        """
        reads serial reply, peices together a string of character and string is returned.
        """
        string = ''
        try:
            x = self.ser.read().decode()
        except:
            x = ''
        while (len(x) > 0):
            if (x == '\r'):
                #print (string)
                string = ''
                #break
            else:
                string = string + x
            try:
                x = self.ser.read().decode()
            except:
                x = ''
        return string


if __name__ == "__main__":

    # Create directories
    if not os.path.exists(os.path.join(dir_path, 'IMU Data')):
        os.mkdir(os.path.join(dir_path, 'IMU Data'))

    # Sets status to active for recording user input sources
    status = 'Active'
    sources = []

    #~ # Prompts user for inputs
    #~ print('Please input the letter corresponding to which sources you would like to include: ')
    #~ print('l - Left Wheel Module')
    #~ print('r - Right Wheel Module')
    #~ print('f - Frame Module')
    #~ print('None / Wrong - End input or enter defaults')

    #~ # Collects all user input sources
    #~ while status == 'Active':
        #~ source = input('Input: ')

        #~ if source == 'l' and Left not in sources:
            #~ sources.append(Left)
            #~ print('Sources: {}'.format([source['Name'] for source in sources]))
        #~ elif source == 'r' and Right not in sources:
            #~ sources.append(Right)
            #~ print('Sources: {}'.format([source['Name'] for source in sources]))
        #~ elif source == 'f' and RaspberryPi not in sources:
            #~ sources.append(RaspberryPi)
            #~ print('Sources: {}'.format([source['Name'] for source in sources]))
        #~ elif not sources:
            #~ status = 'Inactive'
            #~ sources = [Left, Right]
            #~ print('Sources: {}'.format([source['Name'] for source in sources]))
        #~ else:
            #~ status = 'Inactive'
            #~ print('Sources: {}'.format([source['Name'] for source in sources]))

    # Begin data collection
    sources = [Left, Right]
    instControl = Control(sources)
    instControl.fnStart()
