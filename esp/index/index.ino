#include "SD.h"
#include <SPI.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "AudioTools.h"
#include "AudioCodecs/CodecMP3Helix.h"

#define SD_CS 5

#define SpeakerPIN_WS GPIO_NUM_15
#define SpeakerPIN_SCK GPIO_NUM_14
#define SpeakerPIN_SD GPIO_NUM_22

#define MicPIN_WS GPIO_NUM_21
#define MicPIN_SCK GPIO_NUM_12
#define MicPIN_SD GPIO_NUM_32

#define BUTTON_PIN GPIO_NUM_4

#define SAMPLE_RATE 16000

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* url = "http://YOUR_IP/talk";

I2SStream speaker;                                            // final output of decoded stream
EncodedAudioStream decoder(&speaker, new MP3DecoderHelix());  // Decoding stream.

I2SStream mic;                                             // Access I2S as a stream
File audioFile;                                            //empty audio file object
EncodedAudioStream encoder(&audioFile, new WAVEncoder());  // Access audioFile as a stream
StreamCopy micCopier(encoder, mic);                        // copies sound from i2s to audio file stream

short int internetConnectRetries = 5;

/** Plays an audio file from an SD card to an I2S speaker */
void playAudio(char* filePath) {
  audioFile = SD.open(filePath, FILE_READ);

  if (!audioFile) {
    Serial.println("Could not open file");
    while(1);
  }

  decoder.setNotifyAudioChange(speaker);
  decoder.begin();

  uint8_t buffer[128];

  while (audioFile.available()) {
    size_t readSize = audioFile.read(buffer, sizeof(buffer));
    // Serial.println("Reading: " + String(readSize));
    decoder.write(buffer, readSize);  // Write decoded audio file to I2S
  }

  decoder.end();
  audioFile.close();
}

void setup() {
  Serial.begin(115200);
  AudioLogger::instance().begin(Serial, AudioLogger::Info);

  // Input button
  pinMode(GPIO_NUM_4, INPUT_PULLUP);

  // SD
  if (!SD.begin(SD_CS)) {
    Serial.println("Card Mount Failed");
    while (1)
      ;
  }

  // I2S speaker
  auto speakerConfig = speaker.defaultConfig(TX_MODE);
  speakerConfig.channels = 1;
  speakerConfig.sample_rate = SAMPLE_RATE;
  speakerConfig.pin_ws = SpeakerPIN_WS;
  speakerConfig.pin_bck = SpeakerPIN_SCK;
  speakerConfig.pin_data = SpeakerPIN_SD;
  speakerConfig.port_no = 1;
  speaker.begin(speakerConfig);

  // Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");

    internetConnectRetries -= 1;

    if (internetConnectRetries <= 0) {
      playAudio("/internet-not-connected.wav");
    }
    delay(2500);
  }
  Serial.println("Connected to WiFi");

  // I2S microphone
  auto micConfig = mic.defaultConfig(RX_MODE);
  micConfig.channels = 1;
  micConfig.sample_rate = SAMPLE_RATE;
  micConfig.pin_ws = MicPIN_WS;
  micConfig.pin_bck = MicPIN_SCK;
  micConfig.pin_data = MicPIN_SD;
  micConfig.port_no = 0;
  mic.begin(micConfig);

  // I2S to SD card WAV encoder
  auto cfg_out = encoder.defaultConfig();
  cfg_out.channels = 1;
  cfg_out.sample_rate = SAMPLE_RATE;
  encoder.begin(cfg_out);
  micCopier.setCheckAvailableForWrite(false);

  playAudio("/ready.wav");
}

bool isFetching = false;
bool isRecording = false;

void recordSound() {
  if (SD.remove("/input.wav")) {
    Serial.println("File deleted");
  }

  audioFile.close();  // Close any previous instance (if open from a previous recording)
  audioFile = SD.open("/input.wav", FILE_WRITE);

  encoder.end();  // End any previous instance (if open from a previous recording)
  auto cfg_out = encoder.defaultConfig();
  cfg_out.channels = 1;
  cfg_out.sample_rate = SAMPLE_RATE;

  encoder.begin(cfg_out);
  micCopier.begin(encoder, mic);
}

void loop() {
  int buttonPressed = digitalRead(GPIO_NUM_4) == LOW;

  if (isRecording) {
    micCopier.copy();
  }

  if (buttonPressed) {
    if (!isFetching) {
      if (!isRecording) {
        Serial.println("Start recording");
        recordSound();
        isRecording = true;
      }
    }

  } else {
    if (isRecording) {
      Serial.println("Ending recording");
      micCopier.end();
      audioFile.close();
      isRecording = false;
      isFetching = true;
    }
  }

  if (isFetching) {
    Serial.println("Beginning fetch process");
    delay(100);  // Debounce delay

    audioFile = SD.open("/input.wav", FILE_READ);
    if (!audioFile) {
      Serial.println("Failed to open file for reading");
      return;
    }

    // Send POST request
    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/octet-stream");
    int httpCode = http.sendRequest("POST", &audioFile, audioFile.size());

    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
        WiFiClient* stream = http.getStreamPtr();
        uint8_t buffer[128];
        decoder.setNotifyAudioChange(speaker);
        decoder.begin();
        while (stream->available()) {
          size_t readSize = stream->read(buffer, sizeof(buffer));
          //Serial.println("reading stream: " + String(readSize));
          decoder.write(buffer, readSize);
        }
        Serial.println("Stream end");
        decoder.end();
      } else {
        Serial.printf("Failed to send POST request, httpcode: %d\n", httpCode);
        playAudio("/did_not_understand.wav");
      }
    } else {
      Serial.printf("Failed to send POST request, error: %s\n", http.errorToString(httpCode).c_str());
      playAudio("/did_not_understand.wav");
    }
    http.end();

    Serial.println("Ending fetch process");
    isFetching = false;
  }
}