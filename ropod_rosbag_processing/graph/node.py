from ropod_rosbag_processing.pose import Pose


class TravelNode:
    def __init__(self, name, pose):
        self.name = name
        self.pose = pose

    def __str__(self):
        to_print = ""
        to_print += "{}: {}".format(self.name, self.pose)
        return to_print

    @classmethod
    def from_dict(cls, travel_node_dict):
        """
        Converts a dictionary to a TravelNode object
        Entries:
        -    key: name
             value (str): Name of the node

        -    key: pose
             value (list): Position and orientation in the map [x, y, z]

        Returns:
            TravelNode object
        """
        name = travel_node_dict.get('name')
        x, y, z = travel_node_dict.get('pose')
        pose = Pose(x, y, z)
        travel_node = cls(name, pose)
        return travel_node

    def to_dict(self):
        travel_node_dict = dict()
        travel_node_dict['name'] = self.name
        travel_node_dict['pose'] = [self.pose.x, self.pose.y, self.pose.z]
        return travel_node_dict

    @staticmethod
    def get_travel_nodes(nodes_dict):
        nodes = list()
        for name, pose in nodes_dict.items():
            travel_node = TravelNode.from_dict({'name': name,
                                                'pose': pose})
            print(travel_node)
            nodes.append(travel_node)

        return nodes
