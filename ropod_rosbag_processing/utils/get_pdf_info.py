import os
import statistics

import yaml


def get_files(path):
    edge_files = dict()

    for root, directories, files in os.walk(path):
        if root != path:
            try:
                edge_name = root.replace(path, '')
                index = files.index('all_runs.out')
                edge_files[edge_name] = root + '/' + files[index]
            except ValueError:
                print("All runs file not present in", root)

    return edge_files


def get_duration(file):
    durations = list()
    with open(file, 'r') as file:
        for line in file.readlines():
            duration = float(line.split(' ')[1])
            durations.append(duration)
    return durations


if __name__ == '__main__':

    edge_files = get_files('../angela/')

    for edge_name, all_runs_file in edge_files.items():
        pdf_info = dict()
        print("-----------------------------------------")
        print("Edge: ", edge_name)
        durations = get_duration(all_runs_file)
        print("# entries: ", len(durations))

        if len(durations) > 1:
            mu = statistics.mean(durations)
            sigma = statistics.stdev(durations)
        else:
            mu = durations[0]
            sigma = 0

        print("mean: ", mu)
        print("standard deviation: ", sigma)
        pdf_info['mean'] = mu
        pdf_info['standard_deviation'] = sigma

        pdf_file = all_runs_file.replace('all_runs.out', 'pdf_file.yaml')

        with open(pdf_file, 'w') as outfile:
            yaml.dump(pdf_info, outfile, default_flow_style=False)



