import os
import statistics


class EdgeSummary:
    def __init__(self):
        self.edge_info = dict()

    @staticmethod
    def get_stats(durations):
        if len(durations) > 1:
            mean = statistics.mean(durations)
            variance = statistics.variance(durations)
        else:
            mean = durations[0]
            variance = 0

        return mean, variance

    def to_file(self, file_path):
        with open(file_path, 'w') as out_file:
            for max_n_obstacles, durations in self.edge_info.items():
                mean, variance = self.get_stats(durations)
                out_file.write(str(len(durations)))  # Number of measurements
                out_file.write(' ')
                out_file.write(str(mean))
                out_file.write(' ')
                out_file.write(str(variance))
                out_file.write(' ')
                out_file.write(str(max_n_obstacles))
                out_file.write('\n')

    @staticmethod
    def from_file(file_path):
        edge_summary = EdgeSummary()

        with open(file_path, 'r') as source_file:
            for line in source_file.readlines():
                values = line.split(' ')
                duration = float(values[1])
                max_n_obstacles = int(values[3])

                if max_n_obstacles not in edge_summary.edge_info:
                    edge_summary.edge_info[max_n_obstacles] = list()
                edge_summary.edge_info[max_n_obstacles].append(duration)
        return edge_summary


dir_names = ['angela']

if __name__ == '__main__':

    print("Here")

    for base_dir in dir_names:

        path = './' + base_dir + '/results/'
        # find sub directories (only current level)
        for edge_name in os.listdir(path):
            if os.path.isfile(path + edge_name) and edge_name.endswith('.out'):
                print(path + edge_name)
                file_path = path + edge_name
                summary_file_path = file_path.replace('.out', '.summary')
                edge_summary = EdgeSummary.from_file(file_path)
                edge_summary.to_file(summary_file_path)



