from lm_datahandler.postprocess.label_smooth import pp_label_smooth
import numpy as np


def tst_compute(hypno, epoch_length):
    """
    compute total sleep time from hypno
    :param hypno: sleep stage
    :param epoch_length: seconds per epoch
    :return: tst: total sleep time
    """
    copy = hypno.copy()
    is_sleep = np.zeros(copy.shape)
    is_sleep[copy < 3] = 1
    sleep_epoch_count = np.sum(is_sleep)

    return sleep_epoch_count * epoch_length


def sl_compute(hypno, epoch_length):
    """
    从记录开始，到第一次进入长时间睡眠(30分钟以上，且中间清醒时间少于3分钟)开始的时间
    前期若存在短时睡眠则忽略
    :param hypno: sleep stage
    :param epoch_length: seconds per epoch
    :return sl: sleep latency
    """
    index = -1
    copy = hypno.copy()
    copy[hypno >= 3] = 1
    copy[hypno < 3] = 0

    for i in range(hypno.shape[0] - 30 * 4):
        score = np.sum(copy[i:i + 30 * 4])
        if score < 3 * 4:
            index = i
            break

    while index < hypno.shape[0] - 5 * 4 and np.sum(copy[index:index + 5 * 4]) > 0:
        index += 1

    return -1 if index < 0 else index * epoch_length


def get_up_time_compute(hypno, epoch_length):
    copy = hypno.copy()
    copy = np.asarray(copy).tolist()
    copy.reverse()

    index = sl_compute(np.asarray(copy), epoch_length)


    return -1 if index < 0 else index


def waso_compute(hypno, epoch_length, sleep_range=None):
    """
    :param hypno: sleep stage
    :param epoch_length: seconds per epoch
    :return: waso: awake time during sleep
    """

    if sleep_range is None:
        first_sleep_time = sl_compute(hypno, epoch_length)
        if first_sleep_time == -1:
            return -1
        last_sleep_time = get_up_time_compute(hypno, epoch_length)
    else:
        first_sleep_time = sleep_range[0]
        first_sleep_time = int(first_sleep_time / epoch_length)
        last_sleep_time = sleep_range[1]
        last_sleep_time = int(last_sleep_time / epoch_length)

    sleep_hypno = hypno[first_sleep_time:last_sleep_time]
    sleep_hypno = sleep_hypno.copy()
    sleep_hypno = pp_label_smooth(sleep_hypno, window=5)
    sleep_hypno[sleep_hypno < 3] = 0
    sleep_hypno[sleep_hypno == 3] = 1
    arousal_time = np.sum(sleep_hypno)

    return arousal_time * epoch_length


def se_compute(hypno):
    """
    :param hypno: sleep stage
    :return: se: sleep efficiency
    """
    copy = hypno.copy()
    is_sleep = np.zeros(hypno.shape)
    is_sleep[copy < 3] = 1
    sleep_epoch_count = np.sum(is_sleep)

    return sleep_epoch_count / hypno.shape[0]


def arousal_time_compute(hypno, epoch_length, sleep_range=None):
    """
    :param hypno: sleep stage
    :return: arousal_time: awake time during sleep
    """
    copy = np.copy(hypno)
    hypno_smooth = pp_label_smooth(copy, window=5)


    if sleep_range is None:
        first_sleep_time = sl_compute(hypno, epoch_length)
        if first_sleep_time == -1:
            return -1
        last_sleep_time = get_up_time_compute(hypno, epoch_length)
    else:
        first_sleep_time = sleep_range[0]
        last_sleep_time = sleep_range[1]
    first_sleep_time = int(first_sleep_time / epoch_length)

    last_sleep_time = len(hypno) - int(last_sleep_time / epoch_length)

    sleep_hypno = hypno_smooth[first_sleep_time:last_sleep_time]
    sleep_hypno = sleep_hypno.copy()
    sleep_hypno[sleep_hypno < 3] = 0
    sleep_hypno[sleep_hypno == 3] = 1
    arousal_count = sleep_hypno[1:] - sleep_hypno[0:-1]
    arousal_count = np.where(arousal_count == 1)[0]
    arousal_time = np.where(sleep_hypno == 1)[0]
    return arousal_count.shape[0], first_sleep_time + arousal_time
