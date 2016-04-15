import sys
import os
import pickle

import numpy
import scipy.io.wavfile
import scipy.signal
import pylab

import onset_strength
import beat_period_detection
import accumulator_overall

import defs_class

def load_wavfile(filename):
    sample_rate, data_unnormalized = scipy.io.wavfile.read(filename)
    maxval = numpy.iinfo(data_unnormalized.dtype).max+1
    data_normalized = (numpy.array(data_unnormalized, dtype=numpy.float64)
        / float(maxval))
    return sample_rate, data_normalized

def bpm_of_file(defs, filename, plot=False, regen=False):
    defs.basename = os.path.splitext(os.path.basename(filename))[0]
    ### handle OSS
    pickle_filename = filename + "-onsets-%i.pickle" % (
        defs.OPTIONS_ONSET)
    if os.path.exists(pickle_filename) and not regen:
        pickle_file = open(pickle_filename, 'rb')
        oss_sr, oss_data = pickle.load(pickle_file)
        pickle_file.close()
    else:
        wav_sr, wav_data = load_wavfile(filename)
        oss_sr, oss_data = onset_strength.onset_strength_signal(
            defs, wav_sr, wav_data,
            #plot=False)
            plot=plot)
        pickle_file = open(pickle_filename, 'wb')
        pickle.dump( (oss_sr, oss_data), pickle_file, -1 )
        pickle_file.close()
    #print "OSS sr, len(data), seconds:\t", oss_sr, len(oss_data), len(oss_data)/oss_sr


    if defs.OPTIONS_BH < 0:
        pylab.show()
        exit(1)
    ### handle Beat Histogram
    pickle_filename = filename + "-bh-%i-%i.pickle" % (
        defs.OPTIONS_ONSET, defs.OPTIONS_BH)
    if os.path.exists(pickle_filename) and not regen:
        pickle_file = open(pickle_filename, 'rb')
        tempo_lags = pickle.load(pickle_file)
        pickle_file.close()
    else:
        tempo_lags = beat_period_detection.beat_period_detection(
            defs, oss_sr, oss_data,
            #plot=False)
            plot=plot)
        pickle_file = open(pickle_filename, 'wb')
        pickle.dump( (tempo_lags), pickle_file, -1 )
        pickle_file.close()

    #return tempo_lags, [tempo_lags]

    if defs.OPTIONS_BP < 0:
        cands = numpy.zeros(4*defs.BPM_MAX)
        for i in range(len(tempo_lags)):
            for j in range(len(tempo_lags[i])):
                bpm = tempo_lags[i][j]
                cands[bpm] += 9-j
        if plot:
            pylab.figure()
            pylab.plot(cands)
            pylab.title("combo BPM cands")
            pylab.show()
        bestbpm = 4*cands.argmax()
        fewcands = []
        for i in range(4):
            bpm = cands.argmax()
            cands[bpm] = 0.0
            fewcands.append(4*bpm)
        return bestbpm, fewcands

    bpm = accumulator_overall.accumulator_overall(defs, tempo_lags, oss_sr)

    if plot:
        pylab.show()
    #print bpm
    #return bpm, tempo_lags
    return bpm, tempo_lags[-1]


defs = defs_class.Defs()
bpm, cands = bpm_of_file(defs, 'test.wav')
print "The BPM of supplied file is : %.2f" % bpm
