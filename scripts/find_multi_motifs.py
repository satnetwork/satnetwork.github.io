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
G_baseline = nx.Graph()
sat_positions = {}
city_positions = {}
city_coverage = {}
city_pairs = {}
orb_0_sat_positions = {}
valid_isls = {}


def read_sat_positions(sat_pos_file):
    """
    Reads satellite positions from input file
    :param sat_pos_file: input file containing satellite positions at a particular instant of time
    """
    global G
    global sat_positions
    global orb_0_sat_positions
    sat_positions = {}
    orb_0_sat_positions = {}
    cnt = 0
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
        if cnt < NUM_SATS_PER_ORBIT / 4 and int(val[1]) == 0:  # we need first quadrant of satellites
            orb_0_sat_positions[int(val[0])] = {
                "orb_id": int(val[1]),
                "orb_sat_id": int(val[2]),
                "lat_deg": float(val[3]),
                "lat_rad": math.radians(float(val[3])),
                "long_deg": float(val[4]),
                "long_rad": math.radians(float(val[4])),
                "alt_km": float(val[5])
            }
            cnt += 1


def find_sat_with_min_motifs(lat, next_lat):
    """
    Gets the satellite with the minimum number of motifs for a specific latitude ring
    :param lat: The lower latitude
    :param next_lat: The upper latitude
    :return: Satellite id for the satellite with the minimum number of motifs
    """
    sat_id = -1
    min_motifs = 9999999
    for index in range(len(orb_0_sat_positions)):
        if lat < orb_0_sat_positions[index]["lat_deg"] < next_lat:
            num_motifs = len(find_motifs_for_lat(index))
            if num_motifs < min_motifs:
                min_motifs = num_motifs
                sat_id = index
    return sat_id


def find_motifs_for_lat(sat_id):
    """
    Get all feasible north and right links for a specific satellite
    :param sat_id: Satellite id
    :return: Collection of motif possibilities for the satellite
    """
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


def find_motif_possibilities(lat, next_lat):
    """
    Get all feasible north and right links for a specific latitude range
    :param lat: The lower latitude
    :param next_lat: The upper latitude
    :return: Collection of motif possibilities for the latitude ring
    """
    lat_buffered = lat - 2
    sat_id = find_sat_with_min_motifs(lat_buffered, next_lat)
    print("sat id with min motifs", lat, ":", sat_id)
    orbit_offset = NUM_ORBITS / 4
    valid_motif_links = {}
    valid_link_cnt = 0
    for i in range(len(valid_isls)):
        if valid_isls[i]["sat_1"] == sat_id and valid_isls[i]["sat_2"] > sat_id and \
                sat_positions[valid_isls[i]["sat_2"]]["orb_id"] < orbit_offset:
            orb_id = math.floor(valid_isls[i]["sat_2"] / NUM_SATS_PER_ORBIT)
            sat_rel_id = valid_isls[i]["sat_2"] - sat_id - orb_id * NUM_SATS_PER_ORBIT
            if sat_rel_id - sat_id > NUM_SATS_PER_ORBIT / 4:
                sat_rel_id = sat_rel_id - NUM_SATS_PER_ORBIT
            if not (orb_id == 0 and sat_rel_id < 0):
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
                    "M1": -1.0,
                    "M2": -1.0,
                    "future": None
                }
                motif_cnt += 1
    return motif_possibilities


