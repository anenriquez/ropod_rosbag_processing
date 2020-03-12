import matplotlib.pyplot as plt
import networkx as nx
import json


def load_graph_from_file(json_file):
    with open(json_file) as file_:
        data = json.load(file_)
    graph = nx.node_link_graph(data)
    return graph


def plot(graph, occ_grid, meta_data, map_name, pos='pose'):
    plt.rcParams['figure.figsize'] = [50, 50]
    ax = plt.axes()
    ax.imshow(occ_grid, cmap='gray', interpolation='none', origin='lower')
    resolution = meta_data.get('resolution')
    origin = meta_data.get('origin')
    ymax, xmax = occ_grid.shape

    def map_to_img(x, y):
        x_ = (x - origin[0]) / resolution
        y_ = ymax - ((y - origin[1]) / resolution)
        return [x_, y_]

    pose = nx.get_node_attributes(graph, pos)
    pos_ = {p: map_to_img(coord[0], coord[1]) for p, coord in pose.items()}

    nx.draw_networkx(graph, pos=pos_, node_size=1 / resolution, ax=ax, font_size=6)
    plt.savefig("maps/" + map_name + "/roadmap_complete.png", dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    from matplotlib.pyplot import imread

    map_name = "osm"

    occ_grid = imread('map.pgm', True)
    meta_data = nx.read_yaml('map.yaml')

    data = nx.read_yaml('maps/' + map_name + '/topology_updated.yaml')
    G = nx.node_link_graph(data)

    plot(G, occ_grid, meta_data, map_name)
