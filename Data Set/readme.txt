This aim of this file is to clarify the data set naming and content

==================================================================================


Naming of the folders:

	The first part is the date of the dataset (YY_MM_DD)

	The secong part is how this test performed (walk, drive, or flight)

	The thrid part is what data obtained from that test (1 radio parameter "ex: RSSI, LTE paramters "RSRP,RSRQ,...etc", Iperf "network speed in Mbps", Ping "connection delay in msec", Wifi data since the pMLTE module have a 2.4GHz wifi modem built in)
	
    The forth part is how these data points obtained (WebGUI "which the built in module method", Pyton code "a code written from scratch to get these data") 
	
==================================================================================	

Inside each folder Test logs, maps, and statistics and as below

Folder named "LTE logs": this folder contains text files (depend on what data collected in that test)
- lte_log.txt: this text file contains the raw data of the test obtained
- lte_data.txt: this text file contains the extracted data from the lte_log and ready for processing
- iperf3_log.txt: this text file contain the raw data of the end-to-end speed test by iperf3
- iperf3_data.txt: this text file contains the extracted data of the speed test ready for processing
- nping_log.txt: this text file contain the raw data of the end-to-end delay test by nping
- nping_data.txt: this text file contain the extracted data of the end-to-end delay ready for porcessing

 -------------------------------------

Folder named "LTE maps": this folder conatins the spatio heat map of the LTE radio parameters RSRP, RSRQ
SINR, RSSI, ... etc depend on the data collected from the test and on street view map

 -------------------------------------

Folder named "LTE Statistics": this folder conatins PNGs CDF and PDF of the LTE radio parameter per whole 
test and per serving cell level

 and all above PNGs will be combined in 1 PDF file