def add_motif_links_to_graph(grph, motif, lat_level, lat_color):
    """
    Adds ISLs to graph based on the current motif
    :param grph: The graph under consideration with nodes being the satellites and/or cities
    :param motif: Motif containing the relative positions of the neighboring satellites
    :param lat_level: The zone for which the motif is added
    :param lat_color:  The assigned color for this zone
    :return: Updated graph
    """
    for i in sat_positions:
        sel_sat_id = util.get_neighbor_satellite(sat_positions[i]["orb_id"], sat_positions[i]["orb_sat_id"],
                                                 motif["sat_1_orb_offset"], motif["sat_1_sat_offset"], sat_positions,
                                                 NUM_ORBITS, NUM_SATS_PER_ORBIT)
        is_possible = util.check_edge_availability(grph, i, sel_sat_id)
        if is_possible and math.fabs(sat_positions[i]["lat_deg"]) > lat_level and math.fabs(
                sat_positions[sel_sat_id]["lat_deg"]) > lat_level:
            dist = util.compute_isl_length(i, sel_sat_id, sat_positions)
            grph.add_edge(i, sel_sat_id, length=dist, color=lat_color, level=lat_level)
        sel_sat_id = util.get_neighbor_satellite(sat_positions[i]["orb_id"], sat_positions[i]["orb_sat_id"],
                                                 motif["sat_2_orb_offset"], motif["sat_2_sat_offset"], sat_positions,
                                                 NUM_ORBITS, NUM_SATS_PER_ORBIT)
        is_possible = util.check_edge_availability(grph, i, sel_sat_id)
        if is_possible and math.fabs(sat_positions[i]["lat_deg"]) > lat_level and math.fabs(
                sat_positions[sel_sat_id]["lat_deg"]) > lat_level:
            dist = util.compute_isl_length(i, sel_sat_id, sat_positions)
            grph.add_edge(i, sel_sat_id, length=dist, color=lat_color, level=lat_level)
    print("total edges", grph.number_of_edges())
    return grph


def add_motif_links_to_graph_in_range(motif, lat_level_bottom, lat_level_top, lat_color):
    """
    Add ISLs to the master graph only within the zone specified by the upper and lower latitudes
    :param motif: The selected optimal motif
    :param lat_level_bottom: The lower latitude
    :param lat_level_top: The upper latitude
    :param lat_color: The assigned color for this zone
    """
    global G
    print("adding edges to final graph")
    for i in sat_positions:
        sel_sat_id = util.get_neighbor_satellite(sat_positions[i]["orb_id"], sat_positions[i]["orb_sat_id"],
                                                 motif["sat_1_orb_offset"], motif["sat_1_sat_offset"], sat_positions,
                                                 NUM_ORBITS, NUM_SATS_PER_ORBIT)
        is_possible = util.check_edge_availability(G, i, sel_sat_id)
        is_in_range = check_edge_range(i, sel_sat_id, lat_level_bottom, lat_level_top)
        if is_possible and is_in_range and math.fabs(sat_positions[i]["lat_deg"]) > lat_level_bottom and math.fabs(
                sat_positions[sel_sat_id]["lat_deg"]) > lat_level_bottom:
            dist = util.compute_isl_length(i, sel_sat_id, sat_positions)
            G.add_edge(i, sel_sat_id, length=dist, color=lat_color, level=lat_level_bottom)
        sel_sat_id = util.get_neighbor_satellite(sat_positions[i]["orb_id"], sat_positions[i]["orb_sat_id"],
                                                 motif["sat_2_orb_offset"], motif["sat_2_sat_offset"], sat_positions,
                                                 NUM_ORBITS, NUM_SATS_PER_ORBIT)
        is_possible = util.check_edge_availability(G, i, sel_sat_id)
        is_in_range = check_edge_range(i, sel_sat_id, lat_level_bottom, lat_level_top)
        if is_possible and is_in_range and math.fabs(sat_positions[i]["lat_deg"]) > lat_level_bottom and math.fabs(
                sat_positions[sel_sat_id]["lat_deg"]) > lat_level_bottom:
            dist = util.compute_isl_length(i, sel_sat_id, sat_positions)
            G.add_edge(i, sel_sat_id, length=dist, color=lat_color, level=lat_level_bottom)


