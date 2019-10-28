from ropod_rosbag_processing.utils.get_files import get_bagfiles
from ropod_rosbag_processing.utils.get_files import add_bagfile_to_register


# File with name of bagfiles that have been copied to the workstation
bagfile_bookkepper = "utils/bookkeeper.csv"
WORKSTATION_DIR = '/home/ropod/guido_bags/'


if __name__ == '__main__':
    bagfiles = get_bagfiles(WORKSTATION_DIR)
    for bagfile in bagfiles:
        if not bagfile.endswith('_joined.bag'):
            add_bagfile_to_register(bagfile_bookkepper, bagfile)
