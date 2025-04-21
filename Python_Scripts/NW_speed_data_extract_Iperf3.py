import re
from datetime import datetime

def extract_iperf3_data(input_filename, output_filename):
    with open(input_filename, 'r') as file:
        lines = file.readlines()

    results = ["date time,DL_speed,UL_speed"]
    current_date_time = ""
    dl_speed = ""
    ul_speed = ""

    for line in lines:
        # Extract date and time
        date_time_match = re.search(r'\d{4}/\d{2}/\d{2},\d{2}:\d{2}:\d{2}', line)
        if date_time_match:
            dt_obj = datetime.strptime(date_time_match.group(), '%Y/%m/%d,%H:%M:%S')
            current_date_time = dt_obj.strftime('%m/%d/%y %H:%M:%S')

        # Extract DL speed (receiver)
        if 'receiver' in line:
            dl_match = re.search(r'(\d+ KBytes\s+|\d+\.\d+ Mbits/sec\s+)', line)
            if dl_match:
                dl_speed = line.split()[6]  # Bandwidth column (example: '1.13')

        # Extract UL speed (sender)
        if 'sender' in line:
            ul_match = re.search(r'(\d+ KBytes\s+|\d+\.\d+ Mbits/sec\s+)', line)
            if ul_match:
                ul_speed = line.split()[6]  # Bandwidth column (example: '1.64')

                # Append the result when both DL and UL speeds are found
                results.append(f"{current_date_time},{ul_speed},{dl_speed}")

    # Writing the results to the output file
    with open(output_filename, 'w') as file:
        file.write("\n".join(results) + '\n')

# File names
input_filename = 'iperf3_log.txt'
output_filename = 'iperf3_data.txt'

extract_iperf3_data(input_filename, output_filename)
