from ropod_rosbag_processing.utils.utils import load_yaml
from ropod_rosbag_processing.graph.node import TravelNode


def get_travel_nodes(nodes_dict):
    nodes = list()
    for name, pose in nodes_dict.items():
        travel_node = TravelNode.from_dict({'name': name,
                                            'pose': pose})
        print(travel_node)
        nodes.append(travel_node)

    return nodes


if __name__ == '__main__':
    config = "../config/config.yaml"
    config_params = load_yaml(config)
    nodes_dict = config_params.get('nodes')
    nodes = get_travel_nodes(nodes_dict)


