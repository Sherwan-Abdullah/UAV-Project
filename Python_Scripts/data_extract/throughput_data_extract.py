#!/usr/bin/env python3
"""
iperf3 Log Parser
Extracts date/time, upload speed (UL), and download speed (DL) from iperf3_log.txt 
and saves to iperf3_data.txt as CSV
"""

import re
import csv

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
                    results.append({
                        'datetime': current_datetime,
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
            results.append({
                'datetime': current_datetime,
                'upload_mbps': upload_speed,
                'download_mbps': download_speed
            })
                
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    return results

def save_to_csv(data, output_filename):
    """Save data to CSV file"""
    
    if not data:
        print("No data to save!")
        return
    
    try:
        with open(output_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow(['datetime', 'UL', 'DL'])
            
            # Write data
            for row in data:
                writer.writerow([row['datetime'], row['upload_mbps'], row['download_mbps']])
        
        #print(f"Successfully saved {len(data)} records to {output_filename}")
        
        #for row in data:
           # print(f"{row['datetime']}, {row['upload_mbps']}, {row['download_mbps']}")
            
    except Exception as e:
        print(f"Error saving file: {e}")

def main():
    """Main function"""
    
    input_file = 'iperf3_log.txt'
    output_file = 'iperf3_data.txt'
    
    #print(f"Reading from: {input_file}")
    #print(f"Writing to: {output_file}")
    
    # Parse the log file
    data = parse_iperf_log(input_file)
    
    # Save to CSV
    save_to_csv(data, output_file)

if __name__ == "__main__":
    main()
