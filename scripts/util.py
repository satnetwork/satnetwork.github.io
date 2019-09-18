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

EARTH_RADIUS = 6371  # Kms


def compute_isl_length(sat1, sat2, sat_positions):
    """
    Computes ISL length between pair of satellites. This function can also be used to compute
    city-satellite up/down-link length.
    :param sat1: Satellite 1 with position information (latitude, longitude, altitude)
    :param sat2: Satellite 2 with position information (latitude, longitude, altitude)
    :param sat_positions: Collection of satellites along with their current position data
    :return: ISl length in km
    """
    x1 = (EARTH_RADIUS + sat_positions[sat1]["alt_km"]) * math.cos(sat_positions[sat1]["lat_rad"]) * math.sin(
        sat_positions[sat1]["long_rad"])
    y1 = (EARTH_RADIUS + sat_positions[sat1]["alt_km"]) * math.sin(sat_positions[sat1]["lat_rad"])
    z1 = (EARTH_RADIUS + sat_positions[sat1]["alt_km"]) * math.cos(sat_positions[sat1]["lat_rad"]) * math.cos(
        sat_positions[sat1]["long_rad"])
    x2 = (EARTH_RADIUS + sat_positions[sat2]["alt_km"]) * math.cos(sat_positions[sat2]["lat_rad"]) * math.sin(
        sat_positions[sat2]["long_rad"])
    y2 = (EARTH_RADIUS + sat_positions[sat2]["alt_km"]) * math.sin(sat_positions[sat2]["lat_rad"])
    z2 = (EARTH_RADIUS + sat_positions[sat2]["alt_km"]) * math.cos(sat_positions[sat2]["lat_rad"]) * math.cos(
        sat_positions[sat2]["long_rad"])
    dist = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2) + math.pow((z2 - z1), 2))
    return dist


def read_city_positions(city_pos_file, graph):
    """
    eads city coordinates and population
    :param city_pos_file: file containing city coordinates and population
    :param graph: The graph to populate
    :return: collection of cities with coordinates and populations, updated graph
    """
    city_positions = {}
    lines = [line.rstrip('\n') for line in open(city_pos_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        city_positions[int(val[0])] = {
            "lat_deg": float(val[2]),
            "long_deg": float(val[3]),
            "pop": float(val[4])
        }
        graph.add_node(int(val[0]))
    return city_positions, graph


def read_valid_isls(valid_isl_file):
    """
    Reads ISLs which are sorter than the maximum allowed distance at this height
    :param valid_isl_file: File containing ISLs : satellite 1, satellite 2, ISL length in km
    :return: Collection of valid ISLs
    """
    valid_isls = {}
    lines = [line.rstrip('\n') for line in open(valid_isl_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        valid_isls[i] = {
            "sat_1": int(val[0]),
            "sat_2": int(val[1]),
            "dist_km": float(val[2])
        }
    return valid_isls


def read_city_coverage(coverage_file):
    """
    Reads city covrage in terms of which satellites a city can communicate with
    :param coverage_file: This file holds the city-satellite mapping along with the up/down-link distance in km
    :return: Collection of city-satellite mappings
    """
    city_coverage = {}
    lines = [line.rstrip('\n') for line in open(coverage_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        city_coverage[i] = {
            "city": int(val[0]),
            "sat": int(val[1]),
            "dist": float(val[2])
        }
    return city_coverage


def read_city_pair_file(city_pair_file):
    """
    Reads the city pairs to be considered while computing the performance metric.
    :param city_pair_file:  This file contains city pairs and the geodesic distance in km between them
    :return: Collection of city-city geodesic distances
    """
    city_pairs = {}
    lines = [line.rstrip('\n') for line in open(city_pair_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        city_pairs[i] = {
            "city_1": int(val[0]),
            "city_2": int(val[1]),
            "geo_dist": float(val[2])
        }
    return city_pairs


def get_neighbor_satellite(sat1_orb, sat1_rel_id, sat2_orb, sat2_rel_id, sat_positions, num_orbits, num_sats_per_orbit):
    """
    Get the absolute id of the neighbor satellite from relative ids
    :param sat1_orb: orbit id of satellite 1
    :param sat1_rel_id: relative id within orbit for satellite 1
    :param sat2_orb: orbit id of satellite 2
    :param sat2_rel_id: relative id within orbit for satellite 2
    :param sat_positions: Collection of satellites with position data
    :param num_orbits: Number of orbits in the constellation
    :param num_sats_per_orbit: Number of satellites per orbit
    :return: absolute id of the neighbor satellite
    """
    neighbor_abs_orb = (sat1_orb + sat2_orb) % num_orbits
    neighbor_abs_pos = (sat1_rel_id + sat2_rel_id) % num_sats_per_orbit
    sel_sat_id = -1
    for sat_id in sat_positions:
        if sat_positions[sat_id]["orb_id"] == neighbor_abs_orb \
                and sat_positions[sat_id]["orb_sat_id"] == neighbor_abs_pos:
            sel_sat_id = sat_id
            break
    return sel_sat_id


def check_edge_availability(graph, node1, node2):
    """
    Checks if an edge between 2 satellites is possible considering each satellite can have at most 4 ISLs
    :param graph: The graph under consideration with nodes being the satellites and/or cities
    :param node1: Denotes satellite 1
    :param node2: Denotes satellite 2
    :return: Decision whether an ISL is possible given the current degrees of the 2 nodes
    """
    is_possible = True
    deg1 = graph.degree(node1)
    deg2 = graph.degree(node2)
    if deg1 > 3 or deg2 > 3:
        is_possible = False
    return is_possible


def add_coverage_for_city(graph, city, city_coverage):
    """
    Adds city-satellite up/down-links to the graph
    :param graph: The graph under consideration with nodes being the satellites and/or cities
    :param city: The city for which coverage needs to be added
    :param city_coverage: Collection of city-satellite mappings
    :return: Updated graph
    """
    for i in range(len(city_coverage)):
        if city_coverage[i]["city"] == city:
            graph.add_edge(city_coverage[i]["city"], city_coverage[i]["sat"], length=city_coverage[i]["dist"])
    return graph


def remove_coverage_for_city(graph, city, city_coverage):
    """
    Removes city-satellite up/down-links from the graph
    :param grph: The graph under consideration with nodes being the satellites and/or cities
    :param city: The city for which coverage needs to be removed
    :param city_coverage: Collection of city-satellite mappings
    :return: Updated graph
    """
    for i in range(len(city_coverage)):
        if city_coverage[i]["city"] == city:
            graph.remove_edge(city_coverage[i]["city"], city_coverage[i]["sat"])
    return graph


def get_best_motif_at_level(motifs):
    """
    Gets the motif with the best (minimum) aggregated metric value
    :param motifs: Collection of motifs with computed aggregated metric values
    :return: Best motif in terms of the metric
    """
    min_metric = 999999.0
    min_motif = None
    for i in range(len(motifs)):
        try:
            if motifs[i]["wMetric"] < min_metric:
                min_metric = motifs[i]["wMetric"]
                min_motif = motifs[i]
        except Exception as e:
            pass
    return min_motif
