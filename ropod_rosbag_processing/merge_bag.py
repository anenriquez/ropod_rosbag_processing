import rosbag
from ropod_rosbag_processing.collect_files.get_files import get_bagfiles
import shutil

TO_PROCESS_DIR = '/home/ropod/to_process_bags/'
MERGED_BAGFILES_DIR = '/home/ropod/merged_bags/'


def join_bagfiles(outbagfile, bagfiles):
    print("Joining bagfiles to: ", outbagfile)

    with rosbag.Bag(outbagfile, 'w') as output_file:
        for bagfile in bagfiles:
            print("Reading bagfile: ", bagfile)
            with rosbag.Bag(MERGED_BAGFILES_DIR, 'r') as input_file:
                for topic, msg, t in input_file:
                    if "/amcl_pose" in topic \
                            or '/autonomous_navigation/local_costmap/costmap' in topic:
                        output_file.write(topic, msg, t)


def get_bagfiles_to_join(bagfiles):
    threshold = 3600  # seconds
    last_time = 0
    bagfiles_to_join = dict()
    outbagfile = None

    for bagfile in bagfiles:
        try:
            bag = rosbag.Bag(TO_PROCESS_DIR + bagfile)

            for topic, msg, cur_time in bag.read_messages():
                if cur_time.to_sec() - last_time > threshold:
                    outbagfile = TO_PROCESS_DIR + bagfile.replace('.bag', '') + '_joined.bag'
                    print("Outbagfile: ", outbagfile)
                    bagfiles_to_join[outbagfile] = list()

                last_time = cur_time.to_sec()

            if outbagfile is not None:
                print("Adding {} to joined bagfile {}".format(bagfile, outbagfile))
                bagfiles_to_join[outbagfile].append(bagfile)

            print("Moving {} to merged bagfiles dir".format(bagfile))
            try:
                shutil.move(TO_PROCESS_DIR + bagfile, MERGED_BAGFILES_DIR)
            except shutil.Error as err:
                print("The file already exists in the destination")

        except rosbag.bag.ROSBagFormatException:
            print("Error opening file:", bagfile)

    return bagfiles_to_join


if __name__ == "__main__":
    print("Joining bagfiles")
    bagfiles = get_bagfiles(TO_PROCESS_DIR)
    bagfiles_to_join = get_bagfiles_to_join(bagfiles)

    for outbagfile, files in bagfiles_to_join.items():
        join_bagfiles(outbagfile, files)




