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
#
#Note: This script has been adopted from https://github.com/ndal-eth/topobench 

### STYLING

# Terminal (gnuplot 4.4+); Swiss neutral Helvetica font
set terminal pngcairo font "Helvetica, 18" linewidth 1.5 rounded dashed


# Line style for axes
set style line 80 lt rgb "#808080"

# Line style for grid
set style line 81 lt 0  # Dashed
set style line 81 lt rgb "#cccccc"  # Grey grid

# Grey grid and border
set grid back linestyle 81
set border 3 back linestyle 80
set xtics nomirror
set ytics nomirror

# Line styles
set style line 1 lt rgb "#2177b0" lw 2.4 pt 6 ps 1.4
set style line 2 lt rgb "#fc7f2b" lw 2.4 pt 1 ps 1.4
set style line 3 lt rgb "#2f9e37" lw 2.4 pt 2 ps 1.4
set style line 4 lt rgb "#d42a2d" lw 2.4 pt 8 ps 1.4
set style line 5 lt rgb "#80007F" lw 2.4 pt 4 ps 1.4
set style line 6 lt rgb "#8a554c" lw 2.4 pt 3 ps 1.4
set style line 7 lt rgb "#e079be" lw 2.4 pt 5 ps 1.4
set style line 8 lt rgb "#7d7d7d" lw 2.4 pt 7 ps 1.4
set style line 9 lt rgb "#000000" lw 2.4 pt 9 ps 1.4
set style line 10 lt rgb "#fc7f2b" lw 2.4 pt 1 ps 1.4 dt 3

#####################################

set output "motif_compare.png"
set xlabel 'Avg Hop Count'
set ylabel 'Avg Stretch'

set xrange [4.5:6.5]
set yrange [1.2:2]

set key bottom left 
set key Left reverse

set datafile separator ","

plot "single_motif/level_0_motif_metrics.txt" using 5:4 title "" with points lc rgb "#2f9e37" lw 0.3 pt 7 ps 0.5 ,  \
