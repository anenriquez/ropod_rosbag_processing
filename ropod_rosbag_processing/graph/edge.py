from datetime import datetime

NS_TO_SEC = 1000000000


class TravelEdge:
    def __init__(self, start_node, start_time, end_node, end_time):
        self.start_node = start_node
        self.start_time = start_time
        self.end_node = end_node
        self.end_time = end_time
        self.name = self.get_edge_name(fancy=True)

    def __str__(self):
        edge_str = ""
        edge_str += "\nEdge: " + self.name
        edge_str += "\nTime: " + self.get_time_traveled_string()
        edge_str += "\nDistance: " + self.get_dist_traveled_string()
        edge_str += "\nAverage Speed: " + self.get_average_speed_string()
        return edge_str

    def get_edge_name(self, fancy=False):
        joiner = "_to_"
        if fancy:
            joiner = "->"
        return self.start_node.name + joiner + self.end_node.name

    def get_time_traveled(self):
        ts = (self.end_time.to_nsec() - self.start_time.to_nsec())/NS_TO_SEC
        return ts

    def get_time_traveled_string(self):
        return str("{0:.2f}".format(self.get_time_traveled())) + " seconds"

    def get_dist_traveled(self):
        dist_traveled = self.start_node.pose.calc_dist(self.end_node.pose)
        return dist_traveled

    def get_dist_traveled_string(self):
        dist_traveled = self.get_dist_traveled()
        return str("{0:.2f}".format(dist_traveled)) + " meters"

    def get_start_time_string(self):
        ts = self.start_time.to_nsec()/NS_TO_SEC
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    def get_end_time_string(self):
        ts = self.end_time.to_nsec()/NS_TO_SEC
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    def get_average_speed(self):
        return self.get_dist_traveled() / self.get_time_traveled()

    def get_average_speed_string(self):
        try:
            avg_speed = self.get_dist_traveled() / self.get_time_traveled()
        except ZeroDivisionError:
            print("Cannot divide by zero")
            return str("{0:.2f}".format(0.0)) + " meters/second"
        return str("{0:.2f}".format(avg_speed)) + " meters/second"
