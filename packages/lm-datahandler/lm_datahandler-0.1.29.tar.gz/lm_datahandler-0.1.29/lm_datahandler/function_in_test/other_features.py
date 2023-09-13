import numpy as np
import scipy.signal as sp_sig
from scipy.integrate import simps


def generate_cluster_feature3(data_handler):
    epochs = data_handler.eeg.shape[0] // (data_handler.sf_eeg * data_handler.epoch_len)
    input_eeg = data_handler.eeg[0:epochs * data_handler.sf_eeg * data_handler.epoch_len].reshape(-1,
                                                                                                  data_handler.sf_eeg * data_handler.epoch_len)
    hypno = data_handler.sleep_staging_result
    n3_index = np.where(hypno == 0)
    n12_index = np.where(hypno == 1)
    rem_index = np.where(hypno == 2)

    bands = [
        (0.5, 4, "delta"),
        (4, 8, "theta"),
        (8, 11, "alpha"),
        (11, 16, "spindle"),
        (16, 24, "beta1"),
        (24, 32, "beta2"),
        (20, 30, "beta3"),
        (32, 48, "gamma"),
    ]

    win = int(5 * 500)
    kwargs_welch = dict(window="hamming", nperseg=win, average="median")
    freqs, psd = sp_sig.welch(input_eeg, 500, **kwargs_welch)

    n3_psd = psd[n3_index]
    n12_psd = psd[n12_index]
    rem_psd = psd[rem_index]

    n3_beta_abnormal_percentage = None
    n12_beta_abnormal_percentage = None
    rem_beta_abnormal_percentage = None

    if len(n3_psd) != 0:
        n3_percentile_10 = np.percentile(n3_psd, 10, axis=0)
        n3_percentile_90 = np.percentile(n3_psd, 90, axis=0)
        n3_psd_new = []
        for i in range(n3_psd.shape[0]):
            temp = n3_psd[i, :]
            temp[temp < n3_percentile_10] = n3_percentile_10[temp < n3_percentile_10]
            temp[temp > n3_percentile_90] = n3_percentile_90[temp > n3_percentile_90]
            n3_psd_new.append(temp)
        n3_psd = np.asarray(n3_psd_new)
        n3_bp = bandpower_from_psd_ndarray(bands, n3_psd, freqs, relative=False)
        n3_bp_avg = np.average(n3_bp, axis=1)
        n3_thresh = n3_bp_avg[0] / 3.5 / 75
        n3_beta_bp = n3_bp[5, :] / 10
        n3_beta_abnormal_percentage = len(np.where(n3_beta_bp > n3_thresh)[0]) / len(n3_index[0]) * 100

    if len(n12_psd) != 0:
        n12_percentile_10 = np.percentile(n12_psd, 10, axis=0)
        n12_percentile_90 = np.percentile(n12_psd, 90, axis=0)
        n12_psd_new = []
        for i in range(n12_psd.shape[0]):
            temp = n12_psd[i, :]
            temp[temp < n12_percentile_10] = n12_percentile_10[temp < n12_percentile_10]
            temp[temp > n12_percentile_90] = n12_percentile_90[temp > n12_percentile_90]
            n12_psd_new.append(temp)
        n12_psd = np.asarray(n12_psd_new)
        n12_bp = bandpower_from_psd_ndarray(bands, n12_psd, freqs, relative=False)
        n12_bp_avg = np.average(n12_bp, axis=1)
        n12_thresh = n12_bp_avg[0] / 3.5 / 75
        n12_beta_bp = n12_bp[5, :] / 10
        n12_beta_abnormal_percentage = len(np.where(n12_beta_bp > n12_thresh)[0]) / len(n12_index[0]) * 100

    if len(rem_psd) != 0:
        rem_percentile_10 = np.percentile(rem_psd, 10, axis=0)
        rem_percentile_90 = np.percentile(rem_psd, 90, axis=0)
        rem_psd_new = []
        for i in range(rem_psd.shape[0]):
            temp = rem_psd[i, :]
            temp[temp < rem_percentile_10] = rem_percentile_10[temp < rem_percentile_10]
            temp[temp > rem_percentile_90] = rem_percentile_90[temp > rem_percentile_90]
            rem_psd_new.append(temp)
        rem_psd = np.asarray(rem_psd_new)
        rem_bp = bandpower_from_psd_ndarray(bands, rem_psd, freqs, relative=False)
        rem_bp_avg = np.average(rem_bp, axis=1)
        rem_thresh = rem_bp_avg[0] / 3.5 / 20
        rem_beta_bp = rem_bp[5, :] / 10
        rem_beta_abnormal_percentage = len(np.where(rem_beta_bp > rem_thresh)[0]) / len(rem_index[0]) * 100

    return {
        "n3_beta_abnormal_percentage": [n3_beta_abnormal_percentage] if n3_beta_abnormal_percentage is not None else [""],
        "n12_beta_abnormal_percentage": [n12_beta_abnormal_percentage] if n12_beta_abnormal_percentage is not None else [""],
        "rem_beta_abnormal_percentage": [rem_beta_abnormal_percentage] if rem_beta_abnormal_percentage is not None else [""]
    }


