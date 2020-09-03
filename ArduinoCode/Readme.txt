Setup for Teensy 3.6
1. Install Arduino IDE
2. Add Teensy board to the list of avaliable boards
3. Copy the libraries to Arduino IDE libraries directory eg (C:\Program Files (x86)\Arduino\libraries)
4. Open "teensyClient.ino" and upload to the board

Making changes to the bluetooth message and Protocol Buffer
1. edit "pbSensorMsgGen.cpp/h" files
2. edit "teensyClient.ino" file as needed to edit message
3. edit "carisPAWBuffers.proto" file, located at (..\Arduino\libraries\nanopb\generator-bin)
4. open cmd terminal
5. navigate to "..\Arduino\libraries\nanopb\generator-bin"
6. enter following into the terminal
"protoc --python_out=. carisPAWBuffers.proto" enter and
"protoc --nanopb_out=. carisPAWBuffers.proto" enter
full lines could look like this
C:\Program Files (x86)\Arduino\libraries\nanopb\generator-bin>protoc --python_out=. carisPAWBuffers.proto
C:\Program Files (x86)\Arduino\libraries\nanopb\generator-bin>protoc --nanopb_out=. carisPAWBuffers.proto
7. copy "carisPAWBuffers.pb.c/h" files to libraries (..\Arduino\libraries\CarisPAWBuffers) and overwrite
8. copy "carisPAWBuffers_pb2.py" file to Raspberry Pi