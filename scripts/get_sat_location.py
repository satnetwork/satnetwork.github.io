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

import ephem
import math
import sys

# Generate a satellite from orbital elements
# Check parent script 02_get_sat_positions_at_time.sh for the arguments supplied
sat1 = ephem.EarthSatellite()
sat1._epoch = sys.argv[1]+' '+sys.argv[2]
sat1._inc = ephem.degrees(float(sys.argv[9]))
sat1._e = float(sys.argv[10])
sat1._raan = ephem.degrees(float(sys.argv[5]))
sat1._ap = float(sys.argv[11])
sat1._M = ephem.degrees(float(sys.argv[6]))
sat1._n = float(sys.argv[12])
sat1.compute(sys.argv[3]+' '+sys.argv[4])
counter = sys.argv[7]
num_orbit = sys.argv[8]
num_sat_in_orbit = sys.argv[13]
# Print the satellite position in terms of coordinates and elevation
print('%d %d %d %s %s %s' % (int(counter), int(num_orbit), int(num_sat_in_orbit), math.degrees(sat1.sublat), math.degrees(sat1.sublong), sat1.elevation))
