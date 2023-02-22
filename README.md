# Arena Evaluation

![](http://img.shields.io/badge/stability-stable-orange.svg?style=flat)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![support level: consortium / vendor](https://img.shields.io/badge/support%20level-consortium%20/%20vendor-brightgreen.svg)](http://rosindustrial.org/news/2016/10/7/better-supporting-a-growing-ros-industrial-software-platform)

> 🚧 This project is still under development

The Arena Evaluation package provides tools to record, evaluate, and plot navigational metrics to evaluate ROS navigation planners. It is best suited for usage with our [arena-rosnav repository](https://github.com/Arena-Rosnav/arena-rosnav) but can also be integrated into any other ROS-based project.

It consists of 3 parts:

- [Data recording](#01-data-recording)
- [Data transformation and evaluation](#02-data-transformation-and-evaluation)
- [Plotting](#03-plotting)

<img  src="overview image.png">

<!-- ## General

- To integrate arena evaluation into your project, see the guide [here](docs/integration-requirements.md)
- To use it along side with the arena repository, install the following requirements:

```bash
pip install scikit-learn seaborn pandas matplotlib
``` -->

# Record Data

Record the data by setting `record_data:=true` when starting up the ros structure. Doing so will create a new folder in `/data` and fill it with multiple `.csv` files, each containing one topic.

# Transform data and calculate metrics

To transform the dataset for later plotting and calculate the metrics from the recorded data run `python get_metrics.py --dir <DIR>`, whereas `dir` is the directory which is created in the recording phase. The metrics which are created are shown in the following table:

| Name                 | Datatype                             | Description                                                                                                                               |
| -------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| curvature            | Float[]                              | The curvature of the planner for each <br>timestep calculated with the [menger curvature](https://en.wikipedia.org/wiki/Menger_curvature) |
| normalized curvature | Float[]                              | The curvature multiplied by the length of the<br> path for this specific part.                                                            |
| roughness            | Float[]                              | Describes how sudden and abrupt the planner changes directions.                                                                           |
| path length          | Float                                | The complete length of the part                                                                                                           |
| path length values   | Float[]                              | The length of each path between two continuous timestamps                                                                                 |
| acceleration         | Float[]                              | The acceleration of the robot. Calculated as the gradient between two velocities.                                                         |
| jerk                 | Float[]                              | Describes the change in acceleration.                                                                                                     |
| velocity             | Float[][]                            | The real velocity of the robot.                                                                                                           |
| cmd_vel              | Float[][]                            | The robots desired velocity denoted by the planner                                                                                        |
| collision amount     | Int                                  | Absolute amount of collisions in an episode.                                                                                              |
| collisions           | Int[]                                | Index of the positions in which a collision occured.                                                                                      |
| path                 | Float[][]                            | Array of positions in which the robot was located for specific timestamps.                                                                |
| angle over length    | Float                                | The complete angle over the complete length of the path the robot took.                                                                   |
| time diff            | Int                                  | The complete time of the episode.                                                                                                         |
| result               | TIMEOUT \| GOAL_REACHED \| COLLISION | The reason the episode has ended.                                                                                                         |

# Plot Data

In order to make plotting easy, the plots are created from a declaration file, in which the exaclt data you want to plot is described. The declaration file should have the following schema, which is also shown in `plot_declarations/sample_schema.yaml`:

```yaml
# Wether you want to show or save the plots
show_plots: boolean
# Name of the directory in ./path
save_location: string

# List of all datasets that should be compared
# Name of the directory in ./data
datasets: string[]

# Wether you want to plot the result counts
results:
    # Should plot?
    plot: boolean
    # Title of the plot
    title: string
    # Name of the file the plot should be saved ot
    save_name: string
    # Denotes which data should be shown seperately for a single planner
    differentiate: key in Dataset
    # Additional Plot arguments
    plot_args: {} # Optional


# Plot values that are collected in every time step.
# Thus, being arrays for each episode.
# Possible values are:
# - curvature
# - normalized_curvature
# - roughness
# - path_length_values
# - acceleration
# - jerk
# - velocity

#  It is possible to plot
#  - A line plot to show the course in a single episode
#    You can list multiple value to create multiple plots
single_episode_line:
  # Name of the coloumn you want to plot
  - data_key: string # Required
    # Number of values that should be skipped to reduce datapoints
    step_size: int # Optional -> Defaults to 5
    # Coloumn for differentiation
    # Denotes which data should be shown seperately for a single planner
    differentiate: key in Dataset
    # Index of the episode -> If none all episodes are plotted
    episode: int # Optional -> Defaults to none
    title: string
    save_name: string
    plot_args: {} # Optional
# - A Distributional plot for a single episode
#   You can list multiple value to create multiple plots
single_episode_distribution:
  - data_key: string
    episode: int
    # Denotes which data should be shown seperately for a single planner
    differentiate: key in Dataset
    plot_key: "swarm" | "violin" | "box" | "boxen" | "strip" # Optional -> Defaults to "swarm"
    title: string
    save_name: string
    plot_args: {} # Optional
# - A line plot showing aggregated values for all episodes.
#   Like a line plot for the max value of each episode
aggregated_distribution:
  - data_key: string
    # Denotes which data should be shown seperately for a single planner
    differentiate: key in Dataset
    # Function that should be used for aggregation. We offer: max, min, mean
    aggregate: "max" | "min" | "mean" | "sum"
    # Name of the dist plot you want to use. Can be strip, swarm, box, boxen, violin
    plot_key: "swarm" | "violin" | "box" | "boxen" | "strip" # Optional -> Defaults to "swarm"
    title: string
    save_name: string
    plot_args: {} # Optional
# - A distributional plot for aggregated values for all episodes.
aggregated_line:
  - data_key: string
    # Denotes which data should be shown seperately for a single planner
    differentiate: key in Dataset
    # Function that should be used for aggregation. We offer: max, min, mean
    aggregate: "max" | "min" | "mean" | "sum"
    title: string
    save_name: string
    plot_args: {} # Optional


## Plot values that are collected for each episode.
# Single values for each episode
# Possible values are:
# - time_diff
# - angle_over_length
# - path_length

# It is possible to plot
# - A categorical plot over all episodes to show the values in a line or bar plot
all_episodes_categorical:
  - data_key: string
    # Denotes which data should be shown seperately for a single planner
    differentiate: key in Dataset
    plot_key: "line" | "bar"
    title: string
    save_name: string
    plot_args: {} # Optional
# - Plot a distribution over all episodes
all_episodes_distribution:
  - data_key: string
    # Denotes which data should be shown seperately for a single planner
    differentiate: key in Dataset
    plot_key: "swarm" | "violin" | "box" | "boxen" | "strip" # Optional -> Defaults to "swarm"
    title: string
    save_name: string
    plot_args: {} # Optional


## Plot the path the robots took

# Plot all paths of all episodes for each robot
episode_plots_for_namespaces:
    # list of desired results that should be plotted
    desired_results: ("TIMEOUT" | "GOAL_REACHED" | "COLLISION")[]
    # Wether or not to add the obstacles from the scenario file to the plot
    should_add_obstacles: boolean # Optional -> Defaults to False
    # Wether or not to mark where collisions happened
    should_add_collisions: boolean # Optional -> Defaults to False
    title: string
    save_name: string

# Plot the best path of each robot
# Only select the paths that reached the goal and take the path that took the least amount of time
create_best_plots:
    # Wether or not to add the obstacles from the scenario file to the plot
    should_add_obstacles: boolean # Optional -> Defaults to False
    # Wether or not to mark where collisions happened
    should_add_collisions: boolean # Optional -> Defaults to False
    title: string
    save_name: string

```

<!-- ## 01 Data Recording

To record data as csv file while doing evaluation runs set the flag `recorder_data:="true"` in your `roslaunch` command. For example:

```bash
workon rosnav
roslaunch arena_bringup start_arena_gazebo.launch world:="aws_house" scenario_file:="aws_house_obs05.json" local_planner:="teb" model:="turtlebot3_burger" use_recorder:="true"
```

The data will be recorded in `.../catkin_ws/src/forks/arena-evaluation/01_recording`.
The script stops recording as soon as the agent finishes the scenario and stops moving or after termination criterion is met. Termination criterion as well as recording frequency can be set in `data_recorder_config.yaml`.

```yaml
max_episodes: 15 # terminates simulation upon reaching xth episode
max_time: 1200 # terminates simulation after x seconds
record_frequency: 0.2 # time between actions recorded
```

> **NOTE**: Leaving the simulation running for a long time after finishing the set number of repetitions does not influence the evaluation results as long as the agent stops running. Also, the last episode of every evaluation run is pruned before evaluating the recorded data.

> **NOTE**: Sometimes csv files will be ignored by git so you have to use git add -f <file>. We recommend using the code below.

```bash
roscd arena-evaluation && git add -f .
git commit -m "evaluation run"
git pull
git push
```

## 02 Data Transformation and Evaluation

1. After finishing all the evaluation runs, recording the desired csv files and run the `get_metrics.py` script in `/02_evaluation`.
   This script will evaluate the raw data recorded from the evaluation and store it (or them) `.ftr` file with the following naming convention: `data_<planner>_<robot>_<map>_<obstacles>.ftr`. During this process all the csv files will be moved from `/01_recording` to `/02_evaluation` into a directory with the naming convention `data_<timestamp>`. The ftr file will be stored in `/02_evaluation`.\
    Some configurations can be set in the `get_metrics_config.yaml` file. Those are:

- `robot_radius`: dictionary of robot radii, relevant for collision measurement
- `time_out_treshold`: treshold for episode timeout in seconds
- `collision_treshold`: treshold for allowed number of collisions until episode deemed as failed

  > **NOTE**: Do NOT change the `get_metrics_config_default.yaml`!\
  > We recommend using the code below:\

  ```bash
  workon rosnav && roscd arena-evaluation/02_evaluation && python get_metrics.py
  ```

  > **NOTE**: If you want to reuse csv files, simply move the desired csv files from the data directory to `/01_recording` and execute the `get_metrics.py` script again.

  The repository can be used in two ways:

  - Firstly it can be used to evaluate the robot performance within the scenario run, e.g visualizing the velocity distribution within each simulation run (this usage mode is currently still under development).
  - Secondly, it can be used to evaluate the robot performance compare robot performance between different scenarios. For this use-case continue with the following step 2.

2. The observations of the individual runs can be joined into one large dataset, using the following script:
   ```bash
   workon rosnav && roscd arena-evaluation/02_evaluation && python combine_into_one_dataset.py
   ```
   This script will combine all ftr files in the `02_evaluation/ftr_data` folder into one large ftr file, taking into account the planner, robot etc.

## 03 Plotting

The data prepared in the previous steps can be visualized with two different modes, the automated or the custom mode.

### Custom Plotting (recommended)

Open the following [notebook](03_plotting/data_visualization.ipynb) to visualize your data. It contains a step-by-step guide on how to create an accurate visual representation of your data. For examples of supported plots (and when to use which plot), refer to the documentation [here](docs/plotting_examples.md).

### Automated Plotting (in development) -->

<!-- The `get_plots.py` script grabs all `data.json` files located in `/02_evaluation` and moves them to `/03_plotting/data`. During the process the last in order JSON file from the grabbed files will be deemed as "most recent" file. If no file was grabbed, the last data.json used for plotting will remain the "most recent" file. Alternatively, it's possible to specify a `data.json` to be used for plotting. To specify a dataset set the following keys in the `get_plots_config.yaml`:

```yaml
specify_data: true
specified_data_filename: <your_dataset>.json
```

For running the script recommend using the code below:
```bash
workon rosnav && roscd arena-evaluation/03_plotting && python get_plots.py
```

#### Mandatory fields:
- `labels`
- `color_scheme`

Make sure for those fields **all** your local planner or planner-waypoint-generator combinations with the robot they were used on are defined. Examples:
- labels:
    - rlca_jackal: RLCA
    - rlca_turtlebot3_burger: RLCA
- color_scheme:
    - rlca_jackal

See the documentation [here](docs/fields.md) for an explanation of the possible parameters fields. -->

<!-- # Mesure complexity of you map

1. run: `roscd arena-evaluation`
2. run: `python world_complexity.py --image_path {IMAGE_PATH} --yaml_path {YAML_PATH} --dest_path {DEST_PATH}`

with:\
 IMAGE_PATH: path to the floor plan of your world. Usually in .pgm format\
 YAML_PATH: path to the .yaml description file of your floor plan\
 DEST_PATH: location to store the complexity data about your map

Example launch:

```bash
python world_complexity.py --image_path ~/catkin_ws/src/forks/arena-tools/aws_house/map.pgm --yaml_path ~/catkin_ws/src/forks/arena-tools/aws_house/map.yaml --dest_path ~/catkin_ws/src/forks/arena-tools/aws_house
``` -->
