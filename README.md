# Atlas

Atlas contains several folders with different functionalities.

analyze_codes: The scripts associated with how to analyze the obtained/existing traces are put here. (May be merged with the folder plot latter)

conduct_measurements: The scripts used to conduct the different kinds of active measurements are put in this folder.

figures_and_tables: The obtained figures and tables are stored here to simplify writting reports and showing the results.

plot: The scripts belong to this folder are used to generate the figures using the already analyzed traces. This folder may merge with the folder analyze_codes someday, when we need to produce the figures as long as the traces are analyzed.

traces: A folder used to store the download traces, which can be further divied into "Built-in_measurement_traces" and "Produced_traces".

Before executing the scripts, some environment variables should be added in ~/.bash_profile:

export  ATLAS_ANALYZE_TRACES=$HOME/Documents/Codes/Atlas/analyze_traces

export  ATLAS_CONDUCT_MEASUREMENTS=$HOME/Documents/Codes/Atlas/conduct_measurements

export  ATLAS_FIGURES_AND_TABLES=$HOME/Documents/Codes/Atlas/figures_and_tables

export  ATLAS_PLOT=$HOME/Documents/Codes/Atlas/plot

export  ATLAS_TRACES=$HOME/Documents/Codes/Atlas/traces

export  ATLAS_WENQIN_CODES=$HOME/Documents/Codes/Atlas/Wenqin_codes

export  ATLAS_AUTH=$HOME/Documents/Codes/Atlas/auth
