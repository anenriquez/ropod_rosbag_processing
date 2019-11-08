from ropod_rosbag_processing.graph.obstacle_info import ObstacleInfo


class TravelObstacle:
    def __init__(self):
        self.edge_name = None
        self.obstacle_samples = []
        self.static_obstacle_samples = []
        self.estimated_dynamic_obstacles = []

    def __str__(self):
        to_print = ""
        to_print += "Edge: " + str(self.edge_name)
        return to_print

    def set_edge_info(self, edge_name, static_obstacle_samples):
        self.edge_name = edge_name
        self.static_obstacle_samples = static_obstacle_samples

        for obstacle_sample in self.obstacle_samples:
            self.estimated_dynamic_obstacles.append(
                obstacle_sample.get_estimated_dynamic_obstacles(static_obstacle_samples))

    def update_obstacle_info(self, timestamp, n_obstacles, pose):
        self.obstacle_samples.append(ObstacleInfo(timestamp, n_obstacles, pose))

    def get_average(self, dynamic=False):
        if dynamic:
            return sum(dynamic_obstacle.quantity
                       for dynamic_obstacle in self.estimated_dynamic_obstacles)\
                    / len(self.estimated_dynamic_obstacles)
        else:
            return sum(static_obstacle.quantity
                       for static_obstacle in self.static_obstacle_samples) \
                   / len(self.static_obstacle_samples)

    def get_max(self, dynamic=False):
        if dynamic:
            return max(dynamic_obstacle.quantity
                       for dynamic_obstacle in self.estimated_dynamic_obstacles)
        else:
            return max(static_obstacle.quantity
                       for static_obstacle in self.static_obstacle_samples)

    def get_min(self, dynamic=False):
        if dynamic:
            return min(dynamic_obstacle.quantity
                       for dynamic_obstacle in self.estimated_dynamic_obstacles)
        else:
            return min(static_obstacle.quantity
                       for static_obstacle in self.static_obstacle_samples)

    def get_start_time(self, dynamic=False):
        if dynamic:
            return min(dynamic_obstacle.timestamp
                       for dynamic_obstacle in self.estimated_dynamic_obstacles)
        else:
            return min(static_obstacle.timestamp
                       for static_obstacle in self.static_obstacle_samples)

    def get_end_time(self, dynamic=False):
        if dynamic:
            return max(dynamic_obstacle.timestamp
                       for dynamic_obstacle in self.estimated_dynamic_obstacles)
        else:
            return max(static_obstacle.timestamp
                       for static_obstacle in self.static_obstacle_samples)

    def get_total_time(self, dynamic=False):
        self.get_end_time(dynamic) - self.get_start_time(dynamic)


