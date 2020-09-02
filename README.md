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



