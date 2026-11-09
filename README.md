# Audio Reactive LED Strip
Real-time LED strip music visualization using Python and the ESP8266 or Raspberry Pi.

![block diagram](images/block-diagram.png)

![overview](images/description-cropped.gif)

# Demo (click gif for video)

[![visualizer demo](images/scroll-effect-demo.gif)](https://www.youtube.com/watch?v=HNtM7jH5GXgD)

# Overview
The repository includes everything needed to build an LED strip music visualizer (excluding hardware):

- Python visualization code, which includes code for:
  - Recording audio from a microphone, or on Windows from whatever the computer is playing ([microphone.py](python/microphone.py))
  - Digital signal processing ([dsp.py](python/dsp.py))
  - Constructing 1D visualizations ([visualization.py](python/visualization.py))
  - Sending pixel information to the ESP8266 over WiFi, or driving the LED strip directly from a Raspberry Pi ([led.py](python/led.py))
  - Configuration and settings ([config.py](python/config.py))
- Arduino firmware for the ESP8266 ([ws2812_controller.ino](arduino/ws2812_controller/ws2812_controller.ino))

# What do I need to make one?
## Computer + ESP8266
To build a visualizer using a computer and ESP8266, you will need:
- Computer with Python 3.10 or newer (installed automatically by [uv](https://docs.astral.sh/uv/))
- ESP8266 module with RX1 pin exposed. These modules can be purchased for as little as $5 USD. These modules are known to be compatible, but many others will work too:
  - NodeMCU v3
  - Adafruit HUZZAH
  - Adafruit Feather HUZZAH
- WS2812B LED strip (such as Adafruit Neopixels). These can be purchased for as little as $5-15 USD per meter.
- 5V power supply
- 3.3V-5V level shifter (optional, must be non-inverting)

Limitations when using a computer + ESP8266:
- The communication protocol between the computer and ESP8266 currently supports a maximum of 256 LEDs.

## Standalone Raspberry Pi
You can also build a standalone visualizer using a Raspberry Pi. For this you will need: 
- Raspberry Pi 3, 4 or Zero 2 W running 64-bit Raspberry Pi OS (Lite is fine). The Raspberry Pi 5 is not yet supported by the [rpi_ws281x](https://github.com/jgarff/rpi_ws281x) LED library, and older models (Pi 1, 2 and the original Zero) can't run the 64-bit OS that the Python dependencies need.
- USB audio input device. This could be a USB microphone or a sound card. You just need to find some way of giving the Raspberry Pi audio input.
- WS2812B LED strip (such as Adafruit Neopixels)
- 5V power supply
- 3.3V-5V level shifter (optional)

Limitations when using the Raspberry Pi:
- The visualization runs headless on the Raspberry Pi: the GUI window is not installed there.
- The ESP8266 uses a technique called temporal dithering to improve the color depth of the LED strip. Unfortunately the Raspberry Pi lacks this capability.

# Installation for Computer + ESP8266
## Python Dependencies
Python dependencies are managed with [uv](https://docs.astral.sh/uv/) and declared in [python/pyproject.toml](python/pyproject.toml):
- Numpy
- Scipy (for digital signal processing)
- PyQtGraph + PyQt6 (for GUI visualization)
- PyAudio (for recording audio; on Windows, the [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch) fork, which can also capture what the computer is playing)

[Install uv](https://docs.astral.sh/uv/getting-started/installation/), then from the root of this repository run:
```
cd python
uv sync
```
This downloads a compatible Python (see [python/.python-version](python/.python-version)) if needed, creates a `python/.venv` virtual environment, and installs the locked dependencies from `python/uv.lock`.

### Installing macOS dependencies
On macOS, `portaudio` must be installed before PyAudio can be built.
If you don't have brew installed you can get it here: https://brew.sh

```
brew install portaudio
cd python
uv sync
```

### Installing Linux dependencies
On Linux, PyAudio is also built during installation and needs a compiler and the PortAudio headers. On Debian or Ubuntu:
```
sudo apt install build-essential portaudio19-dev
cd python
uv sync
```

## Running the visualization
Run the visualization from the `python` directory using `uv run`, which uses the project's virtual environment automatically:
```
cd python
uv run python visualization.py
```

## Arduino dependencies
ESP8266 firmware is uploaded using the Arduino IDE. See [this tutorial](https://learn.sparkfun.com/tutorials/esp8266-thing-hookup-guide/installing-the-esp8266-arduino-addon) to setup the Arduino IDE for ESP8266.

### Install NeoPixelBus library
[Download Here](https://github.com/Makuna/NeoPixelBus) or using library manager, search for "NeoPixelBus".

## Hardware Connections
### ESP8266
The ESP8266 has hardware support for [I²S](https://en.wikipedia.org/wiki/I%C2%B2S) and this peripheral is used <!-- by the [ws2812b i2s library](https://github.com/JoDaNl/esp8266_ws2812_i2s)  -->to control the ws2812b LED strip. This significantly improves performance compared to bit-banging the IO pin. Unfortunately, this means that the LED strip **must** be connected to the RX1 pin, which is not accessible in some ESP8266 modules (such as the ESP-01).

The RX1 pin on the ESP8266 module should be connected to the data input pin of the ws2812b LED strip (often labelled DIN or D0).

For the NodeMCU v3 and Adafruit Feather HUZZAH, the location of the RX1 pin is shown in the images below. Many other modules also expose the RX1 pin.

![nodemcu-pinout](images/NodeMCUv3-small.png)
![feather-huzzah-pinout](images/FeatherHuzzah-small.png)

### Raspberry Pi
Since the Raspberry Pi is a 3.3V device, the best practice is to use a logic level converter to shift the 3.3V logic to 5V logic (WS2812 LEDs use 5V logic). There is a good overview on the [best practices here](https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices).

Although a logic level converter is the best practice, sometimes it will still work if you simply connect the LED strip directly to the Raspberry Pi.

You cannot power the LED strip using the Raspberry Pi GPIO pins, you need to have an external 5V power supply.

The connections are:

* Connect GND on the power supply to GND on the LED strip and GND on the Raspberry Pi (they MUST share a common GND connection)
* Connect +5V on the power supply to +5V on the LED strip
* Connect a PWM GPIO pin on the Raspberry Pi to the data pin on the LED strip. The default in [config.py](python/config.py) is GPIO 18, which is physical pin 12 on the header.

# Setup and Configuration
1. Install Python and Python dependencies
2. [Install Arduino IDE and ESP8266 addon](https://learn.sparkfun.com/tutorials/esp8266-thing-hookup-guide/installing-the-esp8266-arduino-addon)
3. Download and extract all of the files in this repository onto your computer
4. Connect the RX1 pin of your ESP8266 module to the data input pin of the ws2812b LED strip. Ensure that your LED strip is properly connected to a 5V power supply and that the ESP8266 and LED strip share a common electrical ground connection.
5. In [ws2812_controller.ino](arduino/ws2812_controller/ws2812_controller.ino):
  - Set `const char* ssid` to your router's SSID
  - Set `const char* password` to your router's password
  - Set `IPAddress gateway` to match your router's gateway
  - Set `IPAddress ip` to the IP address that you would like your ESP8266 to use (your choice)
  - Set `#define NUM_LEDS` to the number of LEDs in your LED strip
6. Upload the [ws2812_controller.ino](arduino/ws2812_controller/ws2812_controller.ino) firmware to the ESP8266. Ensure that you have selected the correct ESP8266 board from the boards menu. In the dropdown menu, set `CPU Frequency` to 160 MHz for optimal performance.
7. In [config.py](python/config.py):
  - Set `N_PIXELS` to the number of LEDs in your LED strip (must match `NUM_LEDS` in [ws2812_controller.ino](arduino/ws2812_controller/ws2812_controller.ino))
  - Set `UDP_IP` to the IP address of your ESP8266 (must match `ip` in [ws2812_controller.ino](arduino/ws2812_controller/ws2812_controller.ino))
  - Set `AUDIO_SOURCE` to `'loopback'` (Windows only) to visualize whatever the computer is playing, or to `'microphone'` to use the default recording device. See [Audio Input](#audio-input).
  - If needed, set `MIC_RATE` to your microphone sampling rate in Hz. Most of the time you will not need to change this, and it is ignored for `'loopback'`.

# Installation for Raspberry Pi
If you encounter any problems running the visualization on a Raspberry Pi, please [open a new issue](https://github.com/scottlawsonbc/audio-reactive-led-strip/issues). Also, please consider opening an issue if you have any questions or suggestions for improving the installation process.

These steps assume a fresh install of 64-bit Raspberry Pi OS.

## Installing the Python dependencies
PyAudio and the rpi_ws281x LED library are compiled during installation, so install a compiler and the PortAudio headers first:
```
sudo apt update
sudo apt install git build-essential portaudio19-dev
```

Then [install uv](https://docs.astral.sh/uv/getting-started/installation/):
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Log out and back in (or run `source $HOME/.local/bin/env`) so `uv` is on your `PATH`, then download the code and install the dependencies:
```
git clone https://github.com/scottlawsonbc/audio-reactive-led-strip.git
cd audio-reactive-led-strip/python
uv sync --no-group gui --extra pi
```
`--extra pi` adds the rpi_ws281x LED library. `--no-group gui` skips the GUI packages (PyQtGraph and PyQt6), which aren't needed on the Pi and don't install on Raspberry Pi OS Bookworm. As on a computer, uv downloads a compatible Python and creates a virtual environment in `python/.venv`.

## Disable the onboard audio
The LED strip is driven by the Pi's PWM hardware, which the onboard (headphone jack) audio also uses, so the two can't run at the same time. Disable the onboard audio:
```
echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/snd-blacklist.conf
sudo reboot
```

## Audio device configuration
The USB audio device needs to be the default audio input. With the USB device plugged in, find its card number:
```
arecord -l
```
Then create `/etc/asound.conf`:
```
sudo nano /etc/asound.conf
```
with the following text, replacing `1` with the card number of your USB device:
```
pcm.!default {
    type hw
    card 1
}
ctl.!default {
    type hw
    card 1
}
```

## Test the LED strip
Before running the visualization, check the wiring with the rpi_ws281x example program:
```
cd audio-reactive-led-strip/python
curl -O https://raw.githubusercontent.com/rpi-ws281x/rpi-ws281x-python/master/examples/strandtest.py
nano strandtest.py
```
Set `LED_COUNT` and `LED_PIN` at the top of the file to match your strip, and set `LED_INVERT = True` if you are using an inverting logic level converter. You will likely need a level converter to convert the Raspberry Pi's 3.3V logic to the 5V logic used by the WS2812B LED strip. Then run it (controlling the LEDs requires root):
```
sudo .venv/bin/python strandtest.py -c
```
You should see a series of color wipes and rainbow animations. Press Ctrl+C to stop; `-c` turns the LEDs off on exit.

## Configure the visualization code
In [config.py](python/config.py):
- Set `DEVICE = 'pi'` and configure the GPIO, LED and other hardware settings.
- Set `LED_INVERT = True` if you are using an inverting logic level converter, or `LED_INVERT = False` if you are not (i.e. connecting the LED strip directly to the GPIO pin).
- Set `USE_GUI = False`.
- Set `AUDIO_SOURCE = 'microphone'` (loopback capture is only available on Windows).
- Set `N_PIXELS` to the number of LEDs in your strip.
- If the audio stream fails to open, set `MIC_RATE` to a sample rate your USB device supports (many only support `48000`).

## Running the visualization
Controlling the LEDs requires root, so run the virtual environment's Python with `sudo`:
```
cd audio-reactive-led-strip/python
sudo .venv/bin/python visualization.py
```

# Audio Input
The audio source is chosen with `AUDIO_SOURCE` in [config.py](python/config.py):
* `'loopback'` (Windows only, the default): captures whatever the computer is playing through its default output device, so music from any app drives the visualization with no extra setup.
* `'microphone'`: records from the default audio input device, set by the operating system. Use this on macOS, Linux and the Raspberry Pi.

Examples of typical microphone sources:
* Audio cable connected to the audio input jack (requires USB sound card on Raspberry Pi)
* Webcam microphone, headset, studio recording microphone, etc

## Virtual Audio Source
On macOS and Linux you can use a "virtual audio device" to route playback from one application into the visualization program, so you can play music on your computer and visualize it directly.

![audio-input-sources](images/audio-source.png)

### Linux
On desktops using PipeWire or PulseAudio, every output device has a "Monitor of ..." input that carries what it is playing. Set it as the default input device (for example with `pavucontrol`, under Input Devices, showing "All Input Devices"), and use `AUDIO_SOURCE = 'microphone'`.

### macOS
On macOS, a virtual audio device such as [BlackHole](https://github.com/ExistentialAudio/BlackHole) (free) or [Loopback](https://rogueamoeba.com/loopback/) can route playback into an input device.

# Running the Visualization
Once everything has been configured, run [visualization.py](python/visualization.py) to start the visualization (see [Running the visualization](#running-the-visualization) above).

A PyQtGraph GUI will open to display the output of the visualization on the computer, with sliders for the frequency range and LED brightness and buttons to switch between the energy, scroll and spectrum effects. There is a setting to enable/disable the GUI display in [config.py](python/config.py).

![visualization-gui](images/visualization-gui.png)

If you encounter any issues or have questions about this project, feel free to [open a new issue](https://github.com/scottlawsonbc/audio-reactive-led-strip/issues).

# Limitations
* ESP8266 supports a maximum of 256 LEDs. This limitation will be removed in a future update. The Raspberry Pi can use more than 256 LEDs.
* Even numbers of pixels must be used. For example, if you have 71 pixels then use the next lowest even number, 70. Odd pixel quantities will be supported in a future update.

# License
This project was developed by Scott Lawson and is released under the MIT License.
