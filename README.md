# Bus Vibration Logger
A combined vibration logger and CSV analyser which plots vibration data in the timeframe that a bus travels between two stops.

- [Installation](#Installation)
- [Usage](#Usage)
- [Wiring and practical setup](#Wiring-and-practical-setup)

# Installation
### Prerequisites:
- Arduino CLI
- Python
- pip

### Using GitHub CLI:
```
  // Installing necessary Python and Arduino libraries
  pip install matplotlib requests
  arduino-cli lib install "RTClib"
  arduino-cli lib install "SD"

  gh repo clone ebldx/Bus-Vibration-Logger
```

# Usage
### Logging
The .ino sketch must first be flashed to the Arduino UNO. This can be done using arduino-cli.
```
  // In the vibrationLogger directory
  arduino-cli compile --fqbn arduino:avr:uno .
  arduino-cli upload -p MYPORT --fqbn arduino:avr:uno
```
Replace **MYPORT** with your UNO's port, you can find it with `arduino-cli board list`

After connecting the components (See [wiring](#Wiring-and-practical-setup)), the UNO can stay plugged in for an indefinite amount of time but somewhere between 24h and 1 week is enough. Beware that if the UNO is stood too long the SD card may fill up and make the analysis slower.

### Analysing
After moving the CSV file to the installation directory, run the csvReader.py file by running `python csvReader.py`. Continue by following the instructions provided in the terminal window.


# Wiring and practical setup
### Components
- Arduino UNO R3 (or similar)
- Data logging shield with a DS1307 RTC module
- Piezoelectric vibration sensor with a VCC, GND and Signal port
- SD card with sufficient storage
- 9V power supply with barrel jack
- CR1220 battery (for RTC module)

The piezoelectric vibration sensor should be connected to 3.3V, GND and A0 on the data logging shield. The shield should in turn be seated on the UNO with a formatted SD card and a battery inserted. The power supply will be used to power the UNO, enabling for a longer period of active time than a 9V battery would allow. During operation, the Piezoelectric sensor should be in full contact with the surface it will be sensing the vibration of.
