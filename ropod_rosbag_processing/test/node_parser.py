from ropod_rosbag_processing.utils.utils import load_yaml
from ropod_rosbag_processing.graph.node import TravelNode


if __name__ == '__main__':
    config = "../config/config_ethan.yaml"
    config_params = load_yaml(config)
    nodes_dict = config_params.get('nodes')
    nodes = TravelNode.get_travel_nodes(nodes_dict)


