#!/usr/bin/env python

import glob
import obspy
import numpy as np
import scipy.signal
import seisbench.models


def readFilesAsStream(pattern):
    stream = obspy.core.stream.Stream()
    for filename in glob.glob(pattern):
        stream += obspy.core.stream.read(filename)
    return stream


def annotationToPicks(annotation, label):
    """
    For the time being just prints the picks found in annotation function.
    """
    meta = annotation.meta

    net = meta.network
    sta = meta.station
    loc = meta.location
    cha = meta.channel  # nothing to do with SEED conventions!

    # only interested in P and S
    flag = cha[-1] if cha[-2] == "_" else "X"
    if flag not in ["P", "S"]:
        return

    annotation.write("annotation-%s-%s.sac" % (flag, label), format="SAC")

    data = annotation.data.astype(np.double)
    times = annotation.times()
    peaks, _ = scipy.signal.find_peaks(data, height=0.1)
    for peak in peaks:
        picktime = annotation.stats.starttime + times[peak]
        confidence = data[peak]
        print("%-2s %-5s %-2s   %s   %s %.3f" % (
            net, sta, loc, flag, str(picktime)[:23]+"Z", confidence))


# Read one day of data from a previously downloaded file
files = "2023-05-05-GE.FLT1..BH.mseed"
whole = readFilesAsStream(files)
stream = whole.copy()

model = seisbench.models.EQTransformer.from_pretrained('geofon', update=True)

for label in ['long', 'short-good', 'short-strange']:
    if label == 'short-good':
        # There is an very clear and impulsive P pick around that time
        tp = obspy.core.UTCDateTime("2023-05-05T05:54:07.59")
        # Trim the stream to just work on a small snippet.
        stream = whole.copy()
        stream.trim(tp-60, tp+60)
        # This yields a sharp peak with amplitude of around 0.76

    if label == 'short-strange':
        # Whereas there is no plausible pick around this time
        tp = obspy.core.UTCDateTime("2023-05-05T05:49:41.5")
        stream = whole.copy()
        stream.trim(tp-60, tp+60)
        # Strangely this also yields a sharp peak with amplitude of around 0.76

    annotations = model.annotate(stream)

    for annotation in annotations:
        annotationToPicks(annotation, label)
