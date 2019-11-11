import shutil
import csv
import os
import argparse

# File with name of bagfiles that have been copied to the workstation
bagfile_bookkepper = "bookkeeper.csv"

# Directories to put bagfiles
ROBOT_DIR = '/home/narko5/.ros/gbot/bag'
USB_DIR = '/mnt/guido_bags'
WORKSTATION_DIR = '/home/ropod/to_process_bags'

# ROBOT_DIR = '/home/angela/Documents/MAS/robot'
# USB_DIR = '/home/angela/Documents/MAS/usb'
# WORKSTATION_DIR = '/home/angela/Documents/MAS/workstation'


def get_bagfile_names(a_file):
    bagfile_names = list()
    with open(a_file, 'r') as a_file:
        csv_reader = csv.DictReader(a_file)
        for row in csv_reader:
            bagfile_names.append(row['bagfile_name'])
    return bagfile_names


def get_bagfiles(path):
    print("Getting bagfiles")
    print("Path", path)
    bagfiles = list()

    for item in os.listdir(path):
        if os.path.isfile(os.path.join(path, item)):
            if item.endswith('.bag'):
                bagfiles.append(os.path.join(item))

    bagfiles.sort()
    return bagfiles


def add_bagfile_to_register(register, file_name):
    with open(register, mode='a') as csv_file:
        print("Adding bagfile {} to bookkeeping file: ".format(file_name))
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([file_name])


def copy(source, destination):
    bagfiles = get_bagfiles(source)
    print("Bagfiles in source: ", len(bagfiles))

    copied_bagfiles_names = get_bagfile_names(bagfile_bookkepper)
    print("Bagfiles already copied\n", copied_bagfiles_names)

    n_copied_files = 0

    for bagfile in bagfiles:
        if bagfile not in copied_bagfiles_names:
            print("Copying {} to {}".format(bagfile, destination))
            shutil.copy(source + '/' + bagfile, destination)

            if destination == WORKSTATION_DIR:
                add_bagfile_to_register(bagfile_bookkepper, bagfile)

            n_copied_files += 1
        print("Number of copied files: {}/{}".format(n_copied_files, len(bagfiles)))


def get_source(source_name):
    if source_name == 'robot':
        source = ROBOT_DIR
    elif source_name == 'usb':
        source = USB_DIR
    return source


def get_destination(destination_name):
    if destination_name == 'usb':
        destination = USB_DIR
    elif destination_name == 'workstation':
        destination = WORKSTATION_DIR
    return destination


def move(source, destination):
    bagfiles = get_bagfiles(source)
    print("Bagfiles in source: ", len(bagfiles))

    copied_bagfiles_names = get_bagfile_names(bagfile_bookkepper)
    print("Bagfiles already copied\n", copied_bagfiles_names)

    n_copied_files = 0

    for bagfile in bagfiles:
        if bagfile not in copied_bagfiles_names:
            print("Moving {} to {}".format(bagfile, destination))
            try:
                shutil.move(source + '/' + bagfile, destination)

                if destination == WORKSTATION_DIR:
                    add_bagfile_to_register(bagfile_bookkepper, bagfile)

                n_copied_files += 1

            except shutil.Error as err:
                print("The file already exists in the destination")
        print("Number of copied files: {}/{}".format(n_copied_files, len(bagfiles)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, action='store',
                        help='Action to perform',
                        choices=['cp', 'mv'])

    parser.add_argument('source', type=str, action='store',
                        help='Constant representing the bagfile source directory',
                        choices=['robot', 'usb'])

    parser.add_argument('destination', type=str, action='store',
                        help='Constant representing the bagfile destination directory',
                        choices=['usb', 'workstation'])

    args = parser.parse_args()

    source = get_source(args.source)
    destination = get_destination(args.destination)
    print("source: ", source)
    print("destination", destination)

    if args.action == 'cp':
        copy(source, destination)
    elif args.action == 'mv':
        move(source, destination)










