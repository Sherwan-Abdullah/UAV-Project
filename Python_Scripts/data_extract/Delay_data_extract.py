import re
import csv

# Input and output filenames
input_file = "nping_log.txt"   # Ensure this is in the same directory
output_file = "nping_data.txt"

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
    dt = timestamp.replace("Date and Time: ", "")

    # Extract Max RTT (or N/A)
    rtt_match = re.search(r"Max rtt: ([\d.]+|N/A)", block)
    max_rtt = rtt_match.group(1) if rtt_match else "N/A"

    # Sent packets
    sent_match = re.search(r"Raw packets sent: (\d+)", block)
    sent = sent_match.group(1) if sent_match else "0"

    # Received packets
    rcvd_match = re.search(r"Rcvd: (\d+)", block)
    rcvd = rcvd_match.group(1) if rcvd_match else "0"

    summary.append((dt, max_rtt, sent, rcvd))

# Save as CSV-style .txt file
with open(output_file, "w", newline="") as f_out:
    writer = csv.writer(f_out)
    writer.writerow(["Date Time", "Max_RTT_ms", "Sent_Packets", "Received_Packets"])
    writer.writerows(summary)

print(f"✅ Summary saved to '{output_file}'")
