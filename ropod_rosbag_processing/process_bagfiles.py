from ropod_rosbag_processing.utils.utils import load_yaml
import os
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.utils.get_files import get_bagfiles
from ropod_rosbag_processing.graph.travel_logger import TravelLogger
import rosbag
from ropod_rosbag_processing.pose import Pose


TO_PROCESS_DIR = '../../input/'


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
    seen_topics = {}

    bag = rosbag.Bag(TO_PROCESS_DIR + bagfile)
    for topic, msg, cur_time in bag.read_messages():
        seen_topics[topic] = topic

        if "/amcl_pose" in topic:
            ros_pose = msg.pose.pose.position
            cur_pose = Pose(ros_pose.x, ros_pose.y, ros_pose.z)
            for travel_logger in travel_loggers:
                travel_logger.event_update(cur_pose, cur_time)


def process():
    config_files = get_config_files('config/')
    bagfiles = get_bagfiles(TO_PROCESS_DIR)
    travel_loggers = list()
    output_dirs = list()
    for config_file in config_files:
        nodes, output_dir = parse_config_file(config_file)
        travel_logger = TravelLogger(nodes)
        travel_loggers.append(travel_logger)
        output_dirs.append(output_dir)

    for bagfile in bagfiles:
        update_travel_logger(bagfile, travel_loggers)
        for i, travel_logger in enumerate(travel_loggers):
            print(travel_logger.get_history())
            travel_logger.to_file(output_dirs[i], file_suffix=bagfile.replace('.bag', '.txt'))

process()

    # TODO: Move files from TO_PROCESS_DIR to PROCESSED_DIR


