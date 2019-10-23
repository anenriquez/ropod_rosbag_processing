from datetime import datetime
import rosbag
import subprocess
import os
import math
from ropod_rosbag_processing.utils.utils import load_yaml
from ropod_rosbag_processing.graph.node import TravelNode
from ropod_rosbag_processing.graph.travel_logger import TravelLogger
from ropod_rosbag_processing.pose import Pose

bag_dir = "../../input/"
# SUCCESS (mostly)
#bag = rosbag.Bag(bag_dir + '20190510_hochschulstrasse.bag')
#bag = rosbag.Bag(bag_dir + '20190314_maneuver_navigation_brsu_success.bag')
#bag = rosbag.Bag(bag_dir + '_2019-09-30-12-53-15_2.bag')

bag_root = '_2019-09-30-13-08-39_0'
bag_name = bag_root + '.bag'
bag = rosbag.Bag(bag_dir + bag_name)

# ERRORs
#bag = rosbag.Bag(bag_dir + '20190523_hochschul_nav_robosense_sunlight.bag')


count = 0
seen_topics = {}

# TODO move this test
config = "./config/config.yaml"
config_params = load_yaml(config)
nodes_dict = config_params.get('nodes')
nodes = TravelNode.get_travel_nodes(nodes_dict)

travel_logger = TravelLogger(nodes)
for topic, msg, cur_time in bag.read_messages():
    seen_topics[topic] = topic

    if ("/amcl_pose" in topic):
        ros_pose = msg.pose.pose.position
        cur_pose = Pose(ros_pose.x, ros_pose.y, ros_pose.z)
        travel_logger.event_update(cur_pose, cur_time)


print(travel_logger.get_history())
edge_histories = travel_logger.get_history_dict()
travel_logger.to_file(file_suffix = (bag_root + ".txt"))


#for topic in seen_topics:
#    print(topic)

bag.close()
