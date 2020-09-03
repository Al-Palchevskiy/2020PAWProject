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

Motor controller prametes
Number of polls: 23    
Closed loop feedback sensor: Hall Sensor
Switching mode: "Trapazoidal" or "Sinusoidal"

| Number | Location | Motor Direction | Hall Sensor Map |
| :----: | :------: | :-------------: | :-------------: |
| 1      | LEFT     | Direct          | 1               |
| 2      | RIGHT    | Inverted        | 5               |




