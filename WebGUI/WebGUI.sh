#!/bin/bash

# --- Debugging Information ---
echo "--- Script Start ---"
echo "Running user: $(whoami)"
echo "Current working directory before CD: $(pwd)"
echo "Script path (BASH_SOURCE[0]): ${BASH_SOURCE[0]}"

# Navigate to the directory where the script is located
# This ensures that server.py and your other scripts are found relative to the .sh file
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -z "$SCRIPT_DIR" ]; then
    echo "Error: Could not determine script directory."
    exit 1
fi

echo "Changing directory to: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

echo "Current working directory after CD: $(pwd)"

# Explicitly set the path to your Anaconda Python 3 executable
PYTHON_EXECUTABLE="/home/s338a494/anaconda3/bin/python3"

# Verify the specified Python executable exists
if [ ! -f "$PYTHON_EXECUTABLE" ]; then
    echo "Error: Anaconda Python executable not found at: $PYTHON_EXECUTABLE"
    echo "Please verify the path to your Anaconda Python installation."
    read -p "Press Enter to close this window..."
    exit 1
fi

echo "Using Python executable: $PYTHON_EXECUTABLE"
echo "Python version: "$($PYTHON_EXECUTABLE --version 2>&1) # Capture both stdout and stderr for version info

# Verify Flask is installed for the specified Python
echo "Checking for Flask installation..."
if ! "$PYTHON_EXECUTABLE" -c "import flask" &> /dev/null; then
    echo "Error: Flask is not installed for this Python environment ($PYTHON_EXECUTABLE)."
    echo "Please install it using: '$PYTHON_EXECUTABLE' -m pip install Flask"
    read -p "Press Enter to close this window..."
    exit 1
fi
echo "Flask is installed."

# Verify server.py exists in the current directory
if [ ! -f "server.py" ]; then
    echo "Error: server.py not found in the current directory ($(pwd))."
    read -p "Press Enter to close this window..."
    exit 1
fi
echo "server.py found."

echo ""
echo "--- Starting Flask Server ---"
echo "Press Ctrl+C in this window to stop the server."
echo ""

# The server needs a moment to start up before the browser tries to open it.
# We'll use a small delay.
SERVER_URL="http://127.0.0.1:5000"
echo "Attempting to open browser at: $SERVER_URL after a short delay..."

# Start the Flask server in the background and capture its PID
# Using `&` to run in background, `trap` to ensure it's killed on script exit
# `nohup` to prevent it from being killed if the terminal is closed (though `exec` below will prevent this)
# More robust approach for backgrounding the server:
# python -c "import subprocess, time; p = subprocess.Popen(['$PYTHON_EXECUTABLE', 'server.py']); time.sleep(1); print(p.pid)" &
# SERVER_PID=$!

# For a simple script like this, it's often better to just run the server
# and then open the browser concurrently in a new process, or in a new terminal.
# Let's try running the server and then opening the browser.
# The `exec` command will replace the current shell, so we need to open the browser *before* `exec`.

# Open browser in the background.
# Adding a sleep *before* opening the browser to give the server a moment to start.
( sleep 2 && xdg-open "$SERVER_URL" & ) &

# Now, execute the Python server script, replacing the current shell process
exec "$PYTHON_EXECUTABLE" server.py

# The following lines will only execute if the 'exec' command fails
echo "Server process terminated unexpectedly."
read -p "Press Enter to close this window..."
