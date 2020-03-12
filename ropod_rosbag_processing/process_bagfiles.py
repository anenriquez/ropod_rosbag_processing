import os
import shutil

import rosbag
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.graph.pose import Pose
from ropod_rosbag_processing.process_files.travel_logger import TravelLogger
from ropod_rosbag_processing.utils.utils import load_yaml

MERGED_BAGFILES_DIR = '/home/ropod/merged_bags/'
PROCESSED_DIR = '/home/ropod/processed_bags/'


def get_joined_bagfiles(path):
    bagfiles = list()
    for root, directories, files in os.walk(path):
        for file in files:
            if file.endswith('joined.bag'):
                bagfiles.append(os.path.join(file))
    bagfiles.sort()
    return bagfiles


def get_travel_loggers(path):
    travel_loggers = list()

    # map_directories = [x[0] for x in os.walk(path)]
    # map_directories = map_directories[1:]

    map_directories = ['config/maps/osm']
    print("map directories: ", map_directories)

    for directory in map_directories:
        config = load_yaml(directory + "/edges.yaml")
        nodes = load_yaml(directory + "/nodes.yaml")
        for logger_name, logger_config in config.items():
            print("Logger name: ", logger_name)
            travel_logger = get_travel_logger(logger_name, logger_config, nodes)
            travel_loggers.append(travel_logger)
    return travel_loggers


def get_travel_logger(logger_name, logger_config, nodes):
    nodes_of_interest = get_nodes_of_interest(nodes, logger_config)
    edges_of_interest = get_edges_of_interest(logger_config)
    logger_config.update(logger_name=logger_name)
    logger_config.update(nodes_of_interest=nodes_of_interest)
    logger_config.update(edges_of_interest=edges_of_interest)
    return TravelLogger(**logger_config)


def get_nodes_of_interest(nodes, logger_config):
    nodes_of_interest = dict()
    for edge in logger_config.get("edges"):
        nodes_of_interest[str(edge[0])] = nodes.get(edge[0])
        nodes_of_interest[str(edge[1])] = nodes.get(edge[1])
    return TravelNode.get_travel_nodes(nodes_of_interest)


def get_edges_of_interest(logger_config):
    edges_of_interest = list()
    for edge in logger_config.get("edges"):
        edges_of_interest.append(str(edge[0]) + '_to_' + str(edge[1]))
        edges_of_interest.append(str(edge[1]) + '_to_' + str(edge[0]))
    return edges_of_interest


def update_travel_logger(bagfile, travel_loggers):

    bag = rosbag.Bag(MERGED_BAGFILES_DIR + bagfile)
    prev_time = None

    for topic, msg, cur_time in bag.read_messages():

        if "/amcl_pose" in topic:
            ros_pose = msg.pose.pose.position
            cur_pose = Pose(ros_pose.x, ros_pose.y, ros_pose.z)

            for travel_logger in travel_loggers:
                travel_logger.update_pose(cur_pose, cur_time)

        if "/autonomous_navigation/local_costmap/costmap" in topic:
            if prev_time is None or cur_time.secs - prev_time.secs >= 1:
                prev_time = cur_time
                costmap = msg.data

                cur_pose = Pose(msg.info.origin.position.x, msg.info.origin.position.y, msg.info.origin.position.z)

                for travel_logger in travel_loggers:
                    travel_logger.update_costmap(cur_time, costmap, cur_pose)


def process():
    bagfiles = get_joined_bagfiles(MERGED_BAGFILES_DIR)

    for bagfile in bagfiles:
        print("Processing bagfile: ", bagfile)

        travel_loggers = get_travel_loggers('config/maps/')

        update_travel_logger(bagfile, travel_loggers)

        for i, travel_logger in enumerate(travel_loggers):
            print(travel_logger.get_history())
            travel_logger.to_file(file_suffix=bagfile.replace('.bag', '.txt'))
            # This should only be done for bagfiles without obstacles!
            # travel_logger.obstacle_ground_truth_to_file()
            travel_logger.dynamic_obstacles_to_file()

        print("Moving {} to processed bagfiles".format(bagfile))
        try:
            shutil.move(MERGED_BAGFILES_DIR + bagfile, PROCESSED_DIR)
        except shutil.Error as err:
            print("The file already exists in the destination")


if __name__ == '__main__':
    process()



