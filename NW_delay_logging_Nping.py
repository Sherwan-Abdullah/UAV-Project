import pexpect
import datetime


with open('nping_log.txt', 'w') as file:  # 'w' for new file
            file.write("")
# Define the command
command = 'sudo nping -p 62 --tcp 129.237.161.212 -c 1'

# Set your password
password = 'comms'

try:
    while True:
        # Run the command using pexpect
        child = pexpect.spawn(command)
        child.expect('[sudo]', timeout=30)  # General pattern to match the sudo prompt
        child.sendline(password)
        child.expect(pexpect.EOF)
        output = child.before.decode()

        # Get the current date and time
        current_time = datetime.datetime.now().strftime('%Y/%b/%d %H:%M:%S')

        # Save the result to a text file
        with open('nping_result.txt', 'a') as file:  # 'a' for append mode
            file.write(f"Date and Time: {current_time}\n")
            file.write(output)
            file.write("\n\n")  # Add some spacing between entries

        print(f"Nping result saved with timestamp: {current_time}")

except pexpect.TIMEOUT:
    print("The command timed out. Make sure the password prompt pattern is correct.")
except KeyboardInterrupt:
    print("\nScript stopped manually.")
except Exception as e:
    print(f"An error occurred: {e}")
