import mne
import logging
import numpy as np
import pandas as pd
from scipy.io import savemat

from lm_datahandler.utils.numba_func import _corr, _detrend, _slope_lstsq, _rms, _covar
from scipy import signal
from mne.filter import filter_data
from collections import OrderedDict
from scipy.interpolate import interp1d, RectBivariateSpline
from scipy.fftpack import next_fast_len
from sklearn.ensemble import IsolationForest


def get_centered_indices(data, idx, npts_before, npts_after):
    """Get a 2D array of indices in data centered around specific time points,
    automatically excluding indices that are outside the bounds of data.

    Parameters
    ----------
    data : 1-D array_like
        Input data.
    idx : 1-D array_like
        Indices of events in data (e.g. peaks)
    npts_before : int
        Number of data points to include before ``idx``
    npts_after : int
        Number of data points to include after ``idx``

    Returns
    -------
    idx_ep : 2-D array
        Array of indices of shape (len(idx_nomask), npts_before +
        npts_after + 1). Indices outside the bounds of data are removed.
    idx_nomask : 1-D array
        Indices of ``idx`` that are not masked (= valid).

    Examples
    --------
    # >>> import numpy as np
    # >>> from yasa import get_centered_indices
    # >>> np.random.seed(123)
    # >>> data = np.random.normal(size=100).round(2)
    # >>> idx = [1., 10., 20., 30., 50., 102]
    # >>> before, after = 3, 2
    # >>> idx_ep, idx_nomask = get_centered_indices(data, idx, before, after)
    # >>> idx_ep
    array([[ 7,  8,  9, 10, 11, 12],
           [17, 18, 19, 20, 21, 22],
           [27, 28, 29, 30, 31, 32],
           [47, 48, 49, 50, 51, 52]])

    # >>> data[idx_ep]
    array([[-0.43,  1.27, -0.87, -0.68, -0.09,  1.49],
           [ 2.19,  1.  ,  0.39,  0.74,  1.49, -0.94],
           [-1.43, -0.14, -0.86, -0.26, -2.8 , -1.77],
           [ 0.41,  0.98,  2.24, -1.29, -1.04,  1.74]])

    # >>> idx_nomask
    array([1, 2, 3, 4], dtype=int64)
    """
    # Safety check
    assert isinstance(npts_before, (int, float))
    assert isinstance(npts_after, (int, float))
    assert float(npts_before).is_integer()
    assert float(npts_after).is_integer()
    npts_before = int(npts_before)
    npts_after = int(npts_after)
    data = np.asarray(data)
    idx = np.asarray(idx, dtype="int")
    assert idx.ndim == 1, "idx must be 1D."
    assert data.ndim == 1, "data must be 1D."

    def rng(x):
        """Create a range before and after a given value."""
        return np.arange(x - npts_before, x + npts_after + 1, dtype="int")

    idx_ep = np.apply_along_axis(rng, 1, idx[..., np.newaxis])
    # We drop the events for which the indices exceed data
    idx_ep = np.ma.mask_rows(np.ma.masked_outside(idx_ep, 0, data.shape[0]))
    # Indices of non-masked (valid) epochs in idx
    idx_ep_nomask = np.unique(idx_ep.nonzero()[0])
    idx_ep = np.ma.compress_rows(idx_ep)
    return idx_ep, idx_ep_nomask


