import numpy as np
import yaml
from ropod_rosbag_processing.utils.utils import load_yaml


def get_landmarks(source_map, goal_map, section):
    landmarks = load_yaml("maps/reference_landmarks.yaml")
    original = landmarks.get(source_map).get(section)
    goal = landmarks.get(goal_map).get(section)

    # The landmark names should be the same
    names, original_landmarks = get_data_matrix(original)
    names, goal_landmarks = get_data_matrix(goal)

    return names, original_landmarks, goal_landmarks


def get_data_matrix(nodes):
    names = list()
    x = list()
    y = list()
    for node in nodes:
        for name, pose in node.items():
            names.append(name)
            x.append(pose[0])
            y.append(pose[1])
    x = np.asarray(x)
    y = np.asarray(y)
    return names, np.vstack((x, y))


def get_transformation_procrustes(original_landmarks, goal_landmarks):
    """Returns the rotation and translation required to transform
    "original_landmarks to "goal_landmarks"

    Keyword arguments:
    original_landmarks -- an n x m matrix of landmark positions in the original map
    goal_landmarks -- an n x m matrix of landmark positions in the goal map

    """
    c_real = np.mean(original_landmarks, axis=1)[np.newaxis].T
    c_measured = np.mean(goal_landmarks, axis=1)[np.newaxis].T

    A = original_landmarks - c_real
    B = goal_landmarks- c_measured

    U,s,VT = np.linalg.svd(A.dot(B.T))

    # Q is a 2x2 rotation matrix: V.U^T
    Q = VT.T.dot(U.T)

    # calculate theta from rotation matrix
    theta = np.arctan2(Q[1,0], Q[0,0])
    print('Rotation: %f' % np.degrees(theta))

    translation = c_measured - Q.dot(c_real)
    print('Translation:\n%s' % (translation,))

    return theta, Q, translation


def update_topology(topology_file, new_poses):
    topology = load_yaml(topology_file)
    for node in topology.get("nodes"):
        new_pose = new_poses.get(node["id"])
        node["pose"] = new_pose

    new_topology_file = topology_file.replace('topology', 'topology_updated')
    with open(new_topology_file, 'w') as outfile:
        yaml.safe_dump(topology, outfile, default_flow_style=False)


if __name__ == '__main__':
    # Transforms nodes from osm map to guido

    all_nodes = load_yaml('maps/osm/osm_nodes.yaml')
    transformed_nodes = dict()

    for section, nodes in all_nodes.items():
        print("section: ", section)
        names, original_data = get_data_matrix(nodes)

        _, _original_landmarks, _goal_landmarks = get_landmarks('osm', 'guido', section)
        theta, Q, translation = get_transformation_procrustes(_original_landmarks, _goal_landmarks)
        transformed = Q.dot(original_data) + translation
        for i, name in enumerate(names):
            transformed_nodes[name] = [float(transformed[0][i]), float(transformed[1][i]), 0]

    with open("maps/osm/nodes.yaml", 'w') as outfile:
        yaml.safe_dump(transformed_nodes, outfile, default_flow_style=False)

    topology_file = "maps/osm/topology.yaml"
    update_topology(topology_file, transformed_nodes)