def generate_cluster_feature2(data_handler):
    epochs = data_handler.eeg.shape[0] // (data_handler.sf_eeg * data_handler.epoch_len)
    input_eeg = data_handler.eeg[0:epochs * data_handler.sf_eeg * data_handler.epoch_len].reshape(-1,
                                                                                                  data_handler.sf_eeg * data_handler.epoch_len)

    hypno = data_handler.sleep_staging_result
    n3_index = np.where(hypno == 0)
    n12_index = np.where(hypno == 1)
    rem_index = np.where(hypno == 2)

    bands = [
        (0.5, 4, "delta"),
        (4, 8, "theta"),
        (8, 11, "alpha"),
        (11, 16, "spindle"),
        (16, 24, "beta1"),
        (24, 32, "beta2"),
        (32, 48, "gamma"),
    ]

    win = int(5 * 500)
    kwargs_welch = dict(window="hamming", nperseg=win, average="median")
    freqs, psd = sp_sig.welch(input_eeg, 500, **kwargs_welch)

    n3_psd = psd[n3_index]
    n12_psd = psd[n12_index]
    rem_psd = psd[rem_index]

    n3_bp = None
    n12_bp = None
    rem_bp = None

    if len(n3_psd) != 0:
        n3_percentile_10 = np.percentile(n3_psd, 10, axis=0)
        n3_percentile_90 = np.percentile(n3_psd, 90, axis=0)
        n3_psd_new = []
        for i in range(n3_psd.shape[0]):
            temp = n3_psd[i, :]
            temp[temp < n3_percentile_10] = n3_percentile_10[temp < n3_percentile_10]
            temp[temp > n3_percentile_90] = n3_percentile_90[temp > n3_percentile_90]
            n3_psd_new.append(temp)
        n3_psd = np.asarray(n3_psd_new)
        n3_bp = bandpower_from_psd_ndarray(bands, n3_psd, freqs)
        n3_bp = np.average(n3_bp, axis=1) * 100


    if len(n12_psd) != 0:
        n12_percentile_10 = np.percentile(n12_psd, 10, axis=0)
        n12_percentile_90 = np.percentile(n12_psd, 90, axis=0)
        n12_psd_new = []
        for i in range(n12_psd.shape[0]):
            temp = n12_psd[i, :]
            temp[temp < n12_percentile_10] = n12_percentile_10[temp < n12_percentile_10]
            temp[temp > n12_percentile_90] = n12_percentile_90[temp > n12_percentile_90]
            n12_psd_new.append(temp)
        n12_psd = np.asarray(n12_psd_new)
        n12_bp = bandpower_from_psd_ndarray(bands, n12_psd, freqs)
        n12_bp = np.average(n12_bp, axis=1) * 100


    if len(rem_psd) != 0:
        rem_percentile_10 = np.percentile(rem_psd, 10, axis=0)
        rem_percentile_90 = np.percentile(rem_psd, 90, axis=0)
        rem_psd_new = []
        for i in range(rem_psd.shape[0]):
            temp = rem_psd[i, :]
            temp[temp < rem_percentile_10] = rem_percentile_10[temp < rem_percentile_10]
            temp[temp > rem_percentile_90] = rem_percentile_90[temp > rem_percentile_90]
            rem_psd_new.append(temp)
        rem_psd = np.asarray(rem_psd_new)
        rem_bp = bandpower_from_psd_ndarray(bands, rem_psd, freqs)
        rem_bp = np.average(rem_bp, axis=1) * 100

    # n3_psd_avg = np.average(n3_psd, axis=0)
    # n12_psd_avg = np.average(n12_psd, axis=0)

    return {
        "n3_delta_rp": [n3_bp[0]] if n3_bp is not None else [""],
        "n3_theta_rp": [n3_bp[1]] if n3_bp is not None else [""],
        "n3_alpha_rp": [n3_bp[2]] if n3_bp is not None else [""],
        "n3_spindle_rp": [n3_bp[3]] if n3_bp is not None else [""],
        "n3_beta1_rp": [n3_bp[4]] if n3_bp is not None else [""],
        "n3_beta2_rp": [n3_bp[5]] if n3_bp is not None else [""],
        "n3_gamma_rp": [n3_bp[6]] if n3_bp is not None else [""],

        "n12_delta_rp": [n12_bp[0]] if n12_bp is not None else [""],
        "n12_theta_rp": [n12_bp[1]] if n12_bp is not None else [""],
        "n12_alpha_rp": [n12_bp[2]] if n12_bp is not None else [""],
        "n12_spindle_rp": [n12_bp[3]] if n12_bp is not None else [""],
        "n12_beta1_rp": [n12_bp[4]] if n12_bp is not None else [""],
        "n12_beta2_rp": [n12_bp[5]] if n12_bp is not None else [""],
        "n12_gamma_rp": [n12_bp[6]] if n12_bp is not None else [""],

        "rem_delta_rp": [rem_bp[0]] if rem_bp is not None else [""],
        "rem_theta_rp": [rem_bp[1]] if rem_bp is not None else [""],
        "rem_alpha_rp": [rem_bp[2]] if rem_bp is not None else [""],
        "rem_spindle_rp": [rem_bp[3]] if rem_bp is not None else [""],
        "rem_beta1_rp": [rem_bp[4]] if rem_bp is not None else [""],
        "rem_beta2_rp": [rem_bp[5]] if rem_bp is not None else [""],
        "rem_gamma_rp": [rem_bp[6]] if rem_bp is not None else [""],
    }


