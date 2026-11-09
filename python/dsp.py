from __future__ import print_function
import numpy as np
import config
import melbank


class ExpFilter:
    """Simple exponential smoothing filter"""
    def __init__(self, val=0.0, alpha_decay=0.5, alpha_rise=0.5):
        """Small rise / decay factors = more smoothing"""
        assert 0.0 < alpha_decay < 1.0, 'Invalid decay smoothing factor'
        assert 0.0 < alpha_rise < 1.0, 'Invalid rise smoothing factor'
        self.alpha_decay = alpha_decay
        self.alpha_rise = alpha_rise
        self.value = val

    def update(self, value):
        if isinstance(self.value, (list, np.ndarray, tuple)):
            alpha = value - self.value
            alpha[alpha > 0.0] = self.alpha_rise
            alpha[alpha <= 0.0] = self.alpha_decay
        else:
            alpha = self.alpha_rise if value > self.value else self.alpha_decay
        self.value = alpha * value + (1.0 - alpha) * self.value
        return self.value


def rfft(data, window=None):
    window = 1.0 if window is None else window(len(data))
    ys = np.abs(np.fft.rfft(data * window))
    xs = np.fft.rfftfreq(len(data), 1.0 / config.MIC_RATE)
    return xs, ys


def fft(data, window=None):
    window = 1.0 if window is None else window(len(data))
    ys = np.fft.fft(data * window)
    xs = np.fft.fftfreq(len(data), 1.0 / config.MIC_RATE)
    return xs, ys


def create_mel_bank():
    global samples, mel_y, mel_x
    # Must match the zero-padded FFT in visualization.microphone_update(),
    # whose rfft output has n_fft // 2 + 1 bins spanning 0 to MIC_RATE / 2
    n_window = int(config.MIC_RATE / config.FPS) * config.N_ROLLING_HISTORY
    n_fft = 2**int(np.ceil(np.log2(n_window)))
    samples = n_fft // 2 + 1
    mel_y, (_, mel_x) = melbank.compute_melmat(num_mel_bands=config.N_FFT_BINS,
                                               freq_min=config.MIN_FREQUENCY,
                                               freq_max=config.MAX_FREQUENCY,
                                               num_fft_bands=samples,
                                               sample_rate=config.MIC_RATE)
samples = None
mel_y = None
mel_x = None
create_mel_bank()