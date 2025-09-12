from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

def extract_and_combine_data(lte_log, lte_data):
    tf = TimezoneFinder()

    with open(lte_log, 'r') as infile, open(lte_data, 'w') as outfile:
        outfile.write("Altitude,latitude,longitude,Date Time")
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
            if line.startswith(' $GPGGA'):
                fields = line.split(',')
                if len(fields) >= 10:
                    alt_text = fields[9]
                    if alt_text:
                        altitude = int(float(alt_text) / 10) * 10
                        outfile.write(f"\n {altitude},")
                    else:
                        outfile.write("\n altitude,")

            if line.startswith(' $GPRMC'):
                fields = line.split(',')
                if len(fields) >= 10:
                    lat_text = fields[3]
                    lat_dir = fields[4]
                    lon_text = fields[5]
                    lon_dir = fields[6]
                    utc_time = fields[1]
                    utc_date = fields[9]

                    if lat_text and lon_text and utc_time and utc_date:
                        try:
                            # Latitude
                            lat_deg = float(lat_text[:2]) + float(lat_text[2:]) / 60
                            if lat_dir == 'S':
                                lat_deg *= -1

                            # Longitude
                            lon_deg = float(lon_text[:3]) + float(lon_text[3:]) / 60
                            if lon_dir == 'W':
                                lon_deg *= -1

                            # UTC datetime object
                            dt_utc = datetime.strptime(utc_date + utc_time.split('.')[0], "%d%m%y%H%M%S")
                            dt_utc = pytz.utc.localize(dt_utc)

                            # Timezone lookup
                            tz_name = tf.timezone_at(lat=lat_deg, lng=lon_deg)
                            if tz_name:
                                tz = pytz.timezone(tz_name)
                                dt_local = dt_utc.astimezone(tz)
                                local_time_str = dt_local.strftime("%Y/%b/%d %H:%M:%S")
                            else:
                                local_time_str = dt_utc.strftime("%Y/%b/%d %H:%M:%S")

                            outfile.write(f"{lat_deg},{lon_deg},{local_time_str},")
                        except Exception as e:
                            print("Error parsing GPRMC:", e)
                            outfile.write("invalid_lat,invalid_lon,invalid_time,")
                    else:
                        outfile.write("lat,lon,date time,")
            
            if line.startswith(' "servingcell"'):
                fields = line.split(',')
                if len(fields) >= 17:
                    MCC = fields[4]
                    MNC = fields[5]
                    PCI = fields[7]
                    EARFCN = fields[8]
                    CellID = str(int(fields[6], 16) // 256) + "." + str(int(fields[6], 16) % 256)
                    LAC = int(fields[12], 16)
                    RSRP = fields[13]
                    RSRQ = fields[14]
                    RSSI = fields[15]
                    SINR = fields[16]
                    outfile.write(f"{MCC},{MNC},{PCI},{EARFCN},{CellID},{LAC},{RSRP},{RSRQ},{RSSI},{SINR},")
            
            if line.startswith(' "neighbourcell intra"'):
                fields = line.split(',')
                if len(fields) >= 8:
                    NB_EARFCN = fields[2]
                    NB_PCI = fields[3]
                    NB_RSRQ = fields[4]
                    NB_RSRP = fields[5]
                    NB_RSSI = fields[6]
                    outfile.write(f"{NB_EARFCN},{NB_PCI},{NB_RSRQ},{NB_RSRP},{NB_RSSI},")

# Usage
extract_and_combine_data('lte_log.txt', 'lte_data.txt')


