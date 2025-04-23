import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Step 1: Read the file and extract values
cellid_values = []
lac_values = []
rsrp_values = []
rsrq_values = []
rssi_values = []
sinr_values = []
data = []

altitude_values = []
alt_rsrp_values = []
alt_rsrq_values = []
alt_rssi_values = []
alt_sinr_values = []

try:
    with open('lte_data.txt', 'r') as file:
        for line in file:
            values = line.strip().split(',')
            if len(values) >= 16:
                try:
                    altitude = float(values[0])
                    cellid = float(values[8])
                    lac = float(values[9])
                    rsrp = float(values[10])
                    rsrq = float(values[11])
                    rssi = float(values[12])
                    sinr = float(values[13])
                    cellid_values.append(cellid)
                    lac_values.append(lac)
                    rsrp_values.append(rsrp)
                    rsrq_values.append(rsrq)
                    rssi_values.append(rssi)
                    sinr_values.append(sinr)
                    data.append((cellid, rsrp, rsrq, rssi, sinr))
                    altitude_values.append(altitude)
                    alt_rsrp_values.append((altitude, rsrp))
                    alt_rsrq_values.append((altitude, rsrq))
                    alt_rssi_values.append((altitude, rssi))
                    alt_sinr_values.append((altitude, sinr))
                except ValueError:
                    continue
except FileNotFoundError:
    print("Error: The file 'lte_data.txt' was not found.")

# Step 2: Function to calculate the CDF
def calculate_cdf(values):
    sorted_values = np.sort(values)
    cdf = np.arange(1, len(sorted_values) + 1) / len(sorted_values)
    return sorted_values, cdf

# Step 3: Function to plot and save the CDF for each metric
def plot_cdf(sorted_values, cdf, xlabel, title, filename, color):
    plt.figure(figsize=(10, 6))
    plt.step(sorted_values, cdf, where='mid', color=color, alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel('CDF')
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(filename, dpi=300)
    plt.close()

# Generate CDF plots
plot_cdf(*calculate_cdf(rsrp_values), 'RSRP (dBm)', 'CDF of RSRP', 'CDF_RSRP.png', 'blue')
plot_cdf(*calculate_cdf(rsrq_values), 'RSRQ (dB)', 'CDF of RSRQ', 'CDF_RSRQ.png', 'green')
plot_cdf(*calculate_cdf(rssi_values), 'RSSI (dB)', 'CDF of RSSI', 'CDF_RSSI.png', 'black')
plot_cdf(*calculate_cdf(sinr_values), 'SINR (dB)', 'CDF of SINR', 'CDF_SINR.png', 'red')

# Step 4: Function to plot normalized histogram (PDF)
def plot_pdf(values, xlabel, title, filename, color):
    unique_values, counts = np.unique(values, return_counts=True)
    normalized_counts = counts / np.sum(counts)
    rec_wide = 1

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(unique_values)), normalized_counts, color=color, alpha=0.7, edgecolor='black', width=rec_wide)
    plt.xlabel(xlabel)
    plt.ylabel('PDF')
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.xticks(range(len(unique_values)), 
               [f'{x:.2f}' if xlabel not in ['Cell ID', 'LAC'] else int(x) for x in unique_values], 
               rotation=90)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

# Generate PDF plots
plot_pdf(cellid_values, 'Cell ID', 'PDF of Cell IDs', 'PDF_CellID.png', 'orange')
plot_pdf(lac_values, 'LAC', 'PDF of LACs', 'PDF_LAC.png', 'brown')

# Step 5: Min/Mean/Max for each metric
def plot_min_mean_max(data, metric, xlabel, ylabel, title, filename):
    df = pd.DataFrame(data, columns=['CellID', 'RSRP', 'RSRQ', 'RSSI', 'SINR'])
    stats_df = df.groupby('CellID')[metric].agg(['mean', 'min', 'max']).reset_index()

    image_width = 10
    bar_width = 0.3

    r1 = np.arange(len(stats_df))
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]

    plt.figure(figsize=(image_width, 6))
    plt.bar(r1, stats_df['min'], color='blue', width=bar_width, edgecolor='grey', label='Min')
    plt.bar(r2, stats_df['mean'], color='green', width=bar_width, edgecolor='grey', label='Mean')
    plt.bar(r3, stats_df['max'], color='red', width=bar_width, edgecolor='grey', label='Max')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.xticks([r + bar_width for r in range(len(stats_df))], 
               [f'{x:.2f}' for x in stats_df['CellID']], rotation=90)

    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), fancybox=True, shadow=False, ncol=3)

    plt.subplots_adjust(bottom=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

# Generate Min/Mean/Max plots
plot_min_mean_max(data, 'RSRP', 'Cell ID', 'RSRP (dBm)', 'Statistics of RSRP', 'stats_RSRP.png')
plot_min_mean_max(data, 'RSRQ', 'Cell ID', 'RSRQ (dB)', 'Statistics of RSRQ', 'stats_RSRQ.png')
plot_min_mean_max(data, 'RSSI', 'Cell ID', 'RSSI (dB)', 'Statistics of RSSI', 'stats_RSSI.png')
plot_min_mean_max(data, 'SINR', 'Cell ID', 'SINR (dB)', 'Statistics of SINR', 'stats_SINR.png')

# Step 6: Function to plot metrics per altitude
def plot_metric_per_altitude(alt_metric_values, metric_name, ylabel, filename, bar_color):
    df = pd.DataFrame(alt_metric_values, columns=['Altitude', metric_name])
    grouped = df.groupby('Altitude')[metric_name].agg(['mean', 'std']).reset_index()

    plt.figure(figsize=(12, 6))
    plt.bar(grouped['Altitude'], grouped['mean'], color=bar_color, width=8, edgecolor='black', label=f'Mean {metric_name}')
    plt.errorbar(x=grouped['Altitude'], y=grouped['mean'], 
                 yerr=grouped['std'], fmt='none', 
                 ecolor='black', capsize=5, label='± Std Dev')

    plt.xlabel('Altitude over sea level (m)')
    plt.ylabel(ylabel)
    plt.title(f'Mean {metric_name} with Standard Deviation per Altitude')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

# Step 7: Plot RSRP/RSRQ/RSSI/SINR per Altitude
plot_metric_per_altitude(alt_rsrp_values, 'RSRP', 'RSRP (dBm)', 'RSRP_vs_Altitude.png', 'skyblue')
plot_metric_per_altitude(alt_rsrq_values, 'RSRQ', 'RSRQ (dB)', 'RSRQ_vs_Altitude.png', 'lightgreen')
plot_metric_per_altitude(alt_rssi_values, 'RSSI', 'RSSI (dB)', 'RSSI_vs_Altitude.png', 'lightcoral')
plot_metric_per_altitude(alt_sinr_values, 'SINR', 'SINR (dB)', 'SINR_vs_Altitude.png', 'gold')

# Step 8: Count samples per altitude and plot bar chart
def plot_altitude_count(altitude_values, xlabel, ylabel, title, filename):
    # Calculate count of samples for each unique altitude
    unique_altitudes, counts = np.unique(altitude_values, return_counts=True)
    
    # Create bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(unique_altitudes, counts, color='purple', width=8, alpha=0.7, edgecolor='black')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

# Generate the altitude count bar chart
plot_altitude_count(altitude_values, 'Altitude over sea level(m)', 'Sample Count', 'Sample Count per Altitude', 'Altitude_Count.png')
