import os

from ropod_rosbag_processing.graph.edge import TravelEdge
from ropod_rosbag_processing.graph.travel_obstacles import TravelObstacle
from ropod_rosbag_processing.utils.costmap_processing import from_costmap_to_coordinates
from ropod_rosbag_processing.utils.costmap_processing import get_n_obstacles

NS_TO_MS = 1000000


class TravelLogger:
    def __init__(self, nodes_of_interest, event_radius=.5, event_threshold=.1):
        self.edges = []
        self.travel_obstacles = {}
        self.cur_travel_obstacle = TravelObstacle()
        self.at_node = False
        self.last_node = None
        self.last_time = None
        self.nodes_of_interest = nodes_of_interest
        self.event_radius = event_radius
        self.event_threshold = event_threshold

    def update_pose(self, cur_pose, cur_time):
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
                        self.cur_travel_obstacle.set_edge_name(self.edges[-1].get_edge_name())

                        if self.cur_travel_obstacle.edge_name not in self.travel_obstacles:
                            self.travel_obstacles[self.cur_travel_obstacle.edge_name] = []
                        self.travel_obstacles[self.cur_travel_obstacle.edge_name].append(self.cur_travel_obstacle)

                        print("Edges: ", [edge.get_edge_name() for edge in self.edges])
                        print("Current travel obstacle \n", self.cur_travel_obstacle)
                        self.cur_travel_obstacle = TravelObstacle()

                    self.last_node = node
                    self.last_time = cur_time
                    self.at_node = True

    def update_costmap(self, cur_time, costmap):
        coordinates = from_costmap_to_coordinates(costmap)
        if coordinates.any():
            n_obstacles = get_n_obstacles(coordinates)
            self.cur_travel_obstacle.update_obstacle_info(cur_time, n_obstacles)

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
        travel_time_dir = dir_name + '/travel_time'
        obstacles_dir = dir_name + '/obstacles'

        if not os.path.exists(travel_time_dir):
            os.makedirs(travel_time_dir)

        if not os.path.exists(obstacles_dir):
            os.makedirs(obstacles_dir)

        self.travel_time_to_file(travel_time_dir, file_suffix)
        self.obstacle_to_file(obstacles_dir, file_suffix)

    def travel_time_to_file(self, dir_name, file_suffix=".txt"):
        edge_histories = self.get_history_dict()
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

    def obstacle_to_file(self, dir_name, file_suffix=".txt"):
        for edge_name, obstacles in self.travel_obstacles.items():
            out_dir = dir_name + "/" + edge_name

            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            out_dest = out_dir + "/" + edge_name + file_suffix
            with open(out_dest, 'w') as out_file:  # Use file to refer to the file object
                for obstacle in obstacles:
                    if obstacle.obstacle_info:
                        for info in obstacle.obstacle_info:
                            out_file.write(str(int(info[0].to_sec())) + " " + str(info[1]) + "\n")





