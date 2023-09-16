import scipy.signal, numpy as np
import matplotlib.pyplot as plt
import lmfit, tempfile
# from lmfit import Parameters, fit_report, minimize
from numpy import arcsin, sin, pi
from matplotlib.lines import Line2D
import math, re, os
import sox
from subprocess import Popen, PIPE
from pathlib import Path
import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
}) # for sox  "output file already exists and will be overwritten on build"
from datetime import datetime, timezone, timedelta
from collections import deque
from loguru import logger
from sklearn.mixture import GaussianMixture
import ffmpeg, shutil
# import opentimelineio as otio
from rich import print

# try:
#     from cfuzzyset import cFuzzySet as FuzzySet
# except ImportError:
#     from fuzzyset import FuzzySet
# pip install fuzzyset2


CACHING = True

MAXDRIFT = 10e-3 # in sec, normally 10e-3 (10 ms)
# MAXDRIFT = 0 # in sec, normally 10e-3 (10 ms)

SAFE_SILENCE_WINDOW_WIDTH = 400 # ms, not the full 500 ms, to accommodate decay
# used in _get_silent_zone_indices()
WORDWIDTHFACTOR = 2
# see _get_word_width_parameters()

MINIMUM_LENGTH = 4 # sec
TRIAL_TIMES = [ # in seconds
            (0.5, -2),
            (0.5, -3.5),
            (2, -2),
            (2, -3.5)]
SOUND_EXTRACT_LENGTH = 1.56 # second
SYMBOL_LENGTH_TOLERANCE = 0.05 # relative
SAMD21_LATENCY = 63 # microseconds

################## pasted from FSKfreqCalculator.py output:
F1 = 630.00 # Hertz
F2 = 1190.00 # Hz , both from FSKfreqCalculator output
SYMBOL_LENGTH = 14.286 # ms, from FSKfreqCalculator.py
N_SYMBOLS_SAMD21 = 35 # including sync pulse
##################


try:
    layouts, _ = (
    ffmpeg.input('').output('')
    .global_args("-loglevel", "quiet","-nostats","-hide_banner","-layouts")
    .run(capture_stdout=True)
    )
except ffmpeg.Error as e:
    print('error',e.stderr)        



names_str, layouts = [l.split('\n') for l in 
    layouts.decode("utf-8").split('DECOMPOSITION')]
[names_str.pop(0) for i in range(2)]
[names_str.pop(-1) for i in range(3)]
layouts.pop(0)
layouts.pop(-1)
channel_name_regex = re.compile(r'(\w+)\s+(.+)')
layouts_regex = re.compile(r'(\S+)\s+(.+)')
FFMPEG_CHAN_NAMES = [
    channel_name_regex.match(name).group(1)
    for name in names_str
]
FFMPEG_LAYO_NAMES = dict([
    layouts_regex.match(lay_out).groups()
    for lay_out in layouts
])

"""
FFMPEG_CHAN_NAMES are the names used by ffmpeg for channels, eg: FL, FR, FC for
front left, front right and front center.
FFMPEG_LAYO_NAMES are the order of channels for each layout, eg: stereo is FL+FR
and 5.1 is FL+FR+FC+LFE+BL+BR. Layout names are the dict keys.
Run ffmpeg -layouts for details.

"""

# utility for accessing pathnames
def _pathname(tempfile_or_path):
    if isinstance(tempfile_or_path, type('')):
        return tempfile_or_path
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path)
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name
    else:
        raise Exception('%s should be Path or tempfile... is %s'%(
            tempfile_or_path,
            type(tempfile_or_path)))

