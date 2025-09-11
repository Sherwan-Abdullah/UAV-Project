# UAV-Project
This is the data logger of a UAV-based system to record the RAN (Radio Access Network of a mobile service provider) and End-to-End network performance (Delay and Throughput). The folders are arranged as below:

- Data_Set: contains the log files of the test performed with a variety of scenarios
- Python_Scripts: contain the scripts of how this project works
    - Logging: contains the Python scripts that log the metric records
    - data_extract: contains the Python scripts that extract the wanted parameters from the log files and arrange them into CSV text files
    - visualize_data: contains the Python scripts that plot the data either to 2D+3D maps or statistical charts
- WebGUI: contains the files that can run a Web based tool to:
    - Extract data from the log files
    - Plot the statistical charts
    - Map RAN metrics on 2D and 3D maps

For the Python scripts inside the data_extract and visualize_data folders, if you want to run any of them, please make sure that the script and the data or the log file are in the same folder


Inside each folder, you will find a README file that contains more information
