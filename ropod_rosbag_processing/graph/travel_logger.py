from ropod_rosbag_processing.graph.edge import TravelEdge
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.pose import Pose

class TravelLogger:
    def __init__(self, nodes_of_interest, event_radius=.3, event_threshold=.1):
        self.edges = []
        self.at_node = False
        self.last_node = None
        self.last_time = None
        self.nodes_of_interest = nodes_of_interest
        self.event_radius = event_radius
        self.event_threshold = event_threshold

    def event_update(self, cur_pose, cur_time):
        for node in self.nodes_of_interest:
            distance = node.pose.calc_dist(cur_pose)

            # check if we've exited the node we are currently inside
            if self.at_node and self.last_node.name is node.name:
                if distance > (self.event_radius + self.event_threshold):
                    self.last_node = node
                    self.at_node = False
            else:
                # check if we've entered any new nodes
                if distance < (self.event_radius - self.event_threshold):
                    # if this isn't the first node add the edge
                    if self.last_node is not None:
                        self.edges.append(TravelEdge(self.last_node, self.last_time, node, cur_time))
                        print(len(self.edges))
                    self.last_node = node
                    self.last_time = cur_time
                    self.at_node = True

    def get_history_dict(self):
        histories = {}
        for edge in self.edges:
            if edge.name not in histories:
                histories[edge.name] = []
            histories[edge.name].append(edge)

        return histories

    def get_history(self):
        history = ""
        for edge in self.edges:
            history += str(edge)

        return history
