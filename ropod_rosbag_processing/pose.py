class Pose:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        to_print = ""
        to_print += "[{}, {}, {}]".format(self.x, self.y, self.z)
        return to_print
