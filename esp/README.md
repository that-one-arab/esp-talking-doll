## Requirements
- ESP32 development board
- MAX98357A
- INMP441
- Micro SD Adapter
- Button

## Setup
- Connect the required devices to the ESP using the map supplied inside `map.ods`
- Install [Arduino IDE](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)
- Install ESP board manager ([Example tutorial](https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/))
- Set your development board to **DOIT ESP32 DEVKIT V1**
- Install the below dependancies using Arduino IDE .zip library installation:
- - [arduino-audio-tools](https://github.com/pschatzmann/arduino-audio-tools)
- - [arduino-libhelix](https://github.com/pschatzmann/arduino-libhelix)
- Place the files inside `wav` directory to the root of your SD card
- Open `esp/index/index.ino`, modify the below values (you should not need to modify anything else):
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* url = "http://YOUR_IP/talk";
```

## Usage
Upload the `esp/index/index.ino` sketch to your ESP32. If you hear the sound "ready" play, you are ready to communicate with the ESP.


## Notes
- You should make sure that your Micro SD Card is formatted to a FAT32 file system.

- To avoid timeout errors that can occur if the request takes too long, increase HTTPClient's default HTTP request timeout by modifying `HTTPCLIENT_DEFAULT_TCP_TIMEOUT`. I used 15000 (15 seconds)
```cpp
#define HTTPCLIENT_DEFAULT_TCP_TIMEOUT (15000)
```
(You need to find where the `ESP32`'s default libraries are stored. In ubuntu they are stored in `/home/yourusername/.arduino15/packages/esp32/hardware/esp32/2.0.9/libraries` so in my case I need to modify `/home/yourusername/.arduino15/packages/esp32/hardware/esp32/2.0.9/libraries/HTTPClient/src/HTTPClient.h` In other OSs a quick google search should help you)

- If there are any library issues (happens too often with arduino projects) I have uploaded the library dependencies [here](https://drive.google.com/drive/folders/1Yyq3cKPAaLeDT-WV92RhvdenckKjznbN?usp=sharing)