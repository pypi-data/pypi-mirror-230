import antropy as ant
import numpy as np
import pandas as pd
import scipy.signal as sp_sig
import scipy.stats as sp_stats
from scipy.integrate._quadrature import simps
from sklearn.preprocessing import robust_scale


# input:
#   raw_eeg:[n_epochs, 15000]
#   raw_acc:[n_epochs, 3, 1500]
class RSCFeature:
    # bands = [
    #     (0.4, 1, "sdelta"),
    #     (1, 4, "fdelta"),
    #     (0.4, 4, "delta"),
    #     (4, 8, "theta"),
    #     (8, 12, "alpha"),
    #     (12, 16, "sigma"),
    #     (16, 30, "beta"),
    # ]

    bands = [
        (0.4, 1, "sdelta"),
        (0.4, 2, "delta2"),
        (0.4, 3, "delta3"),
        (0.4, 4, "delta"),
        (1, 4, "fdelta"),
        (2, 3, "delta4"),
        (2, 8, "theta2"),
        (4, 6, "theta3"),

        (4, 8, "theta"),
        (4, 12, "n_wave"),
        (8, 12, "alpha"),
        (8, 10, "alpha2"),

        (11, 16, "sp_wave1"),
        (12, 15, "sp_wave2"),
        (10, 15, "sp_wave3"),

        (12, 16, "sigma"),
        (15, 30, "rem_wave3"),
        (15, 20, "rem_wave"),

        (16, 20, "empty_band1"),

        (16, 23, "beta2"),
        (16, 30, "beta3"),

        (20, 30, "beta"),

        (30, 40, "empty_band2"),

        (35, 49, "gama"),
        (49, 51, "gama2"),
        (51, 60, "gama3"),
        (60, 75, "gama4"),
    ]

    def __init__(self, person_info, raw_eeg, sf_eeg=500, raw_acc=None, sf_acc=50):
        super().__init__()
        self.feature_name_ = None
        self.raw_eeg = raw_eeg
        self.sf_eeg = sf_eeg
        self.raw_acc = raw_acc
        self.sf_acc = sf_acc
        self.feature_in_dataframe = None
        self.person_info = person_info

        self.fit()

    def fit(self):
        feature = {}

        freq_feature, freqs, psd = self.generate_freq_feature()
        feature.update(freq_feature)

        statistic_feature = self.generate_statistic_feature(self.raw_eeg)
        feature.update(statistic_feature)

        # bio_feature = self.generate_biomarker_features(self.raw_eeg, self.sf_eeg)
        # feature.update(bio_feature)

        other_feature = self.generate_other_feature(freqs, psd, self.raw_eeg)
        feature.update(other_feature)

        self.feature_in_dataframe = pd.DataFrame(feature).add_prefix("eeg_")
        if self.raw_acc is not None:
            acc_feature = self.generate_acc_feature(raw_acc=self.raw_acc)
            acc_feature_in_dataframe = pd.DataFrame(acc_feature).add_prefix("acc_")
            self.feature_in_dataframe = self.feature_in_dataframe.join(acc_feature_in_dataframe)

        self.feature_in_dataframe.index.name = "epoch"

        # Apply centered rolling average (15 epochs = 7 min 30)
        # Triang: [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.,
        #          0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125]

        rollc = self.feature_in_dataframe.rolling(window=25, center=True, min_periods=1, win_type="triang").mean()
        rollc[rollc.columns] = robust_scale(rollc, quantile_range=(5, 95))
        rollc = rollc.add_suffix("_c6min_norm")

        # Now look at the past 2 minutes
        rollp = self.feature_in_dataframe.rolling(window=15, min_periods=1).mean()
        rollp[rollp.columns] = robust_scale(rollp, quantile_range=(5, 95))
        rollp = rollp.add_suffix("_p2min_norm")
        self.feature_in_dataframe = self.feature_in_dataframe.join(rollp)
        self.feature_in_dataframe = self.feature_in_dataframe.join(rollc)

        # if context_mode == 1:
        #     rollp = self.feature_in_dataframe.rolling(window=15, min_periods=1).mean()
        #     # rollp[rollp.columns] = robust_scale(rollp, quantile_range=(5, 95))
        #     rollp = rollp.add_suffix("_p2min_norm")
        #     self.feature_in_dataframe = self.feature_in_dataframe.join(rollp)

        #######################################################################
        # TEMPORAL + METADATA FEATURES AND EXPORT
        #######################################################################

        # Add temporal features
        epochs = self.raw_eeg.shape[0]
        times = np.arange(0, epochs, 1) * 15

        self.feature_in_dataframe["time_hour"] = times / 3600
        self.feature_in_dataframe["time_norm"] = times / times[-1]

        if self.person_info is not None:
            for c in self.person_info.keys():
                self.feature_in_dataframe[c] = self.person_info[c]


        # Sort the column names here (same behavior as lightGBM)
        self.feature_in_dataframe.sort_index(axis=1, inplace=True)
        self.feature_name_ = self.feature_in_dataframe.columns.tolist()

    def generate_other_feature(self, freqs, psd, epochs):
        freq_broad = (0.4, 75)
        idx_broad = np.logical_and(freqs >= freq_broad[0], freqs <= freq_broad[1])
        dx = freqs[1] - freqs[0]
        # Calculate entropy and fractal dimension features

        other_features = {
            "abspow": np.trapz(psd[:, idx_broad], dx=dx),
            "perm": np.apply_along_axis(ant.perm_entropy, axis=1, arr=epochs, normalize=True),
            "higuchi": np.apply_along_axis(ant.higuchi_fd, axis=1, arr=epochs),
            "petrosian": ant.petrosian_fd(epochs, axis=1)
        }

        return other_features




    def generate_freq_feature(self, welch_window=5):
        win = int(welch_window * self.sf_eeg)
        kwargs_welch = dict(window="hamming", nperseg=win, average="median")
        freqs, psd = sp_sig.welch(self.raw_eeg, self.sf_eeg, **kwargs_welch)

        feature = {}

        bp = self.bandpower_from_psd_ndarray(psd, freqs, relative=False)
        for j, (_, _, b) in enumerate(self.bands):
            feature[b] = bp[j]

        # zscore(a, axis=0, ddof=0, nan_policy='propagate')

        delta = feature["delta"]
        # band_ratio = {
        #     "dt": delta / feature["theta"],
        #     "ds": delta / feature["sigma"],
        #     "db": delta / feature["beta"],
        #     "at": feature["alpha"] / feature["theta"],
        # }
        band_ratio = {
            "dt": feature["delta"] / feature["theta"],
            "dn": feature["delta"] / feature["n_wave"],
            "dr": feature["delta"] / feature["rem_wave"],
            "ds": feature["delta"] / feature["sigma"],
            "db": feature["delta"] / feature["beta"],
            "da": feature["delta"] / feature["alpha"],
            "at": feature["alpha"] / feature["theta"],
            "as": feature["alpha"] / feature["sigma"],
            "ar": feature["alpha"] / feature["rem_wave"],
            "ab": feature["alpha"] / feature["beta"],
            "rn": feature["rem_wave"] / feature["n_wave"],
            "gr": feature["gama"] / feature["rem_wave"],
            "gn": feature["gama"] / feature["n_wave"],
            "g3n": feature["gama3"] / feature["n_wave"],
            "g3a": feature["gama3"] / feature["alpha"],
            "g3b": feature["gama3"] / feature["beta"],
            "g3t": feature["gama3"] / feature["theta"],
            "g3r": feature["gama3"] / feature["rem_wave"],
            "g3d": feature["gama3"] / feature["delta"],
            "sp2d": feature["sp_wave2"] / feature["delta"],
            "sp2a": feature["sp_wave2"] / feature["alpha2"],
            "sp2r": feature["sp_wave2"] / feature["rem_wave3"],
        }

        feature.update(band_ratio)
        # feature = band_ratio

        return feature, freqs, psd

    def generate_statistic_feature(self, raw_eeg):
        hmob, hcomp = ant.hjorth_params(raw_eeg, axis=1)
        feat = {
            "std": np.std(raw_eeg, ddof=1, axis=1),
            "iqr": sp_stats.iqr(raw_eeg, rng=(25, 75), axis=1),
            "skew": sp_stats.skew(raw_eeg, axis=1),
            "kurt": sp_stats.kurtosis(raw_eeg, axis=1),
            "nzc": ant.num_zerocross(raw_eeg, axis=1),
            "hmob": hmob,
            "hcomp": hcomp,
        }

        return feat

    def generate_acc_feature(self, raw_acc):
        abs_acc = np.abs(raw_acc)
        # abs_acc_avg = np.average(abs_acc, axis=2)
        # abs_acc_std = np.std(abs_acc, axis=2)
        # feat = {"x_abs_avg": abs_acc_avg[:, 0],
        #         "y_abs_avg": abs_acc_avg[:, 1],
        #         "z_abs_avg": abs_acc_avg[:, 2],
        #         "x_abs_std": abs_acc_std[:, 0],
        #         "y_abs_std": abs_acc_std[:, 1],
        #         "z_abs_std": abs_acc_std[:, 2]
        #         }
        feat = {}
        max_channel = np.zeros([abs_acc.shape[0], abs_acc.shape[2]])
        max_channel[(abs_acc[:, 0, :] > abs_acc[:, 1, :]) & (abs_acc[:, 0, :] > abs_acc[:, 2, :])] = 1
        feat["x_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        max_channel = np.zeros([abs_acc.shape[0], abs_acc.shape[2]])
        max_channel[(abs_acc[:, 1, :] > abs_acc[:, 2, :]) & (abs_acc[:, 1, :] > abs_acc[:, 0, :])] = 1
        feat["y_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        max_channel = np.zeros([abs_acc.shape[0], abs_acc.shape[2]])
        max_channel[(abs_acc[:, 2, :] > abs_acc[:, 1, :]) & (abs_acc[:, 2, :] > abs_acc[:, 0, :])] = 1
        feat["z_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        diff_acc_x = np.abs(raw_acc[:, 0, 1:-2] - raw_acc[:, 0, 2:-1])
        diff_acc_y = np.abs(raw_acc[:, 1, 1:-2] - raw_acc[:, 1, 2:-1])
        diff_acc_z = np.abs(raw_acc[:, 2, 1:-2] - raw_acc[:, 2, 2:-1])
        diff_acc = diff_acc_z + diff_acc_y + diff_acc_x
        # feat["diff_sum"] = np.sum(diff_acc, axis=1)
        feat["diff_avg"] = np.average(diff_acc, axis=1)
        feat["diff_std"] = np.std(diff_acc, axis=1)
        diff_global_avg = np.average(diff_acc)
        diff_global_std = np.std(diff_acc)
        feat["diff_avg_ratio"] = feat["diff_avg"] / diff_global_avg
        feat["diff_std_ratio"] = feat["diff_std"] / diff_global_std

        feat["diff_iqr"] = sp_stats.iqr(diff_acc, rng=(25, 75), axis=1)
        feat["diff_median"] = np.median(diff_acc, axis=1)

        max_channel = np.zeros(diff_acc.shape)
        max_channel[(diff_acc_x > diff_acc_y) & (diff_acc_x > diff_acc_z)] = 1
        feat["x_diff_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        max_channel = np.zeros(diff_acc.shape)
        max_channel[(diff_acc_y > diff_acc_x) & (diff_acc_y > diff_acc_z)] = 1
        feat["y_diff_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        max_channel = np.zeros(diff_acc.shape)
        max_channel[(diff_acc_z > diff_acc_x) & (diff_acc_z > diff_acc_y)] = 1
        feat["z_diff_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        return feat

    # def generate_biomarker_features(self, raw_eeg, sf):
    #     epoch = raw_eeg.shape[0]
    #     raw_eeg = np.reshape(raw_eeg, [raw_eeg.shape[0] * raw_eeg.shape[1]])
    #
    #     sp = spindles_detect(raw_eeg, sf, duration=(0.4, 2))
    #     os = sw_detect(raw_eeg, sf)
    #
    #     sp = (sp["Start_Index"] // (sf * 15)).value_counts()
    #     os = (os["StartIndex"] // (sf * 15)).value_counts()
    #
    #     sp_counts = np.zeros(epoch)
    #     sp_counts[sp.index] = sp.values
    #     os_counts = np.zeros(epoch)
    #     os_counts[os.index] = os.values
    #
    #     feat = {}
    #     feat["spindles"] = sp_counts
    #     feat["slow_waves"] = os_counts
    #
    #     return feat

    def get_features(self):
        if not hasattr(self, "feature_in_dataframe"):
            self.fit()
        return self.feature_in_dataframe.copy()

    def bandpower_from_psd_ndarray(self, psd, freqs, relative=True):
        """Compute bandpowers in N-dimensional PSD.

        This is a NumPy-only implementation of the :py:func:`yasa.bandpower_from_psd` function,
        which supports 1-D arrays of shape (n_freqs), or N-dimensional arays (e.g. 2-D (n_chan,
        n_freqs) or 3-D (n_chan, n_epochs, n_freqs))

        .. versionadded:: 0.2.0

        Parameters
        ----------
        psd : :py:class:`numpy.ndarray`
            Power spectral density of data, in uV^2/Hz. Must be a N-D array of shape (..., n_freqs).
            See :py:func:`scipy.signal.welch` for more details.
        freqs : :py:class:`numpy.ndarray`
            Array of frequencies. Must be a 1-D array of shape (n_freqs,)
        bands : list of tuples
            List of frequency bands of interests. Each tuple must contain the lower and upper
            frequencies, as well as the band name (e.g. (0.5, 4, 'Delta')).
        relative : boolean
            If True, bandpower is divided by the total power between the min and
            max frequencies defined in ``band`` (default 0.5 to 40 Hz).

        Returns
        -------
        bandpowers : :py:class:`numpy.ndarray`
            Bandpower array of shape *(n_bands, ...)*.
        """
        # Type checks
        assert isinstance(self.bands, list), "bands must be a list of tuple(s)"
        assert isinstance(relative, bool), "relative must be a boolean"

        # Safety checks
        freqs = np.asarray(freqs)
        psd = np.asarray(psd)
        assert freqs.ndim == 1, "freqs must be a 1-D array of shape (n_freqs,)"
        assert psd.shape[-1] == freqs.shape[-1], "n_freqs must be last axis of psd"

        # Extract frequencies of interest
        all_freqs = np.hstack([[b[0], b[1]] for b in self.bands])
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
        bp = np.zeros((len(self.bands), *psd.shape[:-1]), dtype=np.float64)

        # Enumerate over the frequency bands
        labels = []
        for i, band in enumerate(self.bands):
            b0, b1, la = band
            labels.append(la)
            idx_band = np.logical_and(freqs >= b0, freqs <= b1)
            bp[i] = simps(psd[..., idx_band], dx=res, axis=-1)

        if relative:
            bp /= total_power

        all_freqs = all_freqs.reshape(-1, 2)
        total_bands = all_freqs[:, 1] - all_freqs[:, 0]
        total_bands = total_bands[..., np.newaxis]
        bp /= total_bands
        return bp



class WearDectectFeature:
    # bands = [
    #     (0.4, 1, "sdelta"),
    #     (1, 4, "fdelta"),
    #     (0.4, 4, "delta"),
    #     (4, 8, "theta"),
    #     (8, 12, "alpha"),
    #     (12, 16, "sigma"),
    #     (16, 30, "beta"),
    # ]

    bands = [
        (1, 2, "sdelta"),
        (0, 4, "delta"),
        (1, 4, "fdelta"),
        (2, 3, "delta4"),

        (4, 8, "theta"),
        (4, 6, "theta2"),

        (4, 12, "n_wave"),
        (4, 10, "n_wave2"),

        (8, 12, "alpha"),
        (8, 10, "alpha2"),

        (12, 16, "sigma"),
        (12, 20, "sigma2"),
        (14, 18, "sigma3"),

        (12, 24, "rem_wave3"),
        (12, 30, "rem_wave"),
        (10, 16, "rem_wave2"),

        (16, 30, "beta"),
        (16, 23, "beta2"),
        (23, 30, "beta3"),

        (30, 35, "gama0"),
        (35, 49, "gama"),
        (49, 51, "gama2"),
        (51, 60, "gama3"),
        (60, 75, "gama4"),

        (49, 51, "noise1"),
        (99, 101, "noise2"),
        (149, 151, "noise3"),
        (199, 201, "noise4"),
        (19, 21, "noise5"),
        (29, 31, "noise6"),
        (39, 41, "noise7"),
    ]

    def __init__(self, person_info, raw_eeg, sf_eeg=500, raw_acc=None, sf_acc=50, context_mode=1, data_type=0):
        super().__init__()
        self.feature_name_ = None
        self.raw_eeg = raw_eeg
        self.sf_eeg = sf_eeg
        self.raw_acc = raw_acc
        self.sf_acc = sf_acc
        self.feature_in_dataframe = None
        self.person_info = person_info

        self.fit(context_mode, data_type)

    def fit(self, context_mode, data_type):
        feature = {}

        freq_feature, freqs, psd = self.generate_freq_feature(welch_window=1)
        feature.update(freq_feature)

        statistic_feature = self.generate_statistic_feature(self.raw_eeg, context_mode=context_mode)
        feature.update(statistic_feature)

        other_feature = self.generate_other_feature(freqs, psd, self.raw_eeg, context_mode=context_mode)
        feature.update(other_feature)

        self.feature_in_dataframe = pd.DataFrame(feature).add_prefix("eeg_")
        if self.raw_acc is not None:
            acc_feature = self.generate_acc_feature(raw_acc=self.raw_acc)
            acc_feature_in_dataframe = pd.DataFrame(acc_feature).add_prefix("acc_")
            self.feature_in_dataframe = self.feature_in_dataframe.join(acc_feature_in_dataframe)

        self.feature_in_dataframe.index.name = "epoch"

        # Apply centered rolling average (15 epochs = 7 min 30)
        # Triang: [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.,
        #          0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125]
        if context_mode == 2:
            rollc = self.feature_in_dataframe.rolling(window=25, center=True, min_periods=1, win_type="triang").mean()
            rollc[rollc.columns] = robust_scale(rollc, quantile_range=(5, 95))
            rollc = rollc.add_suffix("_c6min_norm")

            # Now look at the past 2 minutes
            rollp = self.feature_in_dataframe.rolling(window=15, min_periods=1).mean()
            rollp[rollp.columns] = robust_scale(rollp, quantile_range=(5, 95))
            rollp = rollp.add_suffix("_p2min_norm")
            self.feature_in_dataframe = self.feature_in_dataframe.join(rollp)
            self.feature_in_dataframe = self.feature_in_dataframe.join(rollc)

        if context_mode == 1:
            rollp = self.feature_in_dataframe.rolling(window=15, min_periods=1).mean()
            # rollp[rollp.columns] = robust_scale(rollp, quantile_range=(5, 95))
            rollp = rollp.add_suffix("_p2min_norm")
            self.feature_in_dataframe = self.feature_in_dataframe.join(rollp)

        if context_mode == 3:
            pass

        #######################################################################
        # TEMPORAL + METADATA FEATURES AND EXPORT
        #######################################################################

        # Add temporal features
        epochs = self.raw_eeg.shape[0]
        times = np.arange(0, epochs, 1) * 5

        self.feature_in_dataframe["time_hour"] = times / 3600
        self.feature_in_dataframe["time_norm"] = times / times[-1]

        if self.person_info is not None:
            for c in self.person_info.keys():
                self.feature_in_dataframe[c] = self.person_info[c]

        self.feature_in_dataframe["data_type"] = data_type

        # Sort the column names here (same behavior as lightGBM)
        self.feature_in_dataframe.sort_index(axis=1, inplace=True)
        self.feature_name_ = self.feature_in_dataframe.columns.tolist()

    def generate_other_feature(self, freqs, psd, epochs, context_mode):
        freq_broad = (0, 210)
        idx_broad = np.logical_and(freqs >= freq_broad[0], freqs <= freq_broad[1])
        dx = freqs[1] - freqs[0]
        # Calculate entropy and fractal dimension features
        if context_mode == 2:
            other_features = {
                "abspow": np.trapz(psd[:, idx_broad], dx=dx),
                "perm": np.apply_along_axis(ant.perm_entropy, axis=1, arr=epochs, normalize=True),
                "higuchi": np.apply_along_axis(ant.higuchi_fd, axis=1, arr=epochs),
                "petrosian": ant.petrosian_fd(epochs, axis=1)
            }
        elif context_mode == 1 or context_mode == 3:
            other_features = {
                "abspow": np.trapz(psd[:, idx_broad], dx=dx),
                # "perm": np.apply_along_axis(ant.perm_entropy, axis=1, arr=epochs, normalize=True),
                # "higuchi": np.apply_along_axis(ant.higuchi_fd, axis=1, arr=epochs),
                "petrosian": ant.petrosian_fd(epochs, axis=1)
            }
        return other_features

    def generate_freq_feature(self, welch_window=1):
        win = int(welch_window * self.sf_eeg)
        kwargs_welch = dict(window="hamming", nperseg=win, average="median")
        freqs, psd = sp_sig.welch(self.raw_eeg, self.sf_eeg, **kwargs_welch)

        feature = {}

        bp = self.bandpower_from_psd_ndarray(psd, freqs, relative=False)
        for j, (_, _, b) in enumerate(self.bands):
            feature[b] = bp[j]

        # zscore(a, axis=0, ddof=0, nan_policy='propagate')

        delta = feature["delta"]
        # band_ratio = {
        #     "dt": delta / feature["theta"],
        #     "ds": delta / feature["sigma"],
        #     "db": delta / feature["beta"],
        #     "at": feature["alpha"] / feature["theta"],
        # }
        band_ratio = {
            "dt": feature["delta"] / feature["theta"] ,
            "dn": feature["delta"] / feature["n_wave"] ,
            "dr": feature["delta"] / feature["rem_wave"] ,
            "ds": feature["delta"] / feature["sigma"] ,
            "db": feature["delta"] / feature["beta"] ,
            "da": feature["delta"] / feature["alpha"] ,
            "at": feature["alpha"] / feature["theta"] ,
            "as": feature["alpha"] / feature["sigma"] ,
            "ar": feature["alpha"] / feature["rem_wave"] ,
            "ab": feature["alpha"] / feature["beta"] ,
            "rn": feature["rem_wave"] / feature["n_wave"],
            "gr": feature["gama"] / feature["rem_wave"],
            "gn": feature["gama"] / feature["n_wave"] ,
            "g3n": feature["gama3"] / feature["n_wave"],
            "g3a": feature["gama3"] / feature["alpha"],
            "g3b": feature["gama3"] / feature["beta"] ,
            "g3t": feature["gama3"] / feature["theta"],
            "g3r": feature["gama3"] / feature["rem_wave"],
            "g3d": feature["gama3"] / feature["delta"] ,
        }


        feature.update(band_ratio)
        # feature = band_ratio

        return feature, freqs, psd

    def generate_statistic_feature(self, raw_eeg, context_mode):
        if context_mode == 2:
            hmob, hcomp = ant.hjorth_params(raw_eeg, axis=1)
            feat = {
                "std": np.std(raw_eeg, ddof=1, axis=1),
                "iqr": sp_stats.iqr(raw_eeg, rng=(25, 75), axis=1),
                "skew": sp_stats.skew(raw_eeg, axis=1),
                "kurt": sp_stats.kurtosis(raw_eeg, axis=1),
                "nzc": ant.num_zerocross(raw_eeg, axis=1),
                "hmob": hmob,
                "hcomp": hcomp,
            }
        elif context_mode == 1 or context_mode == 3:
            feat = {
                "std": np.std(raw_eeg, ddof=1, axis=1),
                "iqr": sp_stats.iqr(raw_eeg, rng=(25, 75), axis=1),
                "skew": sp_stats.skew(raw_eeg, axis=1),
                "kurt": sp_stats.kurtosis(raw_eeg, axis=1),
                "nzc": ant.num_zerocross(raw_eeg, axis=1),
            }
        return feat

    def generate_acc_feature(self, raw_acc):
        abs_acc = np.abs(raw_acc)
        # abs_acc_avg = np.average(abs_acc, axis=2)
        # abs_acc_std = np.std(abs_acc, axis=2)
        # feat = {"x_abs_avg": abs_acc_avg[:, 0],
        #         "y_abs_avg": abs_acc_avg[:, 1],
        #         "z_abs_avg": abs_acc_avg[:, 2],
        #         "x_abs_std": abs_acc_std[:, 0],
        #         "y_abs_std": abs_acc_std[:, 1],
        #         "z_abs_std": abs_acc_std[:, 2]
        #         }
        feat = {}
        max_channel = np.zeros([abs_acc.shape[0], abs_acc.shape[2]])
        max_channel[(abs_acc[:, 0, :] > abs_acc[:, 1, :]) & (abs_acc[:, 0, :] > abs_acc[:, 2, :])] = 1
        feat["x_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        max_channel = np.zeros([abs_acc.shape[0], abs_acc.shape[2]])
        max_channel[(abs_acc[:, 1, :] > abs_acc[:, 2, :]) & (abs_acc[:, 1, :] > abs_acc[:, 0, :])] = 1
        feat["y_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        max_channel = np.zeros([abs_acc.shape[0], abs_acc.shape[2]])
        max_channel[(abs_acc[:, 2, :] > abs_acc[:, 1, :]) & (abs_acc[:, 2, :] > abs_acc[:, 0, :])] = 1
        feat["z_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        diff_acc_x = np.abs(raw_acc[:, 0, 1:-2] - raw_acc[:, 0, 2:-1])
        diff_acc_y = np.abs(raw_acc[:, 1, 1:-2] - raw_acc[:, 1, 2:-1])
        diff_acc_z = np.abs(raw_acc[:, 2, 1:-2] - raw_acc[:, 2, 2:-1])
        diff_acc = diff_acc_z + diff_acc_y + diff_acc_x
        # feat["diff_sum"] = np.sum(diff_acc, axis=1)
        feat["diff_avg"] = np.average(diff_acc, axis=1)
        feat["diff_std"] = np.std(diff_acc, axis=1)
        diff_global_avg = np.average(diff_acc)
        diff_global_std = np.std(diff_acc)
        feat["diff_avg_ratio"] = feat["diff_avg"] / diff_global_avg
        feat["diff_std_ratio"] = feat["diff_std"] / diff_global_std

        feat["diff_iqr"] = sp_stats.iqr(diff_acc, rng=(25, 75), axis=1)
        feat["diff_median"] = np.median(diff_acc, axis=1)

        max_channel = np.zeros(diff_acc.shape)
        max_channel[(diff_acc_x > diff_acc_y) & (diff_acc_x > diff_acc_z)] = 1
        feat["x_diff_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        max_channel = np.zeros(diff_acc.shape)
        max_channel[(diff_acc_y > diff_acc_x) & (diff_acc_y > diff_acc_z)] = 1
        feat["y_diff_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        max_channel = np.zeros(diff_acc.shape)
        max_channel[(diff_acc_z > diff_acc_x) & (diff_acc_z > diff_acc_y)] = 1
        feat["z_diff_max_percentage"] = np.sum(max_channel, axis=1) / max_channel.shape[1]

        return feat

    def get_features(self):
        if not hasattr(self, "feature_in_dataframe"):
            self.fit()
        return self.feature_in_dataframe.copy()

    def bandpower_from_psd_ndarray(self, psd, freqs, relative=True):
        """Compute bandpowers in N-dimensional PSD.

        This is a NumPy-only implementation of the :py:func:`yasa.bandpower_from_psd` function,
        which supports 1-D arrays of shape (n_freqs), or N-dimensional arays (e.g. 2-D (n_chan,
        n_freqs) or 3-D (n_chan, n_epochs, n_freqs))

        .. versionadded:: 0.2.0

        Parameters
        ----------
        psd : :py:class:`numpy.ndarray`
            Power spectral density of data, in uV^2/Hz. Must be a N-D array of shape (..., n_freqs).
            See :py:func:`scipy.signal.welch` for more details.
        freqs : :py:class:`numpy.ndarray`
            Array of frequencies. Must be a 1-D array of shape (n_freqs,)
        bands : list of tuples
            List of frequency bands of interests. Each tuple must contain the lower and upper
            frequencies, as well as the band name (e.g. (0.5, 4, 'Delta')).
        relative : boolean
            If True, bandpower is divided by the total power between the min and
            max frequencies defined in ``band`` (default 0.5 to 40 Hz).

        Returns
        -------
        bandpowers : :py:class:`numpy.ndarray`
            Bandpower array of shape *(n_bands, ...)*.
        """
        # Type checks
        assert isinstance(self.bands, list), "bands must be a list of tuple(s)"
        assert isinstance(relative, bool), "relative must be a boolean"

        # Safety checks
        freqs = np.asarray(freqs)
        psd = np.asarray(psd)
        assert freqs.ndim == 1, "freqs must be a 1-D array of shape (n_freqs,)"
        assert psd.shape[-1] == freqs.shape[-1], "n_freqs must be last axis of psd"

        # Extract frequencies of interest
        all_freqs = np.hstack([[b[0], b[1]] for b in self.bands])
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
        bp = np.zeros((len(self.bands), *psd.shape[:-1]), dtype=np.float64)

        # Enumerate over the frequency bands
        labels = []
        for i, band in enumerate(self.bands):
            b0, b1, la = band
            labels.append(la)
            idx_band = np.logical_and(freqs >= b0, freqs <= b1)
            bp[i] = simps(psd[..., idx_band], dx=res, axis=-1)

        if relative:
            bp /= total_power

        all_freqs = all_freqs.reshape(-1, 2)
        total_bands = all_freqs[:, 1] - all_freqs[:, 0]
        total_bands = total_bands[..., np.newaxis]
        bp /= total_bands
        return bp