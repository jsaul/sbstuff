#!/bin/sh

test -f 2023-05-05-GE.FLT1..BH.mseed || \
wget -O 2023-05-05-GE.FLT1..BH.mseed 'http://geofon.gfz-potsdam.de/fdsnws/dataselect/1/query?net=GE&sta=FLT1&loc=*&cha=BH*&start=2023-05-05T00:00:00&end=2023-05-06T00:00:00'
