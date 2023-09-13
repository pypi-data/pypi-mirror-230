import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import uproot
import time
import cppimport as cpi
funcs = cpi.imp("wrap")

ch1_low_cut = 9182.09
ch1_high_cut = 11147.9
ch0_low_cut = 2460.48
ch0_high_cut = 3375.7606
# window = 0.096*10**6 # in pico seconds
window = 15*1000

key = ['Timestamp', 'Energy', 'Flags']
# paths = ["C:\\Users\\chloe\\OneDrive - McGill University\\Coincidence Testing\\Summer 2023 - CoMPASS\\DAQ\\run3\\RAW\\DataR_eq2611@DT5751_1989_run3.root", "C:\\Users\\chloe\\OneDrive - McGill University\\Coincidence Testing\\Summer 2023 - CoMPASS\\DAQ\\run3\\RAW\\DataR_eq2432@DT5751_1989_run3.root"]
# filtered_paths = ["FILTERED\\\\DataF_CH0@DT5751_1989_Co60-EQ2611-20-CFD.root", "FILTERED\\\\DataF_CH1@DT5751_1989_Co60-EQ2611-20-CFD.root"]

# files = [uproot.open(path) for path in paths]
# trees = [root["Data_R"] for root in files]
# data = [tree.arrays(key, library="np") for tree in trees]

# filtered_files = [uproot.open(path) for path in filtered_paths]
# filtered_trees = [root["Data_F"] for root in filtered_files]
# filtered_data = [tree.arrays(key, library="np") for tree in filtered_trees]

def get_unfiltered(data):
    indexes = np.where(data['Flags'] == 16384)[0]
    timestamps = data['Timestamp'][indexes]
    energies = data['Energy'][indexes]
    flags = data['Flags'][indexes]
    return pd.DataFrame({'Timestamp':timestamps, 'Energy':energies, 'Flags':flags})

def get_selection_index(data, start, stop):
    indexes = np.where((start <= data) & (data <= stop))[0]
    return indexes

# unfiltered_ch0 = get_unfiltered(data[0])
# unfiltered_ch1 = get_unfiltered(data[1])

# ENERGY_CH0 = unfiltered_ch0['Energy'][get_selection_index(unfiltered_ch0['Energy'], ch0_low_cut, ch0_high_cut)]
# ENERGY_CH1 = unfiltered_ch1['Energy'][get_selection_index(unfiltered_ch1['Energy'], ch1_low_cut, ch1_high_cut)]

# TIME_CH0 = unfiltered_ch0['Timestamp'][get_selection_index(unfiltered_ch0['Energy'], ch0_low_cut, ch0_high_cut)]
# TIME_CH1 = unfiltered_ch1['Timestamp'][get_selection_index(unfiltered_ch1['Energy'], ch1_low_cut, ch1_high_cut)]

# TIME_CH0 = np.array(list(TIME_CH0))
# TIME_CH1 = np.array(list(TIME_CH1))

# print(len(TIME_CH0), len(TIME_CH1))
# time_start = time.time()

# for index, time in enumerate(TIME_CH1):
#     diffs = np.abs(TIME_CH0 - time)
#     indexes = np.where(diffs <= window)[0]
#     if len(indexes) != 0:
#         start.append(time)
#         stop.append(TIME_CH0[indexes[0]])
#     print(len(start), len(stop))

# start, stop = funcs.TOF(TIME_CH1, TIME_CH0, window)
# time_stop = time.time()
# print(time_stop - time_start)
# print(len(start))

# diffs = (stop - start)*10**(-3)
# hist = np.histogram(diffs, bins=8192)


# x = hist[1][1:]
# y = hist[0]
# plt.plot(x,y, drawstyle='steps-mid')
# plt.show()