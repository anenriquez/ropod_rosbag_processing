#!/bin/sh

python3 /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/merge_bag.py
python3 /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/process_bagfiles.py
cd /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/ethan/travel_time
./cat_files.sh
cd /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/angela/travel_time
./cat_files.sh
python3 /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/results_generator.py
python3 /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/get_edge_summary.py
