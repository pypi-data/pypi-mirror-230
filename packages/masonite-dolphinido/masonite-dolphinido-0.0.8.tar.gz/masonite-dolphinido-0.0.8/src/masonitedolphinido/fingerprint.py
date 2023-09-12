import hashlib
import numpy
import matplotlib.mlab as mlab
from typing import List
from scipy.ndimage import maximum_filter
from scipy.ndimage import (generate_binary_structure, iterate_structure, binary_erosion)
from operator import itemgetter
from masonitedolphinido import settings as config

class Fingerprint:
    
    def fingerprint(self, samples: List[int],
                            Fs=config.DEFAULT_FS,
                            wsize=config.DEFAULT_WINDOW_SIZE,
                            wratio=config.DEFAULT_OVERLAP_RATIO,
                            fan_value=config.DEFAULT_FAN_VALUE,
                            amp_min=config.DEFAULT_AMP_MIN):

        # FFT the channel, log transform output, find local maxima, then return
        # locally sensitive hashes.
        # FFT the signal and extract frequency components

        # plot the angle spectrum of segments within the signal in a colormap
        arr2D = mlab.specgram(
            samples,
            NFFT=wsize,
            Fs=Fs,
            window=mlab.window_hanning,
            noverlap=int(wsize * wratio))[0]

        # apply log transform since spec-gram() returns linear array
        arr2D = 10 * numpy.log10(arr2D, where=arr2D > 0)  # calculates the base 10 logarithm for all elements of arr2D
        arr2D[arr2D == -numpy.inf] = 0  # replace with zeros

        # find local maxima
        local_maxima = self.__get_2D_peaks(arr2D, amp_min=amp_min)

        # return hashes
        return self.__generate_hashes(local_maxima, fan_value=fan_value)

    @staticmethod
    def __get_2D_peaks(arr2D, amp_min=config.DEFAULT_AMP_MIN):


        struct = generate_binary_structure(2, 1)
        neighborhood = iterate_structure(struct, config.PEAK_NEIGHBORHOOD_SIZE)

        # find local maxima using our filter shape
        local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
        background = (arr2D == 0)
        eroded_background = binary_erosion(background, structure=neighborhood,
                                           border_value=1)
        # Boolean mask of arr2D with True at peaks
        detected_peaks = local_max ^ eroded_background

        # extract peaks
        amps = arr2D[detected_peaks]
        j, i = numpy.where(detected_peaks)

        # filter peaks
        amps = amps.flatten()
        peaks = list(zip(i, j, amps))
        peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

        # get indices for frequency and time
        frequency_idx = [x[1] for x in peaks_filtered]
        time_idx = [x[0] for x in peaks_filtered]

        return list(zip(frequency_idx, time_idx))

    @staticmethod
    def __generate_hashes(peaks, fan_value=config.DEFAULT_FAN_VALUE):

        if config.PEAK_SORT:
            peaks.sort(key=itemgetter(1))

        # bruteforce all peaks
        for i in range(len(peaks)):
            for j in range(1, fan_value):
                if (i + j) < len(peaks):

                    # take current & next peak frequency value
                    freq1 = peaks[i][config.IDX_FREQ_I]
                    freq2 = peaks[i + j][config.IDX_FREQ_I]

                    # take current & next -peak time offset
                    t1 = peaks[i][config.IDX_TIME_J]
                    t2 = peaks[i + j][config.IDX_TIME_J]

                    # get diff of time offsets
                    t_delta = t2 - t1

                    # check if delta is between min & max
                    if config.MIN_HASH_TIME_DELTA <= t_delta <= config.MAX_HASH_TIME_DELTA:
                        string_of_data = f"%s|%s|%s" % (str(freq1), str(freq2), str(t_delta))
                        hashing = hashlib.sha256(string_of_data.encode('utf-8'))
                        digest = hashing.hexdigest()[0:config.FINGERPRINT_REDUCTION]
                        offset = int.from_bytes(t1, 'little')
                        yield digest, offset

