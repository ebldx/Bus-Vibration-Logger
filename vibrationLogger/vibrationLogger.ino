#include "RTClib.h"
#include <SD.h>

RTC_DS1307 rtc;
const int SAVE_INTERVAL = 1000; // In milliseconds
const int LOOP_INTERVAL = 100; // In milliseconds
const int VIBRATION_THRESHOLD = 0; // Minimum vibration for storage
const char LOG_FILENAME[] = "VIBRATION_LOG.csv";



struct Log_Entry {
  uint16_t year;
  uint8_t month;
  uint8_t day;
  uint8_t hour;
  uint8_t minute;
  uint8_t second;
  int vibration;
};

Log_Entry tempData[SAVE_INTERVAL/LOOP_INTERVAL];
int dataIndex = 0;
int vibration;

File logFile;

void setup() {
  Serial.begin(9600);
  Serial.println();
  Serial.println("Starting!");
  pinMode(10, OUTPUT);
  if (!rtc.begin()) {
    Serial.println("RTC failed!");
    while (1);
  };

  if (!SD.begin(10)) {
    Serial.println("SD failed!");
    while (1);
  };

  logFile = SD.open(LOG_FILENAME, FILE_WRITE);
  if (!logFile) {
    Serial.println("Couldn't create logfile");
    while (1);
  };
  logFile.println("year,month,day,hour,minute,second,vibration");
  Serial.println("year,month,day,hour,minute,second,vibration");
};

void loop() {
  DateTime now = rtc.now();
  vibration = analogRead(A0);
  if (vibration >= VIBRATION_THRESHOLD) {
    if (dataIndex >= SAVE_INTERVAL/LOOP_INTERVAL) {
      Serial.println("Saving data to SD card...");
      for (int i = 0; i < dataIndex; i++) {
        logFile.print(tempData[i].year, DEC);
        logFile.print(",");
        logFile.print(tempData[i].month, DEC);
        logFile.print(",");
        logFile.print(tempData[i].day, DEC);
        logFile.print(",");
        logFile.print(tempData[i].hour, DEC);
        logFile.print(",");
        logFile.print(tempData[i].minute, DEC);
        logFile.print(",");
        logFile.print(tempData[i].second, DEC);
        logFile.print(",");
        logFile.print(tempData[i].vibration);
        logFile.println();
      };
      logFile.flush();
      dataIndex = 0;
    };
    if (dataIndex < SAVE_INTERVAL/LOOP_INTERVAL) {
      tempData[dataIndex].year = now.year();
      tempData[dataIndex].month = now.month();
      tempData[dataIndex].day = now.day();
      tempData[dataIndex].hour = now.hour();
      tempData[dataIndex].minute = now.minute();
      tempData[dataIndex].second = now.second();
      tempData[dataIndex].vibration = vibration;
      Serial.print(now.year(), DEC);
      Serial.print(",");
      Serial.print(now.month(), DEC);
      Serial.print(",");
      Serial.print(now.day(), DEC);
      Serial.print(",");
      Serial.print(now.hour(), DEC);
      Serial.print(",");
      Serial.print(now.minute(), DEC);
      Serial.print(",");
      Serial.print(now.second(), DEC);
      Serial.print(",");
      Serial.print(vibration);
      Serial.println();
      dataIndex++;
    };
  };
  delay(LOOP_INTERVAL);
};