def stft_power(data, sf, window=2, step=0.2, band=(1, 30), interp=True, norm=False):
    """Compute the pointwise power via STFT and interpolation.

    Parameters
    ----------
    data : array_like
        Single-channel data.
    sf : float
        Sampling frequency of the data.
    window : int
        Window size in seconds for STFT. 2 or 4 seconds are usually a good default.
        Higher values = higher frequency resolution = lower time resolution.
    step : int
        Step in seconds for the STFT.
        A step of 0.2 second (200 ms) is usually a good default.

        * If ``step`` == 0, overlap at every sample (slowest)
        * If ``step`` == nperseg, no overlap (fastest)

        Higher values = higher precision = slower computation.
    band : tuple or None
        Broad band frequency range. Default is 1 to 30 Hz.
    interp : boolean
        If True, a cubic interpolation is performed to ensure that the output is the same size as
        the input (= pointwise power).
    norm : bool
        If True, return bandwise normalized band power, i.e. for each time point, the sum of power
        in all the frequency bins equals 1.

    Returns
    -------
    f : :py:class:`numpy.ndarray`
        Frequency vector
    t : :py:class:`numpy.ndarray`
        Time vector
    Sxx : :py:class:`numpy.ndarray`
        Power in the specified frequency bins of shape (f, t)

    Notes
    -----
    2D Interpolation is done using :py:class:`scipy.interpolate.RectBivariateSpline`
    which is much faster than :py:class:`scipy.interpolate.interp2d` for a rectangular grid.
    The default is to use a bivariate spline with 3 degrees.
    """
    # Safety check
    data = np.asarray(data)
    assert step <= window
    step = 1 / sf if step == 0 else step

    # Define STFT parameters
    nperseg = int(window * sf)
    noverlap = int(nperseg - (step * sf))

    # Compute STFT and remove the last epoch
    f, t, Sxx = signal.stft(
        data, sf, nperseg=nperseg, noverlap=noverlap, detrend=False, padded=True
    )

    # Let's keep only the frequency of interest
    if band is not None:
        idx_band = np.logical_and(f >= band[0], f <= band[1])
        f = f[idx_band]
        Sxx = Sxx[idx_band, :]

    # Compute power and interpolate
    Sxx = np.square(np.abs(Sxx))
    if interp:
        func = RectBivariateSpline(f, t, Sxx)
        t = np.arange(data.size) / sf
        Sxx = func(f, t)

    # Normalize
    if norm:
        sum_pow = Sxx.sum(0).reshape(1, -1)
        np.divide(Sxx, sum_pow, out=Sxx)
    return f, t, Sxx


def moving_transform(x, y=None, sf=100, window=0.3, step=0.1, method="corr", interp=False):
    """Moving transformation of one or two time-series.

    Parameters
    ----------
    x : array_like
        Single-channel data
    y : array_like, optional
        Second single-channel data (only used if method in ['corr', 'covar']).
    sf : float
        Sampling frequency.
    window : int
        Window size in seconds.
    step : int
        Step in seconds.
        A step of 0.1 second (100 ms) is usually a good default.
        If step == 0, overlap at every sample (slowest)
        If step == nperseg, no overlap (fastest)
        Higher values = higher precision = slower computation.
    method : str
        Transformation to use.
        Available methods are::

            'mean' : arithmetic mean of x
            'min' : minimum value of x
            'max' : maximum value of x
            'ptp' : peak-to-peak amplitude of x
            'prop_above_zero' : proportion of values of x that are above zero
            'rms' : root mean square of x
            'slope' : slope of the least-square regression of x (in a.u / sec)
            'corr' : Correlation between x and y
            'covar' : Covariance between x and y
    interp : boolean
        If True, a cubic interpolation is performed to ensure that the output
        has the same size as the input.

    Returns
    -------
    t : np.array
        Time vector, in seconds, corresponding to the MIDDLE of each epoch.
    out : np.array
        Transformed signal

    Notes
    -----
    This function was inspired by the `transform_signal` function of the
    Wonambi package (https://github.com/wonambi-python/wonambi).
    """
    # Safety checks
    assert method in [
        "mean",
        "min",
        "max",
        "ptp",
        "rms",
        "prop_above_zero",
        "slope",
        "covar",
        "corr",
    ]
    x = np.asarray(x, dtype=np.float64)
    if y is not None:
        y = np.asarray(y, dtype=np.float64)
        assert x.size == y.size

    if step == 0:
        step = 1 / sf

    halfdur = window / 2
    n = x.size
    total_dur = n / sf
    last = n - 1
    idx = np.arange(0, total_dur, step)
    out = np.zeros(idx.size)

    # Define beginning, end and time (centered) vector
    beg = ((idx - halfdur) * sf).astype(int)
    end = ((idx + halfdur) * sf).astype(int)
    beg[beg < 0] = 0
    end[end > last] = last
    # Alternatively, to cut off incomplete windows (comment the 2 lines above)
    # mask = ~((beg < 0) | (end > last))
    # beg, end = beg[mask], end[mask]
    t = np.column_stack((beg, end)).mean(1) / sf

    if method == "mean":

        def func(x):
            return np.mean(x)

    elif method == "min":

        def func(x):
            return np.min(x)

    elif method == "max":

        def func(x):
            return np.max(x)

    elif method == "ptp":

        def func(x):
            return np.ptp(x)

    elif method == "prop_above_zero":

        def func(x):
            return np.count_nonzero(x >= 0) / x.size

    elif method == "slope":

        def func(x):
            times = np.arange(x.size, dtype=np.float64) / sf
            return _slope_lstsq(times, x)

    elif method == "covar":

        def func(x, y):
            return _covar(x, y)

    elif method == "corr":

        def func(x, y):
            return _corr(x, y)

    else:

        def func(x):
            return _rms(x)

    # Now loop over successive epochs
    if method in ["covar", "corr"]:
        for i in range(idx.size):
            out[i] = func(x[beg[i]: end[i]], y[beg[i]: end[i]])
    else:
        for i in range(idx.size):
            out[i] = func(x[beg[i]: end[i]])

    # Finally interpolate
    if interp and step != 1 / sf:
        f = interp1d(t, out, kind="cubic", bounds_error=False, fill_value=0, assume_sorted=True)
        t = np.arange(n) / sf
        out = f(t)

    return t, out


