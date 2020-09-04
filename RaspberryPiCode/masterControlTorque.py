
"""
Authors:        Kevin Ta & Al Palchevskiy
Date:           2020 Aug 20
Purpose:        This code starts serrial communication with Roboteq motor controller, and sends initial configuration settings.
                Next two bluetooth connections are started on separate threads.
                In an infinite loop hall sensor reading are retrived from each bluetooth connection and converted into torque commands for each wheel.
                Then torque commands get sent to the motor controller.

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
DEFAULT_ACCELERATION = 500000 # (mA/s) in torque mode
DEFAULT_DECELERATION = 500000
AMP_LIMIT = 100 # (dA)
MAX_POWER = 100 # (%)
MIN_POWER = 25

MAX_RPM = MAX_SPEED*1000/60/(math.pi*WHEEL_DIAMETER) # Covert km/h to m/min to rev/min

DEAD_ZONE_MIN = -300
DEAD_ZONE_MAX = 150

MAX_HALL_VALUE = 2700 # 2600 is max output out of 4096 (12bit) resolution
MIN_HALL_VALUE = -2300 # -1900 is the lowest output out of 4096

#list of commands to that have a reply with a value from roboteq
#?A 1 is a command to get amp draw on motor 1
#?A is a command to get amp draw on all motors
queryCommandsList = ['?A 1','?A 2'] 


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
        Passed:     Sources of data (Left Wheel, Right Wheel)
        """
        self.ser = serial.Serial(port = '/dev/serial0', baudrate = 115200, timeout = 0)
        time.sleep(2)
        
        print ("Initializing motor controller")
        commandsList = []
        commandsList.append ('^ECHOF 1') #turn echo off
        commandsList.append ('^MMOD 1 5') #mode 1 closed loop speed, mode 5 closed loop torque
        commandsList.append ('^MMOD 2 5')
        commandsList.append ('^MAC 1 {}'.format(DEFAULT_ACCELERATION)) #set default acceleration rate
        commandsList.append ('^MAC 2 {}'.format(DEFAULT_ACCELERATION))
        commandsList.append ('^MDEC 1 {}'.format(DEFAULT_DECELERATION)) #set defualt deceleration rate
        commandsList.append ('^MDEC 2 {}'.format(DEFAULT_DECELERATION))
        commandsList.append ('^ALIM 1 {}'.format(AMP_LIMIT)) #set amp limit
        commandsList.append ('^ALIM 2 {}'.format(AMP_LIMIT))
        commandsList.append ('^MXPF 1 {}'.format(MAX_POWER)) #set power limit to 100% forward
        #~ commandsList.append ('^MXPR 1 {}'.format(MIN_POWER)) #set power limit in reverse
        commandsList.append ('^MXPF 2 {}'.format(MAX_POWER))
        #~ commandsList.append ('^MXPR 2 {}'.format(MIN_POWER))
        commandsList.append ('^RWD 500') #set watchdog timeout to 500ms
        commandsList.append ('!EX') #Emergency Stop, turn off regen for both motors (coast mode)
        commandsList.append ('!G 1 0') #set motors torque to zero
        commandsList.append ('!G 2 0')
        commandsList.append ('!MG')
        
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
        This function first saves the initial value from both sensors and used as offset value for calibration
        Enters into a infinite loop where data from hall sensors is converted into a torque command and sent out to roboteq
        Query commands are also sent and replys are recoreded.
        Prints to screen torque commands, replies from Query commands, and hall sensor data from both sides
        """
        replyList = []
        safe = True
        
        # calibration, there is probably a better way to do this.
        offsetLeft = self.instDAQLoop['Left'].hallData[-1]
        offsetRight = self.instDAQLoop['Right'].hallData[-1]
        
        while safe:
            # this is list of commands to control the motors, no reply is saved from these commands
            commandsList = []
            
            # check if the values are updating
            safe = self.saftyCheck()
            
            #fliping the signs because hall sensor are installed backwards (flip left to right)
            hallDataLeft = -(self.instDAQLoop['Left'].hallData[-1] - offsetLeft)
            hallDataRight = -(self.instDAQLoop['Right'].hallData[-1] - offsetRight)

            torqueLeft = self.calcTorque(hallDataLeft, offsetLeft)
            torqueRight = self.calcTorque(hallDataRight, offsetRight)
            
            #the value in the command is formatted to fill 4 spaces {:<4}
            #this formating is done for ease of reading the values off teh screen not for roboteq
            commandsList.append ('!G 1 {:<4}'.format(torqueLeft))
            commandsList.append ('!G 2 {:<4}'.format(torqueRight))
            
            #sending commands to reboteq, not saving reply from commands that make motors rotate
            self.sendCommandsList(commandsList);
            #saving the replys from the query commands
            replyList = self.sendCommandsList(queryCommandsList)
            
            print('{} {} Left {:<5} Right {:<5}'.format(commandsList, replyList, int(hallDataLeft), int(hallDataRight)))
                
        #if safty check failed, the loop brakes
        print("Loss of input, ending program")
        
    def calcTorque (self, hallValue, offset):
        """
        Basically this function scales down the hall value from range of (-4096 to +4096) down to range (-1000 to +1000)
        because that is the acceptable range for the torque commands. +1000 = 100% of the max amp draw will be set as target
        Also implents deadzone where the small imputs are ignored.
        """
        if hallValue < DEAD_ZONE_MIN:
            torque = int(1000*(hallValue-DEAD_ZONE_MIN)/abs(MIN_HALL_VALUE+offset))
        elif hallValue > DEAD_ZONE_MAX:
            torque = int(1000*(hallValue-DEAD_ZONE_MAX)/(MAX_HALL_VALUE+offset))
        # hall values is within deadzone, the input is ignored
        else:
            torque = 0
        return torque
        
    def saftyCheck (self):
        """
        checks if the values are updating. If values not updating sensor lost connection, safty check fails.
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
        reply = []
        
        for command in commandsList:
            #~ print ('{}'.format(command))
            self.ser.write((command + '\r').encode())
            time.sleep(RESPONSE_TIME)
            reply.append ('{:<5}'.format (self.readSerialReply()))
            
        return reply
            
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
                pass
            else:
                string = string + x
            try:
                x = self.ser.read().decode()
            except:
                x = ''
        #~ print (string)
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