def to_precision(x,p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """
    x = float(x)
    if x == 0.:
        return "0." + "0"*(p-1)
    out = []
    if x < 0:
        out.append("-")
        x = -x
    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)
    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)
    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1
    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1
    m = "%.*g" % (p, n)
    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return "".join(out)

class Decoder:
    """
    Object encapsulating DSP processes to demodulate YaLTC track from audio file;
    Decoders are instantiated by their respective Recording object. Produces
    plots on demand for diagnostic purposes.

    Attributes:
        sound_extract : numpy.ndarray of int16, shaped (N) 
            sound data extract, could be anywhere in the audio file (start, end, etc...)
            Set by Recording object. This audio signal might or might not be the YaLTC track.
        sound_extract_position : int
            where the sound_extract is located in the file, samples
        samplerate : int
            sound sample rate, set by Recording object.
        SN_ratio : float
            signal over noise ratio in dB.
        cached_convolution_fit : dict
            if _fit_trig_signal_to_convoluted_env() has already been called, will use cached
            values if sound_extract_position is the same. 

    """

    def __init__(self):
        """
        Initialises Decoder

        Returns
        -------
        an instance of Decoder.

        """
        self.sound_data_extract = None
        self.cached_convolution_fit = {'sound_extract_position': None}

    def set_sound_extract_and_sr(self, extract, s_r, where):
        self.sound_extract = extract
        self.samplerate = s_r
        self.sound_extract_position = where
        self.cached_convolution_fit = {'sound_extract_position': None}
        logger.debug('sound_extract set, samplerate %i location %i'%(s_r, where))
   

        # there's always at least one complete 0.5 silence interval in a 1.5 second signal

    def _get_envelope(self):
        """
        Compute self.sound_extract envelope, filtering its hilbert transform.
        Uses scipy.signal.hilbert() and scipy.signal.savgol_filter();
        window_length and polyorder savgol_filter() parameters values 
        have been found by hit and miss on audio data.

        maybe:
        Values are roughly normalized: between 0 and approximately 1.0

        Returns
        -------
        numpy.ndarray the same length of self.recording.sound_extract

        """
        WINDOW_LENGTH, POLYORDER = (15, 3) # parameters found by experiment, hit and miss
        abs_hil = np.abs(scipy.signal.hilbert(self.sound_extract))
        envelope = scipy.signal.savgol_filter(abs_hil,
                                              WINDOW_LENGTH, POLYORDER)

        # plt.plot(self.sound_extract)
        # plt.plot(abs_hil)
        # plt.plot(envelope)
        # plt.show()

        # mean = envelope.mean()
        # if mean: # in case of zero padding
        #     factor = 0.5/mean # since 50% duty cycle
        # else:
        #     factor = 1
        # return factor*envelope
        return envelope

    def _get_signal_level(self):
        abs_signal = abs(self.sound_extract)
        return 2 * abs_signal.mean() # since 50% duty cycle

    def _get_square_convolution(self):
        """
        Compute self.sound_extract envelope convolution with a square signal of
        0.5 second (+ SYMBOL_LENGTH) width, using numpy.convolve().
        Values are roughly normalized: between 0 and approximately 1.0


        Returns:
    
         #1 the normalized convolution, a numpy.ndarray shorter than 
             self.sound_extract, see numpy.convolve(..., mode='valid')

         #2 a list of int, samples indexes where the convolution is computed

        """
        sqr_window_width = int((0.5 + SYMBOL_LENGTH/1e3)*self.samplerate) # in samples
        sqr_signal = np.ones(sqr_window_width,dtype=int)
        envelope = self._get_envelope()
        mean = envelope.mean()
        if mean: # in case of zero padding (? dont remember why)
            factor = 0.5/mean # since 50% duty cycle
        else:
            factor = 1
        normalized_envelope = factor*envelope
        convol = np.convolve(normalized_envelope, sqr_signal,
                             mode='valid')/sqr_window_width
        start = int(sqr_window_width/2)

        x = range(start, len(convol) + start)
        return [*x], convol

    def _get_word_envelope(self, pulse_position):
        """
        Chop the signal envelope keeping the word region and smooth it over the
        longest BFSK period
        """
        max_period = int(self.samplerate*max(1/F1,1/F2))
        logger.debug('max BFSK period %i samples'%max_period)
        period_window = np.ones(max_period,dtype=int)/max_period
        envelope = self._get_envelope()
        symbol_width_samples = 1e-3*SYMBOL_LENGTH*self.samplerate
        word_start = int(pulse_position + 3*symbol_width_samples)
        word_end = int(pulse_position + 0.5*self.samplerate)
        word_end -= 2*symbol_width_samples # slide to the left a little
        logger.debug('word start, end: %i %i'%(word_start, word_end))
        w_envelope = envelope[word_start:int(word_end)]
        # plt.plot(w_envelope)
        # plt.show()
        return w_envelope
        # return np.convolve(w_envelope, period_window, mode='same')

    def _get_minimal_bfsk(self, pulse_position):
        """
        because of non-flat frequency response, bfsk bits dont have the same
        amplitude. This returns the least of both by detecting a bimodal
        gaussian distribution

        """
        # w_envelope = self._get_word_envelope(pulse_position)
        # word_start = int(min_position + shift + 0.3*self.samplerate)
        # word = w_envelope[word_start :  int(word_start + 0.4*self.samplerate)]
        word = self._get_word_envelope(pulse_position)
        # plt.plot(word)
        # plt.show()
        n = len(word)
        word = word.reshape(n, 1)
        gm = GaussianMixture(n_components=2, random_state=0).fit(word)
        bfsk_minimal_amplitude = min(gm.means_)
        logger.debug('bfsk_minimal_amplitude %f'%bfsk_minimal_amplitude)
        return bfsk_minimal_amplitude

    def _fit_trig_signal_to_convoluted_env(self):
        """
        Try to fit a triangular signal to the envelope convoluted with a square
        signal to evaluate if audio is composed of 0.5 sec signal and 0.5 s 
        silence. If so, the convolution is a triangular fct and a
        Levenberg–Marquardt fit is used to detect this occurence (lmfit).
        Results are cached in self.cached_convolution_fit alongside
        self.sound_extract_position for hit/miss checks.


        Returns
        -------
        float
            chi_sqr from lmfit.minimize(), indicative of fit quality
        int
            position of triangular minimum (base of the v shape), this
            corresponds to the center of silent zone.

        """
        cached_value = self.cached_convolution_fit['sound_extract_position']
        if (CACHING and
                    # cache_is_clean and
                    cached_value and 
                    math.isclose(
                        self.sound_extract_position,
                        cached_value,
                        abs_tol=0.1)):
            logger.debug('cache hit')
            return (
                self.cached_convolution_fit['chi_square'],
                self.cached_convolution_fit['minimum position'])
                # cached!
        x_shifted, convolution = self._get_square_convolution()

        shift = x_shifted[0] # convolution is shorter than sound envelope
        # see numpy.convolve(..., mode='valid')
        x = np.arange(len(convolution))
        trig_params = lmfit.Parameters()
        trig_params.add(
            'A', value=1, min=0, max=2
            )
        period0 = 2*self.samplerate
        trig_params.add(
            'period', value=period0, min=0.9*period0,
            max=1.1*period0
            )
        trig_params.add(
            'min_position', value=len(convolution)/2
            ) # at center
        def trig_wave(pars, x, signal_data=None):
            # looking for phase sx with a sin of 1 sec period and 0<y<1.0
            A = pars['A']
            p = pars['period']
            mp = pars['min_position']
            model = 2*A*arcsin(abs(sin((x - mp)*2*pi/p)))/pi
            if signal_data is None:
                return model
            return model - signal_data
        fit_trig = lmfit.minimize(
                            trig_wave, trig_params,
                            args=(x,), kws={'signal_data': convolution}
                            )
        chi_square = fit_trig.chisqr
        min_position = int(fit_trig.params['min_position'].value)
        logger.debug('chi_square %.1f minimum convolution position %i'%
                     (chi_square, min_position + shift))
        self.cached_convolution_fit['sound_extract_position'] = self.sound_extract_position
        self.cached_convolution_fit['chi_square'] = chi_square
        self.cached_convolution_fit['minimum position'] = min_position + shift

        return chi_square, min_position + shift

    def extract_seems_YaLTC(self):
        """
        evaluate if sound data is half signal, half silence
        no test is done on frequency components nor BFSK modulation.

        Returns
        -------
        True if sound seems YaLTC

        """
        chi_square, _ = self._fit_trig_signal_to_convoluted_env()
        seems_YaLTC = chi_square < 200 # good fit so, yes
        logger.debug('seems YaLTC: %s'%seems_YaLTC)
        return seems_YaLTC

    def _get_silent_zone_indices(self):
        """
        Returns silent zone boundary positions relative to the start
        of self.sound_extract. Adjustment are made so a complete
        0.5 second signal is at the left of the silent zone for word
        decoding.

        Returns
        -------
        left_window_boundary : int
            left indice.
        right_window_boundary : int
            right indice.
        float
            bfsk_minimal_amplitude, the lowest value detected in the
            signal portion

        """
        _, silence_center_position = self._fit_trig_signal_to_convoluted_env()
        srate = self.samplerate
        half_window = int(SAFE_SILENCE_WINDOW_WIDTH * 1e-3 * srate/2)
        left_window_boundary = silence_center_position - half_window
        right_window_boundary = silence_center_position + half_window
        margin = 0.75 * srate
        logger.debug('initial silent zone, left: %i, right %i, center %i'%
            (left_window_boundary, right_window_boundary,
             silence_center_position))
        logger.debug('final silent zone, left: %i, right %i'%
            (left_window_boundary, right_window_boundary))
        return (left_window_boundary, right_window_boundary )
 
    def _get_silence_floor(self):
        start_silent_zone, end_silent_zone = self._get_silent_zone_indices()
        signal = self.sound_extract
        silent_signal = signal[start_silent_zone:end_silent_zone]
        max_value = 1.001*np.abs(silent_signal).max() # a little headroom
        five_sigmas = 5 * silent_signal.std()
        return max(max_value, five_sigmas) # if guassian, five sigmas will do it

    def make_silence_analysis_plot(self, title=None, filename=None):
        # save figure in filename if set, otherwise
        # start an interactive plot, title is for matplotlib
        start_silent_zone, end_silent_zone = self._get_silent_zone_indices()
        signal = self.sound_extract
        x_signal = range(len(signal))
        x_convolution, convolution = self._get_square_convolution()
        scaled_convo = self._get_signal_level()*convolution
        # since 0 < convolution < 1
        max_noise = self._get_silence_floor()
        fig, ax = plt.subplots()
        yt = ax.get_yaxis_transform()
        xt = ax.get_xaxis_transform()
        _, silence_center_x = self._fit_trig_signal_to_convoluted_env()
        symbol_width_samples = 1e-3*SYMBOL_LENGTH
        pulse_relative_pos = int(0.5*(0.5 - 1e-3*SYMBOL_LENGTH)*self.samplerate)
        approx_pulse_x = silence_center_x + pulse_relative_pos
        ax.vlines(
            silence_center_x, 0.4, 0.6, 
            transform=xt, linewidth=1, colors='black'
            )
        ax.vlines(
            approx_pulse_x, 0.1, 0.9, 
            transform=xt, linewidth=1, colors='yellow'
            )
        bfsk_min = self._get_minimal_bfsk(approx_pulse_x)
        ax.hlines(
            bfsk_min, 0, 1, 
            transform=yt, linewidth=1, colors='red'
            )
        ax.hlines(
            max_noise, 0, 1, 
            transform=yt, linewidth=1, colors='blue'
            )
        ax.hlines(
            0, 0, 1, 
            transform=yt, linewidth=0.5, colors='black'
            )
        plt.title(title)
        custom_lines = [
            Line2D([0], [0], color='black', lw=2),
            Line2D([0], [0], color='green', lw=2),
            Line2D([0], [0], color='blue', lw=2),
            Line2D([0], [0], color='red', lw=2),
            Line2D([0], [0], color='yellow', lw=2),
            ]
        ax.legend(
            custom_lines,
            'sqr convolution,silence zone,found silence thld,lower FSK ampl., approx puls.'.split(','),
            loc='lower right')
        # plt.ylim( (pow(10,0),pow(10,5)) )
        ax.plot(
            x_signal, signal,
            marker='o', markersize='1',
            linewidth=0.3, color='purple', alpha=0.3)

        # ax.plot(
        #     x_signal, envelope,
        #     marker='o', markersize='1',
        #     linewidth=0.3, color='red', alpha=0.3)
        # # ax.set_yscale('log')
        ax.axvspan(
            start_silent_zone, end_silent_zone,
            alpha=0.1, color='green')
        ax.plot(
            x_convolution, scaled_convo,
            marker='.', markersize='0.2',
            linestyle='None', color='black', alpha=1)
            # linewidth=0.3, linestyle='None', color='black', alpha=0.3)
        ax.set_xlabel('Decoder.sound_extract samples')
        if filename == None:
            plt.show()
        else:
            logger.debug('saving ilence_analysis_plot to %s'%filename)
            plt.savefig(
                filename,
                format="png")
            plt.close()

    def _detect_sync_pulse_position(self):
        """
        Determines noise level during silence period and use it to detect
        the sync pulse position. Computes SN_ratio and stores it.
        Returns the pulse position relative to the extract beginnning.
        """
        start_silent_zone, end_silent_zone = self._get_silent_zone_indices()
        noise_threshold = self._get_silence_floor()
        abs_signal = abs(self.sound_extract)
        mean_during_word = 2*abs_signal.mean()
        self.SN_ratio = 20*math.log10(mean_during_word/noise_threshold)
        logger.debug('SN ratio: %f dB'%(self.SN_ratio))
        search_pulse_start_point = end_silent_zone
        distance_to_end = len(abs_signal) - search_pulse_start_point
        if distance_to_end/self.samplerate < 0.75: # sec
            search_pulse_start_point -= self.samplerate
        search_pulse_start_point = max(search_pulse_start_point, 0)
        logger.debug('search_pulse_start_point: %i'%
                search_pulse_start_point)
        abs_signal_after_silence = abs_signal[search_pulse_start_point:]
        first_point = \
            np.argmax(abs_signal_after_silence > noise_threshold)
        return (first_point + search_pulse_start_point)

    def _get_word_width_parameters(self, pulse_position):
        abs_signal = abs(self.sound_extract)
        # half_amplitude = abs_signal.mean() # since 50% duty cycle OLD
        # params = {'word_width_threshold':WORDWIDTHFACTOR*half_amplitude} OLD
        bfsk_min = self._get_minimal_bfsk(pulse_position)
        params = {'word_width_threshold': 0.8*bfsk_min}
        sr = self.samplerate
        presumed_symbol_length = SYMBOL_LENGTH*1e-3*sr
        # in ms, now in samples
        # params['search_start_position'] = \
        #     int(0.67 * presumed_symbol_length + pulse_position)
        presumed_word_width = presumed_symbol_length * N_SYMBOLS_SAMD21
        # word includes sync pulse
        params['search_end_position'] = \
                    int(0.67 * presumed_symbol_length + pulse_position + \
                    presumed_word_width) + 1700 # samples for headroom
        params['presumed_symbol_length'] = presumed_symbol_length
        return params

    def _get_BFSK_word_boundaries(self, pulse_position):
        n_bits = N_SYMBOLS_SAMD21 - 1
        sr = self.samplerate
        wwp = self._get_word_width_parameters(pulse_position)
        # search_start_position = wwp['search_start_position']
        search_end_position = wwp['search_end_position']
        word_width_threshold = wwp['word_width_threshold']
        word_extract = self.sound_extract[pulse_position :
            search_end_position]
        logger.debug('word left boundary search position: %i relative to extract'%
            (search_end_position))
        logger.debug('extract starting at %i in file (Decoder.sound_extract_position)'%
                self.sound_extract_position)
        flipped_extract = np.flip(np.abs(word_extract))
        right_boundary = len(word_extract) - \
            np.argmax(flipped_extract > word_width_threshold)  + \
                pulse_position
        # left_boundary = np.argmax(
        #     np.abs(word_extract) > word_width_threshold)  + \
        #     search_start_position
        left_boundary = pulse_position
        left_in_file = left_boundary + self.sound_extract_position
        right_in_file = right_boundary + self.sound_extract_position
        logger.debug('word boundaries: %i and %i in file'%
                                (left_in_file, right_in_file))
        eff_symbol_length = 1e3*(right_boundary-left_boundary)/(n_bits*sr)
        logger.debug('effective symbol length %.4f ms '%
                                eff_symbol_length)
        logger.debug('presumed symbol length %.4f ms '%SYMBOL_LENGTH)
        relative_error = (eff_symbol_length-SYMBOL_LENGTH)/SYMBOL_LENGTH
        status = True
        if relative_error > SYMBOL_LENGTH_TOLERANCE:
            logger.error(
                'actual symbol length differs too much: %.2f vs %.2f ms, aborting'%
                (eff_symbol_length, SYMBOL_LENGTH))
            # return None, None
            status = False
        logger.debug(' relative discrepancy %.4f%%'%(abs(100*relative_error)))
        return status, left_boundary, right_boundary

    def _get_BFSK_symbols_boundaries(self, pulse_position):
        # returns indices of start of each slice and boundaries
        boundaries_OK, left_boundary, right_boundary = \
                self._get_BFSK_word_boundaries(pulse_position)
        if left_boundary is None:
            return None, None, None
        symbol_width_samples = \
                float(right_boundary - left_boundary)/N_SYMBOLS_SAMD21
        symbol_positions = symbol_width_samples * \
                np.arange(float(0), float(N_SYMBOLS_SAMD21 + 1)) + \
                pulse_position
        int_symb_positions = symbol_positions.round().astype(int)
        logger.debug('%i symbol positions %s samples in file'%
                (
                len(int_symb_positions),
                int_symb_positions + self.sound_extract_position)
                )
        return int_symb_positions[:-1], left_boundary, right_boundary

    def _values_from_bits(self, bits):
        word_payload_bits_positions = {
            'version':(0,2),
            'clock source':(2,3),
            'seconds':(3,9),
            'minutes':(9,15),
            'hours':(15,20),
            'day':(20,25),
            'month':(25,29),
            'year offset':(29,34),
            }
        binary_words = { key : bits[slice(*value)]
                for key, value 
                in word_payload_bits_positions.items()
                }
        int_values = { key : self._get_int_from_binary_str(val)
                for key, val                 in binary_words.items()
                }
        logger.debug(' Demodulated values %s'%int_values)
        return int_values

    def _slice_sound_extract(self, symbols_indices):
        indices_left_shifted = deque(list(symbols_indices))
        indices_left_shifted.rotate(-1)
        all_intervals = list(zip(
                                symbols_indices,
                                indices_left_shifted
                                ))
        word_intervals = all_intervals[1:-1]
        # [0, 11, 23, 31, 45] => [(11, 23), (23, 31), (31, 45)]
        logger.debug('slicing intervals, word_intervals = %s'%
                                                word_intervals)
        # skip sample after pulse, start at BFSK word
        slices = [self.sound_extract[slice(*pair)]
                            for pair in word_intervals]
        np.set_printoptions(threshold=5)
        # logger.debug('data slices: \n%s'%pprint.pformat(slices))
        # raise Exception
        return slices

    def _get_main_frequency(self, symbol_data):
        w = np.fft.fft(symbol_data)
        freqs = np.fft.fftfreq(len(w))
        idx = np.argmax(np.abs(w))
        freq = freqs[idx]
        freq_in_hertz = abs(freq * self.samplerate)
        return int(round(freq_in_hertz))

    def _get_bit_from_freq(self, freq):
        if math.isclose(freq, F1, rel_tol=0.05):
            return '0'
        if math.isclose(freq, F2, rel_tol=0.05):
            return '1'
        else:
            return None

    def _get_int_from_binary_str(self, string_of_01s):
        return int(''.join(reversed(string_of_01s)),2)
        # LSB is leftmost in YaLTC

    def _demod_values_are_OK(self, values_dict):
        ranges = {
            'seconds': range(60),
            'minutes': range(60),
            'hours': range(24),
            'day': range(1,32),
            'month': range(1,13),
            }
        for key in ranges:
            val = values_dict[key]
            ok =  val in ranges[key]
            logger.debug(
                'checking range for %s: %i, Ok? %s'%(key, val, ok))
            if not ok:
                logger.error('demodulated value is out of range')
                return False
        return True

    def _plot_slices(self, sync_pulse, symbols_indices, word_lft, word_rght, title=None, filename=None):
        # save figure in filename if set, otherwise
        # start an interactive plot, title is for matplotlib
        signal = self.sound_extract
        start = self.sound_extract_position
        x_signal_in_file = range(
                                start,
                                start + len(signal)
                                )
        start_silent_zone, end_silent_zone = self._get_silent_zone_indices()
        # sync_pulse = self._detect_sync_pulse_position()
        wwp = self._get_word_width_parameters(sync_pulse)
        # search_start_position = wwp['search_start_position'] + start
        search_end_position = wwp['search_end_position'] + start
        fig, ax = plt.subplots()
        plt.title(title)
        # plt.title('bit slicing for\n%s'%filename)
        ax.plot(
            x_signal_in_file, signal,
            marker='.', markersize='1',
            linewidth=0.3, color='purple', alpha=0.3)
        yt = ax.get_yaxis_transform()
        ax.hlines(
            wwp['word_width_threshold'], 0, 1, 
            transform=yt, linewidth=0.6, colors='blue')
        ax.hlines(
            0, 0, 1, 
            transform=yt, linewidth=0.6, colors='black')
        ax.hlines(
            -wwp['word_width_threshold'], 0, 1, 
            transform=yt, linewidth=0.6, colors='blue')
        xt = ax.get_xaxis_transform()
        # ax.vlines(
        #     search_start_position,
        #     0, 1, transform=xt, linewidth=0.6, colors='blue')
        ax.vlines(
            search_end_position,
            0, 1, transform=xt, linewidth=0.6, colors='blue')
        ax.plot(
            [sync_pulse + start], [0],
            marker='D', markersize='7',
            linewidth=0.3, color='blue', alpha=0.3)
        ax.plot(
            [start_silent_zone + start], [0],
            marker='>', markersize='10',
            linewidth=0.3, color='green', alpha=0.3)
        ax.plot(
            [end_silent_zone + start], [0],
            marker='<', markersize='10',
            linewidth=0.3, color='green', alpha=0.3)
        # symbols_indices = self._get_BFSK_symbols_boundaries(sync_pulse)
        boundaries_OK, word_lft, word_rght = \
            self._get_BFSK_word_boundaries(sync_pulse)
        ax.vlines(
            word_lft + start, 0, 1,
            transform=ax.get_xaxis_transform(),
            linewidth=0.6, colors='red')
        ax.vlines(
            word_rght + start, 0, 1, 
            transform=ax.get_xaxis_transform(),
            linewidth=0.6, colors='red')
        for x in symbols_indices + self.sound_extract_position:
            ax.vlines(
            x, 0, 1,
            transform=ax.get_xaxis_transform(),
            linewidth=0.3, colors='green')
        ax.set_xlabel(
            'samples in file')
        plt.xlim(
            [sync_pulse - 300 + start, wwp['search_end_position'] + 400 + start])
        if filename == None:
            plt.show()
        else:
            plt.ylim(
                [-1.5*wwp['word_width_threshold'],
                1.1*signal.max()])
            height = 1000
            plt.savefig(
                filename,
                format='png',
                dpi=height/fig.get_size_inches()[1])
            plt.close()

    def get_time_in_sound_extract(self, plot_slicing):
        if self.sound_extract is None:
            return None
        start_silent_zone, end_silent_zone = self._get_silent_zone_indices()
        pulse_position = self._detect_sync_pulse_position()
        logger.debug('found sync pulse at %i in extract, at %i in file'%
            (pulse_position, pulse_position + self.sound_extract_position))
        symbols_indices, word_lft, word_rght = \
            self._get_BFSK_symbols_boundaries(pulse_position)
        if symbols_indices is None:
            return None
        if plot_slicing:
            logger.debug('will plot slices')
            self._plot_slices(pulse_position, symbols_indices, word_lft, word_rght)
        sliced_data = self._slice_sound_extract(symbols_indices)
        frequencies = [self._get_main_frequency(data_slice)
                            for data_slice
                            in sliced_data
                            ]
        logger.debug('frequencies = %s'%frequencies)
        bits = [self._get_bit_from_freq(f) for f in frequencies]
        for i, bit in enumerate(bits):
            if bit == None:
                logger.warning('cant decode frequency %i for bit at %i-%i'%(
                                frequencies[i],
                                symbols_indices[i],
                                symbols_indices[i+1]))
        if None in bits:
            return None
        bits_string = ''.join(bits)
        logger.debug('bits = %s'%bits_string)
        time_values = self._values_from_bits(bits_string)
        time_values['pulse at'] = (pulse_position +
                                    self.sound_extract_position -
                                    SAMD21_LATENCY*1e-6*self.samplerate)
        # time_values['clock source'] :  1 => GPS; 0 => RTC
        # replace with text
        time_values['clock source'] = 'GPS' \
            if time_values['clock source'] == 1 else 'RTC'
        if self._demod_values_are_OK(time_values):
            return time_values
        else:
            return None

class Recording:
    """
    Wrapper for file objects, ffmpeg read operations and fprobe functions
    
    Attributes:
        AVpath : pathlib.path
            path of video+sound+YaLTC file, relative to working directory

        media_without_YaLTC : pathlib.path
            path of video+sound file stripped of YaLTC channel

        device: str
            identifies the device used for the recording, set in __init__()

        new_rec_name: str
            built using the device name, ex: "CAM_A001"
            set by Timeline._rename_all_recs()

        probe : dict
            returned value of ffmpeg.probe(self.AVpath)

        YaLTC_channel : tuple of int
            which channel is sync track, 0 for left or mono, 
            1 for right. Value is None if not YaLTC found.
            Set in _read_sound_extract().

        decoder : yaltc.decoder
            associated decoder object, if file is audiovideo

        true_samplerate: float
            true sample rate using GPS time

        start_time: datetime or str
            time and date of the first sample in the file, cached
            after a call to get_start_time(). Value on initialization
            is None, 'Failed' if previous get_start_time() found none.

        sync_position: int
            position of first detected syn pulse

        is_reference: bool (True for ref rec only)
            in multi recorders set-ups, user decides if a sound-only recording
            is the time reference for all other audio recordings. By
            default any video recording is the time reference for other audio,
            so this attribute is only relevant to sound recordings and is
            implicitly True for each video recordings (but not set)

        device_relative_speed: float
            the ratio of the recording device clock speed relative to the
            reference_rec clock device, in order to correct clock drift with
            pysox tempo transform. If value < 1.0 then the recording is slower
            than reference_rec. Updated by each Montage instance so the value
            can change depending on the reference recording (video or main
            sound). A mean is calculated for all recordings of the same device
            in Montage._get_concatenated_audiofile_for()

        time_position: float
            The time (in seconds) at which the recording starts relative to the
            reference recording. Updated by each Montage instance so the value
            can change depending on the reference recording (a video or main
            sound).

        final_synced_file : a pathlib.Path
            contains the path of the merged video file after the call to
            AudioStitcher.build_audio_and_write_video if the Recording is a
            reference recording, relative to the working directory
            
        synced_audio : pathlib.Path
            contains the path of audio only of self.final_synced_file. Absolute
            path to tempfile.

        in_cam_audio_sync_error: int
            in cam audio sync error, read in the camera folder. Negative value
            for lagging video (audio leads) positive value for lagging audio
            (video leads)


    """

    def __init__(self, media):
        """
        If multifile recording, AVfilename is sox merged audio file;
        Set AVfilename string and check if file exists, does not read
        any media data right away but uses ffprobe to parses the file and
        sets probe attribute. 
        Logs a warning if ffprobe cant interpret the file or if file
        has no audio; if file contains audio, instantiates a Decoder object
        (but doesnt try to decode anything yet)

        Parameters
        ----------
        media : dict as
                {
                'path' : as is ,
                'device type' : REC or CAM,
                'sample length' : as is
                'dev UID' : see get_device_ffprobe_UID()
                }

        Raises
        ------
        an Exception if AVfilename doesnt exist

        """

        # self.AVpath = [pathlib.Path(fn) for fn in AVfilename] 
        self.AVpath = media['path']
        # self.soxed_audio = None
        # self.file_alias = media['path'].name
        self.device = media['dev UID']
        self.true_samplerate = None
        self.start_time = None
        self.in_cam_audio_sync_arror = 0
        self.decoder = None
        self.probe = None
        self.YaLTC_channel = None
        self.is_reference = False
        self.device_relative_speed = 1.0
        self.media_without_YaLTC = None
        self.final_synced_file = None
        self.synced_audio = None
        self.new_rec_name = media['path'].name
        # self.matched_audio_records = []
        # self.relative_position = 0
        # self.editing_front = {'what':None,'how': 0}
        # self.editing_rear =  {'what':None,'how': 0}
        logger.debug('__init__ Recording object %s'%self.__repr__())
        logger.debug(' in directory %s'%self.AVpath.parent)
        recording_init_fail = ''
        if not self.AVpath.is_file():
            raise OSError('file "%s" doesnt exist'%self.AVpath)        
        try:
            self.probe = ffmpeg.probe(self.AVpath)
        except:
            logger.warning('"%s" is not recognized by ffprobe'%self.AVpath)
            recording_init_fail = 'not recognized by ffprobe'
        if self.probe is None:
            recording_init_fail ='no ffprobe'
        elif self.probe['format']['probe_score'] < 99:
            logger.warning('ffprobe score too low')
            # raise Exception('ffprobe_score too low: %i'%probe_score)
            recording_init_fail = 'ffprobe score too low'
        elif not self.has_audio():
            # logger.warning('file has no audio')
            recording_init_fail = 'no audio in file'
        elif self.get_duration() < MINIMUM_LENGTH:
            recording_init_fail = 'file too short, %f s'%self.get_duration()
        if recording_init_fail == '':
            self.decoder = Decoder()
            # self._set_multi_files_siblings()
        else:
            logger.warning('Recording init failed: %s'%recording_init_fail)
            print('Recording init failed: %s'%recording_init_fail)
            self.probe = None
            self.decoder = None
        logger.debug('ffprobe found: %s'%self.probe)
        logger.debug('n audio chan: %i'%self.get_audio_channels_nbr())
        self._check_for_camera_error_correction()

    def _check_for_camera_error_correction(self):
        # look for a file number
        streams = self.probe['streams']
        codecs = [stream['codec_type'] for stream in streams]
        if 'video' in codecs:
            calib_file = list(self.AVpath.parent.rglob('*ms.txt'))
            # print(list(files))
            if len(calib_file) == 1:
                value_string = calib_file[0].stem.split('ms')[0]
                try:
                    value = int(value_string)
                except:
                    f = str(calib_file[0])
                    print('problem parsing name of [gold1]%s[/gold1],'%f)
                    print('move elsewhere and rerun, quitting.\n')
                    quit()
                self.in_cam_audio_sync_arror = value
                logger.debug('found error correction %i'%value)

    def __repr__(self):
        return 'Recording of %s'%_pathname(self.new_rec_name)

    def get_path(self):
        return self.AVpath

    def get_duration(self):
        """
        Raises
        ------
        Exception
            If ffprobe has no data to compute duration.

        Returns
        -------
        float
            recording duration in seconds.

        """
        # if self.soxed_audio:
        #     val = sox.file_info.duration(_pathname(self.soxed_audio))
        #     logger.debug('duration of soxed_audio %f'%val)
        #     return val
        if self.media_without_YaLTC:
            val = sox.file_info.duration(_pathname(self.media_without_YaLTC))
            logger.debug('duration of media_without_YaLTC %f'%val)
            return val
        else:
            if self.probe is None:
                return 0
            # audio_stream = self._ffprobe_audio_stream()
            # sample_rate = int(audio_stream['sample_rate'])
            # if 'duration' in audio_stream:
            #     probed_duration = float(audio_stream['duration'])
            # elif 'nb_frames' in audio_stream:
            #     nb_frames = int(audio_stream['nb_frames'])
            #     probed_duration =  nb_frames / sample_rate
            try:
                probed_duration = float(self.probe['format']['duration'])
            except:
                logger.error('oups, cant find duration from ffprobe')
                raise Exception('stopping here')
            logger.debug('ffprobed duration is: %f sec'%probed_duration)
            return probed_duration # duration in s

    def get_original_duration(self):
        """
        Raises
        ------
        Exception
            If ffprobe has no data to compute duration.

        Returns
        -------
        float
            recording duration in seconds.

        """
        val = sox.file_info.duration(_pathname(self.media_without_YaLTC))
        logger.debug('duration of media_without_YaLTC %f'%val)
        return val

    def get_corrected_duration(self):
        """
        uses device_relative_speed to compute corrected duration. Updated by each
        Montage object in Montage._get_concatenated_audiofile_for()
        """
        return self.get_duration()/self.device_relative_speed

    def needs_dedrifting(self):
        rel_sp = self.device_relative_speed
        if rel_sp > 1:
            delta = (rel_sp - 1)*self.get_original_duration()
        else:
            delta = (1 - rel_sp)*self.get_original_duration()
        logger.debug('%s delta drift %.2f ms'%(str(self), delta*1e3))
        return delta > MAXDRIFT, delta

    def get_end_time(self):
        return (
            self.get_start_time() + 
            timedelta(seconds=self.get_duration())
            )

        """        
            Check if datetime fits inside recording interval,
            ie if start < datetime < end

            Returns a bool
        
        """
        start = self.get_start_time()
        end = self.get_end_time()
        return start < datetime and datetime < end

    def _find_time_around(self, time, plot_slicing):
        # actually reading sound data and trying to decode it
        # through decoder object, if successful  return a time dict, eg:
        # {'version': 0, 'clock source': 'GPS', 'seconds': 44, 'minutes': 57,
        # 'hours': 19, 'day': 1, 'month': 3, 'year offset': 1, 
        # 'pulse at': 670451.2217 }
        # otherwise return None
        if time < 0:
            there = self.get_duration() + time
        else:
            there = time
        self._read_sound_find_YaLTC(there, SOUND_EXTRACT_LENGTH)
        if self.YaLTC_channel is None:
            return None
        else:
            return self.decoder.get_time_in_sound_extract(plot_slicing)

    def _get_timedate_from_dict(self, time_dict):
        python_datetime = datetime(
            time_dict['year offset'] + 2023,
            time_dict['month'],
            time_dict['day'],
            time_dict['hours'],
            time_dict['minutes'],
            time_dict['seconds'],
            tzinfo=timezone.utc)
        python_datetime += timedelta(seconds=1) # PPS precedes NMEA sequ
        return python_datetime

    def _two_times_are_coherent(self, t1, t2):
        """
        For error checking. This verifies if two sync pulse apart
        are correctly space with sample interval deduced from
        time difference of demodulated YaLTC times. The same 
        process is used for determining the true sample rate
        in _compute_true_samplerate(). On entry check if either time
        is None, return False if so.

        Parameters
        ----------
        t1 : dict of demodulated time
            see _find_time_around().
        t2 : dict of demodulated time
            see _find_time_around().

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        if t1 == None or t2 == None:
            return False
        datetime_1 = self._get_timedate_from_dict(t1)
        datetime_2 = self._get_timedate_from_dict(t2)
        sample_position_1 = t1['pulse at']
        sample_position_2 = t2['pulse at']
        samplerate = self.get_samplerate()
        delta_seconds_with_samples = \
                (sample_position_2 - sample_position_1)/samplerate
        delta_seconds_with_UTC = (datetime_2 - datetime_1).total_seconds()
        logger.debug('check for delay between \n%s and\n%s'%
                            (datetime_1, datetime_2))
        logger.debug('delay using samples number: %f sec'%
                            (delta_seconds_with_samples))
        logger.debug('delay using timedeltas: %.2f sec'%
                            (delta_seconds_with_UTC))
        return round(delta_seconds_with_samples) == delta_seconds_with_UTC

    def _compute_true_samplerate(self, t1, t2):
        datetime_1 = self._get_timedate_from_dict(t1)
        pulse_position_1 = t1['pulse at']
        datetime_2 = self._get_timedate_from_dict(t2)
        if datetime_1 == datetime_2:
            msg = 'times at start and end are indentical, file too short? %s'%self.AVpath
            logger.error(msg)
            raise Exception(msg)
        pulse_position_2 = t2['pulse at']
        delta_seconds_whole = (datetime_2 - datetime_1).total_seconds()
        delta_samples_whole = pulse_position_2 - pulse_position_1
        true_samplerate = delta_samples_whole / delta_seconds_whole
        logger.debug('delta seconds between pulses %f'%
                                delta_seconds_whole)
        logger.debug('delta samples between pulse %i'%
                                delta_samples_whole)
        logger.debug('true sample rate = %s Hz'%
                                to_precision(true_samplerate, 8))
        return true_samplerate

    def set_time_position_to(self, reference_recording):
        """
        Sets self.time_position, the time (in seconds) at which the recording
        starts relative to the reference recording. Updated by each Montage
        instance so the value can change depending on the reference
        recording (a video or main sound).

        called by timeline.AudioStitcher._get_concatenated_audiofile_for()
        
        """
        ref_start_time = reference_recording.get_start_time()
        self.time_position = (self.get_start_time()
                                            - ref_start_time).total_seconds()

    def get_Dt_with(self, later_recording):
        """
        Returns delta time in seconds
        """
        if not later_recording:
            return 0
        t1 = self.get_end_time()
        t2 = later_recording.get_start_time()
        return t2 - t1

    def get_start_time(self, plot_slicing=False):
        # returns a python datetime object
        if self.start_time is not None:
            return self.start_time
        cached_times = {}
        def find_time(t_sec, plot_slicing=False):
            time_k = int(t_sec)
            # if cached_times.has_key(time_k):
            if CACHING and time_k in cached_times:
                logger.debug('cache hit _find_time_around() for t=%s s'%time_k)
                return cached_times[time_k]
            else:
                logger.debug('_find_time_around() for t=%s s not cached'%time_k)
                new_t = self._find_time_around(t_sec, plot_slicing)
                cached_times[time_k] = new_t
                return new_t
        for i, pair in enumerate(TRIAL_TIMES):
            near_beg, near_end = pair
            logger.debug('Will try to decode times at: %s and %s secs'%
                (near_beg, near_end))
            logger.debug('Trial #%i, beg at %f'%(i+1, near_beg))
            if i > 1:
                logger.warning('More than one trial: #%i/4'%(i+1))
            # time_around_beginning = self._find_time_around(near_beg)
            time_around_beginning = find_time(near_beg, plot_slicing)
            if self.YaLTC_channel is None:
                return None
            logger.debug('Trial #%i, end at %f'%(i+1, near_end))
            # time_around_end = self._find_time_around(near_end)
            time_around_end = find_time(near_end)
            logger.debug('trial result, time_around_beginning:\n   %s'%
                    (time_around_beginning))
            logger.debug('trial result, time_around_end:\n   %s'%
                    (time_around_end))
            if self._two_times_are_coherent(
                    time_around_beginning,
                    time_around_end):
                break
        if None in [time_around_beginning, time_around_end]:
            logger.warning('didnt find two times in file')
            self.start_time = 'Failed'
            return None
        true_sr = self._compute_true_samplerate(
                        time_around_beginning,
                        time_around_end)
        # self.true_samplerate = to_precision(true_sr,8)
        self.true_samplerate = true_sr
        first_pulse_position = time_around_beginning['pulse at']
        delay_from_start = timedelta(
                seconds=first_pulse_position/true_sr)
        first_time_date = self._get_timedate_from_dict(
                                    time_around_beginning)
        in_cam_correction = timedelta(seconds=self.in_cam_audio_sync_arror/1000)
        start_UTC = first_time_date - delay_from_start + in_cam_correction
        logger.debug('recording started at %s'%start_UTC)
        self.start_time = start_UTC
        self.sync_position = time_around_beginning['pulse at']
        if self.is_audio():
            self.media_without_YaLTC = self._strip_yaltc()
        return start_UTC

    def _strip_yaltc(self):
        # return the path of video+sound file stripped of YaLTC channel, 
        input_file = _pathname(self.AVpath)
        # building dict according to pysox.remix format.
        # eg: 4 channels with YaLTC_channel = 2  returns {1: [1], 2: [3], 3: [4]}
        # ie the number of channels drops by one and chan 2 is missing
        YaLTC_channel = self.YaLTC_channel + 1 # sox channels start at 1
        n_channels = sox.file_info.channels(input_file) # eg 2
        chan_list_out = range(1, n_channels) # eg [1,2,3]
        all_channels = range(1, n_channels + 1) # eg [1,2,3,4]
        chan_list_in = [[n] for n in  all_channels if n != YaLTC_channel]
        # eg [[1], [3], [4]]
        sox_remix_dict = dict(zip(chan_list_out, chan_list_in))
        # {1: [1], 2: [3], 3: [4]}
        output_fh = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        # recording_path = self.AVpath
        # if len(self.AVpath) != 1:
        #     logger.error('multifile recs not yet supported')
        #     quit()
        out_file = _pathname(output_fh)
        logger.debug('sox in and out files: %s %s'%(input_file, out_file))
        # sox_transform.set_output_format(channels=1)
        sox_transform = sox.Transformer()
        sox_transform.remix(sox_remix_dict)
        logger.debug('sox remix transform: %s'%sox_transform)
        logger.debug('sox remix dict: %s'%sox_remix_dict)
        status = sox_transform.build(input_file, out_file, return_output=True )
        logger.debug('sox.build exit code %s'%str(status))
        # logger.debug('input_file ffprobe:\n%s'%subprocess.check_output([
        #     'ffprobe',
        #     input_file,
        #     '-hide_banner',
        #     ]).decode('utf-8'))
        # p = Popen('ffprobe %s -hide_banner'%out_file, stdout=PIPE, stderr=PIPE)
        p = Popen('ffprobe %s -hide_banner'%input_file,
            shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        logger.debug('remixed input_file ffprobe:\n%s'%(stdout +
            stderr).decode('utf-8'))
        p = Popen('ffprobe %s -hide_banner'%out_file,
            shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        logger.debug('remixed out_file ffprobe:\n%s'%(stdout +
            stderr).decode('utf-8'))
        return output_fh

    def _ffprobe_audio_stream(self):
        streams = self.probe['streams']
        audio_streams = [
            stream 
            for stream
            in streams
            if stream['codec_type']=='audio'
            ]
        if len(audio_streams) > 1:
            raise Exception('ffprobe gave multiple audio streams?')
        audio_str = audio_streams[0]
        return audio_str

    def _ffprobe_video_stream(self):
        streams = self.probe['streams']
        audio_streams = [
            stream 
            for stream
            in streams
            if stream['codec_type']=='video'
            ]
        if len(audio_streams) > 1:
            raise Exception('ffprobe gave multiple video streams?')
        audio_str = audio_streams[0]
        return audio_str

    def get_samplerate_drift(self):
        # return drift in ppm (int), relative to nominal sample rate, neg = lag
        nominal = self.get_samplerate()
        true = self.true_samplerate
        if true > nominal:
            ppm = (true/nominal - 1) * 1e6
        else:
            ppm = - (nominal/true - 1) * 1e6
        return int(ppm)

    def get_speed_ratio(self, ref_recording):
        nominal = self.get_samplerate()
        true = self.true_samplerate
        ratio = true/nominal
        nominal_ref = ref_recording.get_samplerate()
        true_ref = ref_recording.true_samplerate
        ratio_ref = true_ref/nominal_ref
        return ratio/ratio_ref

    def get_samplerate(self):
        # return int samplerate (nominal)
        string = self._ffprobe_audio_stream()['sample_rate']
        return eval(string) # eg eval(24000/1001)

    def get_framerate(self):
        # return int samplerate (nominal)
        string = self._ffprobe_video_stream()['avg_frame_rate']
        return eval(string) # eg eval(24000/1001)

    def get_timecode(self, with_offset=0):
        # returns a HHMMSS:FR string
        start_datetime = self.get_start_time()
        logger.debug('start_datetime %s'%start_datetime)
        start_datetime += timedelta(seconds=with_offset)
        logger.debug('shifted start_datetime %s (offset %f)'%(start_datetime,
                                                    with_offset))
        HHMMSS = start_datetime.strftime("%H:%M:%S")
        fps = self.get_framerate()
        frame_number = str(round(fps*1e-6*start_datetime.microsecond))
        timecode  = HHMMSS + ':' + frame_number.zfill(2)
        logger.debug('timecode: %s'%(timecode))
        return timecode

    def write_file_timecode(self, timecode):
        # set self.final_synced_file metadata to timecode string
        if self.final_synced_file == None:
            logger.error('cant write timecode for unexisting file, quitting..')
            raise Exception
        try:
            video_path = self.final_synced_file
            in1 = ffmpeg.input(_pathname(video_path))
            video_extension = video_path.suffix
            silenced_opts = ["-loglevel", "quiet", "-nostats", "-hide_banner"]
            file_handle = tempfile.NamedTemporaryFile(suffix=video_extension, delete=False)
            out1 = in1.output(file_handle.name,
                timecode=timecode,
                acodec='copy', vcodec='copy')
            ffmpeg.run([out1.global_args(*silenced_opts)], overwrite_output=True)
        except ffmpeg.Error as e:
            logger.error('ffmpeg.run error')
            logger.error(e)
            logger.error(e.stderr)
        os.remove(_pathname(video_path))
        shutil.copy(_pathname(file_handle), _pathname(video_path))

    # def write_file_metadata(self, timecode, reel_name):
    #     # set self.final_synced_file metadata to timecode string
    #     if self.final_synced_file == None:
    #         logger.error('cant write timecode for unexisting file, quitting..')
    #         raise Exception
    #     try:
    #         video_path = self.final_synced_file
    #         in1 = ffmpeg.input(_pathname(video_path))
    #         video_extension = video_path.suffix
    #         # video_extension = 'MOV'
    #         silenced_opts = ["-loglevel", "quiet", "-nostats", "-hide_banner"]
    #         file_handle = tempfile.NamedTemporaryFile(suffix=video_extension, delete=False)
    #         out1 = in1.output(file_handle.name,
    #             # timecode=timecode, metadata='reel_name=%s'%reel_name,
    #             metadata='reel_name=%s'%reel_name,
    #             acodec='copy', vcodec='copy')
    #         ffmpeg.run([out1.global_args(*silenced_opts)], overwrite_output=True)
    #     except ffmpeg.Error as e:
    #         logger.error('ffmpeg.run error')
    #         logger.error(e)
    #         logger.error(e.stderr)
    #     os.remove(_pathname(video_path))
    #     shutil.copy(_pathname(file_handle), _pathname(video_path))

    def has_audio(self):
        if not self.probe:
            return False
        streams = self.probe['streams']
        codecs = [stream['codec_type'] for stream in streams]
        return 'audio' in codecs

    def get_audio_channels_nbr(self):
        if not self.has_audio():
            return 0
        audio_str = self._ffprobe_audio_stream()
        return audio_str['channels']

    def is_video(self):
        if not self.probe:
            return False
        streams = self.probe['streams']
        codecs = [stream['codec_type'] for stream in streams]
        return 'video' in codecs

    def is_audio(self):
        return not self.is_video()

    def _read_sound_find_YaLTC(self, time_where, chunk_length):
        """
        Loads audio data reading from self.AVpath;
        Split data into channels if stereo;
        Send this data to Decoder object with set_sound_extract_and_sr() to find
        which channel contains a YaLTC track and sets YaLTC_channel
        accordingly: a tuple (#file, #chan). On exit, self.decoder.sound_extract
        contains YaLTC data ready to be demodulated. If not, self.YaLTC_channel
        is set to None.

        Args:
            time_where : float
                time of the audio chunk start, in seconds.
            chunk_length : float
                length of the audio chunk, in seconds.

        Returns:
            this Recording instance

        """
        path = self.AVpath
        decoder = self.decoder
        # decoder.cached_convolution_fit['is clean'] = False
        if not self.has_audio():
            self.YaLTC_channel = None
            return
        logger.debug('will read around %.2f sec'%time_where)
        dryrun = (ffmpeg
            .input(str(path), ss=time_where, t=chunk_length)
            .output('pipe:', format='s16le', acodec='pcm_s16le')
            .get_args())
        dryrun = ' '.join(dryrun)
        logger.debug('using ffmpeg-python built args to pipe wav file into numpy array:\nffmpeg %s'%dryrun)
        try:
            out, _ = (ffmpeg
                .input(str(path), ss=time_where, t=chunk_length)
                .output('pipe:', format='s16le', acodec='pcm_s16le')
                .global_args("-loglevel", "quiet")
                .global_args("-nostats")
                .global_args("-hide_banner")
                .run(capture_stdout=True))
            data = np.frombuffer(out, np.int16)
        except ffmpeg.Error as e:
            print('error',e.stderr)        
        sound_extract_position = int(self.get_samplerate()*time_where) # from sec to samples
        n_chan = self.get_audio_channels_nbr()
        if n_chan == 1 and not self.is_video():
            logger.warning('file is sound mono')
        all_channels_data = data.reshape(int(len(data)/n_chan),n_chan).T
        for i_chan, chan_dat in enumerate(all_channels_data):
            logger.debug('testing chan %i'%i_chan)
            decoder.set_sound_extract_and_sr(
                    chan_dat,
                    self.get_samplerate(),
                    sound_extract_position
                    )
            if decoder.extract_seems_YaLTC():
                self.YaLTC_channel = i_chan
                logger.debug('find YaLTC channel, chan #%i'%
                                self.YaLTC_channel)
                return self
        # end of loop: none found
        self.YaLTC_channel = None
        logger.warning('found no YaLTC channel')
        return self
    
    def seems_to_have_YaLTC_at_beginning(self):
        if self.probe is None:
            return False
        self._read_sound_find_YaLTC(TRIAL_TIMES[0][0], SOUND_EXTRACT_LENGTH)
        return self.YaLTC_channel is not None

    # def get_joined_audio_file(self):
    #     # return audio of final synced video
    #     return

    def does_overlap_with_time(self, time):
        A1, A2 = self.get_start_time(), self.get_end_time()
        # R1, R2 = rec.get_start_time(), rec.get_end_time()
        # no_overlap = (A2 < R1) or (A1 > R2)
        return time >= A1 and time <= A2

    def get_otio_videoclip(self):
        if self.new_rec_name == self.AVpath.name:
            # __init__ value still the same?
            logger.error('cant get otio clip if no editing has been done.')
            raise Exception
        clip = otio.schema.Clip()
        clip.name = self.new_rec_name.stem
        clip.media_reference = otio.schema.ExternalReference(
            target_url=_pathname(Path.cwd()/self.final_synced_file))
        length_in_ms = self.get_duration()*1e3 # for RationalTime later
        clip.source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 1), 
            duration=otio.opentime.RationalTime(int(length_in_ms), 1000)
            )
        return clip

    def get_otio_audioclip(self):
        # and place a copy of audio in tictacsync directory
        if not self.synced_audio:
            # no synced audio
            logger.error('cant get otio clip if no editing has been done.')
            raise Exception
        video = self.final_synced_file
        path_WO_suffix = _pathname(Path.cwd()/video).split('.')[0] #better way?
        audio_destination = path_WO_suffix + '.wav'
        shutil.copy(self.synced_audio, audio_destination)
        logger.debug('copied %s'%audio_destination)
        clip = otio.schema.Clip()
        clip.name = self.new_rec_name.stem + ' audio'
        clip.media_reference = otio.schema.ExternalReference(
            target_url=audio_destination)
        length_in_ms = self.get_duration()*1e3 # for RationalTime later
        clip.source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 1), 
            duration=otio.opentime.RationalTime(int(length_in_ms), 1000)
            )
        return clip

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mediafile", nargs="?", help="path of media file with YaLTC")
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()
    if not args.v:
        logger.remove()
    fn = args.mediafile
    a_recording = Recording(fn)
    start_time = a_recording.get_start_time()
    if start_time is not None:
        print('%s started at %s'%(fn, start_time))
    else:
        print("can't find start time for %s"%fn)





