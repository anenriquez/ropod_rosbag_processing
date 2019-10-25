import rosbag
from ropod_rosbag_processing.utils.get_files import get_bagfiles

TO_PROCESS_DIR = '../../input/'


def join_bagfiles(outbagfile, bagfiles):
    print("Joining bagfiles to: ", outbagfile)

    with rosbag.Bag(outbagfile, 'w') as output_file:
        for bagfile in bagfiles:
            print("Reading bag file: ", bagfile)
            with rosbag.Bag(TO_PROCESS_DIR + bagfile, 'r') as input_file:
                for topic, msg, t in input_file:
                    if "/amcl_pose" in topic:
                        output_file.write(topic, msg, t)


def get_bagfiles_to_join(bagfiles):
    threshold = 3600  # seconds
    last_time = 0
    bagfiles_to_join = dict()
    outbagfile = None

    for bagfile in bagfiles:
        bag = rosbag.Bag(TO_PROCESS_DIR + bagfile)

        for topic, msg, cur_time in bag.read_messages():
            if abs(last_time - cur_time.to_sec()) > threshold:
                print("Difference: ", last_time - cur_time.to_sec())
                outbagfile = TO_PROCESS_DIR + bagfile.split('.')[0] + '_joined.bag'
                print("Outbagfile: ", outbagfile)
                bagfiles_to_join[outbagfile] = list()
            last_time = cur_time.to_sec()

        if outbagfile is not None:
            print("Adding {} to joined bagfile {}".format(bagfile, outbagfile))
            bagfiles_to_join[outbagfile].append(bagfile)

    return bagfiles_to_join


if __name__ == "__main__":

    bagfiles = get_bagfiles(TO_PROCESS_DIR)
    bagfiles_to_join = get_bagfiles_to_join(bagfiles)

    for outbagfile, files in bagfiles_to_join.items():
        join_bagfiles(outbagfile, files)



