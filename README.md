# NICA Experiment

This repository belongs to the MPD project and contains software developed during the research
to clean up data obtained after running the ACTS tool.

Repository organization:
1) The file parallel_analyse_example.py contains an example of processing data from one event using all the algorithms we have developed
2) analyze folder - contains software for analyzing the operation of algorithms (including tracks-visualization)
3) data folder - contains examples of test data
4) data_processing folder - contains software for loading data or type casting
5) post_processing folder - Contains the post-processing methods we developed

# OS and Python
_All tests were performed in Python-3.10 on Ubuntu-22.04_

# Installation
```shell
git clone https://github.com/PlekhanovRUE/mpd_tpc_tracker/ .
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Try algorithms
You can test our algorithms by running the following command
```shell
python parallel_analyse_example.py
```
config.py file contains some work settings that you can change at your discretion - such as the number of threads 
for processing tracks, which events will be processed, etc.

# Try Visualization
To use it you need GUI on your system!

You can test visualization of our algorithms by running the following command
```shell
python visualizing_example.py
```
In default settings you will see results of analyse event 0.

Navigation in GUI mode:
1) Mouse wheel - Zoom
2) LMB - Rotate the object
3) CTRL + LMB - Move an object

Hotkeys in GUI mode:
1) Press 'i' - Enable/Disable display of track indexes
2) Press 's' - Enable/Disable display of data from simulation
3) Press 't' - Enable/Disable display of track arcs
4) When you enable multiple post-processing methods at the same time, you can use the number keys (1, 2, etc.) to switch visualization between them
