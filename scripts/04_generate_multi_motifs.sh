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

# Arguments:
#   $1: constellation (options: 40_40_53deg, kuiper_p1, starlink_p1)
#   $2: max_isl_length (options: 5014/1467 (for 40_40_53deg), 5440/1761 (kuiper_p1), 5014/2006 (starlink_p1))
#   $3: number of cores assigned to the routine
# Example: ./04_generate_multi_motifs.sh 40_40_53deg 5014 7

# Remove old data
rm ../output_data_generated/multi_motif/*

# Run script that generates all 3-zone multi_motifs
python3 find_multi_motifs.py $1 $2 $3