def check_edge_range(sat1, sat2, lat_level_bottom, thresh_lat):
    """
    Checks if the ISL lies within the zone as defined by the lower and upper latitudes
    :param sat1: Satellite 1 for the ISL
    :param sat2: Satellite 2 for the ISL
    :param lat_level_bottom: The lower latitude
    :param thresh_lat: The upper latitude
    :return: Whether the ISL lies within the zone
    """
    is_in_range = True
    if math.fabs(sat_positions[sat1]["lat_deg"]) > math.fabs(thresh_lat) \
            and math.fabs(sat_positions[sat2]["lat_deg"]) > math.fabs(thresh_lat):
        is_in_range = False
    elif math.fabs(sat_positions[sat1]["lat_deg"]) < math.fabs(lat_level_bottom) \
            and math.fabs(sat_positions[sat2]["lat_deg"]) < math.fabs(lat_level_bottom):
        is_in_range = False
    return is_in_range


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
    # print("path_through_city_cnt", path_through_city_cnt)

    avgWeightedStretch = weightedStretchSum / weightSum
    avgWeightedHopCount = weightedHopCountSum / weightSum
    wMetric = avgWeightedStretch + avgWeightedHopCount

    b = datetime.datetime.now() - a
    print("time to compute metric:", b.seconds, ", wMetric:", wMetric)

    return_val = {
        "avgWeightedStretch": avgWeightedStretch,
        "avgWeightedHopCount": avgWeightedHopCount,
        "wMetric": wMetric
    }
    return return_val


def write_edges_to_file(graph, writer):
    """
        Writes the edges of a graph to a file
        :param grph: The graph under consideration
        :param writer: Writer corresponding to output file
    """
    edges = graph.edges(data=True)
    for edge in edges:
        writer.write(str(edge[0]) + "," + str(edge[1]) + "\n")


def run_motif_analysis(grph, motif_cnt, motif, level, color, return_dict):
    """
    Runs motif analysis for individual motifs
    :param grph: The graph under consideration
    :param motif_cnt: Motif counter
    :param motif: Motif
    :param level: The latitude zone
    :param color: The assigned color for the zone
    :param return_dict: The return values
    """
    grph = add_motif_links_to_graph(grph, motif, level, color)
    retVal = compute_metric_avoid_city(grph)
    motif["wMetric"] = retVal["wMetric"]
    motif["wStretch"] = retVal["avgWeightedStretch"]
    motif["wHop"] = retVal["avgWeightedHopCount"]
    return_dict[motif_cnt] = motif


def regenerate_baseline(file):
    """
    Regenerates baseline +Grid and computes metric
    :param file: Input file containing baseline configuration
    :return: Computed metric
    """
    global G_baseline
    lines = [line.rstrip('\n') for line in open(file)]
    val = lines[0].split(",")
    lat_bottom = float(val[0])
    best_motif_at_level = {
        "sat_1_orb_offset": int(val[2]),
        "sat_1_sat_offset": int(val[3]),
        "sat_2_orb_offset": int(val[4]),
        "sat_2_sat_offset": int(val[5])
    }
    print(best_motif_at_level)
    G_baseline = add_motif_links_to_graph(G_baseline, best_motif_at_level, lat_bottom, "NONE")
    return compute_metric_avoid_city(G_baseline)


# =====================================================================
# INPUTS
# =====================================================================

config = sys.argv[1]  # 40_40_53deg, kuiper_p1, starlink_p1
max_isl_length = sys.argv[2]  # 5014/1467 (for 40_40_53deg), 5440/1761 (kuiper_p1), 5014/2006 (starlink_p1))
CORE_CNT = int(sys.argv[3])

satPositionsFile = "../input_data/constellation_" + config + "/data_sat_position/sat_positions_0.txt"
validISLFile = "../input_data/constellation_" + config + "/data_validISLs_" + max_isl_length + "/valid_ISLs_0.txt"
cityPositionsFile = "../input_data/data_cities/cities.txt"
cityCoverageFile = "../input_data/constellation_" + config + "/data_coverage/city_coverage_0.txt"
cityPairFile = "../input_data/data_cities/city_pairs_rand_5K.txt"
baseline_config_file = "../input_data/baseline_config.txt"

NUM_ORBITS = -1
NUM_SATS_PER_ORBIT = -1
if config == "40_40_53deg":
    NUM_ORBITS = 40
    NUM_SATS_PER_ORBIT = 40
elif config == "kuiper_p1":
    NUM_ORBITS = 34
    NUM_SATS_PER_ORBIT = 34
elif config == "starlink_p1":
    NUM_ORBITS = 24
    NUM_SATS_PER_ORBIT = 66