def zerocrossings(x):
    """
    Find indices of zero-crossings in a 1D array.

    Parameters
    ----------
    x : np.array
        One dimensional data vector.

    Returns
    -------
    idx_zc : np.array
        Indices of zero-crossings

    Examples
    --------
    # >>> import numpy as np
    # >>> from yasa.main import _zerocrossings
    # >>> a = np.array([4, 2, -1, -3, 1, 2, 3, -2, -5])
    # >>> _zerocrossings(a)
        array([1, 3, 6], dtype=int64)
    """
    pos = x > 0
    npos = ~pos
    return ((pos[:-1] & npos[1:]) | (npos[:-1] & pos[1:])).nonzero()[0]


def trimbothstd(x, cut=0.10):
    """
    Slices off a proportion of items from both ends of an array and then
    compute the sample standard deviation.

    Slices off the passed proportion of items from both ends of the passed
    array (i.e., with ``cut`` = 0.1, slices leftmost 10% **and**
    rightmost 10% of scores). The trimmed values are the lowest and
    highest ones.
    Slices off less if proportion results in a non-integer slice index.

    Parameters
    ----------
    x : np.array
        Input array.
    cut : float
        Proportion (in range 0-1) of total data to trim of each end.
        Default is 0.10, i.e. 10% lowest and 10% highest values are removed.

    Returns
    -------
    trimmed_std : float
        Sample standard deviation of the trimmed array, calculated on the last
        axis.
    """
    x = np.asarray(x)
    n = x.shape[-1]
    lowercut = int(cut * n)
    uppercut = n - lowercut
    atmp = np.partition(x, (lowercut, uppercut - 1), axis=-1)
    sl = slice(lowercut, uppercut)
    return np.nanstd(atmp[..., sl], ddof=1, axis=-1)


def _merge_close(index, min_distance_ms, sf):
    """Merge events that are too close in time.

    Parameters
    ----------
    index : array_like
        Indices of supra-threshold events.
    min_distance_ms : int
        Minimum distance (ms) between two events to consider them as two
        distinct events
    sf : float
        Sampling frequency of the data (Hz)

    Returns
    -------
    f_index : array_like
        Filled (corrected) Indices of supra-threshold events

    Notes
    -----
    Original code imported from the Visbrain package.
    """
    # Convert min_distance_ms
    min_distance = min_distance_ms / 1000.0 * sf
    idx_diff = np.diff(index)
    condition = idx_diff > 1
    idx_distance = np.where(condition)[0]
    distance = idx_diff[condition]
    bad = idx_distance[np.where(distance < min_distance)[0]]
    # Fill gap between events separated with less than min_distance_ms
    if len(bad) > 0:
        fill = np.hstack([np.arange(index[j] + 1, index[j + 1]) for i, j in enumerate(bad)])
        f_index = np.sort(np.append(index, fill))
        return f_index
    else:
        return index


