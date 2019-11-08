from ropod_rosbag_processing.graph.pose import Pose
import numpy as np
import rospy


class ObstacleInfo:
    def __init__(self, timestamp, quantity, pose):
        self.timestamp = timestamp
        self.quantity = quantity
        self.pose = pose

    def __str__(self):
        to_print = ""
        to_print += "Timestamp: " + str(int(self.timestamp.to_sec())) + "\t"
        to_print += "Obstacles: " + str(self.quantity) + "\t"
        to_print += "Pose: " + str(self.pose)
        return to_print

    def to_csv(self):
        to_csv = ""
        to_csv += str(int(self.timestamp.to_sec())) + ","
        to_csv += str(self.quantity) + ","
        to_csv += str(self.pose.x) + ","
        to_csv += str(self.pose.y)
        return to_csv

    def to_sd(self):
        to_sd = ""
        to_sd += str(int(self.timestamp.to_sec())) + " "
        to_sd += str(self.quantity) + " "
        return to_sd

    @classmethod
    def from_csv(cls, csv_string):
        csv_list = csv_string.split(",")
        if len(csv_list) > 3:
            timestamp = rospy.Duration(int(csv_list[0]))
            quantity = int(csv_list[1])
            pose = Pose(float(csv_list[2]), float(csv_list[3]), 0)
            obstacle = cls(timestamp, quantity, pose)

            return obstacle

    @staticmethod
    def dedupe(obstacle_samples, min_distance=0.5):
        visited_samples = []

        for obstacle in obstacle_samples:
            add_sample = True

            for visited_sample in visited_samples:
                distance = visited_sample.pose.calc_dist(obstacle.pose)
                if distance < min_distance:
                    add_sample = False
                    break
            if add_sample:
                visited_samples.append(obstacle)

        return visited_samples

    def get_estimated_dynamic_obstacles(self, static_obstacle_samples):
        smallest_distance = np.inf
        closest_obstacle = ObstacleInfo(None, None, None)

        if len(static_obstacle_samples) < 1:
            return None

        for static_obstacle in static_obstacle_samples:
            distance = self.pose.calc_dist(static_obstacle.pose)
            if distance < smallest_distance:
                smallest_distance = distance
                closest_obstacle.timestamp = self.timestamp
                closest_obstacle.quantity = max(self.quantity - static_obstacle.quantity, 0)
                closest_obstacle.pose = self.pose

        return closest_obstacle

    @staticmethod
    def to_file(file_path, obstacles):
        file_suffix = file_path.split('.')[-1]
        lines = []
        with open(file_path, 'w') as outfile:
            for obstacle in obstacles:
                if file_suffix == 'csv':
                    lines.append(obstacle.to_csv())

                elif file_suffix == 'txt':
                    lines.append(obstacle.to_sd())

            outfile.write("\n".join(lines))

    @classmethod
    def from_file(cls, file):
        obstacles = []
        with open(file, 'r') as csv_file:
            line = csv_file.readline()

            while line:
                obstacle = cls.from_csv(line)
                obstacles.append(obstacle)
                line = csv_file.readline()

        return obstacles
