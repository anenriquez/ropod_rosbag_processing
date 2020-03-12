# Rosbag Processing

Gathers information about the edges traversed by the robot based on ROS bagfiles. 

### Installation
Get the requirements:
```
pip3 install -r requirements.txt
```
Install the package:
```
pip3 install --user -e .
```

### Steps

1. Merge bagfiles: Joins bagfiles to include complete runs. In order to detect the robot entering and leaving an edge,
 a run should not be split between bagfiles. Includes only the topics: `/amcl_pose` and 
`/autonomous_navigation/local_costmap/costmap`
```
pip3 merge_bag.py
``` 

2. Process bagfiles: Gathers travel time and number of obstacles per edge. 
```
pip3 process_bagfiles.py
``` 

3. Concatenate travel time information into a file: Generates an `all_runs.out` file per edge. This file contains all
the travel information for all the bagfiles that included information for that edge. 

Go to the `travel_time` folder within the base directory defined in the config file (e.g. `angela`)
``` 
./cat_files.sh
``` 

4. Generate results: Creates an `.out` file per edge.
``` 
python3 results.generator.py
```  

5. Generate summary: Creates a `.summary` file per edge.

``` 
python3 get_edge_summary.
```

### Config files

- `logger_name`: Name of the TravelLogger object collecting the edge information.

- `edges`: Edges of interest for the TravelLogger.

- `base_dir`: Name of the directory where the edge information will be stored.

- `event_radius`: Builds a circumference with center at the node's coordinates. The robot is considered to be at the 
node if its position is inside the circumference.

- `event_threshold`: Triggers the entrance and exit to the `event_radius` circumference. 

- `min_distance_static_samples`: Minimum distance between obstacle samples in the ground truth. 

- `nodes`: Nodes of interest (in separate config file)

### TravelLogger

- Based on the robot's current pose at each timestamp of the `/amcl_pose` topic, checks whether an edge has been 
traversed or not.

- Keeps track of the edges traversed by the robot and computes the time taken to go from the start node to the finish 
node of an edge (i.e., the edge travel time).

- Compares the number of obstacles (taken from the `/autonomous_navigation/local_costmap/costmap` topic) and the number 
of obstacles in the ground truth to estimate the number of dynamic obstacles encountered by the robot while traversing
an edge. 

- The ground truth is taken from bagfiles where the robot did not encounter obstacles. A `static.csv` file with ground
truth information is generated per edge. 

- The number of obstacles at a current time and robot's pose is computed using the `/autonomous_navigation/local_costmap/costmap` 
topic. 

- Costmaps are processed every second to get the number of obstacles at the current time and robot's pose. The number of
obstacles is the number of clusters computed using the Density-Based Spatial Clustering of Applications with Noise 
[DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html) from sklearn.


### Defining several lanes

Add a .yaml file per lane. E.g., `config/angela/square` includes:
- common_lane.yaml
- connection_lane.yaml
- left_lane.yaml
- right_lane.yaml

The `process_bagfiles.py` script creates a TravelLogger per lane, so that each lane is processed only once.

Possible scenarios: 

- The robot travels between the event radius of two lanes: Information for both lanes is stored. 

<img src="https://github.com/anenriquez/ropod_rosbag_processing/blob/master/ropod_rosbag_processing/images/two_lanes_1.png" width="1000">

- The robot travels only within the event radius of a lane: Information for that lane is stored.

<img src="https://github.com/anenriquez/ropod_rosbag_processing/blob/master/ropod_rosbag_processing/images/two_lanes_2.png" width="1000">

- The robot travels within the event radius of the starting node of one lane and the ending node of the other lane: No
information is stored for any of the lanes.
<p align="center">
  <img src="https://github.com/anenriquez/ropod_rosbag_processing/blob/master/ropod_rosbag_processing/images/two_lanes_3.png" width="300">
</p>


### Results directory structure

```
├── base_dir
|   └── obstacles
|      └── edge_name
|         ├── dynamic
|         |   └── edge_name.txt
|         ├── total
|         |   ├── edge_name_bagfile_1_name.txt
|         |   ├── edge_name_bagfile_2_name.txt
|         |   ...
|         |   └── edge_name_bagfile_n_name.txt
|         └── static.csv 
|   └── results 
|      ├── edge_name.out
|      └── edge_name.summary
|   └── travel_time 
|      └── edge_name
|         ├── edge_name_bagfile_1_name.txt
|         ├── edge_name_bagfile_2_name.txt
|         |   ...
|         ├── edge_name_bagfile_n_name.txt 
|         ├── all_runs.out 
|         └── HEADER.info 
└────── cat_files.sh 

```

### File Description

**Definitions:**

- `start_timestamp`: Time at which the robot started traversing the edge.
- `n_dynamic_obstacles`: Number of dynamic obstacles encountered while traversing the edge.
- `n_static_obstacles`: Number of static obstacles encountered while traversing the edge.
- `n_total_obstacles`: Number of obstacles (dynamic and static) encountered while traversing the edge.
- `travel_time`: Time taken to traverse the edge.
- `average_n_obstacles`: Average number of obstacles encountered while traversing and edge.
- `max_n_obstacles`: Maximum number of obstacles encountered while traversing an edge.
- `n_runs`: Number of times the robot traversed the edge.
- `mean_travel_time`: Mean travel time (also called duration) for the `n_runs` the robot traversed the edge.
- `standard_deviation_travel_time`: Standard deviation of the travel time for the `n_runs` the robot traversed the edge.

**Files:**

- Dynamic obstacles: `base_dir/obstacles/edge_name/dynamic/edge_name.txt`
```
start_timestamp n_dynamic_obstacles
```

- Total obstacles: `base_dir/obstacles/edge_name/total/edge_name_bagfile_1_name.txt`
```
start_timestamp n_total_obstacles
```

- Static obstacles: `base_dir/obstacles/edge_name/static.csv`
```
start_timestamp n_static_obstacles x_coordinate y_coordinate
```
- Travel times: `base_dir/travel_time/edge_name/edge_name_bagfile_1_name.txt`
```
start_timestamp travel_time
```

- All runs travel time: `base_dir/travel_time/edge_name/all_runs.out`
  Includes the travel time for all bagfiles.
```
start_timestamp travel_time
```

- Edge header: `base_dir/travel_time/edge_name/HEADER.info`
(One file for all bagfiles)

```
HEADER INFO: edge_name distance
NODE NAMES: name_node_1 name_node_2
POSITIONS: pose_node_1 pose_node_2
```

- Results: `base_dir/results/edge_name.out`
```
start_timestamp travel time average_n_obstacles max_n_obstacles
```

- Summary of results:`base_dir/results/summary.out` 
```
n_runs mean_travel_time standard_deviation_travel_time max_n_obstacles
```
