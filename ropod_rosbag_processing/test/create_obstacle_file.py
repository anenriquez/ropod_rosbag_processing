from ropod_rosbag_processing.process_files.obstacle_info import ObstacleInfo
import rospy
from ropod_rosbag_processing.graph.pose import Pose

if __name__ == '__main__':
    obstacles = [ObstacleInfo(rospy.Duration(10), 1, Pose(0, 0, 0)) for n in range(0, 10)]

    ObstacleInfo.to_file('./test.csv', obstacles)

    obs = ObstacleInfo.from_file('./test.csv')

    for ob in obs:
        print(ob)
