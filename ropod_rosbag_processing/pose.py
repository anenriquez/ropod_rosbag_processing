import math

class Pose:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def calc_dist(self, other_pose):
        dist_travled = math.sqrt(math.pow(self.x - other_pose.x, 2) +
                                  math.pow(self.y - other_pose.y, 2))
        return dist_travled

    def __str__(self):
        to_print = ""
        to_print += "[{}, {}, {}]".format(self.x, self.y, self.z)
        return to_print
