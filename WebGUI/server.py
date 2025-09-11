import subprocess
from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# Define the path to your Anaconda Python executable here!
# This should match the path you set in your run_flask.sh script
ANACONDA_PYTHON_EXECUTABLE = "/home/s338a494/anaconda3/bin/python3"

# A simple HTML template to serve. We'll load the actual index.html content here.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Python Script Runner</title>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background-color: #f4f4f4; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
        button { padding: 10px 20px; margin: 10px; font-size: 16px; cursor: pointer; background-color: #007bff; color: white; border: none; border-radius: 5px; transition: background-color 0.3s ease; }
        button:hover { background-color: #0056b3; }
        #loading { display: none; margin-top: 20px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #result { margin-top: 20px; padding: 15px; border: 1px solid #ddd; background-color: #e9e9e9; border-radius: 5px; text-align: left; white-space: pre-wrap; word-break: break-all; max-height: 300px; overflow-y: auto; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Run Python Scripts</h1>
        <button onclick="runScript('all_data_extract.py')">Extract data from logfile</button>
        <button onclick="runScript('all_stat_result.py')">Generate Statistics Charts</button>
        <button onclick="runScript('RAN_Map.py')">Generate 2D and 3D maps</button>
        <div id="loading"></div>
        <pre id="result">Results will appear here...</pre>
    </div>

    <script>
        async function runScript(scriptName) {
            const loadingDiv = document.getElementById('loading');
            const resultPre = document.getElementById('result');

            resultPre.textContent = 'Running ' + scriptName + '...';
            loadingDiv.style.display = 'block'; // Show loading animation

            try {
                const response = await fetch('/run_script', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ script: scriptName }),
                });

                const data = await response.json();
                if (data.success) {
                    resultPre.textContent = data.output;
                } else {
                    resultPre.textContent = 'Error: ' + data.error;
                }
            } catch (error) {
                resultPre.textContent = 'An error occurred: ' + error.message;
            } finally {
                loadingDiv.style.display = 'none'; // Hide loading animation
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run_script', methods=['POST'])
def run_script():
    script_name = request.json.get('script')
    if not script_name:
        return jsonify({'success': False, 'error': 'No script name provided.'})

    # UPDATED ALLOWED SCRIPTS LIST
    allowed_scripts = [
        'all_stat_result.py',
        'RAN_Map.py',
        'all_data_extract.py'  # Added the new script
    ]
    if script_name not in allowed_scripts:
        return jsonify({'success': False, 'error': 'Unauthorized script name.'})

    script_path = os.path.join(os.getcwd(), script_name)

    if not os.path.exists(script_path):
        return jsonify({'success': False, 'error': f'Script "{script_name}" not found.'})

    try:
        process = subprocess.run([ANACONDA_PYTHON_EXECUTABLE, script_path], capture_output=True, text=True, check=True)
        return jsonify({'success': True, 'output': process.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': f'Script execution failed:\n{e.stderr}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'An unexpected server error occurred: {str(e)}'})

if __name__ == '__main__':
    current_directory = os.getcwd()
    print(f"Server starting in: {current_directory}")
    print("Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
