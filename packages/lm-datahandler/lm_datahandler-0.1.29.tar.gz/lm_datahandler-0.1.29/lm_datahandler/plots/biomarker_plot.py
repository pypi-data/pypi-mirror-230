import logging

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def sw_plot_with_eeg(eeg, marker):
    if eeg.size > 10000:
        logging.error("The data is out limit, please make sure the count of sample point is smaller than 10000!")
    sf = 200.
    times = np.arange(eeg.size) / sf

    # Plot the signal
    fig, ax = plt.subplots(1, 1, figsize=(14, 4))
    plt.plot(times, eeg, lw=1.5, color='k')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude (uV)')
    plt.xlim([times.min(), times.max()])
    plt.title('N2 sleep EEG data (2 spindles)')
    sns.despine()