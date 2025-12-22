import subprocess
from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import json
import shutil
import pandas as pd
import platform # Re-added for OS detection (needed for open folder functionality)

app = Flask(__name__)

# Global variable to store the working directory for log files
LOG_FILES_DIRECTORY = os.getcwd()
CONFIG_FILE = "config.json"

# Load saved configuration
def load_config():
    global LOG_FILES_DIRECTORY
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                LOG_FILES_DIRECTORY = config.get('log_directory', os.getcwd())
        except:
            pass

# Save configuration
def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'log_directory': LOG_FILES_DIRECTORY}, f)

# Initialize config on startup
load_config()

# Serve files from the current working directory
@app.route('/<path:filename>')
def serve_file(filename):
    """Serve any file from the working directory"""
    return send_from_directory(os.getcwd(), filename)

@app.route('/Statistical Results/<path:filename>')
def serve_stats(filename):
    """Serve files from Statistical Results folder"""
    stats_dir = os.path.join(LOG_FILES_DIRECTORY, 'Statistical Results')
    if os.path.exists(stats_dir):
        return send_from_directory(stats_dir, filename)
    return jsonify({'error': 'File not found'}), 404

@app.route('/spatiotemporal maps results/<path:filename>')
def serve_maps(filename):
    """Serve files from spatiotemporal maps results folder"""
    maps_dir = os.path.join(LOG_FILES_DIRECTORY, 'spatiotemporal maps results')
    if os.path.exists(maps_dir):
        return send_from_directory(maps_dir, filename)
    return jsonify({'error': 'File not found'}), 404

# Define the path to your Anaconda Python executable here!
ANACONDA_PYTHON_EXECUTABLE = "/home/s338a494/anaconda3/bin/python3"

