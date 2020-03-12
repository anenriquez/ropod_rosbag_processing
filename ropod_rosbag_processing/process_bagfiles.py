import os
import shutil

import rosbag
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.graph.pose import Pose
from ropod_rosbag_processing.process_files.travel_logger import TravelLogger
from ropod_rosbag_processing.utils.utils import load_yaml

MERGED_BAGFILES_DIR = '/home/ropod/merged_bags/'
PROCESSED_DIR = '/home/ropod/processed_bags/'
NODES_FILE = 'config/nodes.yaml'


def get_joined_bagfiles(path):
    bagfiles = list()
    for root, directories, files in os.walk(path):
        for file in files:
            if file.endswith('joined.bag'):
                bagfiles.append(os.path.join(file))
    bagfiles.sort()
    return bagfiles


def get_config_files(path):
    config_files = list()
    for root, directories, files in os.walk(path):
        for file in files:
            if file.endswith('.yaml'):
                config_files.append(os.path.join(root, file))
    return config_files


def parse_config_file(config_file):
    config_params = load_yaml(config_file)
    config_params = get_nodes(config_params)
    config_params = get_edges(config_params)
    return config_params


def get_nodes(config_params):
    all_nodes = load_yaml(NODES_FILE)
    nodes_of_interest = dict()
    edges = config_params.get('edges')

    for edge in edges:
        nodes_of_interest[edge[0]] = all_nodes.get(edge[0])
        nodes_of_interest[edge[1]] = all_nodes.get((edge[1]))

    nodes_obj = TravelNode.get_travel_nodes(nodes_of_interest)
    config_params.update(nodes_of_interest=nodes_obj)
    return config_params


def get_edges(config_params):
    edges_list = config_params.pop('edges')
    edge_names = list()
    for edge in edges_list:
        edge_names.append(edge[0] + '_to_' + edge[1])
        edge_names.append(edge[1] + '_to_' + edge[0])
    config_params.update(edges_of_interest=edge_names)
    return config_params


def update_travel_logger(bagfile, travel_loggers):

    try:

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

    except rosbag.ROSBagUnindexedException:
        print("Unindexed bag: ", bagfile)
        raise rosbag.ROSBagUnindexedException

def process():
    config_files_angela = get_config_files('config/angela/')
    config_files_ethan = get_config_files('config/ethan/')
    config_files = config_files_angela + config_files_ethan
    print(config_files)
    bagfiles = get_joined_bagfiles(MERGED_BAGFILES_DIR)
    print("N of bagfiles to process:", len(bagfiles))

    configs = list()

    for config_file in config_files:
        config = parse_config_file(config_file)
        configs.append(config)

    for bagfile in bagfiles:
        print("Processing bagfile: ", bagfile)
        move = True

        travel_loggers = list()

        for config in configs:
            travel_loggers.append(TravelLogger(**config))

        try:
            update_travel_logger(bagfile, travel_loggers)
        except rosbag.ROSBagUnindexedException:
            print("Unindexed bag: ", bagfile)
            move = False

        for i, travel_logger in enumerate(travel_loggers):
            print(travel_logger.get_history())
            travel_logger.to_file(file_suffix=bagfile.replace('.bag', '.txt'))
            # This should only be done for bagfiles without obstacles!
            # travel_logger.obstacle_ground_truth_to_file()
            travel_logger.dynamic_obstacles_to_file()

        if move:
            print("Moving {} to processed bagfiles".format(bagfile))
            try:
                shutil.move(MERGED_BAGFILES_DIR + bagfile, PROCESSED_DIR)
            except shutil.Error as err:
                print("The file already exists in the destination")


if __name__ == '__main__':
    process()



