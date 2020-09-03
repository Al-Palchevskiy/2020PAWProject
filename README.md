# 2020PAWProject
Push-Assist Wheelchair project. Code for a motorized wheelchair with sensor for users input, users input is assisted by electric motors.

**Author:**			Al Palchevskiy  
**Date Started:**	2020 Jul 1st  
**Github Repository:** https://github.com/Al-Palchevskiy/2020PAWProject

***
## 1.0 Introduction
The goal of the project is to have a motorized wheelchair that would be controlled in the same was as a manual wheelchair except with push-assist when users input is sensed. Additional torque would be applied to each wheel independently and proportional to users input.

***
## 2.0 Hardware Set-up
There are 4 main componets    
2x wheel modules (Teensy 3.6)   
1x main controller (Raspberry Pi 3B+)   
1x motor controller (Roboteq SBL2360)   

### 2.1 Wheel Modules
The function of the wheel modules are to get users input and transmit the input data to the main controller via bluetooth.    
The main componets of the wheel modules are   
1x Teensy 3.6 micro-controller    
1x hall effect sensor   
1x HC-05 bluetooth module   
1x Li-ion battery   

The hall effect sensor is used to get users input. The hall effect voltage reading is converted using 13bit resolution ADC with 1.2 for refereance. The 13bit unsigned value is then remapped to a 12bit signed value. The input data is then packaged using serialized data struture "Proto Buffers", encoded using "COBS" and sent over bluetooth.    
HC-05 bluetooth module is connected to Teensy's Serial1 port, the data that is writen to Serial1 gets sent over bluetooth.

Bluetooth Paramters of HC-05 modules    
Baudrate 230400 bit/s   
Slave mode    

| Module | Name        | Bluetooth Address | Pin  |
| :----: | :---------: | :---------------: | :--: |
| Left   | HC-05-LEFT  | 98:D3:51:FD:AD:F5 | 0303 |
| Right  | HC-05-RIGHT | 98:D3:81:FD:48:C9 | 1234 |

HC-05 bluetooth modules can be configured when booted up in "AT Command" mode, to do this hold down the setting button on HC-05 module while powering it up. Then write to Serial1 on Teensy desired commands to configure HC-05 ending each command with \r\n
eg Serial1.write("AT+NAME=HC-05-RIGHT\r\n"); will change the name of the module to "HC-05-RIGHT"

### 2.2 Main controller
The function of the main controller is to send initialization commands to Roboteq motor controller over serial connection, initiate bluetooth connections with both teensy modules and continusly receive user input data (hall sensor reading). The user input data is converted into motor commands for the motor controller and sent over serial. Confirmation replys from motor controller are read and not stored nor deplayed.

### 2.3 Motor Controller
The fuction of the motor controller is to continusly receive stream of serial commands from DB25 port and power the motors acording to the commands received.
Roboteq SBL2360 motor controller can be configured in "Closed loop speed mode" and "Torque mode".   
To use this motor controller in "torque mode", the "switching mode" for both motors has to be configured for "sinusoidal setting".
For "closed loop speed mode" ether Trapazoidal or Sinusoidal switching modes will work.   

In torque control mode commands are sent to motor controller for a trager current draw for each motor. Motor controller has a setting for current ramp up, how fast the currect draw is rasid. This setting can be configured between 1mA/s up to 500,000mA/s this is the upper limit. Withing this upper limit motor controller also has PID setting to configure how this target current draw is achived.

In closed loop speed mode commands are sent to motor controller for a traget RPM speed for each wheel. Motor controller has a setting for maxium speed in RPM and acceleration in RPM/s. The setting for maximum RPM is for the scaling purposes only, this will not limit the speed of the motors if a 110% of the maximum speed is set as traget. PID setting also apply here.

Motor controller prametes   
Number of polls: 23    
Closed loop feedback sensor: Hall Sensor    
Switching mode: "Trapazoidal" or "Sinusoidal"   

| Number | Location | Motor Direction | Hall Sensor Map |
| :----: | :------: | :-------------: | :-------------: |
| 1      | LEFT     | Direct          | 1               |
| 2      | RIGHT    | Inverted        | 5               |

***
## 3.0 Code
Two scrips are available to run the system in either closed loop speed mode or torque mode.   
Both scrips start off by starting a serial connection with a Roboteq motor controller and sending out initialization commands such as: Operating mode, Acceleration, power limit, amp limit, watch dog timeout and more. Next bluetooth connections are initiated on separate threads, bluetooth bufferes are cleared and user input (hall sensor readings) data are ready to be polled.    
The hall sensor voltage reading is mapped (in Teensy code) to -4096 upto 4096 value range. At rest the hall sensor does not sit at exactly zero but some offset value. Calibration is done on Raspberry Pi by saving the first value as "offset" from each hall sensor befor starting a control loop. This offset value is then subtracted from every subsequit reading polled.   
In a control loop user input date is polled, corrected for offset and converted into a speed command or a torque command. Conversion to a speed or torque command is as simple as scaling the value down to -1000 upto 1000 range and including this value in a command. Commands are generated for each wheel independatly, these commands are stored in list (commandsList) then this list is sent into a function (sentCommandsList). This function sends this commands over serial to roboteq with a delay and reply read between each command.   
Roboteq can react to a command within 16ms, that is the delay added in to code between each command. Roboteq replys to Runtime commands with "+" when command is acknoledged. This reply is read (to clear the buffer) each time and not stored.    

***

## 4.0 Future Work    
### 4.1 Software Work   
The torque from the motors doesn't feel natural, sometimes it works and other times the torque comes in very ubruptly and causes the wheels to slip from excessive torque. This can possibly be resolved with sufficent tuning of PID and Acceleration setting. For better ability to troubleshoot and for tuning reasons it would be helpful to have amps readout from each motor desplyed on the console along with commands sent.    

### 4.2 Hardware Deficiencies   
The hall sensor are not idential, the at rest reading (offset value) is very different from one to another. Left sensor is reading +300 and Right sensor is reading -700 out of -4096 to 4096 range. Also it seems like left sensor is very sensative in the negative direction. All of this combined might result in two wheels feeling different requiring user to use more force on one side than another or just unable to drive in a straight line.    
Also Roboteq motor controller does not seem to have a function to turn off regen. The only way to truly turn off regen is "emergency stop" command. And at this point both wheels are free to coast, however if one wheel motor needs to be engauged to correct course the other wheel also engauges in a regen mode. Effectivly resulting in one wheel accelerating while the other wheel is decelerating. Even in torque mode when 0 amps set as target for current draw, the motors generate current if wheels are rotated. This might result in a wheelchair that is good at going uphill or straight line, but feels heavy clubersum in a tight corners, as chair is not able to turn easyly with regen on both wheels.
