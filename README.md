# Atlas

Atlas contains several folders with different functionalities.

analyze_codes: The scripts associated with how to analyze the obtained/existing traces are put here. (May be merged with the folder plot latter)

conduct_measurements: The scripts used to conduct the different kinds of active measurements are put in this folder.

figures_and_tables: The obtained figures and tables are stored here to simplify writting reports and showing the results.

plot: The scripts belong to this folder are used to generate the figures using the already analyzed traces. This folder may merge with the folder analyze_codes someday, when we need to produce the figures as long as the traces are analyzed.

traces: A folder used to store the download traces, which can be further divied into "Built-in_measurement_traces" and "Produced_traces".

Wenqing_codes: A static folder which will not be modified later, since the scripts in this folder are provided by Wenqing to give me a first look at the use of Atlas scripts. There are 3 basic scripts: ping-1.py -- to conduct a ping measuremnt with different parameters; fetch_result.py -- to dowload the experiment traces from Atlas website; plot_ping.py -- to plot a 3D figure associated with RTT of ping.