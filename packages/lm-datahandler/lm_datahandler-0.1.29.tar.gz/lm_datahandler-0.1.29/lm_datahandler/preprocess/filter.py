import scipy.signal as signal


def eeg_filter(eeg, sf_eeg, highpass, highpass_order, lowpass, lowpass_order, bandstop, bandstop_order):
    if bandstop is not None:
        bandstop_count = len(bandstop)
        for i in range(bandstop_count):
            w0 = bandstop[i][0] / (sf_eeg / 2)
            w1 = bandstop[i][1] / (sf_eeg / 2)
            b, a = signal.butter(bandstop_order, [w0, w1], btype='bandstop', analog=False)
            eeg = signal.lfilter(b, a, eeg)
    if highpass is not None:
        wn = 2 * highpass / sf_eeg
        b, a = signal.butter(highpass_order, wn, 'highpass', analog=False)
        eeg = signal.lfilter(b, a, eeg)
    if lowpass is not None:
        wn = 2 * lowpass / sf_eeg
        b, a = signal.butter(lowpass_order, wn, 'lowpass', analog=False)
        eeg = signal.lfilter(b, a, eeg)

    return eeg
