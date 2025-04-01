import re

# Function to extract RTT values (Max, Min, Mean) from a given string
def extract_rtt_values(input_string):    
    pattern = r"Max rtt: (\d+\.\d+)ms \| Min rtt: (\d+\.\d+)ms \| Avg rtt: (\d+\.\d+)ms"
    
    # Search for the pattern in the input string
    match = re.search(pattern, input_string)
    
    if match:
        # Extract Max, Min, and Mean RTT values
        max_rtt = match.group(1)
        min_rtt = match.group(2)
        mean_rtt = match.group(3)
        return max_rtt, min_rtt, mean_rtt
    else:
        return None, None, None  # Return None if the pattern is not found

# Function to read log data, extract relevant info, and write to output file
def extract_nw_delay(nping_log, nping_data):
    with open(nping_log, 'r') as infile, open(nping_data, 'w') as outfile:        
        outfile.write("date time, Max, Min, Mean\n")
        
        for line in infile:
            if line.startswith('Date and Time:'):
                
                fields = line.split(' ') #space delimited values
                if len(fields) >= 5:
                    date_stamp = fields[3].strip()
                    time_stamp = fields[4].strip()                     
                    outfile.write(f"{date_stamp} {time_stamp}")
            
            elif "rtt:" in line:  # Check for lines containing "rtt"                
                max_rtt, min_rtt, mean_rtt = extract_rtt_values(line)
                if max_rtt and min_rtt and mean_rtt:                      
                    outfile.write(f", {max_rtt}, {min_rtt}, {mean_rtt}\n")
                else:
                    outfile.write(", None, None, None\n")  # If no RTT values are found, write None


extract_nw_delay('nping_log.txt', 'nping_data.txt')
