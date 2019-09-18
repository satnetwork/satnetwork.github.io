#!/usr/bin/env bash
# The MIT License (MIT)
#
# Copyright (c) 2019 Debopam Bhattacherjee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

##########################################################################################
# Generate time varying constellation satellite positions based on configuration
##########################################################################################

NUM_ORBITS=40 # options: 40 (for 40_40_53deg), 34 (kuiper_p1), 24 (starlink_p1)
NUM_SATS_PER_ORBIT=40 # options: 40 (for 40_40_53deg), 34 (kuiper_p1), 66 (starlink_p1)
INCLINATION=53 # options: 53 (for 40_40_53deg), 51.9 (kuiper_p1), 53 (starlink_p1)
ECCENTRICITY=0.001 # Circular orbits
ARG_OF_PERIGEE=0.0 # Circular orbits
MEAN_MOTION=15.19 # 15.19 taken from Tintin A anb B TLEs
PHASE_DIFF="Y" # Neighboring satellites in adjacent orbits has a phase difference

rm ../output_data_generated/sat_positions/*

#Get satellite positions for 120 minutes starting from epoch
for (( i=0; i<120; i++ ))
do
	./02_get_sat_positions_at_time.sh $i $NUM_ORBITS $NUM_SATS_PER_ORBIT $INCLINATION $ECCENTRICITY $ARG_OF_PERIGEE $MEAN_MOTION $PHASE_DIFF
done
