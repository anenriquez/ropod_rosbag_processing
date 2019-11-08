from math import floor
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN


def from_position_to_coordinates(position, x_range, y_range):
    x = position % x_range - x_range/2
    y = -(floor(position/y_range) - y_range/2)

    return x, y


def from_costmap_to_coordinates(costmap, x_range=200, y_range=200, pos_threshold=30, neg_threshold=0):
    coordinates = list()

    for i, value in enumerate(costmap):
        if value > pos_threshold or value < neg_threshold:
            x, y = from_position_to_coordinates(i, x_range, y_range)
            coordinates.append([x, y])

    return np.asarray(coordinates)


def get_n_obstacles(coordinates):
    db = DBSCAN(eps=5, min_samples=10).fit(coordinates)
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    return n_clusters_


def plot_clusters(costmap):
    coordinates = from_costmap_to_coordinates(costmap)

    fig, axs = plt.subplots(2)
    axs[0].plot(coordinates[:, 0], coordinates[:, 1], 'o', c='b')

    db = DBSCAN(eps=5, min_samples=10).fit(coordinates)
    labels = db.labels_
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    print('Estimated number of clusters: %d' % n_clusters_)
    print('Estimated number of noise points: %d' % n_noise_)

    # Plot result

    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each)
              for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = (labels == k)

        xy = coordinates[class_member_mask & core_samples_mask]
        axs[1].plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=14)

        xy = coordinates[class_member_mask & ~core_samples_mask]
        axs[1].plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=6)

    plt.show()
