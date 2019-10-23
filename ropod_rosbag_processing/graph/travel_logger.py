from ropod_rosbag_processing.graph.edge import TravelEdge
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.pose import Pose
import os
NS_TO_MS = 1000000

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

    def to_file(self, dir_name="travel_log_output", file_suffix=".txt"):
        edge_histories = self.get_history_dict()
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        for edge_history in edge_histories.values():
            first_edge = edge_history[0]
            edge_name = first_edge.get_edge_name()

            out_dir = dir_name + "/" + edge_name
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
                with open(out_dir + "/HEADER.info", 'w') as header_file:  # Use file to refer to the file object
                    header_file.write("HEADER INFO: " + first_edge.get_edge_name() + " " + first_edge.get_dist_traveled_string() + "\n")
                    header_file.write("NODE NAMES: " + first_edge.start_node.name + " " + first_edge.end_node.name + "\n")
                    header_file.write("POSITIONS" + str(first_edge.start_node.pose) + " " + str(first_edge.end_node.pose) + "\n")
            out_dest = out_dir + "/" + edge_name + file_suffix

            with open(out_dest, 'w') as out_file:  # Use file to refer to the file object
                for edge in edge_history:
                    out_file.write(str(int(edge.start_time.to_sec())) + " " + str(edge.get_time_traveled()) + "\n")






