###  Copyright (c) 2014 Ankit Singla, Sangeetha Abdu Jyothi, Chi-Yao Hong, Lucian Popa, P. Brighten Godfrey, Alexandra Kolla
###  

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
