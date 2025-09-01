import re
import csv

input_file = "iperf3_log.txt"
output_file = "iperf_data.txt"

# Read the file
with open(input_file, "r") as f:
    content = f.read()

# Split the log into blocks for each test based on "Date and Time:"
entries = re.split(r"(Date and Time: \d{4}/\w{3}/\d{2} \d{2}:\d{2}:\d{2})", content)
entries = [e.strip() for e in entries if e.strip()]

# Group into (timestamp, block)
grouped = [(entries[i], entries[i+1]) for i in range(0, len(entries) - 1, 2)]

results = []
for timestamp, block in grouped:
    tx_speed = "0"
    rx_speed = "0"

    # If "Errors:" appears at the top without throughput: keep 0s
    if "Errors:" in block and not re.search(r"\[TX-C\].*Mbits/sec.*\[RX-C\].*Mbits/sec", block, re.DOTALL):
        pass  # leave as 0
    else:
        # Extract only the first TX-C and RX-C throughput lines
        tx_match = re.search(r"\[\s*\d+\]\[TX-C\].*?([\d.]+)\sMbits/sec", block)
        rx_match = re.search(r"\[\s*\d+\]\[RX-C\].*?([\d.]+)\sMbits/sec", block)

        if tx_match:
            tx_speed = tx_match.group(1)
        if rx_match:
            rx_speed = rx_match.group(1)

    results.append((timestamp, tx_speed, rx_speed))

# Write to output file
with open(output_file, "w", newline="") as f_out:
    writer = csv.writer(f_out)
    writer.writerow(["Date Time", "UL_speed", "DL_speed"])
    writer.writerows(results)

print(f"✅ Done! Output saved to '{output_file}'")