def spindles_detect(
        data,
        sf=500,
        mask=None,
        freq_sp=(12, 15),
        freq_broad=(1, 30),
        duration=(0.2, 2),
        min_distance=500,
        thresh_rel_pow=0.2,
        thresh_corr=0.65,
        thresh_rms=1.5,
        remove_outliers=False,
):
    data = np.asarray(data).squeeze()
    n_samples = data.shape[0]

    # 1) Broadband bandpass filter (optional -- careful of lower freq for PAC)
    data_broad = filter_data(data, sf, freq_broad[0], freq_broad[1], method="fir", verbose=0)
    # 2) Sigma bandpass filter
    # The width of the transition band is set to 1.5 Hz on each side,
    # meaning that for freq_sp = (12, 15 Hz), the -6 dB points are located at
    # 11.25 and 15.75 Hz.
    data_sigma = filter_data(data, sf, freq_sp[0], freq_sp[1], l_trans_bandwidth=1.5, h_trans_bandwidth=1.5,
                             method="fir", verbose=0)
    savemat("sp_eeg.mat", {"sp_eeg": data_sigma})
    nfast = next_fast_len(n_samples)
    # Hilbert power (to define the instantaneous frequency / power)
    analytic = signal.hilbert(data_sigma, N=nfast)[:n_samples]
    inst_phase = np.angle(analytic)
    inst_pow = np.square(np.abs(analytic))
    inst_freq = sf / (2 * np.pi) * np.diff(inst_phase, axis=-1)

    # prepare DataFrame
    df = pd.DataFrame()

    # Compute the pointwise relative power using interpolated STFT
    # Here we use a step of 200 ms to speed up the computation.
    # Note that even if the threshold is None we still need to calculate it
    # for the individual spindles parameter (RelPow).
    f, t, Sxx = stft_power(
        data_broad, sf, window=2, step=0.2, band=freq_broad, interp=False, norm=True
    )
    idx_sigma = np.logical_and(f >= freq_sp[0], f <= freq_sp[1])
    rel_pow = Sxx[idx_sigma].sum(0)

    # Let's interpolate `rel_pow` to get one value per sample
    # Note that we could also have use the `interp=True` in the
    # `stft_power` function, however 2D interpolation is much slower than
    # 1D interpolation.
    func = interp1d(t, rel_pow, kind="cubic", bounds_error=False, fill_value=0)
    t = np.arange(n_samples) / sf
    rel_pow = func(t)

    _, mcorr = moving_transform(x=data_sigma, y=data_broad, sf=sf, window=0.3, step=0.1, method="corr", interp=True, )

    _, mrms = moving_transform(x=data_sigma, sf=sf, window=0.3, step=0.1, method="rms", interp=True)
    # Let's define the thresholds
    if mask is None:
        thresh_rms = mrms.mean() + thresh_rms * trimbothstd(mrms, cut=0.10)
    else:
        thresh_rms = mrms[mask].mean() + thresh_rms * trimbothstd(mrms[mask], cut=0.10)
    # Avoid too high threshold caused by Artefacts / Motion during Wake
    thresh_rms = min(thresh_rms, 10)
    logging.info("Moving RMS threshold = %.3f", thresh_rms)

    # Boolean vector of supra-threshold indices
    idx_sum = np.zeros(n_samples)
    # if do_rel_pow:
    idx_rel_pow = (rel_pow >= thresh_rel_pow).astype(int)
    idx_sum += idx_rel_pow
    logging.info("N supra-theshold relative power = %i", idx_rel_pow.sum())
    # if do_corr:
    idx_mcorr = (mcorr >= thresh_corr).astype(int)
    idx_sum += idx_mcorr
    logging.info("N supra-theshold moving corr = %i", idx_mcorr.sum())
    # if do_rms:
    idx_mrms = (mrms >= thresh_rms).astype(int)
    idx_sum += idx_mrms
    logging.info("N supra-theshold moving RMS = %i", idx_mrms.sum())

    # Make sure that we do not detect spindles outside mask
    if mask is not None:
        idx_sum[~mask] = 0

    # The detection using the three thresholds tends to underestimate the
    # real duration of the spindle. To overcome this, we compute a soft
    # threshold by smoothing the idx_sum vector with a ~100 ms window.
    # Sampling frequency = 100 Hz --> w = 10 samples
    # Sampling frequecy = 256 Hz --> w = 25 samples = 97 ms
    w = int(0.1 * sf)
    # Critical bugfix March 2022, see https://github.com/raphaelvallat/yasa/pull/55
    idx_sum = np.convolve(idx_sum, np.ones(w), mode="same") / w
    # And we then find indices that are strictly greater than 2, i.e. we
    # find the 'true' beginning and 'true' end of the events by finding
    # where at least two out of the three treshold were crossed.
    n_thresh = 3
    where_sp = np.where(idx_sum >= (n_thresh - 1))[0]

    # If no events are found, skip to next channel
    if not len(where_sp):
        logging.warning("No spindle were found.")
        return pd.DataFrame({
            "Start_Time": [],
            "Peak_Time": [],
            "End_Time": [],
            "Start_Index": [],
            "End_Index": [],

            "Duration": [],
            "Amplitude": [],
            "RMS": [],
            "AbsPower": [],
            "RelPower": [],
            "Frequency": [],
            "Oscillations": [],
            "Symmetry": [],
            # 'SOPhase': sp_cou,
        })

    # Merge events that are too close
    if min_distance is not None and min_distance > 0:
        where_sp = _merge_close(where_sp, min_distance, sf)

    # Extract start, end, and duration of each spindle
    sp = np.split(where_sp, np.where(np.diff(where_sp) != 1)[0] + 1)
    idx_start_end = np.array([[k[0], k[-1]] for k in sp]) / sf
    sp_start, sp_end = idx_start_end.T
    sp_dur = sp_end - sp_start
    sp_start_index, sp_end_index = np.array([[k[0], k[-1]] for k in sp]).T

    # Find events with bad duration
    good_dur = np.logical_and(sp_dur > duration[0], sp_dur < duration[1])

    # If no events of good duration are found, skip to next channel
    if all(~good_dur):
        logging.warning("No spindle were found.")
        return pd.DataFrame({
            "Start_Time": [],
            "Peak_Time": [],
            "End_Time": [],
            "Start_Index": [],
            "End_Index": [],

            "Duration": [],
            "Amplitude": [],
            "RMS": [],
            "AbsPower": [],
            "RelPower": [],
            "Frequency": [],
            "Oscillations": [],
            "Symmetry": [],
            # 'SOPhase': sp_cou,
        })

    # Initialize empty variables
    sp_amp = np.zeros(len(sp))
    sp_freq = np.zeros(len(sp))
    sp_rms = np.zeros(len(sp))
    sp_osc = np.zeros(len(sp))
    sp_sym = np.zeros(len(sp))
    sp_abs = np.zeros(len(sp))
    sp_rel = np.zeros(len(sp))
    sp_pro = np.zeros(len(sp))
    # sp_cou = np.zeros(len(sp))

    # Number of oscillations (number of peaks separated by at least 60 ms)
    # --> 60 ms because 1000 ms / 16 Hz = 62.5 m, in other words, at 16 Hz,
    # peaks are separated by 62.5 ms. At 11 Hz peaks are separated by 90 ms
    distance = 60 * sf / 1000

    for j in np.arange(len(sp))[good_dur]:
        # Important: detrend the signal to avoid wrong PTP amplitude
        sp_x = np.arange(data_broad[sp[j]].size, dtype=np.float64)
        sp_det = _detrend(sp_x, data_broad[sp[j]])
        # sp_det = signal.detrend(data_broad[i, sp[i]], type='linear')
        sp_amp[j] = np.ptp(sp_det)  # Peak-to-peak amplitude
        sp_rms[j] = _rms(sp_det)  # Root mean square
        sp_rel[j] = np.median(rel_pow[sp[j]])  # Median relative power

        # Hilbert-based instantaneous properties
        sp_inst_freq = inst_freq[sp[j]]
        sp_inst_pow = inst_pow[sp[j]]
        sp_abs[j] = np.median(np.log10(sp_inst_pow[sp_inst_pow > 0]))
        sp_freq[j] = np.median(sp_inst_freq[sp_inst_freq > 0])

        # Number of oscillations
        peaks, peaks_params = signal.find_peaks(
            sp_det, distance=distance, prominence=(None, None)
        )
        sp_osc[j] = len(peaks)

        # For frequency and amplitude, we can also optionally use these
        # faster alternatives. If we use them, we do not need to compute
        # the Hilbert transform of the filtered signal.
        # sp_freq[j] = sf / np.mean(np.diff(peaks))
        # sp_amp[j] = peaks_params['prominences'].max()

        # Peak location & symmetry index
        # pk is expressed in sample since the beginning of the spindle
        pk = peaks[peaks_params["prominences"].argmax()]
        sp_pro[j] = sp_start[j] + pk / sf
        sp_sym[j] = pk / sp_det.size

        # SO-spindles coupling
        # if coupling:
        #     sp_cou[j] = so_phase[i, sp[j]][pk]

    # Create a dataframe
    sp_params = {
        "Start_Time": sp_start,
        "Peak_Time": sp_pro,
        "End_Time": sp_end,
        "Start_Index": sp_start_index,
        "End_Index": sp_end_index,

        "Duration": sp_dur,
        "Amplitude": sp_amp,
        "RMS": sp_rms,
        "AbsPower": sp_abs,
        "RelPower": sp_rel,
        "Frequency": sp_freq,
        "Oscillations": sp_osc,
        "Symmetry": sp_sym,
        # 'SOPhase': sp_cou,
    }

    df_chan = pd.DataFrame(sp_params)[good_dur]

    # We need at least 50 detected spindles to apply the Isolation Forest.
    if remove_outliers and df_chan.shape[0] >= 50:
        col_keep = [
            "Duration",
            "Amplitude",
            "RMS",
            "AbsPower",
            "RelPower",
            "Frequency",
            "Oscillations",
            "Symmetry",
        ]
        ilf = IsolationForest(
            contamination="auto", max_samples="auto", verbose=0, random_state=42
        )
        good = ilf.fit_predict(df_chan[col_keep])
        good[good == -1] = 0
        logging.info(
            "%i outliers were removed." % ((good == 0).sum())
        )
        # Remove outliers from DataFrame
        df_chan = df_chan[good.astype(bool)]
        logging.info("%i spindles were found." % (df_chan.shape[0]))

    # ####################################################################
    # END SINGLE CHANNEL DETECTION
    # ####################################################################
    df = pd.concat([df, df_chan], axis=0, ignore_index=True)

    if df.empty:
        logging.warning("No spindles were found in data. Returning None.")
        return None

    return df
    # return SpindlesResults(events=df, data=data, sf=sf, ch_names=ch_names, hypno=hypno, data_filt=data_sigma)


