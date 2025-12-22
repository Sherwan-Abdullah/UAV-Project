This is a WebGUI interface to get all the results without running each script alone, you need just to click some buttons
to do that you need to:

Download all the files in one folder, these files functions are:

(WebGUI.sh + server.py) to start the WebGUI
(all_data_extract.py + all_stat_result.py + RAN_Map.py) to generate the results visualization
(all log files RAN, Delay, and Throughput) the raw data that will be plotted and mapped
(ML_predict_all) to initiate ML models to predict the RAN metrics (RSRP, RSRQ, RSSI, and SINR) with 2 methods of prediction, Leave-One-Altitude-Out LOAO and Genric ML split method 80% train and 20% test

=============================================================================================================================

Running the WebGUI tool

Run WebGUI.sh (right click --> run as program), a web page will be open and you find buttons for:
- browse for the logfiles in the PC
- extracting the data from all logfiles
- plotting the statistical charts
- maping RAN metrics in 2D and 3D maps
- predict the RAN metrics in measured and unmeasured altitudes


 at the top of the web page you will find:
  - the location (path) of the logfiles in your PC
  - the date and time of the test


at the bottom of the web page you will find a link that opens the folder where the logfiles and more results
