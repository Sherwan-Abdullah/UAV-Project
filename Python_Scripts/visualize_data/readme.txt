The script files are to plot the metrics of:

- all_stat_result.py plot all the RAN, Delay, and Throughput statistics charts and save them to a folder named (Statistics Results)

================================================================================================================================================
================================================================================================================================================

but if you want to plot single extracted data from a log file see below:

- RAN_map_2D3D.py maps the serving cell RAN metrics (RSRP, RSRQ, RSSI, and SINR) into a 4X2 HTML file each metric is plotted in 2D and 3D views.
- RAN_statistics.py: plots the below:
    - The CDF charts of RAN metrics for the whole tested area
    - The PDF charts of the LACs and cells that the RAN modem is most connected to
    - The Min vs Mean vs Max RAN metrics for each cell that the RAN modem connected to
    - The altitude-based views, such as the percentage of the data samples collected for each altitude that the UAV passed, and how the RAN metrics behave for each altitude
    - The Neighbor cells RAN metrics behaviour for each cell that the RAN modem connected to.


- Delay_statistics.py: plots the PDF of RTT (between the Radio modem and a dedicated server) into PNG images.


- throughput_statistics.py: plots the CDF of bidirectional throughput (uplink and downlink) into PNG images.
