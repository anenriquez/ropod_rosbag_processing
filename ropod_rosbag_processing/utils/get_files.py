import shutil
import csv
import os
import argparse

# File with name of bagfiles that have been copied to the workstation
bagfile_bookkepper = "bookkeeper.csv"

# Directories to put bagfiles
ROBOT_DIR = 'robot/'
USB_DIR = 'usb/'
WORKSTATION_DIR = '../workstation/'


def get_bagfile_names(file):
    bagfile_names = list()
    with open(file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            bagfile_names.append(row['bagfile_name'])
        return bagfile_names


def get_bagfiles(path):
    bagfiles = list()
    for root, directories, files in os.walk(path):
        for file in files:
            if file.endswith('.bag'):
                bagfiles.append(os.path.join(root, file))
    return bagfiles


def add_bagfile_to_register(register, file_name):
    with open(register, mode='a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([file_name])


def copy(source, destination):
    bagfiles = get_bagfiles(source)
    print("Bagfiles in source\n", bagfiles)

    copied_bagfiles_names = get_bagfile_names(bagfile_bookkepper)
    print("Bagfiles already copied\n", copied_bagfiles_names)

    for bagfile in bagfiles:
        bagfile_name = bagfile.split('/')[-1]

        if bagfile_name not in copied_bagfiles_names:
            print("Copying {} to {}".format(bagfile, destination))
            shutil.copy(bagfile, destination)

            if destination == WORKSTATION_DIR:
                add_bagfile_to_register(bagfile_bookkepper, bagfile.split('/')[-1])


def move(source, destination):
    bagfiles = get_bagfiles(source)
    print("Bagfiles in source\n", bagfiles)

    copied_bagfiles_names = get_bagfile_names(bagfile_bookkepper)
    print("Bagfiles already copied\n", copied_bagfiles_names)

    for bagfile in bagfiles:
        bagfile_name = bagfile.split('/')[-1]

        if bagfile_name not in copied_bagfiles_names:
            print("Moving {} to {}".format(bagfile, destination))
            shutil.move(bagfile, destination)

            if destination == WORKSTATION_DIR:
                add_bagfile_to_register(bagfile_bookkepper, bagfile.split('/')[-1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, action='store', help='Action to perform', choices=['cp', 'mv'])
    parser.add_argument('source', type=str, action='store', help='Path to the bagfile source directory')
    parser.add_argument('destination', type=str, action='store', help='Path to the bagfile destination directory')

    args = parser.parse_args()

    if args.action == 'cp':
        copy(args.source, args.destination)
    elif args.action == 'mv':
        move(args.source, args.destination)










