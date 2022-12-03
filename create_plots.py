import seaborn as sns
import pandas as pd
import rospkg
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import json
import yaml

from utils import Utils

"""
    TODO: 
    - Create plot titles
    - Check if all legends are added
    - Add dynamic and static obstacles to path map
    - Add collisions to path map
    - Add support for declaration file to declare which data should be plotted and what plots should be used
"""


## Create plots for only one dataset

data_paths = [
    "03-12-2022_15-19-00_burger_0_0",
    "03-12-2022_15-22-43_rto_0_0"
]

DIST_PLOTS = {
    "strip": sns.stripplot,
    "swarm": sns.swarmplot,
    "box": sns.boxplot,
    "boxen": sns.boxenplot,
    "violin": sns.violinplot
}

CAT_PLOTS = {
    "line": sns.lineplot,
    "bar": sns.barplot
}

"""

METRIC FILE SCHEMA:

episode                 INT INCREMENT                           # Index of the episode
curvature               FLOAT[]                                 # (N - 2) menger curvatures
normalized_curvature    FLOAT[]                                 # (N - 2) Normalized curvature
roughness               FLOAT[]                                 # (N - 2) Roughness
path_length_values      FLOAT[]                                 # (N - 1) Length of the path the robot travelled in this step
path_length             FLOAT                                   # Complete path length of the episode
acceleration            FLOAT[]                                 # (N - 1) Difference of velocities
jerk                    FLOAT[]                                 # (N - 2) Rate at which the acceleration changes
velocity                FLOAT[][]                               # (N) Real velocity of the robot
cmd_vel                 FLOAT[][]                               # (N) Desired velocity, output of the network
collision_amount        INT                                     # Sum of collisions in this episode
collisions              INT[]                                   # (unknonw) Index of all collisions
path                    FLOAT[][]                               # (N - 1) Positions for each timestep
angle_over_length       FLOAT                                   # Mean change of the angle over the complete path
action_type             (MOVE | STOP | ROTATE)[]                # Action type of the robot for each timestep
time_diff               INT                                     # Time the episode took, ros time in ns
time                    INT[]                                   # Time of each step
result                  TIMEOUT | GOAL_REACHED | COLLISION      # Wether an episode was successful or not

"""

## FIRST STEP
# Read in all metric files, check if all metrics use the same map and concatenate

datasets = []
scenarios = []

for path in data_paths:
    base_path = os.path.join("data", path)
    metrics = os.path.join(base_path, "metrics.csv")
    params = os.path.join(base_path, "params.yaml")

    assert os.path.exists(
        metrics
    ) and os.path.exists(params), "Metrics or params file does not exist"

    with open(params) as file:
        params_content = yaml.safe_load(file)

    scenarios.append(params_content["scenario_file"])

    dataset = pd.read_csv(metrics, converters={
        "path_length_values": Utils.string_to_float_list,
        "curvature": Utils.string_to_float_list,
        "roughness": Utils.string_to_float_list,
        "time": Utils.string_to_float_list,
        "acceleration": lambda a: json.loads(a),
        "path": lambda a: json.loads(a),
    })

    dataset["local_planner"] = params_content["local_planner"]
    dataset["agent_name"] = params_content["agent_name"]
    dataset["model"] = params_content["model"]
    dataset["namespace"] = params_content["namespace"]

    datasets.append(dataset)

assert len(set(scenarios)) == 1, "Scenario files are not the same"

scenario = scenarios[0]

dataset = pd.concat(datasets)


## FOR RESULT

class ResultPlotter:
    def countplot_for_result(dataset, hue="namespace", plot_args={}):
        sns.count(data=dataset, x="result", hue=hue, **plot_args)


## FOR TIME STEP VALUES -> ARRAYS FOR EACH EPISODE
# curvature, normalized_curvature, roughness, path_length_value, acceleration, velocity

def assert_dist_plot(key):
    assert key in DIST_PLOTS, f"Invalid plot {key} for distribution"

