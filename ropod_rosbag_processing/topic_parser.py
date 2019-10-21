from datetime import datetime
import rosbag
import subprocess
import os
import math

NS_TO_SEC = 1000000000

bag_dir = "../../input/"
# SUCCESS (mostly)
#bag = rosbag.Bag(bag_dir + '20190510_hochschulstrasse.bag')
#bag = rosbag.Bag(bag_dir + '20190314_maneuver_navigation_brsu_success.bag')
#bag = rosbag.Bag(bag_dir + '_2019-09-30-12-53-15_2.bag')
bag = rosbag.Bag(bag_dir + '_2019-09-30-13-08-39_0.bag')

# ERRORs
#bag = rosbag.Bag(bag_dir + '20190523_hochschul_nav_robosense_sunlight.bag')

class Waypoint:
    def __init__(self, time, x, y):
        self.time = time
        self.x = x
        self.y = y

    def get_time_traveled_string(self, prev_waypoint):
        ts = (self.time.to_nsec() - prev_waypoint.time.to_nsec())/NS_TO_SEC
        return str(ts) + " seconds"

    def get_dist_traveled(self, prev_waypoint):
        dist_travled = math.sqrt(math.pow(self.x - prev_waypoint.x, 2) +
                                  math.pow(self.y - prev_waypoint.y, 2))
        return dist_travled

    def get_time_string(self):
        ts = self.time.to_nsec()/NS_TO_SEC
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    def get_pos_string(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __str__(self):
        return self.get_time_string() + " " + self.get_pos_string()


class WaypointLogger:
    def __init__(self):
        self.waypoints = []

    def add_waypoint(self, time, x, y):
        waypoint = Waypoint(time, x, y)
        self.waypoints.append(waypoint)
        print(len(self.waypoints))

    def get_history(self):
        history = ""
        if len(self.waypoints) >= 2:
            waypoints_iter = iter(self.waypoints)
            prev_waypoint = next(waypoints_iter)
            history += "\n********************************************************************************"
            history += "\n* Starting at " + str(prev_waypoint)
            history += "\n********************************************************************************"
            for waypoint in waypoints_iter:
                history += "\n********************************************************************************"
                history += "\nReached Waypoint: " + str(waypoint)
                history += "\nTime traveled: " + waypoint.get_time_traveled_string(prev_waypoint)
                history += "\nDistance travled: " + str(waypoint.get_dist_traveled(prev_waypoint))
                history += "\n********************************************************************************\n\n"
                prev_waypoint = waypoint
        else:
            history = "NOT ENOUGH WAYPOINTS"

        return history


#todo there's got to be a better way to check these messages
count = 0
seen_topics = {}
waypoint_logger = WaypointLogger()
for topic, msg, t in bag.read_messages():

    seen_topics[topic] = topic

    # TODO better handle more than one set of waypoints
    if ("nav_waypoints" in topic):
        #print topic
        print(msg)
        print(t)
        waypoint_start_t = t
        waypoints = msg.poses
        num_waypoints = len(waypoints)
        cur_waypoint_index = 0
        cur_waypoint = waypoints[cur_waypoint_index]
        #print "\n********************************************************************************\n"

    #if ("/costmap" in topic):
    #    print msg

    if ("/initial_pose" in topic):
        print("initial pose", t, msg, "\n")

    #if ("/navigation_status" in topic):
    #    print "nav status", t, msg, "\n"

    #if ("/autonomous_navigation/timings" in topic):
    #    print "nav timings", t, msg, "\n"


    if ("/navigation_command" in topic):
        waypoint_logger.add_waypoint(t, msg.goal.x, msg.goal.y)
        print("nav command", t, msg, "\n")

    if ("/amcl_pose" in topic):
        cur_pose = msg.pose.pose.position
        #print type(cur_pose)
        #print cur_pose
        #print cur_pose.pose.pose.position

        if ("/route_navigation/goal" in topic):
            print(msg)


print(waypoint_logger.get_history())

for topic in seen_topics:
    print(topic)

bag.close()
