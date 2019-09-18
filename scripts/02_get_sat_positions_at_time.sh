#!/bin/bash
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
# Generate constellation satellite positions for a specific time in min as supplied by the parent script
##########################################################################################

# Parent script 01_get_time_varying_sat_positions.sh calls this script.

EPOCH="2018/1/1 00:00:01"

CURR_TIME_MINS=$1
NUM_ORBITS=$2
NUM_SATS_PER_ORBIT=$3
INCLINATION=$4
ECCENTRICITY=$5
ARG_OF_PERIGEE=$6
MEAN_MOTION=$7
PHASE_DIFF=$8

min=$CURR_TIME_MINS
curr_t=$(date +'%Y/%m/%d %T' --date="$EPOCH $min minutes")

last_orbit=0


counter=0
for (( num_orbit=0; num_orbit<$NUM_ORBITS; num_orbit++ ))
do
	raan=$(echo "scale=2; $num_orbit*360/$NUM_ORBITS" | bc) # 2-pi constellations have orbits spread out across 360 degrees of latitude
	orbit_wise_shift=0
	if [[ $((num_orbit % 2)) -eq 1 ]] 
   	then 
		if [[ $PHASE_DIFF -eq "Y" ]] # Every alternate orbit has a phase shift to uniformly spread the satellites over the earth
		then
			orbit_wise_shift=$(echo "scale=2; 360 / ($NUM_SATS_PER_ORBIT * 2)" | bc); 
		else
			orbit_wise_shift=0
		fi
	fi
	for (( num_sat_in_orbit=0; num_sat_in_orbit<$NUM_SATS_PER_ORBIT; num_sat_in_orbit++ ))
	do		
		meanAnomaly=$(echo "scale=2; $orbit_wise_shift + ($num_sat_in_orbit * 360 / $NUM_SATS_PER_ORBIT)" | bc) # Spread satellites along an orbit
		# echo "$num_orbit $num_sat_in_orbit $raan $meanAnomaly"

		python get_sat_location.py $EPOCH $curr_t $raan $meanAnomaly $counter $num_orbit $INCLINATION $ECCENTRICITY $ARG_OF_PERIGEE $MEAN_MOTION $num_sat_in_orbit >> ../output_data_generated/sat_positions/sat_positions_$min"".txt
		last_orbit=$num_orbit
		counter=$(( $counter + 1 ))
	done
done
cat ../output_data_generated/sat_positions/sat_positions_$min"".txt | awk -F' ' '{print $1,$2,$3,$4,$5,$6/1000}' | sed -e "s/ /,/g" >> ../output_data_generated/sat_positions/sat_positions_"$min"_formatted.txt
rm ../output_data_generated/sat_positions/sat_positions_$min"".txt
echo "done for $min min"