def sw_detect(
        data,
        sf=None,
        mask=None,
        include=(2, 3),
        freq_sw=(0.3, 1.5),
        dur_neg=(0.1, 1),
        dur_pos=(0.3, 1.5),
        amp_neg=(40, 200),
        amp_pos=(10, 150),
        amp_ptp=(75, 350),
        coupling=False,
        coupling_params={"freq_sp": (12, 16), "time": 1, "p": 0.05},
        remove_outliers=False
):
    data = np.asarray(data).squeeze()
    n_samples = data.shape[0]

    # Define time vector
    times = np.arange(data.size) / sf
    if mask is not None:
        idx_mask = np.where(mask)[0]
    else:
        idx_mask = np.where(data)[0]
    # Bandpass filter

    data_filt = filter_data(
        data,
        sf,
        freq_sw[0],
        freq_sw[1],
        method="fir",
        verbose=0,
        l_trans_bandwidth=0.2,
        h_trans_bandwidth=0.2,
    )

    savemat("sw_eeg.mat", {"sw_eeg": data_filt})

    # Initialize empty output dataframe
    df = pd.DataFrame()

    # ################################
    # use zero cross point to find SW
    # data_signs = np.signbit(data_filt)
    # data_signs = data_signs[:-1] * data_signs[1:]
    #
    # zero_cross_index = np.where(False == data_signs)
    # zero_cross_index = np.intersect1d(zero_cross_index, idx_mask, assume_unique=True)
    #
    # # find every peak without setting limit
    # idx_neg_peaks, _ = signal.find_peaks(-1 * data_filt[:], height=(0, 500))
    # idx_pos_peaks, _ = signal.find_peaks(data_filt[:], height=(0, 500))
    # idx_neg_peaks = np.intersect1d(idx_neg_peaks, idx_mask, assume_unique=True)
    # idx_pos_peaks = np.intersect1d(idx_pos_peaks, idx_mask, assume_unique=True)

    # ##################################

    # ####################################################################
    # START SINGLE CHANNEL DETECTION
    # ####################################################################

    # todo: data_filt形状
    # Find peaks in data
    # Negative peaks with value comprised between -40 to -300 uV
    idx_neg_peaks, _ = signal.find_peaks(-1 * data_filt[:], height=amp_neg)
    # Positive peaks with values comprised between 10 to 200 uV
    idx_pos_peaks, _ = signal.find_peaks(data_filt[:], height=amp_pos)
    # Intersect with sleep stage vector
    idx_neg_peaks = np.intersect1d(idx_neg_peaks, idx_mask, assume_unique=True)
    idx_pos_peaks = np.intersect1d(idx_pos_peaks, idx_mask, assume_unique=True)

    # If no peaks are detected, return None
    if len(idx_neg_peaks) == 0 or len(idx_pos_peaks) == 0:
        logging.warning("No SW were found.")
        return pd.DataFrame({
            "Start_Time": [],
            "NegPeak": [],
            "MidCrossing": [],
            "PosPeak": [],
            "End_Time": [],
            "Start_Index": [],
            "End_Index": [],
            "Duration": [],
            "ValNegPeak": [],
            "ValPosPeak": [],
            "PTP": [],
            "Slope": [],
            "Frequency": [],
        })

    # Make sure that the last detected peak is a positive one
    if idx_pos_peaks[-1] < idx_neg_peaks[-1]:
        # If not, append a fake positive peak one sample after the last neg
        idx_pos_peaks = np.append(idx_pos_peaks, idx_neg_peaks[-1] + 1)

    # For each negative peak, we find the closest following positive peak
    pk_sorted = np.searchsorted(idx_pos_peaks, idx_neg_peaks)
    closest_pos_peaks = idx_pos_peaks[pk_sorted] - idx_neg_peaks
    closest_pos_peaks = closest_pos_peaks[np.nonzero(closest_pos_peaks)]
    idx_pos_peaks = idx_neg_peaks + closest_pos_peaks

    # Now we compute the PTP amplitude and keep only the good peaks
    sw_ptp = np.abs(data_filt[idx_neg_peaks]) + data_filt[idx_pos_peaks]
    good_ptp = np.logical_and(sw_ptp > amp_ptp[0], sw_ptp < amp_ptp[1])

    # If good_ptp is all False
    if all(~good_ptp):
        logging.warning("No SW were found.")
        return pd.DataFrame({
            "Start_Time": [],
            "NegPeak": [],
            "MidCrossing": [],
            "PosPeak": [],
            "End_Time": [],
            "Start_Index": [],
            "End_Index": [],
            "Duration": [],
            "ValNegPeak": [],
            "ValPosPeak": [],
            "PTP": [],
            "Slope": [],
            "Frequency": [],
        })

    sw_ptp = sw_ptp[good_ptp]
    idx_neg_peaks = idx_neg_peaks[good_ptp]
    idx_pos_peaks = idx_pos_peaks[good_ptp]

    # Now we need to check the negative and positive phase duration
    # For that we need to compute the zero crossings of the filtered signal
    zero_crossings = zerocrossings(data_filt[:])
    # Make sure that there is a zero-crossing after the last detected peak
    if zero_crossings[-1] < max(idx_pos_peaks[-1], idx_neg_peaks[-1]):
        # If not, append the index of the last peak
        zero_crossings = np.append(zero_crossings, max(idx_pos_peaks[-1], idx_neg_peaks[-1]))

    # Find distance to previous and following zc
    neg_sorted = np.searchsorted(zero_crossings, idx_neg_peaks)
    previous_neg_zc = zero_crossings[neg_sorted - 1] - idx_neg_peaks
    following_neg_zc = zero_crossings[neg_sorted] - idx_neg_peaks

    # Distance between the positive peaks and the previous and
    # following zero-crossings
    pos_sorted = np.searchsorted(zero_crossings, idx_pos_peaks)
    previous_pos_zc = zero_crossings[pos_sorted - 1] - idx_pos_peaks
    following_pos_zc = zero_crossings[pos_sorted] - idx_pos_peaks

    # Duration of the negative and positive phases, in seconds
    neg_phase_dur = (np.abs(previous_neg_zc) + following_neg_zc) / sf
    pos_phase_dur = (np.abs(previous_pos_zc) + following_pos_zc) / sf

    # We now compute a set of metrics
    sw_start_index = idx_neg_peaks + previous_neg_zc
    sw_start = times[sw_start_index]
    sw_end_index = idx_pos_peaks + following_pos_zc
    sw_end = times[sw_end_index]
    # This should be the same as `sw_dur = pos_phase_dur + neg_phase_dur`
    # We round to avoid floating point errr (e.g. 1.9000000002)
    sw_dur = (sw_end - sw_start).round(4)
    sw_dur_both_phase = (pos_phase_dur + neg_phase_dur).round(4)
    sw_midcrossing = times[idx_neg_peaks + following_neg_zc]
    sw_idx_neg = times[idx_neg_peaks]  # Location of negative peak
    sw_idx_pos = times[idx_pos_peaks]  # Location of positive peak
    # Slope between peak trough and midcrossing
    sw_slope = sw_ptp / (sw_midcrossing - sw_idx_neg)

    # And we apply a set of thresholds to remove bad slow waves
    good_sw = np.logical_and.reduce(
        (
            # Data edges
            previous_neg_zc != 0,
            following_neg_zc != 0,
            previous_pos_zc != 0,
            following_pos_zc != 0,
            # Duration criteria
            sw_dur == sw_dur_both_phase,  # dur = negative + positive
            sw_dur <= dur_neg[1] + dur_pos[1],  # dur < max(neg) + max(pos)
            sw_dur >= dur_neg[0] + dur_pos[0],  # dur > min(neg) + min(pos)
            neg_phase_dur > dur_neg[0],
            neg_phase_dur < dur_neg[1],
            pos_phase_dur > dur_pos[0],
            pos_phase_dur < dur_pos[1],
            # Sanity checks
            sw_midcrossing > sw_start,
            sw_midcrossing < sw_end,
            sw_slope > 0,
        )
    )

    if all(~good_sw):
        logging.warning("No SW were found.")
        return pd.DataFrame({
            "Start_Time": [],
            "NegPeak": [],
            "MidCrossing": [],
            "PosPeak": [],
            "End_Time": [],
            "Start_Index": [],
            "End_Index": [],
            "Duration": [],
            "ValNegPeak": [],
            "ValPosPeak": [],
            "PTP": [],
            "Slope": [],
            "Frequency": [],
        })

    # Filter good events
    idx_neg_peaks = idx_neg_peaks[good_sw]
    idx_pos_peaks = idx_pos_peaks[good_sw]
    sw_start = sw_start[good_sw]
    sw_idx_neg = sw_idx_neg[good_sw]
    sw_midcrossing = sw_midcrossing[good_sw]
    sw_idx_pos = sw_idx_pos[good_sw]
    sw_end = sw_end[good_sw]
    sw_start_index = sw_start_index[good_sw]
    sw_end_index = sw_end_index[good_sw]
    sw_dur = sw_dur[good_sw]
    sw_ptp = sw_ptp[good_sw]
    sw_slope = sw_slope[good_sw]

    # Create a dictionnary
    sw_params = OrderedDict(
        {
            "Start_Time": sw_start,
            "NegPeak": sw_idx_neg,
            "MidCrossing": sw_midcrossing,
            "PosPeak": sw_idx_pos,
            "End_Time": sw_end,
            "Start_Index": sw_start_index,
            "End_Index": sw_end_index,
            "Duration": sw_dur,
            "ValNegPeak": data_filt[idx_neg_peaks],
            "ValPosPeak": data_filt[idx_pos_peaks],
            "PTP": sw_ptp,
            "Slope": sw_slope,
            "Frequency": 1 / sw_dur,
        }
    )

    # Convert to dataframe, keeping only good events
    df_chan = pd.DataFrame(sw_params)

    # Remove all duplicates
    df_chan = df_chan.drop_duplicates(subset=["Start_Index"])
    df_chan = df_chan.drop_duplicates(subset=["End_Index"])

    # We need at least 50 detected slow waves to apply the Isolation Forest
    if remove_outliers and df_chan.shape[0] >= 50:
        col_keep = ["Duration", "ValNegPeak", "ValPosPeak", "PTP", "Slope", "Frequency"]
        ilf = IsolationForest(
            contamination="auto", max_samples="auto", verbose=0, random_state=42
        )
        good = ilf.fit_predict(df_chan[col_keep])
        good[good == -1] = 0
        logging.info(
            "%i outliers were removed." % ((good == 0).sum())
        )
        # Remove outliers from DataFrame
        df_chan = df_chan[good.astype(bool)]
        logging.info("%i slow-waves were found." % (df_chan.shape[0]))

    # ####################################################################
    # END SINGLE CHANNEL DETECTION
    # ####################################################################

    df = pd.concat([df, df_chan], axis=0, ignore_index=True)

    # If no SW were detected, return None
    if df.empty:
        logging.warning("No SW were found in data. Returning None.")

    return df
    # return SWResults(events=df, data=data, sf=sf, ch_names=ch_names, hypno=hypno, data_filt=data_filt)
