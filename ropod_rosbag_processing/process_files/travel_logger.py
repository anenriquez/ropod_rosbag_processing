from ropod_rosbag_processing.utils.utils import check_path_existence

from ropod_rosbag_processing.graph.edge import TravelEdge
from ropod_rosbag_processing.process_files.travel_obstacles import TravelObstacle
from ropod_rosbag_processing.utils.costmap_processing import from_costmap_to_coordinates
from ropod_rosbag_processing.utils.costmap_processing import get_n_obstacles
from ropod_rosbag_processing.process_files.obstacle_info import ObstacleInfo

NS_TO_MS = 1000000


class TravelLogger:
    def __init__(self, base_dir, nodes_of_interest, event_radius=.5, event_threshold=.1, min_distance_static_samples=.5):
        self.base_dir = base_dir
        self.nodes_of_interest = nodes_of_interest
        self.event_radius = event_radius
        self.event_threshold = event_threshold
        self.min_distance_static_samples = min_distance_static_samples

        self.edges = []
        self.travel_obstacles = {}
        self.cur_travel_obstacle = TravelObstacle()
        self.at_node = False
        self.last_node = None
        self.last_time = None
        self.static_obstacle_samples = {}

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
                        self.update_travel_obstacles()

                    self.last_node = node
                    self.last_time = cur_time
                    self.at_node = True

    def update_travel_obstacles(self):
        edge_name = self.edges[-1].get_edge_name()
        static_obstacle_samples = self.get_static_obstacle_samples(edge_name)
        self.cur_travel_obstacle.set_edge_info(edge_name, static_obstacle_samples)

        if self.cur_travel_obstacle.edge_name not in self.travel_obstacles:
            self.travel_obstacles[self.cur_travel_obstacle.edge_name] = []
        self.travel_obstacles[self.cur_travel_obstacle.edge_name].append(self.cur_travel_obstacle)

        print("Edges: ", [edge.get_edge_name() for edge in self.edges])
        print("Current travel obstacle \n", self.cur_travel_obstacle)
        self.cur_travel_obstacle = TravelObstacle()

    def get_static_obstacle_samples(self, edge_name):
        if edge_name not in self.static_obstacle_samples:
            file_path = str(self.base_dir) + "/obstacles/" + edge_name + "/static.csv"
            self.static_obstacle_samples[edge_name] = ObstacleInfo.from_file(file_path)

        return self.static_obstacle_samples[edge_name]

    def update_costmap(self, cur_time, costmap, cur_pose):
        coordinates = from_costmap_to_coordinates(costmap)
        if coordinates.any():
            n_obstacles = get_n_obstacles(coordinates)
            self.cur_travel_obstacle.update_obstacle_info(cur_time, n_obstacles, cur_pose)

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

    def to_file(self, file_suffix=".txt"):
        travel_time_dir = self.base_dir + '/travel_time'
        obstacles_dir = self.base_dir + '/obstacles'

        check_path_existence(travel_time_dir)
        check_path_existence(obstacles_dir)

        self.travel_time_to_file(travel_time_dir, file_suffix)
        self.obstacle_to_file(obstacles_dir, file_suffix)

    def travel_time_to_file(self, dir_name, file_suffix=".txt"):
        edge_histories = self.get_history_dict()

        for edge_history in edge_histories.values():
            first_edge = edge_history[0]
            edge_name = first_edge.get_edge_name()
            out_dir = dir_name + "/" + edge_name

            check_path_existence(out_dir)

            with open(out_dir + "/HEADER.info", 'w') as header_file:  # Use file to refer to the file object
                header_file.write("HEADER INFO: " + first_edge.get_edge_name() + " " + first_edge.get_dist_traveled_string() + "\n")
                header_file.write("NODE NAMES: " + first_edge.start_node.name + " " + first_edge.end_node.name + "\n")
                header_file.write("POSITIONS" + str(first_edge.start_node.pose) + " " + str(first_edge.end_node.pose) + "\n")

            out_dest = out_dir + "/" + edge_name + file_suffix

            with open(out_dest, 'w') as out_file:  # Use file to refer to the file object
                for edge in edge_history:
                    out_file.write(str(int(edge.start_time.to_sec())) + " " + str(edge.get_time_traveled()) + "\n")

    def obstacle_to_file(self, dir_name, file_suffix=".txt"):
        for edge_name, travel_obstacle_list in self.travel_obstacles.items():
            out_dir = dir_name + "/" + edge_name + "/total/"
            check_path_existence(out_dir)

            out_dest = out_dir + "/" + edge_name + file_suffix

            with open(out_dest, 'w') as out_file:  # Use file to refer to the file object
                for travel_obstacle in travel_obstacle_list:
                    if travel_obstacle.obstacle_samples:
                        for obstacle_info in travel_obstacle.obstacle_samples:
                            timestamp = str(int(obstacle_info.timestamp.to_sec()))
                            quantity = str(obstacle_info.quantity)

                            out_file.write(timestamp + " " + quantity + "\n")

    def obstacle_ground_truth_to_file(self):
        for edge_name, travel_obstacle_list in self.travel_obstacles.items():
            out_dir = self.base_dir + "/obstacles/" + edge_name

            check_path_existence(out_dir)

            filtered_obstacle_samples = \
                ObstacleInfo.dedupe(travel_obstacle_list[0].obstacle_samples, self.min_distance_static_samples)

            ObstacleInfo.to_file(out_dir + "/static.csv", filtered_obstacle_samples)

    def dynamic_obstacles_to_file(self):
        for edge_name, travel_obstacle_list in self.travel_obstacles.items():
            out_dir = self.base_dir + "/obstacles/" + edge_name + "/dynamic/"
            closest_obstacles = []

            check_path_existence(out_dir)

            out_dest = out_dir + edge_name + ".txt"

            for travel_obstacle in travel_obstacle_list:
                for obstacle_sample in travel_obstacle.obstacle_samples:
                    closest_obstacle = obstacle_sample.get_estimated_dynamic_obstacles(travel_obstacle.static_obstacle_samples)
                    closest_obstacles.append(closest_obstacle)

            ObstacleInfo.to_file(out_dest, closest_obstacles)





