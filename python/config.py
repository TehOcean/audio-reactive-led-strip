"""Settings for audio reactive LED strip"""
from __future__ import print_function
from __future__ import division
import os

DEVICE = 'esp8266'
#DEVICE = 'pi'
"""Device used to control LED strip. Must be 'pi',  'esp8266' or 'blinkstick'

'esp8266' means that you are using an ESP8266 module to control the LED strip
and commands will be sent to the ESP8266 over WiFi.

'pi' means that you are using a Raspberry Pi as a standalone unit to process
audio input and control the LED strip directly.

'blinkstick' means that a BlinkstickPro is connected to this PC which will be used
to control the leds connected to it.
"""

BRIGHTNESS = 1.0
"""LED brightness between 0 and 1 (applies to pi, esp8266 and blinkstick)

Can also be adjusted live with the brightness slider in the GUI.
"""

if DEVICE == 'esp8266':
    UDP_IP = '10.0.0.13'
    """IP address of the ESP8266. Must match IP in ws2812_controller.ino"""
    UDP_PORT = 7777
    """Port number used for socket communication between Python and ESP8266"""
    SOFTWARE_GAMMA_CORRECTION = True
    """Set to False because the firmware handles gamma correction + dither"""

if DEVICE == 'pi':
    LED_PIN = 18
    """GPIO pin connected to the LED strip pixels (must support PWM)"""
    LED_FREQ_HZ = 800000
    """LED signal frequency in Hz (usually 800kHz)"""
    LED_DMA = 5
    """DMA channel used for generating PWM signal (try 5)"""
    PI_BRIGHTNESS = 255
    """Hardware brightness of LED strip between 0 and 255. Use BRIGHTNESS
    above for normal brightness control; it is applied in software."""
    LED_INVERT = True
    """Set True if using an inverting logic level converter"""
    SOFTWARE_GAMMA_CORRECTION = True
    """Set to True because Raspberry Pi doesn't use hardware dithering"""

if DEVICE == 'blinkstick':
    SOFTWARE_GAMMA_CORRECTION = True
    """Set to True because blinkstick doesn't use hardware dithering"""

USE_GUI = True
"""Whether or not to display a PyQtGraph GUI plot of visualization"""

GUI_FPS = 15
"""How many times per second the GUI plots are redrawn

Drawing the plots is by far the most expensive part of each frame (about
20 ms vs about 1 ms for the audio processing), so redrawing them every frame
keeps the visualization below its target FPS and adds latency. The LEDs
still update at the full FPS; sliders and effect buttons stay responsive.
"""

DISPLAY_FPS = True
"""Whether to display the FPS when running (can reduce performance)"""

N_PIXELS = 200
"""Number of pixels in the LED strip (must match ESP8266 firmware)"""

GAMMA_TABLE_PATH = os.path.join(os.path.dirname(__file__), 'gamma_table.npy')
"""Location of the gamma correction table"""

AUDIO_SOURCE = 'loopback'
"""Audio input used for the visualization. Must be 'loopback' or 'microphone'

'loopback' captures whatever this PC is playing through its default output
device (Windows only, uses WASAPI loopback via PyAudioWPatch).

'microphone' records from the default input device.
"""

MIC_RATE = 44100
"""Sampling frequency of the microphone in Hz

When AUDIO_SOURCE is 'loopback' this is replaced with the output device's
own sample rate (usually 48000 Hz), since loopback capture can't resample.
"""

if AUDIO_SOURCE == 'loopback':
    import pyaudiowpatch as _pyaudio
    _pa = _pyaudio.PyAudio()
    try:
        LOOPBACK_DEVICE = _pa.get_default_wasapi_loopback()
        """PyAudio device info for the loopback of the default output device"""
    finally:
        _pa.terminate()
    MIC_RATE = int(LOOPBACK_DEVICE['defaultSampleRate'])

FPS = 60
"""Desired refresh rate of the visualization (frames per second)

FPS indicates the desired refresh rate, or frames-per-second, of the audio
visualization. The actual refresh rate may be lower if the computer cannot keep
up with desired FPS value.

Higher framerates improve "responsiveness" and reduce the latency of the
visualization but are more computationally expensive.

Low framerates are less computationally expensive, but the visualization may
appear "sluggish" or out of sync with the audio being played if it is too low.

The FPS should not exceed the maximum refresh rate of the LED strip, which
depends on how long the LED strip is.
"""
_max_led_FPS = int(((N_PIXELS * 30e-6) + 50e-6)**-1.0)
assert FPS <= _max_led_FPS, 'FPS must be <= {}'.format(_max_led_FPS)

MIN_FREQUENCY = 50
"""Frequencies below this value will be removed during audio processing"""

MAX_FREQUENCY = 12000
"""Frequencies above this value will be removed during audio processing"""

N_FFT_BINS = 24
"""Number of frequency bins to use when transforming audio to frequency domain

Fast Fourier transforms are used to transform time-domain audio data to the
frequency domain. The frequencies present in the audio signal are assigned
to their respective frequency bins. This value indicates the number of
frequency bins to use.

A small number of bins reduces the frequency resolution of the visualization
but improves amplitude resolution. The opposite is true when using a large
number of bins. More bins is not always better!

There is no point using more bins than there are pixels on the LED strip.
"""

N_ROLLING_HISTORY = 2
"""Number of past audio frames to include in the rolling window"""

MIN_VOLUME_THRESHOLD = 1e-7
"""No music visualization displayed if recorded audio volume below threshold"""
