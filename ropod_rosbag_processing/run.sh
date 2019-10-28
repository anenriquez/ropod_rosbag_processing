#!/bin/sh

python3 /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/merge_bag.py
python3 /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/process_bagfiles.py
cd /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/ethan
./cat_files.sh
cd /home/ropod/ropod_rosbag_processing/ropod_rosbag_processing/angela
./cat_files.sh
