from ropod_rosbag_processing.utils.utils import load_yaml
import os
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.graph.travel_logger import TravelLogger
import rosbag
from ropod_rosbag_processing.pose import Pose
import shutil


TO_PROCESS_DIR = '/home/ropod/to_process_bags/'
PROCESSED_DIR = '/home/ropod/processed_bags/'


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
    nodes_dict = config_params.get('nodes')
    nodes = TravelNode.get_travel_nodes(nodes_dict)
    output_dir = config_params.get('output')
    return nodes, output_dir


def update_travel_logger(bagfile, travel_loggers):

    bag = rosbag.Bag(TO_PROCESS_DIR + bagfile)
    for topic, msg, cur_time in bag.read_messages():

        if "/amcl_pose" in topic:
            ros_pose = msg.pose.pose.position
            cur_pose = Pose(ros_pose.x, ros_pose.y, ros_pose.z)
            for travel_logger in travel_loggers:
                travel_logger.event_update(cur_pose, cur_time)


def process():
    config_files = get_config_files('config/')
    bagfiles = get_joined_bagfiles(TO_PROCESS_DIR)

    output_dirs = list()
    nodes_of_interest = list()

    for config_file in config_files:
        nodes, output_dir = parse_config_file(config_file)
        output_dirs.append(output_dir)
        nodes_of_interest.append(nodes)

    for bagfile in bagfiles:
        print("Processing bagfile: ", bagfile)

        travel_loggers = list()

        for i, nodes in enumerate(nodes_of_interest):
            travel_loggers.append(TravelLogger(nodes))

        update_travel_logger(bagfile, travel_loggers)

        for i, travel_logger in enumerate(travel_loggers):
            print(travel_logger.get_history())
            travel_logger.to_file(output_dirs[i], file_suffix=bagfile.replace('.bag', '.txt'))

        print("Moving {} to processed bagfiles".format(bagfile)
        try:
            shutil.move(TO_PROCESS_DIR + bagfile, PROCESSED_DIR)
        except shutil.Error as err:
            print("The file already exists in the destination")

if __name__ == '__main__':
    process()

    # TODO: Move files from TO_PROCESS_DIR to PROCESSED_DIR



