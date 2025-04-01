import os
import time

def extract_and_combine_data(lte_log, lte_data):
    last_modified = os.path.getmtime(lte_log)
    while True:
        current_modified = os.path.getmtime(lte_log)
        if current_modified != last_modified:
            last_modified = current_modified
            with open(lte_log, 'r') as infile, open(lte_data, 'w') as outfile:
                outfile.write("Date Time,latitude,longitude")
                outfile.write(",MCC,MNC,PCI,EARFCN,CellID,LAC,RSRP,RSRQ,RSSI,SINR")
                outfile.write(",NB1_EARFCN,NB1_PCI,NB1_RSRQ,NB1_RSRP,NB1_RSSI")
                outfile.write(",NB2_EARFCN,NB2_PCI,NB2_RSRQ,NB2_RSRP,NB2_RSSI")
                outfile.write(",NB3_EARFCN,NB3_PCI,NB3_RSRQ,NB3_RSRP,NB3_RSSI")
                outfile.write(",NB4_EARFCN,NB4_PCI,NB4_RSRQ,NB4_RSRP,NB4_RSSI")
                outfile.write(",NB5_EARFCN,NB5_PCI,NB5_RSRQ,NB5_RSRP,NB5_RSSI")
                outfile.write(",NB6_EARFCN,NB6_PCI,NB6_RSRQ,NB6_RSRP,NB6_RSSI")
                outfile.write(",NB7_EARFCN,NB7_PCI,NB7_RSRQ,NB7_RSRP,NB7_RSSI")
                outfile.write(",NB8_EARFCN,NB8_PCI,NB8_RSRQ,NB8_RSRP,NB8_RSSI")
                outfile.write(",NB9_EARFCN,NB9_PCI,NB9_RSRQ,NB9_RSRP,NB9_RSSI")
                outfile.write(",NB10_EARFCN,NB10_PCI,NB10_RSRQ,NB10_RSRP,NB10_RSSI")
                
                for line in infile:
                if line.startswith (' System Time      :'):
                    fields = line.split(' ')
                    if len(fields) >= 14:
                        year = fields[13].strip()
                        month = fields[10].strip()
                        day = fields [11].strip()
                        time_stamp = fields[12].strip()                        
                        outfile.write(f"\n{year}/{month}/{day} {time_stamp},")
                if line.startswith(' $GPRMC'):
                    fields = line.split(',')
                    if len(fields) >= 10:
                        lat_text = fields[3]
                        lon_text = fields[5]                        
                        if lat_text and lon_text:
                            lat_deg = float(lat_text[:2]) + float(lat_text[2:]) / 60
                            lon_deg = -1 * (float(lon_text[:3]) + float(lon_text[3:]) / 60)
                            outfile.write(f"{lat_deg},{lon_deg},")
                        else: outfile.write(",,") 
                    if line.startswith(' "servingcell"'):
                        fields = line.split(',')
                        if len(fields) >= 17:
                            MCC = fields[4]
                            MNC = fields[5]
                            PCI = fields[7]
                            EARFCN = fields[8]
                            CellID = str(int(fields[6], 16)//256)+"."+str(int(fields[6], 16)%256)
                            LAC = int(fields[12],16)
                            RSRP = fields[13]
                            RSRQ = fields[14]
                            RSSI = fields[15]
                            SINR = fields[16]
                            outfile.write (f"{MCC},{MNC},{PCI},{EARFCN},{CellID},{RSRP},{RSRQ},{RSSI},{SINR},")

                    if line.startswith(' "neighbourcell intra"'):
                        fields = line.split(',')
                        if len(fields) >= 8:
                            NB_EARFCN = fields[2]
                            NB_PCI = fields[3]
                            NB_RSRQ = fields[4]
                            NB_RSRP = fields[5]
                            NB_RSSI = fields[6]
                            outfile.write (f"{NB_EARFCN},{NB_PCI},{NB_RSRQ},{NB_RSRP},{NB_RSSI},")
        time.sleep(0)  # Sleep for a while before checking again

# 'lte_log.txt' is the output file of the test result and 'lte_data.txt' is the file where the test data are rearranged
extract_and_combine_data('lte_log.txt', 'lte_data.txt')
