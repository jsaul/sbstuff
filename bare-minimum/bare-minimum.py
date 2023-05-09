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


# Read one day of data from a previously downloaded file
files = "2023-05-05-GE.FLT1..BH.mseed"
stream = readFilesAsStream(files)

# There is a known P pick around that time
tp = obspy.core.UTCDateTime("2023-05-05T05:54:07.59")
# Trim the stream to just work on a small snippet.
stream.trim(tp-60, tp+60)

model = seisbench.models.EQTransformer.from_pretrained('geofon')
annotations = model.annotate(stream)

for annotation in annotations:
    meta = annotation.meta

    net = meta.network
    sta = meta.station
    loc = meta.location
    cha = meta.channel  # nothing to do with SEED conventions!

    if meta.channel.endswith("_Detection"):
        flag = "D"
    elif meta.channel.endswith("_P"):
        flag = "P"
    elif meta.channel.endswith("_S"):
        flag = "S"
    else:
        flag = "X"

    if flag not in ["P", "S"]:
        continue

    nsl = "%(network)s.%(station)s.%(location)s" % meta
    annotation.write("annotation-%s-%s.sac" % (nsl, flag), format="SAC")

    data = annotation.data.astype(np.double)
    times = annotation.times()
    peaks, _ = scipy.signal.find_peaks(data, height=0.1)
    for peak in peaks:
        picktime = annotation.stats.starttime + times[peak]
        confidence = data[peak]
        print("%-2s %-5s %-2s   %s   %s %.3f" % (
            net, sta, loc, flag, str(picktime)[:23]+"Z", confidence))
