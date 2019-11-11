from ropod_rosbag_processing.utils.utils import load_yaml
import os
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.process_files.travel_logger import TravelLogger
import rosbag
from ropod_rosbag_processing.graph.pose import Pose
import shutil





# TO_PROCESS_DIR = '/home/ropod/to_process_bags/'
TO_PROCESS_DIR = '/home/angela/ropod/input/'

# PROCESSED_DIR = '/home/ropod/processed_bags/'
PROCESSED_DIR = '/home/angela/ropod/input/'


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
    nodes_dict = config_params.get('nodes_of_interest')
    nodes_obj = TravelNode.get_travel_nodes(nodes_dict)
    config_params.update(nodes_of_interest=nodes_obj)
    return config_params


def update_travel_logger(bagfile, travel_loggers):

    bag = rosbag.Bag(PROCESSED_DIR+ bagfile)
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
    config_files = get_config_files('config/')
    bagfiles = get_joined_bagfiles(PROCESSED_DIR)
    print("N of bagfiles to process:", len(bagfiles))

    configs = list()

    for config_file in config_files:
        config = parse_config_file(config_file)
        configs.append(config)

    for bagfile in bagfiles:
        print("Processing bagfile: ", bagfile)

        travel_loggers = list()

        for config in configs:
            travel_loggers.append(TravelLogger(**config))

        update_travel_logger(bagfile, travel_loggers)

        for i, travel_logger in enumerate(travel_loggers):
            print(travel_logger.get_history())
            travel_logger.to_file(file_suffix=bagfile.replace('.bag', '.txt'))
            travel_logger.obstacle_ground_truth_to_file()
            travel_logger.dynamic_obstacles_to_file()

        print("Moving {} to processed bagfiles".format(bagfile))
        try:
            shutil.move(TO_PROCESS_DIR + bagfile, PROCESSED_DIR)
        except shutil.Error as err:
            print("The file already exists in the destination")


if __name__ == '__main__':
    process()

    # TODO: Move files from TO_PROCESS_DIR to PROCESSED_DIR