def generate_cluster_feature1(data_handler):
    epochs = data_handler.eeg.shape[0] // (data_handler.sf_eeg * data_handler.epoch_len)
    input_eeg = data_handler.eeg[0:epochs * data_handler.sf_eeg * data_handler.epoch_len].reshape(-1,
                                                                                                  data_handler.sf_eeg * data_handler.epoch_len)

    hypno = data_handler.sleep_staging_result
    n3_index = np.where(hypno == 0)
    n12_index = np.where(hypno == 1)

    bands = [
        (1, 4, "delta"),
        (4, 8, "theta"),
        (8, 12, "alpha"),
        (11, 16, "spindle"),
        (20, 30, "beta"),
        (30, 40, "gamma"),
    ]

    win = int(5 * 500)
    kwargs_welch = dict(window="hamming", nperseg=win, average="median")
    freqs, psd = sp_sig.welch(input_eeg, 500, **kwargs_welch)

    n3_psd = psd[n3_index]
    n12_psd = psd[n12_index]

    fmax_n3_beta = None
    fmax_n3_alpha = None
    fmax_n12_delta = None
    pmax_n3_delta = None
    pmax_n3_beta = None
    pmax_n3_alpha = None
    pmax_n12_beta = None
    pmax_n12_alpha = None
    n12_psd_avg_delta = None
    n12_psd_avg_beta = None
    n3_psd_avg_beta = None
    n3_psd_avg_delta = None
    n12_psd_avg_alpha = None
    n3_psd_avg_alpha = None

    if len(n3_psd) != 0:
        n3_percentile_10 = np.percentile(n3_psd, 10, axis=0)
        n3_percentile_90 = np.percentile(n3_psd, 90, axis=0)
        n3_psd_new = []
        for i in range(n3_psd.shape[0]):
            temp = n3_psd[i, :]
            temp[temp < n3_percentile_10] = n3_percentile_10[temp < n3_percentile_10]
            temp[temp > n3_percentile_90] = n3_percentile_90[temp > n3_percentile_90]
            n3_psd_new.append(temp)
        n3_psd = np.asarray(n3_psd_new)
        n3_psd_avg = np.average(n3_psd, axis=0)
        n3_psd_avg_beta = np.sum(np.reshape(n3_psd_avg[20 * 5:30 * 5], [-1, 5]), axis=1)
        n3_psd_avg_alpha = np.sum(np.reshape(n3_psd_avg[8 * 5:13 * 5], [-1, 5]), axis=1)
        n3_psd_avg_delta = np.sum(np.reshape(n3_psd_avg[1 * 5:4 * 5], [-1, 5]), axis=1)
        fmax_n3_beta = np.argmax(n3_psd_avg_beta) + 20
        fmax_n3_alpha = np.argmax(n3_psd_avg_alpha) + 8
        pmax_n3_delta = np.max(n3_psd_avg_delta)
        pmax_n3_beta = np.max(n3_psd_avg_beta)
        pmax_n3_alpha = np.max(n3_psd_avg_alpha)

    if len(n12_psd) != 0:
        n12_percentile_10 = np.percentile(n12_psd, 10, axis=0)
        n12_percentile_90 = np.percentile(n12_psd, 90, axis=0)
        n12_psd_new = []
        for i in range(n12_psd.shape[0]):
            temp = n12_psd[i, :]
            temp[temp < n12_percentile_10] = n12_percentile_10[temp < n12_percentile_10]
            temp[temp > n12_percentile_90] = n12_percentile_90[temp > n12_percentile_90]
            n12_psd_new.append(temp)
        n12_psd = np.asarray(n12_psd_new)
        n12_psd_avg = np.average(n12_psd, axis=0)
        n12_psd_avg_delta = np.sum(np.reshape(n12_psd_avg[1 * 5:4 * 5], [-1, 5]), axis=1)
        n12_psd_avg_beta = np.sum(np.reshape(n12_psd_avg[20 * 5:30 * 5], [-1, 5]), axis=1)
        n12_psd_avg_alpha = np.sum(np.reshape(n12_psd_avg[8 * 5:13 * 5], [-1, 5]), axis=1)
        fmax_n12_delta = np.argmax(n12_psd_avg_delta) + 1
        pmax_n12_beta = np.max(n12_psd_avg_beta)
        pmax_n12_alpha = np.max(n12_psd_avg_alpha)




    return {'fmax_n3_beta': [fmax_n3_beta] if fmax_n3_beta is not None else [""],
            'fmax_n3_alpha': [fmax_n3_alpha] if fmax_n3_alpha is not None else [""],
            'fmax_n12_delta': [fmax_n12_delta] if fmax_n12_delta is not None else [""],
            'pmax_n3_delta': [pmax_n3_delta] if pmax_n3_delta is not None else [""],
            'pmax_n3_beta': [pmax_n3_beta] if pmax_n3_beta is not None else [""],
            'pmax_n3_alpha': [pmax_n3_alpha] if pmax_n3_alpha is not None else [""],
            'pmax_n12_beta': [pmax_n12_beta] if pmax_n12_beta is not None else [""],
            'pmax_n12_alpha': [pmax_n12_alpha] if pmax_n12_alpha is not None else [""],
            'avg_n12_delta': [np.average(n12_psd_avg_delta)] if n12_psd_avg_delta is not None else [""],
            'avg_n12_beta': [np.average(n12_psd_avg_beta)] if n12_psd_avg_beta is not None else [""],
            'avg_n12_alpha': [np.average(n12_psd_avg_alpha)] if n12_psd_avg_alpha is not None else [""],
            'avg_n3_delta': [np.average(n3_psd_avg_delta)] if n3_psd_avg_delta is not None else [""],
            'avg_n3_beta': [np.average(n3_psd_avg_beta)] if n3_psd_avg_beta is not None else [""],
            'avg_n3_alpha': [np.average(n3_psd_avg_alpha)] if n3_psd_avg_alpha is not None else [""],
            }



