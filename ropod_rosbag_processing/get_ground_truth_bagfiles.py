import rosbag

from ropod_rosbag_processing.utils.utils import check_path_existence
BAGFILES_DIR = '/home/angela/ropod/thesis/bags_ground_truth/'


square = {'outbagfile': 'square.bag',
          'bagfiles': ['_2019-11-25-19-34-44_2.bag', '_2019-11-25-19-38-57_3.bag'],
          'start_time': 1574706992.58039,
          'end_time': 1574707176.54361}

street = {'outbagfile': 'street.bag',
          'bagfiles': ['_2019-11-25-20-01-26_3.bag', '_2019-11-25-20-05-36_4.bag', '_2019-11-25-20-09-24_5.bag'],
          'start_time': 1574708658.13195,
          'end_time': 1574708999.2097}

faraway = {'outbagfile': 'faraway.bag',
           'bagfiles': ['_2019-11-25-20-33-01_1.bag', '_2019-11-25-20-37-09_2.bag',
                        '_2019-11-25-20-40-57_3.bag', '_2019-11-25-20-44-42_4.bag'],
           'start_time': 1574710594.16895,
           'end_time': 1574711201.91883}


def join_bagfiles(outbagfile, bagfiles, start_time, end_time):
    print("Joining bagfiles to: ", outbagfile)

    check_path_existence(outbagfile)

    with rosbag.Bag(outbagfile, 'w') as output_file:
        for bagfile in bagfiles:
            print("Reading bagfile: ", bagfile)
            with rosbag.Bag(BAGFILES_DIR + bagfile, 'r') as input_file:
                for topic, msg, t in input_file:
                    if (end_time > t.to_sec() > start_time) and \
                            ("/amcl_pose" in topic or
                             '/autonomous_navigation/local_costmap/costmap' in topic or
                                "/tf" in topic):
                        output_file.write(topic, msg, t)


if __name__ == "__main__":
    join_bagfiles(**square)
    join_bagfiles(**street)
    join_bagfiles(**faraway)