# Enhanced HTML template with file browser
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Analysis Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .dashboard {
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .grid-container {
            /* The main grid has 5 columns for the first row */
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .row-1 {
            display: contents; /* Allows children to be placed directly in the main grid */
        }
        
        /* New chart rows will be 3 columns wide, spanning all 5 main grid columns */
        .chart-row {
            grid-column: 1 / span 5; /* Spans all 5 columns of the main grid */
            display: grid;
            grid-template-columns: repeat(3, 1fr); /* Internal 3-column grid for charts */
            gap: 20px;
            margin-bottom: 20px; /* Added spacing between chart rows */
        }
        
        .button-cell {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .button-cell h3 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        button {
            padding: 15px 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            background-color: #fff;
            color: #667eea;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            background-color: #f0f0f0;
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .map-cell, .chart-cell {
            border: 3px solid #667eea;
            border-radius: 10px;
            overflow: hidden;
            background: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            position: relative;
            height: 400px;
        }
        
        /* Charts now span one-third of the width of their 3-column container */
        .chart-row > .chart-cell {
            grid-column: span 1;
        }
        
        .map-cell .title, .chart-cell .title {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            font-weight: bold;
            text-align: center;
            font-size: 1.1em;
        }
        
        .map-cell iframe {
            width: 100%;
            height: calc(100% - 48px);
            border: none;
        }
        
        .chart-cell img {
            width: 100%;
            height: calc(100% - 48px);
            object-fit: contain;
            padding: 10px;
            background: white;
        }
        
        .placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            height: calc(100% - 48px);
            color: #999;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }
        
        #loading {
            display: none;
            margin: 20px auto;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status-bar {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
            color: #667eea;
        }
        
        /* Footer link styles */
        .results-footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 1.1em;
        }

        .results-footer a {
            color: #764ba2;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s;
        }

        .results-footer a:hover {
            color: #667eea;
            text-decoration: underline;
        }

        /* Modal styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .modal-header h2 {
            color: #667eea;
        }
        
        .close {
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.3s;
        }
        
        .close:hover {
            color: #667eea;
        }
        
        .path-display {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-family: monospace;
            word-break: break-all;
            border: 2px solid #667eea;
        }
        
        .file-list {
            list-style: none;
            max-height: 400px;
            overflow-y: auto;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 10px;
        }
        
        .file-item {
            padding: 12px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
        }
        
        .file-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .file-item.directory {
            background: #667eea;
            color: white;
            font-weight: bold;
        }
        
        .file-item.directory:hover {
            background: #5568d3;
        }
        
        .file-icon {
            margin-right: 10px;
            font-size: 1.2em;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .button-group button {
            flex: 1;
        }
        
        .current-directory-info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .info-item {
            display: flex;
            flex-direction: column;
        }
        
        .info-label {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .info-value {
            color: #333;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📡 Network Analysis Dashboard</h1>
        
        <div class="status-bar">
            <span id="status">Ready to process data</span>
        </div>
        
        <div class="current-directory-info">
            <div class="info-item">
                <span class="info-label">Current Log Files Directory:</span>
                <span class="info-value" id="currentLogDir">Loading...</span>
            </div>
            <div class="info-item">
                <span class="info-label">Test Date and Time:</span>
                <span class="info-value" id="testDateTime">Loading...</span>
            </div>
        </div>
        
        <div class="grid-container">
            <div class="row-1">
                <div class="button-cell">
                    <h3>Controls</h3>
                    <button onclick="openFileBrowser()">📁 Browse Log Files</button>
                    <button onclick="runScript('all_data_extract.py')">📊 Extract Data</button>
                    <button onclick="runScript('all_stat_result.py')">📈 Generate Stats</button>
                    <button onclick="runScript('RAN_Map.py')">🗺️ Generate Maps</button>
                    <button onclick="runMLScript()">🤖 Run ML Prediction</button>
                    <button onclick="refreshVisualization()">🔄 Refresh All</button>
                </div>
                
                <div class="map-cell" id="rsrp-3d-container">
                    <div class="title">RSRP - 3D Visualization</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Maps"</div>
                </div>
                
                <div class="map-cell" id="rsrp-map-container">
                    <div class="title">RSRP - 2D Map</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Maps"</div>
                </div>
                
                <div class="map-cell" id="rsrq-3d-container">
                    <div class="title">RSRQ - 3D Visualization</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Maps"</div>
                </div>
                
                <div class="map-cell" id="rsrq-map-container">
                    <div class="title">RSRQ - 2D Map</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Maps"</div>
                </div>
            </div>
            
            <div class="chart-row">
                <div class="chart-cell" id="cdf-rsrp-container">
                    <div class="title">CDF - RSRP</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Stats"</div>
                </div>
                
                <div class="chart-cell" id="cdf-rsrq-container">
                    <div class="title">CDF - RSRQ</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Stats"</div>
                </div>
                
                <div class="chart-cell" id="pdf-cellid-container">
                    <div class="title">PDF - Cell ID</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Stats"</div>
                </div>
            </div>

            <div class="chart-row">
                <div class="chart-cell" id="rsrp-altitude-container">
                    <div class="title">RSRP vs Altitude</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Stats"</div>
                </div>

                <div class="chart-cell" id="pdf-delay-container">
                    <div class="title">PDF - Delay</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Stats"</div>
                </div>
                
                <div class="chart-cell" id="cdf-speed-container">
                    <div class="title">CDF - Throughput</div>
                    <div class="placeholder">Click "Browse Log Files" first, then "Generate Stats"</div>
                </div>
            </div>
            

            <div class="chart-row" id="ml-results-row" style="display: none;">
                <div class="chart-cell" style="grid-column: span 3; height: auto; min-height: 300px; max-height: 600px;">
                    <div class="title">Machine Learning Prediction Results</div>
                    <pre id="ml-results-content" style="padding: 20px; font-family: monospace; overflow-y: auto; overflow-x: auto; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;"></pre>
                </div>
            </div>
        </div>
        
        <div id="loading"></div>

        <div class="results-footer">
            (More results <a href="#" onclick="openResultsFolder(event)">click here</a>)
        </div>
    </div>

    <div id="fileBrowserModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>📁 Select Log Files Directory</h2>
                <span class="close" onclick="closeFileBrowser()">&times;</span>
            </div>
            
            <div class="path-display">
                <strong>Current Path:</strong> <span id="currentPath">/</span>
            </div>
            
            <ul class="file-list" id="fileList">
                <li>Loading...</li>
            </ul>
            
            <div class="button-group">
                <button onclick="selectCurrentDirectory()">✓ Select This Directory</button>
                <button onclick="closeFileBrowser()">✗ Cancel</button>
            </div>
        </div>
    </div>

    <script>
        let currentBrowsePath = '/';
        
        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }
        
        function updateCurrentLogDir() {
            fetch('/get_log_directory')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('currentLogDir').textContent = data.directory;
                    document.getElementById('testDateTime').textContent = data.test_datetime;
                })
                .catch(err => {
                    document.getElementById('currentLogDir').textContent = 'Error loading directory';
                    document.getElementById('testDateTime').textContent = 'N/A';
                });
        }
        
        // Re-added: Function to open the main log directory via a server command
        function openResultsFolder(event) {
            event.preventDefault(); 
            
            updateStatus('Attempting to open log directory on server...');
            
            fetch('/open_stats_folder') // This endpoint now opens the main log directory
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateStatus('✅ Log directory opened successfully (check file explorer on the server)');
                    } else {
                        updateStatus('⚠️ Could not automatically open folder. Path copied to clipboard.');
                        // Fallback: copy path and notify user
                        const path = data.path;
                        if (navigator.clipboard) {
                            navigator.clipboard.writeText(path).then(() => {
                                alert(`Automatic folder opening failed. The path to the Log Files Directory has been copied to your clipboard:\n\n${path}\n\nPlease paste this into your file explorer.`);
                            }).catch(err => {
                                alert(`Automatic folder opening failed. Path:\n\n${path}`);
                            });
                        } else {
                             alert(`Automatic folder opening failed. Path:\n\n${path}`);
                        }
                    }
                })
                .catch(err => {
                    console.error('Error opening results folder:', err);
                    updateStatus('❌ Connection error while trying to open folder.');
                });
        }

        function openFileBrowser() {
            document.getElementById('fileBrowserModal').style.display = 'block';
            fetch('/get_log_directory')
                .then(response => response.json())
                .then(data => {
                    currentBrowsePath = data.directory;
                    loadDirectory(currentBrowsePath);
                });
        }
        
        function closeFileBrowser() {
            document.getElementById('fileBrowserModal').style.display = 'none';
        }
        
        function loadDirectory(path) {
            currentBrowsePath = path;
            document.getElementById('currentPath').textContent = path;
            
            fetch('/browse_directory', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ path: path }),
            })
            .then(response => response.json())
            .then(data => {
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '';
                
                // Add parent directory option if not at root
                if (data.parent) {
                    const li = document.createElement('li');
                    li.className = 'file-item directory';
                    li.innerHTML = '<span class="file-icon">⬆️</span> .. (Parent Directory)';
                    li.onclick = () => loadDirectory(data.parent);
                    fileList.appendChild(li);
                }
                
                // Add directories
                data.directories.forEach(dir => {
                    const li = document.createElement('li');
                    li.className = 'file-item directory';
                    li.innerHTML = `<span class="file-icon">📁</span> ${dir}`;
                    li.onclick = () => loadDirectory(data.path + '/' + dir);
                    fileList.appendChild(li);
                });
                
                // Show files (read-only, for information)
                data.files.forEach(file => {
                    const li = document.createElement('li');
                    li.className = 'file-item';
                    li.innerHTML = `<span class="file-icon">📄</span> ${file}`;
                    fileList.appendChild(li);
                });
                
                if (data.directories.length === 0 && data.files.length === 0) {
                    const li = document.createElement('li');
                    li.className = 'file-item';
                    li.textContent = 'Empty directory';
                    li.style.textAlign = 'center';
                    li.style.color = '#999';
                    fileList.appendChild(li);
                }
            })
            .catch(err => {
                console.error('Error loading directory:', err);
                updateStatus('Error loading directory');
            });
        }
        
        function selectCurrentDirectory() {
            fetch('/set_log_directory', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ path: currentBrowsePath }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus('✅ Log directory set successfully');
                    updateCurrentLogDir();
                    closeFileBrowser();
                } else {
                    updateStatus('❌ Error setting directory');
                }
            })
            .catch(err => {
                updateStatus('❌ Connection error');
            });
        }
        
        function loadMaps() {
            const maps = [
                { container: 'rsrp-3d-container', path: '/spatiotemporal maps results/output/rsrp_3d.html' },
                { container: 'rsrp-map-container', path: '/spatiotemporal maps results/output/rsrp_map.html' },
                { container: 'rsrq-3d-container', path: '/spatiotemporal maps results/output/rsrq_3d.html' },
                { container: 'rsrq-map-container', path: '/spatiotemporal maps results/output/rsrq_map.html' }
            ];
            
            maps.forEach(map => {
                const container = document.getElementById(map.container);
                const title = container.querySelector('.title').textContent;
                container.innerHTML = `
                    <div class="title">${title}</div>
                    <iframe src="${map.path}?t=${new Date().getTime()}"></iframe>
                `;
            });
        }
        
        function loadCharts() {
            const charts = [
                { container: 'cdf-rsrp-container', name: 'CDF_RSRP' },
                { container: 'cdf-rsrq-container', name: 'CDF_RSRQ' }, 
                { container: 'pdf-cellid-container', name: 'PDF_CellID' },
                { container: 'rsrp-altitude-container', name: 'RSRP_vs_Altitude' }, 
                { container: 'pdf-delay-container', name: 'pdf_of_delay' },
                { container: 'cdf-speed-container', name: 'speed_cdf' }
            ];
            
            charts.forEach(chart => {
                fetch(`/get_latest_chart?name=${encodeURIComponent(chart.name)}`)
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById(chart.container);
                        const title = container.querySelector('.title').textContent;
                        
                        if (data.exists) {
                            container.innerHTML = `
                                <div class="title">${title}</div>
                                <img src="${data.path}?t=${new Date().getTime()}" alt="${title}" 
                                     onerror="this.parentElement.innerHTML='<div class=title>${title}</div><div class=placeholder>Chart not found</div>'">
                            `;
                        } else {
                            container.innerHTML = `
                                <div class="title">${title}</div>
                                <div class="placeholder">Chart not available. Click "Generate Stats" to create it.</div>
                            `;
                        }
                    })
                    .catch(err => {
                        console.log('Error loading chart: ' + chart.name, err);
                        const container = document.getElementById(chart.container);
                        const title = container.querySelector('.title').textContent;
                        container.innerHTML = `
                            <div class="title">${title}</div>
                            <div class="placeholder">Error loading chart</div>
                        `;
                    });
            });
        }
        
        function refreshVisualization() {
            updateStatus('Refreshing visualizations...');
            loadMaps();
            loadCharts();
            setTimeout(() => updateStatus('Visualizations refreshed'), 1000);
        }
        
        async function runScript(scriptName) {
            const loadingDiv = document.getElementById('loading');

            updateStatus(`Running ${scriptName}...`);
            loadingDiv.style.display = 'block';

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
                    updateStatus(`✅ ${scriptName} completed successfully`);
                    
                    // NEW LOGIC: Update date/time if data extraction succeeded
                    if (scriptName === 'all_data_extract.py') {
                        updateCurrentLogDir(); 
                    }

                    // Auto-refresh visualizations after successful execution
                    setTimeout(() => {
                        if (scriptName === 'RAN_Map.py') {
                            loadMaps();
                        } else if (scriptName === 'all_stat_result.py') {
                            loadCharts();
                        }
                    }, 500);
                } else {
                    updateStatus(`❌ Error: ${data.error}`);
                    alert(`Error running ${scriptName}:\n${data.error}`);
                }
            } catch (error) {
                updateStatus('❌ Connection error');
                alert('Connection error: ' + error);
            } finally {
                loadingDiv.style.display = 'none';
            }
        }
        
        // Load on page load
        window.onload = function() {
            updateCurrentLogDir();
            loadMaps();
            loadCharts();
            loadMLResults();//
        };
        
        // Close modal on outside click
        window.onclick = function(event) {
            const modal = document.getElementById('fileBrowserModal');
            if (event.target == modal) {
                closeFileBrowser();
            }
        }
        
        async function runMLScript() {
            const loadingDiv = document.getElementById('loading');
            updateStatus("Running ML Predictions (this may take a while)...");
            loadingDiv.style.display = 'block';

            try {
                const response = await fetch('/run_script', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ script: 'ML_predict_all.py' }),
                });

                const data = await response.json();
                if (data.success) {
                    updateStatus("✅ ML Prediction Complete");
                    loadMLResults(); 
                } else {
                    updateStatus(`❌ Error: ${data.error}`);
                }
            } catch (error) {
                updateStatus('❌ Connection error');
            } finally {
                loadingDiv.style.display = 'none';
            }
        }

        function loadMLResults() {
            fetch('/get_ml_results')
                .then(response => response.json())
                .then(data => {
                    if (data.exists) {
                        document.getElementById('ml-results-row').style.display = 'grid';
                        document.getElementById('ml-results-content').textContent = data.content;
                    }
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_log_directory', methods=['GET'])
def get_log_directory():
    """Get the current log files directory and test timestamp"""
    test_datetime = get_test_datetime()
    return jsonify({
        'directory': LOG_FILES_DIRECTORY,
        'test_datetime': test_datetime
    })

def get_test_datetime():
    """Extract test date and time from lte_data.txt first row"""
    try:
        lte_file = os.path.join(LOG_FILES_DIRECTORY, 'lte_data.txt')
        if os.path.exists(lte_file):
            # Using pandas to read the first row efficiently
            # We assume lte_data.txt is CSV-like and has Date/Time columns.
            df = pd.read_csv(lte_file, nrows=1)
            if len(df) > 0 and 'Date' in df.columns and 'Time' in df.columns:
                date_str = str(df['Date'].iloc[0])
                time_str = str(df['Time'].iloc[0])
                # Format: 2025/Sep/04 22:47:45
                return f"{date_str} {time_str}"
    except Exception as e:
        print(f"Error reading test datetime: {e}")
    return "N/A"

@app.route('/get_stats_folder_path', methods=['GET'])
def get_stats_folder_path():
    """Get the absolute path to the main log directory."""
    log_path = os.path.abspath(LOG_FILES_DIRECTORY)
    return jsonify({'path': log_path})

@app.route('/open_stats_folder', methods=['GET'])
def open_stats_folder():
    """Attempt to open the main Log Files Directory using OS commands."""
    target_path = os.path.abspath(LOG_FILES_DIRECTORY)
    
    if not os.path.isdir(target_path):
        return jsonify({'success': False, 'error': 'Log directory not found', 'path': target_path})

    # Determine OS and set the correct command
    system_os = platform.system()
    if system_os == "Windows":
        command = ['start', target_path]
        shell_needed = True # 'start' is a shell built-in command
    elif system_os == "Darwin": # macOS
        command = ['open', target_path]
        shell_needed = False
    elif system_os == "Linux":
        # xdg-open is the standard freedesktop.org way to open files/folders
        command = ['xdg-open', target_path]
        shell_needed = False
    else:
        return jsonify({'success': False, 'error': f'Unsupported OS: {system_os}', 'path': target_path})
    
    try:
        # We don't want to wait for the process, so run in the background
        subprocess.Popen(command, shell=shell_needed, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return jsonify({'success': True})
    except FileNotFoundError:
        # This occurs if the command (e.g., 'open', 'xdg-open') is not found
        return jsonify({'success': False, 'error': 'OS command not found to open folder.', 'path': target_path})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Execution failed: {e}', 'path': target_path})


@app.route('/set_log_directory', methods=['POST'])
def set_log_directory():
    """Set the log files directory"""
    global LOG_FILES_DIRECTORY
    data = request.json
    path = data.get('path')
    
    if not path or not os.path.isdir(path):
        return jsonify({'success': False, 'error': 'Invalid directory path'})
    
    LOG_FILES_DIRECTORY = os.path.abspath(path)
    save_config()
    return jsonify({'success': True, 'directory': LOG_FILES_DIRECTORY})

@app.route('/browse_directory', methods=['POST'])
def browse_directory():
    """Browse a directory and return its contents"""
    data = request.json
    path = data.get('path', '/')
    
    try:
        # Normalize and validate path
        path = os.path.abspath(path)
        
        if not os.path.isdir(path):
            return jsonify({'error': 'Invalid directory'}), 400
        
        # Get directories and files
        items = os.listdir(path)
        directories = []
        files = []
        
        for item in items:
            item_path = os.path.join(path, item)
            try:
                if os.path.isdir(item_path):
                    directories.append(item)
                elif os.path.isfile(item_path):
                    files.append(item)
            except PermissionError:
                continue
        
        # Sort items
        directories.sort(key=str.lower)
        files.sort(key=str.lower)
        
        # Get parent directory
        parent = os.path.dirname(path) if path != '/' else None
        
        return jsonify({
            'path': path,
            'parent': parent,
            'directories': directories,
            'files': files
        })
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/run_script', methods=['POST'])
def run_script():
    """Run a processing script in the log files directory"""
    script_name = request.json.get('script')
    if not script_name:
        return jsonify({'success': False, 'error': 'No script name provided.'})

    allowed_scripts = [
        'all_stat_result.py',
        'RAN_Map.py',
        'all_data_extract.py',
        'ML_predict_all.py'
    ]
    if script_name not in allowed_scripts:
        return jsonify({'success': False, 'error': 'Unauthorized script name.'})

    # Get the script from the server's directory
    server_script_path = os.path.join(os.getcwd(), script_name)
    
    if not os.path.exists(server_script_path):
        return jsonify({'success': False, 'error': f'Script "{script_name}" not found in server directory.'})

    try:
        # Copy the script to the log files directory temporarily
        temp_script_path = os.path.join(LOG_FILES_DIRECTORY, f'temp_{script_name}')
        shutil.copy2(server_script_path, temp_script_path)
        
        # Run the script in the log files directory
        process = subprocess.run(
            [ANACONDA_PYTHON_EXECUTABLE, temp_script_path],
            cwd=LOG_FILES_DIRECTORY,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Clean up temporary script
        try:
            os.remove(temp_script_path)
        except:
            pass
        
        return jsonify({'success': True, 'output': process.stdout})
    except subprocess.CalledProcessError as e:
        # Clean up temporary script on error
        try:
            temp_script_path = os.path.join(LOG_FILES_DIRECTORY, f'temp_{script_name}')
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)
        except:
            pass
        return jsonify({'success': False, 'error': f'Script execution failed:\n{e.stderr}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'An unexpected server error occurred: {str(e)}'})

@app.route('/get_latest_chart', methods=['GET'])
def get_latest_chart():
    """Get the latest chart file matching a pattern"""
    chart_name = request.args.get('name')
    if not chart_name:
        return jsonify({'exists': False, 'path': ''})
    
    stats_dir = os.path.join(LOG_FILES_DIRECTORY, 'Statistical Results')
    if not os.path.exists(stats_dir):
        return jsonify({'exists': False, 'path': ''})
    
    try:
        # List all files in the directory
        files = os.listdir(stats_dir)
        
        # Filter files that match the pattern (e.g., "CDF_RSRP" in filename)
        # Note: Added 'CDF_RSRQ' and 'RSRP_vs_Altitude' to the chart list in HTML
        matching_files = [f for f in files if chart_name in f and f.endswith('.png')]
        
        if not matching_files:
            return jsonify({'exists': False, 'path': ''})
        
        # Sort by modification time (newest first)
        matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(stats_dir, x)), reverse=True)
        
        # Return the most recent file
        latest_file = matching_files[0]
        return jsonify({'exists': True, 'path': f'/Statistical Results/{latest_file}'})
    
    except Exception as e:
        print(f"Error getting latest chart: {e}")
        return jsonify({'exists': False, 'path': ''})

@app.route('/check_file', methods=['GET'])
def check_file():
    """Check if a file exists in the log files directory"""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'exists': False})
    
    full_path = os.path.join(LOG_FILES_DIRECTORY, file_path)
    return jsonify({'exists': os.path.exists(full_path)})
@app.route('/get_ml_results', methods=['GET'])
def get_ml_results():
    """Read the ML prediction results file"""
    try:
        ml_file = os.path.join(LOG_FILES_DIRECTORY, 'ML_prediction.txt')
        
        if not os.path.exists(ml_file):
            return jsonify({'exists': False})
        
        with open(ml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return jsonify({'exists': True, 'content': content})
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)})

if __name__ == '__main__':
    current_directory = os.getcwd()
    print(f"Server starting in: {current_directory}")
    print(f"Current log files directory: {LOG_FILES_DIRECTORY}")
    print("Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