def assert_cat_plot(key):
    assert key in CAT_PLOTS, f"Invalid plot {key} for categorical"

def assert_datakey_valid(key, valid_keys):
    assert key in valid_keys, f"Key {key} not valid"


class EpisodeArrayValuePlotter:
    POSSIBLE_DATA_KEYS = [
        "curvature",
        "normalized_curvature",
        "roughness",
        "path_length_values",
        "acceleration",
        "jerk",
        "velocity"
    ]

    def lineplot_for_single_episode(dataset, data_key, step_size=5, hue="namespace", episode=None, plot_args={}):
        assert_datakey_valid(data_key, EpisodeArrayValuePlotter.POSSIBLE_DATA_KEYS)

        local_data = dataset[[data_key, hue, "time", "episode"]]

        if episode != None:
            local_data = local_data[local_data["episode"] == episode]

        local_data = local_data.apply(lambda x: EpisodeArrayValuePlotter.resize_time(x, data_key, step_size), axis=1)

        local_data = local_data.explode([data_key, "time"]).reset_index()

        sns.lineplot(data=local_data, y=data_key, x="time", hue=hue, **plot_args)

    def distplot_for_single_episode(dataset, data_key, episode=0, plot_key="swarm", plot_args={}):
        assert_datakey_valid(data_key, EpisodeArrayValuePlotter.POSSIBLE_DATA_KEYS)

        assert_dist_plot(plot_key)

        local_data = dataset[dataset["episode"] == episode][[data_key, "namespace"]].explode(data_key)

        DIST_PLOTS[plot_key](data=local_data, y=data_key, x="namespace", **plot_args)

    def distplot_for_aggregated(dataset, data_key, aggregate_callback, differentiate="namespace", plot_key="swarm", plot_args={}):
        assert_datakey_valid(data_key, EpisodeArrayValuePlotter.POSSIBLE_DATA_KEYS)
        assert_dist_plot(plot_key)

        local_data = dataset[[data_key, differentiate]]

        def aggregate_value(row):
            row[data_key] = aggregate_callback(row[data_key])

            return row

        local_data = local_data.apply(aggregate_value, axis=1)

        DIST_PLOTS[plot_key](data=local_data, y=data_key, x=differentiate, **plot_args)

    def lineplot_for_aggregated(dataset, data_key, aggregate_callback, differentiate="namespace", plot_args={}):
        assert_datakey_valid(data_key, EpisodeArrayValuePlotter.POSSIBLE_DATA_KEYS)

        local_data = dataset[[data_key, differentiate, "episode"]].reset_index()

        def aggregate_value(row):
            row[data_key] = aggregate_callback(row[data_key])

            return row

        local_data = local_data.apply(aggregate_value, axis=1)

        sns.lineplot(data=local_data, x="episode", y=data_key, hue=differentiate, **plot_args)

    def resize_time(row, key_reference, step_size):
        time_null = row["time"][0]

        row["time"] = list(map(lambda x: int((x - time_null) / 10e8), row["time"]))
        row["time"] = row["time"][0:len(row[key_reference])]

        row["time"] = row["time"][0::step_size]
        row[key_reference] = row[key_reference][0::step_size]

        return row


## FOR DISCRETE VALUES IN EPISODE

class DiscreteValuePlotter:
    POSSIBLE_VALUES = [
        "time_diff",
        "angle_over_length",
        "collision_amount",
        "path_length"
    ]

    def catplot_over_episodes(dataset, data_key, differentiate="namespace", plot_key="line", plot_args={}):
        assert_datakey_valid(data_key, DiscreteValuePlotter.POSSIBLE_VALUES)
        assert_cat_plot(plot_key)

        CAT_PLOTS[plot_key](data=dataset.reset_index(), x="episode", y=data_key, hue=differentiate, **plot_args)

    def distplot_over_episodes(dataset, data_key, differentiate="namespace", plot_key="swarm", plot_args={}):
        assert_datakey_valid(data_key, DiscreteValuePlotter.POSSIBLE_VALUES)
        assert_dist_plot(plot_key)

        DIST_PLOTS[plot_key](data=dataset.reset_index(), y=data_key, x=differentiate, **plot_args)


