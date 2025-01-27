"""
This script is used to get the OSM data of a place and save it in a csv file.
The place is passed as a command line argument.

Example:
python get_osm_data.py --place "Bologna, Emilia-Romagna, Italy" --exclude-residential

The output files are:
- nodes.csv
- edges.csv

The files are saved in the current directory.
"""

from argparse import ArgumentParser
import logging
import osmnx as ox
import ast

__version__ = "2025.1.16"

RGBA_RED = (1, 0, 0, 1)
RGBA_WHITE = (1, 1, 1, 1)

FLAGS_MOTORWAY = ["motorway", "motorway_link"]
FLAGS_NORMAL = [
    "primary",
    "secondary",
    "tertiary",
    "trunk",
    "primary_link",
    "secondary_link",
    "tertiary_link",
    "trunk_link",
]
FLAGS_RESIDENTIAL = [
    "residential",
    "living_street",
    "unclassified",
    "service",
    "pedestrian",
    "busway",
]

if __name__ == "__main__":
    parser = ArgumentParser("Script to get the OSM data of a place.")
    parser.add_argument(
        "--place",
        required=True,
        help="Place to get the OSM data in the format: city, province, country",
    )
    parser.add_argument(
        "--exclude-motorway",
        action="store_true",
        help="Exclude motorways from the data. Default is False",
    )
    parser.add_argument(
        "--exclude-residential",
        action="store_true",
        help="Exclude residential roads from the data. Default is False",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Allow duplicated edges in the data. Default is False",
    )
    parser.add_argument(
        "-t",
        "--tolerance",
        type=int,
        default=20,
        help="Radius in meters to merge intersections. For more info, see osmnx documentation.",
    )
    parser = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    # set up colored logging
    logging.addLevelName(
        logging.INFO, f"\033[1;32m{logging.getLevelName(logging.INFO)}\033[1;0m"
    )
    logging.addLevelName(
        logging.WARNING, f"\033[1;33m{logging.getLevelName(logging.WARNING)}\033[1;0m"
    )
    logging.addLevelName(
        logging.ERROR, f"\033[1;31m{logging.getLevelName(logging.ERROR)}\033[1;0m"
    )

    logging.info("Welcome to get_osm_data.py v%s", __version__)

    # define CUSTOM_FILTER basing on FLAGS and args
    FLAGS = FLAGS_NORMAL
    if not parser.exclude_motorway:
        FLAGS += FLAGS_MOTORWAY
    if not parser.exclude_residential:
        FLAGS += FLAGS_RESIDENTIAL
    CUSTOM_FILTER = f"[\"highway\"~\"{'|'.join(FLAGS)}\"]"
    logging.info("Custom filter: %s", CUSTOM_FILTER)
    GRAPH = ox.graph_from_place(parser.place, network_type="drive")
    ox.plot_graph(GRAPH, show=False, close=True, save=True, filepath="./original.png")
    

    # Here it saves also the complete consolidated network without duplicates

    GRAPH = ox.consolidate_intersections(
        ox.project_graph(GRAPH), tolerance=parser.tolerance
    )
    logging.info(
        "Original network has %d nodes and %d edges.",
        len(GRAPH.nodes),
        len(GRAPH.edges),
    )

    
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(ox.project_graph(GRAPH, to_latlong=True))
    gdf_nodes.reset_index(inplace=True)
    gdf_edges.reset_index(inplace=True)





   # # # # #       ELIMINATES OSMID STRINGS         # # # # # 





    # for index, row in gdf_nodes.iterrows():
    # # if "osmid_original" is a list, keep the first element
    #     old_list = ast.literal_eval(str(row["osmid_original"]))
    #     if isinstance(old_list, list):
    #         new_id = old_list[0]
    #         # update the edges with u_original or v_original in old_list, with new_id
    #         gdf_edges.loc[gdf_edges["u_original"].isin(old_list), "u_original"] = new_id
    #         gdf_edges.loc[gdf_edges["v_original"].isin(old_list), "v_original"] = new_id
    #         # update the node with new_id
    #         gdf_nodes.loc[index, "osmid_original"] = new_id

    # assert set(gdf_edges["u_original"].astype(str)).issubset(set(gdf_nodes["osmid_original"].astype(str)))
    # assert set(gdf_edges["v_original"]).issubset(set(gdf_nodes["osmid_original"]))










    if parser.allow_duplicates:
        N_DUPLICATES = 0
    else:
        # Check for duplicate edges
        duplicated_mask = gdf_edges.duplicated(subset=["u", "v"])
        N_DUPLICATES = duplicated_mask.sum()

    if N_DUPLICATES > 0:
        logging.warning(
            "There are %d duplicated edges which will be removed. "
            "Please look at them in the promped plot.",
            N_DUPLICATES,
        )
        # Plot the graph with duplicated edges in red
        edge_colors = [
            RGBA_RED if duplicated_mask.iloc[i] else RGBA_WHITE
            for i in range(len(gdf_edges))
        ]
        ox.plot_graph(GRAPH, edge_color=edge_colors)

        # Remove duplicated edges
        gdf_edges = gdf_edges.drop_duplicates(subset=["u", "v"])



    # gdf_edges = gdf_edges[
    #     ["u", "v", "length", "oneway", "lanes", "highway", "maxspeed", "name"]
    # ]
    # gdf_nodes = gdf_nodes[["osmid", "x", "y", "highway"]]



    gdf_edges.to_csv("edges_complete.csv", sep=";", index=False)
    gdf_nodes.to_csv("nodes_complete.csv", sep=";", index=False)

    





    # Here it filters the network

    GRAPH = ox.graph_from_place(
        parser.place, network_type="drive", custom_filter=CUSTOM_FILTER
    )
    logging.info(
        "Custom filtered graph has %d nodes and %d edges.",
        len(GRAPH.nodes),
        len(GRAPH.edges),
    )
    GRAPH = ox.consolidate_intersections(
        ox.project_graph(GRAPH), tolerance=parser.tolerance
    )
    logging.info(
        "Consolidated graph has %d nodes and %d edges.",
        len(GRAPH.nodes),
        len(GRAPH.edges),
    )
    # plot graph on a 16x9 figure and save into file
    ox.plot_graph(GRAPH, show=False, close=True, save=True, filepath="./final.png")
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(ox.project_graph(GRAPH, to_latlong=True))
    # notice that osmnid is the index of the gdf_nodes DataFrame, so take it as a column
    gdf_nodes.reset_index(inplace=True)
    gdf_edges.reset_index(inplace=True)




   # # # # #       ELIMINATES OSMID STRINGS         # # # # # 






    for index, row in gdf_nodes.iterrows():
    # if "osmid_original" is a list, keep the first element
        old_list = ast.literal_eval(str(row["osmid_original"]))
        if isinstance(old_list, list):
            new_id = old_list[0]
            # update the edges with u_original or v_original in old_list, with new_id
            gdf_edges.loc[gdf_edges["u_original"].isin(old_list), "u_original"] = new_id
            gdf_edges.loc[gdf_edges["v_original"].isin(old_list), "v_original"] = new_id
            # update the node with new_id
            gdf_nodes.loc[index, "osmid_original"] = new_id


    assert set(gdf_edges["u_original"].astype(str)).issubset(set(gdf_nodes["osmid_original"].astype(str)))
    assert set(gdf_edges["v_original"]).issubset(set(gdf_nodes["osmid_original"]))









    # #Prepare node dataframe
    # gdf_nodes = gdf_nodes[["osmid", "x", "y", "highway"]]
    # #Prepare edge dataframe


    # gdf_edges = gdf_edges[
    #     ["u", "v", "length", "oneway", "lanes", "highway", "maxspeed", "name"]
    # ]
    if parser.allow_duplicates:
        N_DUPLICATES = 0
    else:
        # Check for duplicate edges
        duplicated_mask = gdf_edges.duplicated(subset=["u", "v"])
        N_DUPLICATES = duplicated_mask.sum()

    if N_DUPLICATES > 0:
        logging.warning(
            "There are %d duplicated edges which will be removed. "
            "Please look at them in the promped plot.",
            N_DUPLICATES,
        )
        # Plot the graph with duplicated edges in red
        edge_colors = [
            RGBA_RED if duplicated_mask.iloc[i] else RGBA_WHITE
            for i in range(len(gdf_edges))
        ]
        ox.plot_graph(GRAPH, edge_color=edge_colors)

        # Remove duplicated edges
        gdf_edges = gdf_edges.drop_duplicates(subset=["u", "v"])



        
    # Save the data
    place = parser.place.split(",")[0].strip().lower()
    gdf_nodes.to_csv(f"{place}_nodes_p.csv", sep=";", index=False)
    logging.info('Nodes correctly saved in "%s_nodes_p.csv"', place)
    gdf_edges.to_csv(f"{place}_edges_p.csv", sep=";", index=False)
    logging.info('Edges correctly saved in "%s_edges_p.csv"', place)