else:
    print("Unable to identify configuration: "+config)
    exit(1)

# =====================================================================
# READING INPUTS
# =====================================================================

read_sat_positions(satPositionsFile)
valid_isls = util.read_valid_isls(validISLFile)
city_positions, G = util.read_city_positions(cityPositionsFile, G)
city_coverage = util.read_city_coverage(cityCoverageFile)
city_pairs = util.read_city_pair_file(cityPairFile)
G_baseline = G.copy()

# =====================================================================
# MULTI MOTIF ROUTINE STARTS
# =====================================================================

best_motif_overall = "../output_data_generated/multi_motif/best_motif_overall.txt"
metric_reduction_file = "../output_data_generated/multi_motif/metric_improvement.txt"

levels = [0.0, 18.0, 36.0, 90.0]
colors = ["green", "blue", "red", "green", "blue"]

writer_level_wise_best_motif = open("../output_data_generated/multi_motif/level_wise_best_motif.txt", 'a+')

best_motif_metric = -1.0
# For each latitude zone, run the motif routine
for l in range(0, len(levels) - 1):
    writer_level_motif_metrics = open("../output_data_generated/multi_motif/level_" + str(l) + "_motif_metrics.txt", 'a+')
    writer_level_best_motif = open("../output_data_generated/multi_motif/level_" + str(l) + "_best_motif.txt", 'a+')
    level = levels[l]
    next_level = levels[l + 1]

    # Get all motif possibilities
    # valid_motif_possibilities = {}
    valid_motif_possibilities = find_motif_possibilities(level, next_level)

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
                            args=(G.copy(), id, valid_motif_possibilities[id], level, colors[l], return_dict))
                threads.append(p)
        for x in threads:
            x.start()
        for x in threads:
            x.join()

        for value in return_dict.values():
            valid_motif_possibilities[value["motif_cnt"]]["wMetric"] = value["wMetric"]
            valid_motif_possibilities[value["motif_cnt"]]["wStretch"] = value["wStretch"]
            valid_motif_possibilities[value["motif_cnt"]]["wHop"] = value["wHop"]

    # Get the zone-wise best motif based on the aggregated metric value
    # and print it to the zone-wise best motif file
    best_motif = util.get_best_motif_at_level(valid_motif_possibilities)
    writer_level_wise_best_motif.write(
        str(level) + "," + str(next_level) + "," + str(best_motif["wStretch"]) + "," + str(
            best_motif["wHop"]) + "," + str(best_motif["wMetric"]) + "," + str(best_motif["sat_1_orb_offset"]) + "," + str(
            best_motif["sat_1_sat_offset"]) + "," + str(best_motif["sat_2_orb_offset"]) + "," + str(
            best_motif["sat_2_sat_offset"]) + "\n")

    # Print zone-wise motif-metric mappings to output file
    for cnt in range(len(valid_motif_possibilities)):
        writer_level_motif_metrics.write(str(cnt) + "," + str(valid_motif_possibilities[cnt]["wStretch"]) + "," + str(
            valid_motif_possibilities[cnt]["wHop"]) + "," + str(valid_motif_possibilities[cnt]["wMetric"]) + "\n")
    writer_level_motif_metrics.close()
    graph = add_motif_links_to_graph(G.copy(), best_motif, level, colors[l])
    write_edges_to_file(graph, writer_level_best_motif)
    writer_level_best_motif.close()

    add_motif_links_to_graph_in_range(best_motif, level, next_level, colors[l])
    print("edges in graph", G.number_of_edges())
    best_motif_metric = best_motif["wMetric"]

# Print ISLs corresponding to the best motif
writer_best_motif_overall = open(best_motif_overall, 'a+')
write_edges_to_file(G, writer_best_motif_overall)
writer_best_motif_overall.close()

# Compute Phi-improvement over baseline
metric = regenerate_baseline(baseline_config_file)
reduction = (metric["wMetric"] - best_motif_metric) * 100 / metric["wMetric"]
print(metric["wMetric"], best_motif_metric, reduction)

writer_imp = open(metric_reduction_file, 'a+')
writer_imp.write(str(reduction))
writer_imp.close()
