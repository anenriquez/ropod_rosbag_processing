import rosbag
from ropod_rosbag_processing.collect_files.get_files import get_bagfiles
import shutil
import subprocess

TO_PROCESS_DIR = '/home/ropod/to_process_bags/'
MERGED_BAGFILES_DIR = '/home/ropod/merged_bags/'


def repair_bagfiles(bagfiles):
    for bagfile in bagfiles:
        if bagfile.endswith('.bag.active'):
            print("Reindexing bagfile: ", bagfile)
            subprocess.call(["rosbag", "reindex", TO_PROCESS_DIR + bagfile])
            new_name = bagfile.replace('bag.active', 'bag')
            subprocess.call(["mv", TO_PROCESS_DIR + bagfile, TO_PROCESS_DIR + new_name])


def join_bagfiles(outbagfile, bagfiles):
    print("Joining bagfiles to: ", outbagfile)

    with rosbag.Bag(outbagfile, 'w') as output_file:
        for bagfile in bagfiles:
            try:
                print("Reading bagfile: ", bagfile)
                with rosbag.Bag(MERGED_BAGFILES_DIR + bagfile, 'r') as input_file:
                    for topic, msg, t in input_file:
                        if "/amcl_pose" in topic \
                                or '/autonomous_navigation/local_costmap/costmap' in topic or '/tf' in topic:
                            output_file.write(topic, msg, t)

            except rosbag.bag.ROSBagFormatException:
                print("Error opening file:", bagfile)
            except rosbag.ROSBagUnindexedException:
                print("Unindexed bag:", bagfile)
            except rosbag.bag.ROSBagException:
                print("ROSBag exception")
            except Exception as e:
                print("Another exception")
            except:
               print("Caught it!")





def get_bagfiles_to_join(bagfiles):
    threshold = 3600  # seconds
    last_time = 0
    last_day = []
    bagfiles_to_join = dict()
    outbagfile = None

    for bagfile in bagfiles:
        try:
            bag = rosbag.Bag(TO_PROCESS_DIR + bagfile)
            current_day = bagfile.split('-')[:3]
            print("Current day: ", current_day)
            print("last day: ", last_day)
            for topic, msg, cur_time in bag.read_messages():
                if cur_time.to_sec() - last_time > threshold or current_day != last_day:
                    outbagfile = MERGED_BAGFILES_DIR + bagfile.replace('.bag', '') + '_joined.bag'
                    print("Outbagfile: ", outbagfile)
                    bagfiles_to_join[outbagfile] = list()

                last_time = cur_time.to_sec()
                last_day = current_day

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
        except rosbag.ROSBagUnindexedException:
            print("Unindexed bag:", bagfile)
        except rosbag.bag.ROSBagException:
            print("ROSBag exception")
        except Exception as e:
            print("Another exception")
        except:
           print("Caught it!")


    return bagfiles_to_join


if __name__ == "__main__":
    print("Joining bagfiles")
    bagfiles = get_bagfiles(TO_PROCESS_DIR)
    repair_bagfiles(bagfiles)
    bagfiles = get_bagfiles(TO_PROCESS_DIR)
    bagfiles_to_join = get_bagfiles_to_join(bagfiles)

    for outbagfile, files in bagfiles_to_join.items():
        join_bagfiles(outbagfile, files)




