import re
import csv
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

def parse_iperf_log(filename):
    """Parse iperf3_log.txt and extract test data"""
    
    results = []
    
    try:
        with open(filename, 'r') as file:
            content = file.read()
            
        lines = content.strip().split('\n')
        
        current_datetime = None
        upload_speed = None
        download_speed = None
        
        for line in lines:
            line = line.strip()
            
            # Match datetime pattern (2025/Sep/04 22:47:45)
            datetime_match = re.match(r'(\d{4}/\w{3}/\d{2}\s+\d{2}:\d{2}:\d{2})', line)
            if datetime_match:
                # If we have a complete test, save it before starting new one
                if current_datetime and upload_speed and download_speed:
                    # Split datetime into separate Date and Time
                    date_part, time_part = current_datetime.split(' ', 1)
                    results.append({
                        'date': date_part, # Stored separately
                        'time': time_part, # Stored separately
                        'upload_mbps': upload_speed,
                        'download_mbps': download_speed
                    })
                
                # Start new test
                current_datetime = datetime_match.group(1)
                upload_speed = None
                download_speed = None
                continue
            
            # Extract TX-C (upload) sender speed
            tx_match = re.search(r'\[\s*\d+\]\[TX-C\].*?([\d.]+)\s+Mbits/sec.*?sender', line)
            if tx_match and current_datetime:
                upload_speed = float(tx_match.group(1))
            
            # Extract RX-C (download) sender speed  
            rx_match = re.search(r'\[\s*\d+\]\[RX-C\].*?([\d.]+)\s+Mbits/sec.*?sender', line)
            if rx_match and current_datetime:
                download_speed = float(rx_match.group(1))
        
        # Don't forget the last test if file doesn't end with timestamp
        if current_datetime and upload_speed and download_speed:
            # Split datetime into separate Date and Time
            date_part, time_part = current_datetime.split(' ', 1)
            results.append({
                'date': date_part, # Stored separately
                'time': time_part, # Stored separately
                'upload_mbps': upload_speed,
                'download_mbps': download_speed
            })
                
    except FileNotFoundError:
        print(f"Warning: {filename} not found! Skipping throughput data.")
        return []
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []
    
    return results

def extract_ran_data(lte_log, lte_data):
    """Extract and combine RAN data from LTE log"""
    
    try:
        tf = TimezoneFinder()

        # Header: "Date,Time" is now split into "Date" and "Time" columns
        with open(lte_log, 'r') as infile, open(lte_data, 'w') as outfile:
            outfile.write("Altitude,latitude,longitude,Date,Time") 
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
                            outfile.write(f"\n{altitude},")
                        else:
                            outfile.write("\naltitude,")

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
                                    # Data is now split into Date and Time fields
                                    date_str = dt_local.strftime("%Y/%b/%d")
                                    time_str = dt_local.strftime("%H:%M:%S")
                                else:
                                    date_str = dt_utc.strftime("%Y/%b/%d")
                                    time_str = dt_utc.strftime("%H:%M:%S")

                                # Write two separate fields: lat, lon, Date, Time
                                outfile.write(f"{lat_deg},{lon_deg},{date_str},{time_str},")
                            except Exception as e:
                                print("Error parsing GPRMC:", e)
                                # Write 4 placeholder fields
                                outfile.write("invalid_lat,invalid_lon,invalid_date,invalid_time,")
                        else:
                            # Write 4 placeholder fields
                            outfile.write("LAT,LON,Dat,Time,") 
                
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
        
        print(f"✅ RAN data extracted to {lte_data}")
        
    except FileNotFoundError:
        print(f"Warning: {lte_log} not found! Skipping RAN data.")
    except Exception as e:
        print(f"Error processing RAN data: {e}")

