import time
import numpy as np
import config

try:
    # PyAudioWPatch is a PyAudio fork that adds WASAPI loopback on Windows
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio


CAPTURE_CHUNKS_PER_FRAME = 4
"""How many pieces each visualization frame of audio is captured in

The driver is asked for buffers of a quarter frame (200 frames at 48 kHz /
60 FPS) so audio reaches us in small pieces: on WASAPI loopback, one
800-frame buffer gives about 33 ms of capture latency, 400 or fewer about
22 ms. The size must divide the frame evenly; otherwise a full frame only
becomes available in uneven steps (256-frame chunks, for example, cap the
visualization at about 47 FPS).
"""


def start_stream(callback):
    p = pyaudio.PyAudio()
    frames_per_buffer = int(config.MIC_RATE / config.FPS)
    loopback = config.AUDIO_SOURCE == 'loopback'
    if loopback:
        device = config.LOOPBACK_DEVICE
        channels = device['maxInputChannels']
        print('Capturing audio output from: {}'.format(device['name']))
        stream = p.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=config.MIC_RATE,
                        input=True,
                        input_device_index=device['index'],
                        frames_per_buffer=frames_per_buffer // CAPTURE_CHUNKS_PER_FRAME)
    else:
        channels = 1
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=config.MIC_RATE,
                        input=True,
                        frames_per_buffer=frames_per_buffer // CAPTURE_CHUNKS_PER_FRAME)
    overflows = 0
    prev_ovf_time = time.time()
    frame_period = 1.0 / config.FPS
    last_frame_time = time.time()
    # Mono samples captured but not yet handed to the visualization
    pending = np.zeros(0, dtype=np.float32)
    while True:
        try:
            available = stream.get_read_available()
            if available > 0:
                data = stream.read(available, exception_on_overflow=False)
                y = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                if channels > 1:
                    # Mix interleaved stereo (or more) down to mono
                    y = y.reshape(-1, channels).mean(axis=1)
                pending = np.concatenate((pending, y))
            if len(pending) >= frames_per_buffer:
                # Audio arrives in bursts (10 ms on WASAPI), not in whole
                # frames, so leftover samples are kept for the next frame;
                # discarding them would make each frame wait for an extra
                # burst. If processing fell behind by a whole frame or more,
                # skip the stale frames so the LEDs show the newest audio.
                stale = len(pending) // frames_per_buffer - 1
                pending = pending[stale * frames_per_buffer:]
                frame, pending = pending[:frames_per_buffer], pending[frames_per_buffer:]
                last_frame_time = time.time()
                callback(frame)
            elif loopback and time.time() - last_frame_time >= 2 * frame_period:
                # WASAPI loopback delivers no data while nothing is playing,
                # so waiting for audio would freeze the LEDs on the last
                # frame. Feed silence so they decay to dark.
                last_frame_time = time.time()
                callback(np.zeros(frames_per_buffer, dtype=np.float32))
            else:
                time.sleep(0.001)
        except IOError:
            overflows += 1
            if time.time() > prev_ovf_time + 1:
                prev_ovf_time = time.time()
                print('Audio buffer has overflowed {} times'.format(overflows))
    stream.stop_stream()
    stream.close()
    p.terminate()
