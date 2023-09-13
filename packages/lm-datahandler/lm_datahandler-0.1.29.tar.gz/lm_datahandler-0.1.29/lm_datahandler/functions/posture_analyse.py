import numpy as np
from scipy.io import loadmat
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

def sleep_posture_analyse(acc):
    acc_y = acc[1, :]
    acc_z = acc[2, :]

    cos = acc_z/np.sqrt(acc_z*acc_z + acc_y*acc_y)
    upper_grade = np.arccos(cos)
    grade = upper_grade*(acc_y/np.abs(acc_y))
    grade = savgol_filter(grade, window_length=50, polyorder=1)


    return grade


if __name__ == '__main__':
    acc = loadmat(r"E:\dataset\dev_test_data\20230612_15927226341\acc.mat")
    grade = sleep_posture_analyse(acc)
    plt.plot(grade)
    plt.show()
