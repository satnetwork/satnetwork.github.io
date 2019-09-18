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

import math
import networkx as nx
from multiprocessing import Process
import multiprocessing
import datetime
import sys

try:
    from . import util
except (ImportError, SystemError):
    import util

EARTH_RADIUS = 6371  # km

G = nx.Graph()
sat_positions = {}
city_positions = {}
city_coverage = {}
city_pairs = {}
valid_isls = {}


def read_sat_positions(sat_pos_file):
    """
    Reads satellite positions from input file
    :param sat_pos_file: input file containing satellite positions at a particular instant of time
    """
    global G
    global sat_positions
    sat_positions = {}
    lines = [line.rstrip('\n') for line in open(sat_pos_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        sat_positions[int(val[0])] = {
            "orb_id": int(val[1]),
            "orb_sat_id": int(val[2]),
            "lat_deg": float(val[3]),
            "lat_rad": math.radians(float(val[3])),
            "long_deg": float(val[4]),
            "long_rad": math.radians(float(val[4])),
            "alt_km": float(val[5])
        }
        G.add_node(int(val[0]))


def find_motif_possibilities():
    """
    Get all feasible north and right links for the satellite with id 0
    """
    sat_id = 0
    ORB_OFFSET = NUM_ORBITS / 4
    valid_motif_links = {}
    valid_link_cnt = 0
    for i in range(len(valid_isls)):
        if valid_isls[i]["sat_1"] == sat_id and valid_isls[i]["sat_2"] > sat_id and \
                sat_positions[valid_isls[i]["sat_2"]]["orb_id"] < ORB_OFFSET:
            orb_id = math.floor(valid_isls[i]["sat_2"] / NUM_SATS_PER_ORBIT)
            sat_rel_id = valid_isls[i]["sat_2"] - sat_id - orb_id * NUM_SATS_PER_ORBIT
            if sat_rel_id - sat_id > NUM_SATS_PER_ORBIT / 4:
                sat_rel_id = sat_rel_id - NUM_SATS_PER_ORBIT
            if not (orb_id == 0 and sat_rel_id < 0):
                # print(valid_isls[i]["sat_2"], orb_id, sat_rel_id)
                valid_motif_links[valid_link_cnt] = {
                    "sat_id": valid_isls[i]["sat_2"],
                    "orb_id": orb_id,
                    "sat_rel_id": sat_rel_id
                }
                valid_link_cnt += 1
    # Combined motif possibilities
    # For same orbit, select the other link from different orbit
    motif_possibilities = {}
    motif_cnt = 0
    for i in range(len(valid_motif_links) - 1):
        for j in range(i + 1, len(valid_motif_links)):
            if not (valid_motif_links[i]["orb_id"] == 0 and valid_motif_links[j]["orb_id"] == 0) and not (
                    valid_motif_links[i]["sat_id"] == valid_motif_links[j]["sat_id"]):
                # print(valid_motif_links[i]["sat_id"], valid_motif_links[j]["sat_id"])
                motif_possibilities[motif_cnt] = {
                    "motif_cnt": motif_cnt,
                    "sat_1_id": valid_motif_links[i]["sat_id"],
                    "sat_1_orb_offset": valid_motif_links[i]["orb_id"],
                    "sat_1_sat_offset": valid_motif_links[i]["sat_rel_id"],
                    "sat_2_id": valid_motif_links[j]["sat_id"],
                    "sat_2_orb_offset": valid_motif_links[j]["orb_id"],
                    "sat_2_sat_offset": valid_motif_links[j]["sat_rel_id"],
                    "wStretch": -1.0,
                    "wHop": -1.0,
                    "wMetric": -1.0,
                    "future": None
                }
                motif_cnt += 1
    return motif_possibilities


def add_motif_links_to_graph(grph, motif):
    """
    Adds ISLs to graph based on the current motif
    :param grph: The graph under consideration with nodes being the satellites and/or cities
    :param motif: Motif containing the relative positions of the neighboring satellites
    :return: returns the updated graph
    """
    for i in sat_positions:
        sel_sat_id = util.get_neighbor_satellite(sat_positions[i]["orb_id"], sat_positions[i]["orb_sat_id"],
                                                 motif["sat_1_orb_offset"], motif["sat_1_sat_offset"], sat_positions,
                                                 NUM_ORBITS, NUM_SATS_PER_ORBIT)
        is_possible = util.check_edge_availability(grph, i, sel_sat_id)
        if is_possible:
            dist = util.compute_isl_length(i, sel_sat_id, sat_positions)
            grph.add_edge(i, sel_sat_id, length=dist)
        sel_sat_id = util.get_neighbor_satellite(sat_positions[i]["orb_id"], sat_positions[i]["orb_sat_id"],
                                                 motif["sat_2_orb_offset"], motif["sat_2_sat_offset"], sat_positions,
                                                 NUM_ORBITS, NUM_SATS_PER_ORBIT)
        is_possible = util.check_edge_availability(grph, i, sel_sat_id)
        if is_possible:
            dist = util.compute_isl_length(i, sel_sat_id, sat_positions)
            grph.add_edge(i, sel_sat_id, length=dist)
    print("total edges", grph.number_of_edges())
    return grph


def compute_metric_avoid_city(grph):
    """
    Computes city-pair wise stretch and hop count and the aggregate metric values
    :param grph: The graph with satellites and cities as nodes
    :return: Computed aggregated metric
    """
    weightSum = 0
    weightedStretchSum = 0
    weightedHopCountSum = 0
    a = datetime.datetime.now()
    for i in range(len(city_pairs)):
        city1 = city_pairs[i]["city_1"]
        city2 = city_pairs[i]["city_2"]
        geoDist = city_pairs[i]["geo_dist"]
        try:
            util.add_coverage_for_city(grph, city1, city_coverage)
            util.add_coverage_for_city(grph, city2, city_coverage)
            distance = nx.shortest_path_length(grph, source=city1, target=city2, weight='length')
            path = nx.shortest_path(grph, source=city1, target=city2, weight='length')

            hops = path.__len__() - 1
            stretch = distance / geoDist

            weight = city_positions[city1]["pop"] * city_positions[city2]["pop"] / 10000000
            weightSum += weight
            weightedStretchSum += stretch * weight
            weightedHopCountSum += hops * weight

            util.remove_coverage_for_city(grph, city1, city_coverage)
            util.remove_coverage_for_city(grph, city2, city_coverage)
        except Exception as e:
            util.remove_coverage_for_city(grph, city1, city_coverage)
            util.remove_coverage_for_city(grph, city2, city_coverage)
            return_val = {
                "avgWeightedStretch": 99999.0,
                "avgWeightedHopCount": 99999.0,
                "wMetric": 99999.0
            }
            return return_val
    avgWeightedStretch = weightedStretchSum / weightSum
    avgWeightedHopCount = weightedHopCountSum / weightSum
    wMetric = avgWeightedStretch + avgWeightedHopCount

    b = datetime.datetime.now() - a
    print("time to compute metric:", b.seconds, ", avgWeightedStretch:", avgWeightedStretch, ", avgWeightedHopCount:",
          avgWeightedHopCount)

    return_val = {
        "avgWeightedStretch": avgWeightedStretch,
        "avgWeightedHopCount": avgWeightedHopCount,
        "wMetric": wMetric
    }
    return return_val


def write_edges_to_file(grph, writer):
    """
    Writes the edges of a graph to a file
    :param grph: The graph under consideration
    :param writer: Writer corresponding to output file
    """
    edges = grph.edges(data=True)
    for edge in edges:
        writer.write(str(edge[0]) + "," + str(edge[1]) + "\n")


def run_motif_analysis(grph, motif_cnt, motif, return_dict):
    """
    Runs motif analysis for individual motifs
    :param grph: The graph under consideration
    :param motif_cnt: Motif counter
    :param motif: Motif
    :param return_dict: The return values
    """
    grph = add_motif_links_to_graph(grph, motif)
    retVal = compute_metric_avoid_city(grph)
    motif["wMetric"] = retVal["wMetric"]
    motif["wStretch"] = retVal["avgWeightedStretch"]
    motif["wHop"] = retVal["avgWeightedHopCount"]
    return_dict[motif_cnt] = motif


# =====================================================================
# INPUTS
# =====================================================================


satPositionsFile = "../input_data/constellation_40_40_53deg/data_sat_position/sat_positions_0.txt"
validISLFile = "../input_data/constellation_40_40_53deg/data_validISLs_5014/valid_ISLs_0.txt"
cityPositionsFile = "../input_data/data_cities/cities.txt"
cityCoverageFile = "../input_data/constellation_40_40_53deg/data_coverage/city_coverage_0.txt"
cityPairFile = "../input_data/data_cities/city_pairs_rand_5K.txt"
NUM_ORBITS = 40
NUM_SATS_PER_ORBIT = 40

CORE_CNT = int(sys.argv[1])

# =====================================================================
# OUTPUTS
# =====================================================================

writer_level_motif_metrics = open("../output_data_generated/single_motif/level_0_motif_metrics.txt", 'a+')
writer_level_best_motif = open("../output_data_generated/single_motif/level_0_best_motif.txt", 'a+')

# =====================================================================
# READING INPUTS
# =====================================================================

read_sat_positions(satPositionsFile)
valid_isls = util.read_valid_isls(validISLFile)
city_positions, G = util.read_city_positions(cityPositionsFile, G)
city_coverage = util.read_city_coverage(cityCoverageFile)
city_pairs = util.read_city_pair_file(cityPairFile)

# =====================================================================
# SINGLE MOTIF ROUTINE STARTS
# =====================================================================

# Get all motif possibilities
valid_motif_possibilities = find_motif_possibilities()

# For each motif compute metrics
for i in range(0, len(valid_motif_possibilities), CORE_CNT):
    threads = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    # Parallelize metric computation based on available cores
    for j in range(0, CORE_CNT):
        id = i + j
        if id < len(valid_motif_possibilities):
            print("Generating graph for motif:", valid_motif_possibilities[id]["sat_1_id"], ",",
                  valid_motif_possibilities[id]["sat_2_id"])
            p = Process(target=run_motif_analysis,
                        args=(G.copy(), id, valid_motif_possibilities[id], return_dict))
            threads.append(p)
    for x in threads:
        x.start()
    for x in threads:
        x.join()

    for value in return_dict.values():
        valid_motif_possibilities[value["motif_cnt"]]["wMetric"] = value["wMetric"]
        valid_motif_possibilities[value["motif_cnt"]]["wStretch"] = value["wStretch"]
        valid_motif_possibilities[value["motif_cnt"]]["wHop"] = value["wHop"]

# Get the best motif based on the aggregated metric value
best_motif = util.get_best_motif_at_level(valid_motif_possibilities)

# Print motif-metric mappings to output file
for cnt in range(len(valid_motif_possibilities)):
    try:
        writer_level_motif_metrics.write(str(cnt)
                                         + "," + str(valid_motif_possibilities[cnt]["sat_1_id"])
                                         + "," + str(valid_motif_possibilities[cnt]["sat_2_id"])
                                         + "," + str(valid_motif_possibilities[cnt]["wStretch"])
                                         + "," + str(valid_motif_possibilities[cnt]["wHop"])
                                         + "\n")
    except Exception as e:
        print(valid_motif_possibilities[cnt])

writer_level_motif_metrics.close()

# Print ISLs corresponding to the best motif
G = add_motif_links_to_graph(G, best_motif)
write_edges_to_file(G, writer_level_best_motif)
writer_level_best_motif.close()
