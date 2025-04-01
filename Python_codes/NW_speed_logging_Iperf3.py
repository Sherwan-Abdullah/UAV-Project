import subprocess
import time
from datetime import datetime

# open a new file for the results so the new test won't be added to old ones
with open("iperf3_log.txt", "w") as outfile:
    outfile.write("\n\n\n\n")

def run_iperf3(server_ip, port):
    # Iperf3 command to run on pMLTE side with mbps format
    cmd = ["iperf3", "-c", server_ip, "-f", "m", "-t", "1", "-R"]

    while True:
        # Get the current date and time
        now = datetime.now()
        date_time = now.strftime("%Y/%b/%d %H:%M:%S")

        # Run the iperf test
        with open("iperf3_log.txt", "a") as outfile:
            outfile.write(f"{date_time}\n")  # Add newline for clarity
            process = subprocess.Popen(cmd, stdout=outfile, stderr=subprocess.PIPE)

            # Get the error
            _, stderr = process.communicate()

            # If there is an error and you wanted to know what is that error uncomment below lines, print it and retry the command
            #if stderr:
                #print("Error:", stderr.decode())
                #print("Retrying the iperf3 command...")
                #continue  # Skip waiting and rerun the command immediately

            # If no error, the test ran successfully, so wait for the next one
            print("Iperf3 test completed successfully.")
            # If time delay needed uncomment below line and enter delay in seconds
            #time.sleep(0)  

# Replace with iperf3 server IP and port (which is in our case a PC in Nichols Hall)
run_iperf3("129.237.161.212", 5201)
