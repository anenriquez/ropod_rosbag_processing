import os
import statistics
import numpy as np


def get_stats(durations):
    if len(durations) > 1:
        mean = statistics.mean(durations)
        standard_deviation = statistics.stdev(durations)
    else:
        mean = durations[0]
        standard_deviation = 0

    return mean, standard_deviation


def to_file(edge_summary, file_path, keep_outliers=False):
    with open(file_path, 'w') as out_file:
        for max_n_obstacles, durations in edge_summary.items():
            if not keep_outliers:
                durations = remove_outliers(durations)

            mean, standard_deviation = get_stats(durations)

            out_file.write(str(len(durations)))  # Number of measurements
            out_file.write(' ')
            out_file.write(str(mean))
            out_file.write(' ')
            out_file.write(str(standard_deviation))
            out_file.write(' ')
            out_file.write(str(max_n_obstacles))
            out_file.write('\n')


def from_file(file_path):
    edge_summary = dict()

    with open(file_path, 'r') as source_file:
        for line in source_file.readlines():
            values = line.split(' ')
            duration = float(values[1])
            max_n_obstacles = int(values[3])

            if max_n_obstacles not in edge_summary:
                edge_summary[max_n_obstacles] = list()
            edge_summary[max_n_obstacles].append(duration)
    return edge_summary


def remove_outliers(durations):
    """
    Removes outliers using the interquartile range (IQR)

    Definition from Wikipedia: https://en.wikipedia.org/wiki/Interquartile_range#Outliers
    - The IQR is a measure of variability, based on dividing a data set into quartiles.
    - Quartiles divide a rank-ordered data set into four equal parts.
    - The values that separate parts are called the first, second, and third quartiles;
    and they are denoted by Q1, Q2, and Q3, respectively.

    - The IQR is equal to the difference between 75th and 25th percentiles, or between upper
     and lower quartiles
                    IQR = Q3 − Q1

    - The IQR is often used to find outliers in data.
    - Outliers are defined as observations that fall
            below           Q1 − 1.5 * IQR
            or above        Q3 + 1.5 * IQR.

    durations(list): list of travel durations
    """
    original_data = np.array(sorted(durations))
    filtered_data = list()

    upper_quartile = np.percentile(original_data, 75)
    lower_quartile = np.percentile(original_data, 25)
    IQR = upper_quartile - lower_quartile
    lower_bound = lower_quartile - 1.5 * IQR
    upper_bound = upper_quartile + 1.5 * IQR

    # Data points outside the lower and upper bounds are outliers
    for p in original_data.tolist():
        if lower_bound <= p <= upper_bound:
            filtered_data.append(p)

    return filtered_data


# dir_name: keep_outliers
dir_names = {'angela': False}

if __name__ == '__main__':

    for base_dir, keep_outliers in dir_names.items():
        path = base_dir + '/results/'
        # find sub directories (only current level)
        for edge_name in os.listdir(path):
            if os.path.isfile(path + edge_name) and edge_name.endswith('.out'):
                print(path + edge_name)
                file_path = path + edge_name
                summary_file_path = file_path.replace('.out', '.summary')
                edge_summary = from_file(file_path)

                to_file(edge_summary, summary_file_path, keep_outliers)