def bandpower_from_psd_ndarray(bands, psd, freqs, relative=True):
    # Type checks
    assert isinstance(bands, list), "bands must be a list of tuple(s)"
    assert isinstance(relative, bool), "relative must be a boolean"

    # Safety checks
    freqs = np.asarray(freqs)
    psd = np.asarray(psd)
    assert freqs.ndim == 1, "freqs must be a 1-D array of shape (n_freqs,)"
    assert psd.shape[-1] == freqs.shape[-1], "n_freqs must be last axis of psd"

    # Extract frequencies of interest
    all_freqs = np.hstack([[b[0], b[1]] for b in bands])
    fmin, fmax = min(all_freqs), max(all_freqs)
    idx_good_freq = np.logical_and(freqs >= fmin, freqs <= fmax)
    freqs = freqs[idx_good_freq]
    res = freqs[1] - freqs[0]

    # Trim PSD to frequencies of interest
    psd = psd[..., idx_good_freq]

    # plt.imshow(psd.T[:50,:], cmap='jet')
    # plt.show()
    # assert 0

    # Check if there are negative values in PSD
    if (psd < 0).any():
        pass

    # Calculate total power
    total_power = simps(psd, dx=res, axis=-1)
    total_power = total_power[np.newaxis, ...]

    # Initialize empty array
    bp = np.zeros((len(bands), *psd.shape[:-1]), dtype=np.float64)

    # Enumerate over the frequency bands
    labels = []
    for i, band in enumerate(bands):
        b0, b1, la = band
        labels.append(la)
        idx_band = np.logical_and(freqs >= b0, freqs <= b1)
        bp[i] = simps(psd[..., idx_band], dx=res, axis=-1)

    if relative:
        bp /= total_power

    return bp