## FOR SHOWING PATH THE ROBOT TOOK

class PathVisualizer:

    def __init__(self):
        self.scenario_file, self.scenario_content = PathVisualizer.read_scenario_file(scenario)

        self.map_name = self.scenario_content["map"]
        self.map_path, self.map_content = PathVisualizer.read_map_file(self.map_name)

    def create_map_plot(self):
        map_img = plt.imread(os.path.join(self.map_path, self.map_content["image"]))

        fig, ax = plt.subplots()

        ax.imshow(map_img)

        return fig, ax

    def create_episode_plots_for_namespaces(self, desired_results=[]):
        robots_tested = list(set(dataset["namespace"].to_list()))

        plt.close()

        for namespace in robots_tested:
            fig, ax = self.create_map_plot()

            paths_for_namespace = dataset[dataset["namespace"] == namespace][["path", "result"]]

            path_amount = len(paths_for_namespace.index)

            for i in range(path_amount):
                path = paths_for_namespace["path"][i]
                result = paths_for_namespace["result"][i]

                if len(desired_results) > 0 and not result in desired_results:
                    break 

                path = np.array(list(map(self.ros_to_real_coord, path))).transpose()

                ax.plot(path[0][:-10], path[1][:-10], label="Episode: " + str(i))

            ## TODO PLOT TITLE

            plt.legend()
            plt.show()
            plt.close()

    def create_best_plots(self):
        """
            - Only plot the paths were the goal is reached
            - Plot the path that took the least amount of time
        """
        possible_paths = dataset[dataset["result"] == "GOAL_REACHED"]

        namespaces = list(set(possible_paths["namespace"].to_list()))

        fig, ax = self.create_map_plot()

        for namespace in namespaces:
            paths_for_namespace = possible_paths[possible_paths["namespace"] == namespace]
            
            minimal_path = paths_for_namespace[paths_for_namespace["time_diff"] == paths_for_namespace["time_diff"].min()]["path"].reset_index()

            path = np.array(list(map(self.ros_to_real_coord, minimal_path["path"][0]))).transpose()

            ax.plot(path[0][:-10], path[1][:-10], label=namespace)

        # TODO CREATE PLOT TITLE

        plt.legend()
        plt.show()
        plt.close()

    @staticmethod
    def read_scenario_file(scenario):
        name = os.path.join(rospkg.RosPack().get_path("task-generator"), "scenarios", scenario)

        with open(name) as file:
            content = yaml.safe_load(file)

        return name, content

    @staticmethod
    def read_map_file(map_name):
        map_path = os.path.join(rospkg.RosPack().get_path("arena-simulation-setup"), "maps", map_name)

        with open(os.path.join(map_path, "map.yaml")) as file:
            content = yaml.safe_load(file)

        return map_path, content

    def ros_to_real_coord(self, coord):
        coord = [i / self.map_content["resolution"] for i in coord][:2]

        return coord

    pass

path_visualizer = PathVisualizer()

path_visualizer.create_best_plots()

# codes = [
#     Path.MOVETO,
#     Path.LINETO,
#     Path.LINETO,
#     Path.LINETO,
#     Path.CLOSEPOLY,
# ]

# verts = [
#    (0., 0.),  # left, bottom
#    (0., 100.),  # left, top
#    (100., 100.),  # right, top
#    (100., 0.),  # right, bottom
#    (0., 0.),  # ignored
# ]

# path = Path(verts, codes)
# patch = patches.PathPatch(path, facecolor='none', lw=2, edgecolor="blue")

# # ax.plot([100, 200, 300, 200, 100], [100, 200, 300, 300, 200])

# plt.legend()

# plt.show()
# plt.close()