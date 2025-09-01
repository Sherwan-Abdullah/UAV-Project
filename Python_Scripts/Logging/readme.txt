The script files are to record the metrics of:

- RAN_logging.py records the Radio Access Network parameters every 1 second, including 
      - Serving cell parameters such as RSRP, RSRQ, RSSI, SINR, CellID, LAC, PCI, EARFCN, MCC, MNC
      - Neighboring Cell parameters such as RSRP, RSRQ, RSSI, PCI


- Delay_logging.py records the RTT (in msec) between the LTE modem and a dedicated server using Nping tool; this test is done every 1 second.


- Speed_logging.py records the bidirectional throughput (Uplink and Downlink) in Mbps using Iperf3 protocol; this test is done every 2 seconds.
