class TravelObstacle:
    def __init__(self):
        self.edge_name = None
        self.obstacle_info = list()

    def __str__(self):
        to_print = ""
        to_print += "Edge: " + str(self.edge_name)
        if self.obstacle_info:
            for info in self.obstacle_info:
                to_print += "\n"
                to_print += "Timestamp: " + str(int(info[0].to_sec())) + "\t"
                to_print += "Obstacles: " + str(info[1])
        return to_print

    def set_edge_name(self, edge_name):
        self.edge_name = edge_name

    def update_obstacle_info(self, timestamp, n_obstacles):
        self.obstacle_info.append((timestamp, n_obstacles))

    def get_average(self):
        return sum(n_obstacles[1] for n_obstacles in self.obstacle_info)/len(self.obstacle_info)

    def get_max(self):
        return max(n_obstacles[1] for n_obstacles in self.obstacle_info)

    def get_min(self):
        return min(n_obstacles[1] for n_obstacles in self.obstacle_info)

    def get_start_time(self):
        return min(timestamp[0] for timestamp in self.obstacle_info)

    def get_end_time(self):
        return max(timestamp[0] for timestamp in self.obstacle_info)

    def get_total_time(self):
        self.get_end_time() - self.get_start_time()