def parse_nping_log(input_file):
    """Parse nping log and extract delay data"""
    
    try:
        # Read file content
        with open(input_file, "r") as file:
            content = file.read()

        # Split entries based on Date and Time
        entries = re.split(r"(Date and Time: \d{4}/\w{3}/\d{2} \d{2}:\d{2}:\d{2})", content)
        entries = [e.strip() for e in entries if e.strip()]
        grouped = [(entries[i], entries[i+1]) for i in range(0, len(entries)-1, 2)]

        # Extract and store info
        summary = []
        for timestamp, block in grouped:
            dt_with_space = timestamp.replace("Date and Time: ", "")
            
            # Split datetime into separate Date and Time
            date_part, time_part = dt_with_space.split(' ', 1)

            # Extract Max RTT (or N/A)
            rtt_match = re.search(r"Max rtt: ([\d.]+|N/A)", block)
            max_rtt = rtt_match.group(1) if rtt_match else "N/A"

            # Sent packets
            sent_match = re.search(r"Raw packets sent: (\d+)", block)
            sent = sent_match.group(1) if sent_match else "0"

            # Received packets
            rcvd_match = re.search(r"Rcvd: (\d+)", block)
            rcvd = rcvd_match.group(1) if rcvd_match else "0"

            # Save as separate Date and Time fields
            summary.append((date_part, time_part, max_rtt, sent, rcvd)) 
        
        return summary
        
    except FileNotFoundError:
        print(f"Warning: {input_file} not found! Skipping delay data.")
        return []
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return []

def save_to_csv(data, output_filename, headers):
    """Save data to CSV file"""
    
    if not data:
        print(f"No data to save to {output_filename}!")
        return
    
    try:
        with open(output_filename, 'w', newline='') as file:
            # Writing headers now works without quoting because fields contain no comma
            writer = csv.writer(file)
            writer.writerow(headers) 
            
            if isinstance(data[0], dict):
                # For throughput data (iperf) - uses 'date' and 'time' keys
                for row in data:
                    writer.writerow([row['date'], row['time'], row['upload_mbps'], row['download_mbps']])
            else:
                # For delay data (nping) (tuples) - starts with (date, time, ...)
                writer.writerows(data)
        
        print(f"✅ Successfully saved {len(data)} records to {output_filename}")
            
    except Exception as e:
        print(f"Error saving {output_filename}: {e}")

def main():
    """Main function to process all data types"""
    
    print("🚀 Starting Unified Network Data Extraction...")
    print("=" * 50)
    
    # File mappings
    files = {
        'throughput': {
            'input': 'iperf3_log.txt',
            'output': 'iperf3_data.txt',
            # Split 'Date,Time' into 'Date', 'Time'
            'headers': ['Date', 'Time', 'UL', 'DL'] 
        },
        'ran': {
            'input': 'lte_log.txt',
            'output': 'lte_data.txt'
        },
        'delay': {
            'input': 'nping_log.txt',
            'output': 'nping_data.txt',
            # Split 'Date,Time' into 'Date', 'Time'
            'headers': ['Date', 'Time', 'Max_RTT_ms', 'Sent_Packets', 'Received_Packets']
        }
    }
    
    # Process throughput data
    print("📊 Processing throughput data...")
    throughput_data = parse_iperf_log(files['throughput']['input'])
    if throughput_data:
        save_to_csv(throughput_data, files['throughput']['output'], files['throughput']['headers'])
    
    # Process RAN data
    print("📡 Processing RAN data...")
    extract_ran_data(files['ran']['input'], files['ran']['output'])
    
    # Process delay data
    print("⏱️  Processing delay data...")
    delay_data = parse_nping_log(files['delay']['input'])
    if delay_data:
        save_to_csv(delay_data, files['delay']['output'], files['delay']['headers'])
    
    print("=" * 50)
    print("🎉 Network data extraction complete!")
    print("\nOutput files:")
    print(f"  • {files['throughput']['output']} - Throughput data")
    print(f"  • {files['ran']['output']} - RAN data")  
    print(f"  • {files['delay']['output']} - Delay data")

if __name__ == "__main__":
    main()
