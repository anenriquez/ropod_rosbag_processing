from ropod_rosbag_processing.utils.utils import load_yaml
import os
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.utils.get_files import get_bagfiles

TO_PROCESS_DIR = 'to_process/'


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


def process():
    config_files = get_config_files('config/')
    bagfiles = get_bagfiles(TO_PROCESS_DIR)
    for config_file in config_files:
        nodes, output_dir = parse_config_file(config_file)
        # Create TravelLogger object

    # TODO: Move files from TO_PROCESS_DIR to PROCESSED_DIR



