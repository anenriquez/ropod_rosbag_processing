import os
import math

class EdgeObservation:
    def __init__(self, start_time, duration):
        self.start_time = start_time
        self.duration = duration
        self.end_time = math.ceil(start_time + duration)
        self.obstacle_counts = []


    def is_during(self, observation_time):
        return self.start_time <= observation_time <= self.end_time


    def get_average_obstacles(self):
        if len(self.obstacle_counts) == 0:
            return -1

        return sum(self.obstacle_counts)/len(self.obstacle_counts)


    def add_obstacle_count(self, count):
        self.obstacle_counts.append(count)


    def conditional_add_count(self, time, count):
        if self.is_during(time):
            self.add_obstacle_count(count)



class EdgeObservations:
    def __init__(self, name):
        self.observations = []
        self.name = name


    def add_edge_observation(self, start_time, duration):
        self.observations.append(EdgeObservation(start_time, duration))


    def add_observation(self, time, obstacle_count):
        for observation in self.observations:
            # conditional add will only add the count if time is within range
            observation.conditional_add_count(time, obstacle_count)

    def add_observations_from_file(self, file_path):
        with open(file_path, 'r') as source_file:
            for line in source_file.readlines():
                values = line.split(' ')
                timestamp = int(values[0])
                obstacle_count = int(values[1])
                self.add_observation(timestamp, obstacle_count)


    def to_file(self, file_path):
        with open(file_path, 'w') as out_file:
            for observation in self.observations:
                out_file.write(str(observation.start_time))
                out_file.write(' ')
                out_file.write(str(observation.duration))
                out_file.write(' ')
                out_file.write(str(observation.get_average_obstacles()))
                out_file.write('\n')

    @staticmethod
    def from_file(file_path, name):
        edge_observations = EdgeObservations(name)

        with open(file_path, 'r') as source_file:
            for line in source_file.readlines():
                values = line.split(' ')
                timestamp = int(values[0])
                duration = float(values[1])
                edge_observations.add_edge_observation(timestamp, duration)

        return edge_observations




dir_names = ['ethan', 'angela']
#dir_names = ['ethan']
path = ''

if __name__ == '__main__':
    for base_dir in dir_names:
        edge_observations_dict = {}

        # create EdgeObservations objects and init their durations
        path = './' + base_dir + '/travel_time/'
        # find sub directories (only current level)
        for edge_name in os.listdir(path):
            if os.path.isdir(path + edge_name):
                print(path + edge_name + '/all_runs.out')
                runs_file = path + edge_name + '/all_runs.out'
                edge_observations = EdgeObservations.from_file(runs_file, edge_name)
                edge_observations_dict[edge_observations.name] = edge_observations

        # add observations to the EdgeObservations objects
        path = './' + base_dir + '/obstacles/'
        for edge_name in edge_observations_dict.keys():
            file_path = path + edge_name + '/dynamic/' + edge_name + '.txt'
            print(file_path)
            edge_observations_dict[edge_name].add_observations_from_file(file_path)

        # make sure our output path exists
        path = './' + base_dir + '/results/'
        if not os.path.exists(path):
            os.makedirs(path)

        # generate the output files for all the edges
        for edge_name in edge_observations_dict.keys():
            file_path = path + edge_name + '.out'
            print(file_path)
            edge_observations_dict[edge_name].to_file(file_path)


