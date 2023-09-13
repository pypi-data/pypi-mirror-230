import numpy as np
from lm_datahandler.preprocess.filter import eeg_filter
import matplotlib.pyplot as plt



def plot_stim_sham_sw(eeg, indexs, sf_eeg, savefig):
    indexs = np.asarray(indexs)
    assert indexs.shape[0] >= 10, "The count of stim/sham points is less than expected, at least 10 points are needed."

    if indexs.shape[0] % 2 == 1:
        indexs = indexs[:-1]
    stim_idx_T = indexs.reshape([-1, 2])
    stim_idx = np.squeeze(stim_idx_T[:, 0])
    sham_idx = np.squeeze(stim_idx_T[:, 1])

    stim_idx_total = []
    sham_idx_total = []

    stim_idx_total = np.concatenate((stim_idx_total, stim_idx))
    sham_idx_total = np.concatenate((sham_idx_total, sham_idx))
    # StimIdx = stim_idx_total
    stim_indicator = np.asarray(stim_idx_total * 50).astype(np.int64)
    sham_indicator = np.asarray(sham_idx_total * 50).astype(np.int64)

    # stim_indicator = np.asarray(stim_idx_total).astype(np.int64)
    # sham_indicator = np.asarray(sham_idx_total).astype(np.int64)
    # stim_indicator = stim_idx_total
    # sham_indicator = sham_idx_total

    # data preprocess
    eeg = (eeg - 32767) / 65536 * 2.5 * 1000 * 1000 / 100

    eeg_filtered = eeg_filter(eeg, sf_eeg, 0.5, 3, 4, 3, [[49, 51]], 3)
    # eeg_filtered = eeg_filter_matlab(eeg)
    # eeg_filtered[abs(eeg_filtered) > 200] = 0
    # eeg_filtered = (eeg - 32767) / 65536 * 2.5 * 1000 * 1000 / 100


    figuresize = (16, 9)

    # plot EEG signal and stimulus timing


    # plot ERP of slow wave
    seg_downlim = 1  # ERP downlimitation
    seg_uplim = 4  # ERP uplimitation
    # EEG_phase = {'stim': np.zeros((1, int((seg_downlim + seg_uplim) * 500))),
    #              'sham': np.zeros((1, int((seg_downlim + seg_uplim) * 500)))}

    EEGT = {'stim': [], 'sham': []}
    EEGT['stim'] = np.array(
        [eeg_filtered[i - int(sf_eeg * seg_downlim):i + int(sf_eeg * seg_uplim)] for i in
         stim_indicator])
    EEGT['sham'] = np.array(
        [eeg_filtered[i - int(sf_eeg * seg_downlim):i + int(sf_eeg * seg_uplim)] for i in
         sham_indicator])



    stim_sem = np.std(EEGT['stim'], axis=0) / np.sqrt(len(EEGT['stim']) / 2)
    sham_sem = np.std(EEGT['sham'], axis=0) / np.sqrt(len(EEGT['sham']) / 2)

    t = np.arange(-500, 2000) / sf_eeg
    eeg_stim_mean = np.mean(EEGT['stim'], axis=0)
    eeg_sham_mean = np.mean(EEGT['sham'], axis=0)

    fig2, ax2 = plt.subplots(1, 1, figsize=figuresize)
    # ax2.errorbar(t, eeg_stim_mean, yerr=stim_sem, label='STIM', alpha=0.1, color=ax1[0].lines[2].get_color())
    ax2.errorbar(t, eeg_stim_mean, yerr=stim_sem, label='STIM', alpha=0.1, color='r')
    # ax2.errorbar(t, eeg_sham_mean, yerr=sham_sem, label='SHAM', alpha=0.1, color=ax1[0].lines[3].get_color())
    ax2.errorbar(t, eeg_sham_mean, yerr=sham_sem, label='SHAM', alpha=0.1, color='k')

    onset_idx = 500
    offset_idx = int(onset_idx + 1.075 * sf_eeg)
    ax2.scatter(t[[onset_idx, offset_idx]], eeg_stim_mean[[onset_idx, offset_idx]], c='r',
                label='STIM Timings')
    ax2.scatter(t[[onset_idx, offset_idx]], eeg_sham_mean[[onset_idx, offset_idx]], c='g',
                label='SHAM Timings')

    ax2.set_xlim([min(t), max(t)])
    ax2.set_title('STIM & SHAM', fontdict={'fontsize': 25})
    ax2.set_xlabel('Time (s)', fontsize=25)
    ax2.set_ylabel('Voltage (uV)', fontsize=25)
    ax2.tick_params(labelsize=25)
    ax2.legend(fontsize=20, loc='upper right')
    if savefig is not None:
        plt.savefig(savefig, dpi=300)


