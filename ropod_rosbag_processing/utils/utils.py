import os
import yaml


def load_yaml(file):
    """ Reads a yaml file and returns a dictionary with its contents

    :param file: file to load
    :return: data as dict()
    """
    with open(file, 'r') as file:
        data = yaml.safe_load(file)
    return data


def check_path_existence(full_path):
    if not os.path.exists(full_path):
        os.makedirs(full_path)
