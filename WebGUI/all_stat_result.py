import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

# directory name where the results saved and its location inside the script folder
OUTPUT_DIR = "Statistical Results"

# Global variable to store timestamp
TIMESTAMP_SUFFIX = ""

def extract_timestamp_from_file(filename, date_col='Date', time_col='Time'):
    """Extract timestamp from the first data row of a CSV file"""
    try:
        df = pd.read_csv(filename)
        if len(df) > 0 and date_col in df.columns and time_col in df.columns:
            date_str = str(df[date_col].iloc[0])
            time_str = str(df[time_col].iloc[0])
            
            # Parse the date and time (format: 2025/Sep/04 22:47:45)
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y/%b/%d %H:%M:%S")
            # Return formatted as yymmdd_hhmm
            return dt.strftime("%y%m%d_%H%M")
    except Exception as e:
        print(f"Warning: Could not extract timestamp from {filename}: {e}")
    return None

def initialize_timestamp():
    """Initialize timestamp from available data files"""
    global TIMESTAMP_SUFFIX
    
    # Try to get timestamp from each file in order of preference
    for filename in ['lte_data.txt', 'iperf3_data.txt', 'nping_data.txt']:
        if os.path.exists(filename):
            timestamp = extract_timestamp_from_file(filename)
            if timestamp:
                TIMESTAMP_SUFFIX = f"_{timestamp}"
                print(f"Using timestamp from {filename}: {timestamp}")
                return
    
    # If no timestamp found, use current time
    TIMESTAMP_SUFFIX = f"_{datetime.now().strftime('%y%m%d_%H%M')}"
    print(f"Warning: Could not extract timestamp from data files. Using current time.")

def create_output_directory():
    """Create the output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")
    else:
        print(f"Output directory already exists: {OUTPUT_DIR}")

def get_output_path(filename):
    """Get the full path for output files with timestamp in the Statistical Results directory"""
    # Split filename into name and extension
    name, ext = os.path.splitext(filename)
    # Add timestamp before extension
    timestamped_filename = f"{name}{TIMESTAMP_SUFFIX}{ext}"
    return os.path.join(OUTPUT_DIR, timestamped_filename)

def analyze_delay_statistics():
    """Analyze and plot delay statistics from nping_data.txt"""
    print("Processing delay statistics...")
    
    # Check if file exists
    if not os.path.exists('nping_data.txt'):
        print("Warning: nping_data.txt not found. Skipping delay statistics.")
        return
    
    # how long to bin the dealy time in msec
    bin_width = 1

    # delay log file
    df = pd.read_csv('nping_data.txt', sep=',')

    # Convert 'Max' column to number, handling potential errors
    df['Max_RTT_ms'] = pd.to_numeric(df['Max_RTT_ms'], errors='coerce')

    # Delete rows with NaN values
    df.dropna(subset=['Max_RTT_ms'], inplace=True)

    # Set the graph starts from 0
    min_max = 0
    max_max = np.ceil(df['Max_RTT_ms'].max())

    # Create bins
    bins = np.arange(min_max, max_max + bin_width, bin_width)

    # Calculate the frequency distribution of 'Max' values into bins
    hist, bin_edges = np.histogram(df['Max_RTT_ms'], bins=bins)

    # Calculate the PDF (normalize frequencies by the total number of values)
    pdf = hist / len(df['Max_RTT_ms'])

    # Create a DataFrame for plotting
    pdf_df = pd.DataFrame({'Bin_Start': bin_edges[:-1], 'PDF': pdf})

    # Calculate the center of each bin
    pdf_df['Bin_Center'] = pdf_df['Bin_Start'] + (bin_width / 2)

    # Plotting the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(pdf_df['Bin_Center'], pdf_df['PDF'], width=bin_width, align='center', edgecolor='black')
    plt.xlabel('Latency (ms)', fontsize=18)
    plt.ylabel('Probability Density Function', fontsize=18)
    plt.title(f'PDF of RTT Delay', fontsize=20)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # Set x-axis limits to start from 0 and extend slightly beyond the max value
    plt.xlim(left=0, right=max_max + bin_width / 2)

    # Save the plot to a file
    output_file = get_output_path(f'pdf_of_delay.png')
    plt.savefig(output_file)
    plt.close()
    print(f"Delay statistics plot saved as: {output_file}")

def analyze_ran_statistics():
    """Analyze and plot RAN statistics from lte_data.txt"""
    print("Processing RAN statistics...")
    
    # Check if file exists
    if not os.path.exists('lte_data.txt'):
        print("Warning: lte_data.txt not found. Skipping RAN statistics.")
        return

    # Initialize lists for data storage
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
    nb_data = []

    # Read and parse data
    try:
        with open('lte_data.txt', 'r') as file:
            lines_read = 0
            lines_filtered = 0
            
            for line in file:
                lines_read += 1
                values = line.strip().split(',')
                if len(values) >= 29:
                    try:
                        altitude = float(values[0])
                        cellid = float(values[9])
                        lac = float(values[10])
                        rsrp = float(values[11])
                        rsrq = float(values[12])
                        rssi = float(values[13])
                        sinr = float(values[14])
                        
                        # FILTER: Drop lines where RSRP > -50 or RSRQ > -3
                        if rsrp > -50 or rsrq > -3:
                            lines_filtered += 1
                            continue
                        
                        # Extracting NB RSRP, RSRQ, and RSSI from their respective columns
                        nb1_rsrp = float(values[18])
                        nb2_rsrp = float(values[23])
                        nb3_rsrp = float(values[28])
                        nb1_rsrq = float(values[17])
                        nb2_rsrq = float(values[22])
                        nb3_rsrq = float(values[27])
                        nb1_rssi = float(values[19])
                        nb2_rssi = float(values[24])
                        nb3_rssi = float(values[29])
                        
                        # Append values to the lists
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
                        
                        # Append NB RSRP, RSRQ, and RSSI values to nb_data
                        nb_data.append({
                            'CellID': cellid,
                            'NB1_RSRP': nb1_rsrp, 'NB2_RSRP': nb2_rsrp, 'NB3_RSRP': nb3_rsrp,
                            'NB1_RSRQ': nb1_rsrq, 'NB2_RSRQ': nb2_rsrq, 'NB3_RSRQ': nb3_rsrq,
                            'NB1_RSSI': nb1_rssi, 'NB2_RSSI': nb2_rssi, 'NB3_RSSI': nb3_rssi,
                        })
                    except ValueError:
                        continue
            
            print(f"Data filtering complete:")
            print(f"  - Total lines read: {lines_read}")
            print(f"  - Lines filtered out (RSRP > -50 or RSRQ > -3): {lines_filtered}")
            print(f"  - Valid lines remaining: {len(rsrp_values)}")
            
    except FileNotFoundError:
        print("Error: The file 'lte_data.txt' was not found.")
        return

    # Helper functions for RAN analysis
    def calculate_cdf(values):
        sorted_values = np.sort(values)
        cdf = np.arange(1, len(sorted_values) + 1) / len(sorted_values)
        return sorted_values, cdf

    def plot_cdf(sorted_values, cdf, xlabel, title, filename, color):
        plt.figure(figsize=(10, 6))
        plt.step(sorted_values, cdf, where='mid', color=color, alpha=0.7)
        plt.xlabel(xlabel, fontsize=18)
        plt.ylabel('CDF', fontsize=18)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.title(title, fontsize=20)
        plt.grid(True, linestyle='--', alpha=0.7)
        output_file = get_output_path(filename)
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"RAN CDF plot saved as: {output_file}")

    def plot_pdf(values, xlabel, title, filename, color):
        unique_values, counts = np.unique(values, return_counts=True)
        normalized_counts = counts / np.sum(counts)
        rec_wide = 1

        plt.figure(figsize=(10, 6))
        plt.bar(range(len(unique_values)), normalized_counts, color=color, alpha=0.7, edgecolor='black', width=rec_wide)
        plt.xlabel(xlabel, fontsize=18)
        plt.ylabel('PDF', fontsize=18)
        plt.title(title, fontsize=20)
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.xticks(range(len(unique_values)), 
                   [f'{x:.2f}' if xlabel not in ['CellID', 'LAC'] else int(x) for x in unique_values], 
                   rotation=90)
                   
        plt.yticks(fontsize=18)
        plt.xticks(fontsize=18)
        
        plt.tight_layout()
        output_file = get_output_path(filename)
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"RAN PDF plot saved as: {output_file}")

    def plot_min_mean_max(data, metric, xlabel, ylabel, title, filename):
        df = pd.DataFrame(data, columns=['CellID', 'RSRP', 'RSRQ', 'RSSI', 'SINR'])
        stats_df = df.groupby('CellID')[metric].agg(['mean', 'min', 'max']).reset_index()

        
        bar_width = 0.3

        r1 = np.arange(len(stats_df))
        r2 = [x + bar_width for x in r1]
        r3 = [x + bar_width for x in r2]

        plt.figure(figsize=(10, 6))
        plt.bar(r1, stats_df['min'], color='blue', width=bar_width, edgecolor='grey', label='Min')
        plt.bar(r2, stats_df['mean'], color='green', width=bar_width, edgecolor='grey', label='Mean')
        plt.bar(r3, stats_df['max'], color='red', width=bar_width, edgecolor='grey', label='Max')

        plt.xlabel(xlabel, fontsize=18)
        plt.ylabel(ylabel, fontsize=18)
        plt.title(title, fontsize=20)        
        plt.yticks(fontsize=18)

        plt.xticks([r + bar_width for r in range(len(stats_df))], 
                   [f'{x:.2f}' for x in stats_df['CellID']], rotation=90, fontsize=18)

        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), fancybox=True, shadow=False, ncol=3)

        plt.subplots_adjust(bottom=0.3)
        plt.tight_layout()
        output_file = get_output_path(filename)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"RAN statistics plot saved as: {output_file}")

    def plot_metric_per_altitude(alt_metric_values, metric_name, ylabel, filename, bar_color, y_ax_lim):
        df = pd.DataFrame(alt_metric_values, columns=['Altitude', metric_name])
        grouped = df.groupby('Altitude')[metric_name].agg(['mean', 'std']).reset_index()

        plt.figure(figsize=(12, 6))
        plt.bar(grouped['Altitude'], grouped['mean'], color=bar_color, width=8, edgecolor='black', label=f'Mean {metric_name}')
        plt.errorbar(x=grouped['Altitude'], y=grouped['mean'], 
                     yerr=grouped['std'], fmt='none', 
                     ecolor='black', capsize=5, label='± Std Dev')

        plt.xlabel('Altitude over sea level (m)', fontsize=18)
        plt.ylabel(ylabel, fontsize=18)
        plt.title(f'Mean {metric_name} with Standard Deviation per Altitude', fontsize=20)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        if metric_name == 'SINR' : plt.ylim(bottom=y_ax_lim) 
        else:plt.ylim(top=y_ax_lim)
        plt.legend()
        plt.tight_layout()
        output_file = get_output_path(filename)
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"RAN altitude plot saved as: {output_file}")

    def plot_altitude_count(altitude_values, xlabel, ylabel, title, filename):
        unique_altitudes, counts = np.unique(altitude_values, return_counts=True)
        
        plt.figure(figsize=(12, 6))
        plt.bar(unique_altitudes, counts, color='purple', width=8, alpha=0.7, edgecolor='black')
        plt.xlabel(xlabel, fontsize=18)
        plt.ylabel(ylabel, fontsize=18)
        plt.title(title, fontsize=20)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        output_file = get_output_path(filename)
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"Altitude count plot saved as: {output_file}")

    def plot_nb_metric_per_cellid(nb_data, metric_base, ylabel, title, filename):
        df_nb = pd.DataFrame(nb_data)
        grouped = df_nb.groupby('CellID').agg(['mean', 'std'])

        cellids = grouped.index.astype(str)
        x = np.arange(len(cellids))
        bar_width = 0.25

        plt.figure(figsize=(14, 6))
        colors = ['skyblue', 'lightgreen', 'lightcoral']
        nb_labels = ['NB1', 'NB2', 'NB3']

        for i, nb in enumerate(nb_labels):
            mean_col = (f'{nb}_{metric_base}', 'mean')
            std_col = (f'{nb}_{metric_base}', 'std')
            plt.bar(x + i * bar_width, grouped[mean_col], yerr=grouped[std_col], capsize=5,
                    width=bar_width, label=nb, color=colors[i], edgecolor='black')

        plt.xlabel('Cell ID', fontsize=18)
        plt.ylabel(ylabel, fontsize=18)
        plt.title(title, fontsize=20)
        plt.xticks(x + bar_width, cellids, rotation=90, fontsize=18)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=3)
        plt.subplots_adjust(bottom=0.3)
        plt.tight_layout()
        output_file = get_output_path(filename)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"NB metric plot saved as: {output_file}")

    # Generate all RAN plots
    if rsrp_values:  # Only proceed if we have data
        # Generate CDF plots
        plot_cdf(*calculate_cdf(rsrp_values), 'RSRP (dBm)', 'CDF of RSRP', 'CDF_RSRP.png', 'blue')
        plot_cdf(*calculate_cdf(rsrq_values), 'RSRQ (dB)', 'CDF of RSRQ', 'CDF_RSRQ.png', 'green')
        plot_cdf(*calculate_cdf(rssi_values), 'RSSI (dB)', 'CDF of RSSI', 'CDF_RSSI.png', 'black')
        plot_cdf(*calculate_cdf(sinr_values), 'SINR (dB)', 'CDF of SINR', 'CDF_SINR.png', 'red')

        # Generate PDF plots
        plot_pdf(cellid_values, 'Cell ID', 'PDF of Cell IDs', 'PDF_CellID.png', 'orange')
        plot_pdf(lac_values, 'LAC', 'PDF of LACs', 'PDF_LAC.png', 'brown')

        # Generate Min/Mean/Max plots
        plot_min_mean_max(data, 'RSRP', 'Cell ID', 'RSRP (dBm)', 'Statistics of RSRP', 'stats_RSRP.png')
        plot_min_mean_max(data, 'RSRQ', 'Cell ID', 'RSRQ (dB)', 'Statistics of RSRQ', 'stats_RSRQ.png')
        plot_min_mean_max(data, 'RSSI', 'Cell ID', 'RSSI (dB)', 'Statistics of RSSI', 'stats_RSSI.png')
        plot_min_mean_max(data, 'SINR', 'Cell ID', 'SINR (dB)', 'Statistics of SINR', 'stats_SINR.png')

        # Plot metrics per altitude
        plot_metric_per_altitude(alt_rsrp_values, 'RSRP', 'RSRP (dBm)', 'RSRP_vs_Altitude.png', 'skyblue',-60)
        plot_metric_per_altitude(alt_rsrq_values, 'RSRQ', 'RSRQ (dB)', 'RSRQ_vs_Altitude.png', 'lightgreen',-5)
        plot_metric_per_altitude(alt_rssi_values, 'RSSI', 'RSSI (dB)', 'RSSI_vs_Altitude.png', 'lightcoral',-40)
        plot_metric_per_altitude(alt_sinr_values, 'SINR', 'SINR (dB)', 'SINR_vs_Altitude.png', 'gold',0)

        # Generate altitude count plot
        plot_altitude_count(altitude_values, 'Altitude over sea level(m)', 'Sample Count', 'Sample Count per Altitude', 'Altitude_Count.png')

        # Generate NB plots
        plot_nb_metric_per_cellid(nb_data, 'RSRP', 'RSRP (dBm)', 'NB RSRP per Cell ID', 'NB_RSRP_per_CellID.png')
        plot_nb_metric_per_cellid(nb_data, 'RSRQ', 'RSRQ (dB)', 'NB RSRQ per Cell ID', 'NB_RSRQ_per_CellID.png')
        plot_nb_metric_per_cellid(nb_data, 'RSSI', 'RSSI (dB)', 'NB RSSI per Cell ID', 'NB_RSSI_per_CellID.png')
    else:
        print("Warning: No valid RAN data after filtering. All values were filtered out.")

def analyze_throughput_statistics():
    """Analyze and plot throughput statistics from iperf3_data.txt"""
    print("Processing throughput statistics...")
    
    # Check if file exists
    if not os.path.exists('iperf3_data.txt'):
        print("Warning: iperf3_data.txt not found. Skipping throughput statistics.")
        return

    # Define bin width
    bin_size = 0.1

    # Load the dataset from the file 'iperf3_result.txt'.
    # We skip the second row (index 1) because it contains invalid data ',0,0'.
    df = pd.read_csv('iperf3_data.txt', skiprows=[1])

    # Convert speed columns to numeric types
    df['UL'] = pd.to_numeric(df['UL'], errors='coerce')
    df['DL'] = pd.to_numeric(df['DL'], errors='coerce')

    # Remove any rows that have NaN in speed columns
    df.dropna(subset=['UL', 'DL'], inplace=True)

    # Determine the maximum speed to set the upper limit for our bins
    max_speed = max(df['UL'].max(), df['DL'].max())

    # Create bins using the bin_size variable
    bins = np.arange(0, max_speed + bin_size, bin_size)

    # Calculate the histogram for UL_speed
    ul_counts, ul_bins = np.histogram(df['UL'], bins=bins)
    ul_cdf = np.cumsum(ul_counts) / sum(ul_counts)

    # Calculate the histogram for DL_speed
    dl_counts, dl_bins = np.histogram(df['DL'], bins=bins)
    dl_cdf = np.cumsum(dl_counts) / sum(dl_counts)

    # Plot the CDFs as step line charts
    plt.figure(figsize=(10, 6))

    # Create step line for UL_speed
    plt.step(ul_bins[:-1], ul_cdf, where='post', label='UL_Throughput CDF')

    # Create step line for DL_speed
    plt.step(dl_bins[:-1], dl_cdf, where='post', label='DL_Throughput CDF')

    # Set the title and labels for the plot
    plt.title(f'CDF of Throughput', fontsize=20)
    plt.xlabel('Throughput (Mbps)', fontsize=18)
    plt.ylabel('CDF', fontsize=18)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.xticks(rotation=90, fontsize=18)
    
    plt.yticks(fontsize=18)
    plt.tight_layout()

    # Save the plot
    output_file = get_output_path(f'speed_cdf.png')
    plt.savefig(output_file)
    plt.close()
    print(f"Throughput statistics plot saved as: {output_file}")

def main():
    """Main function to run all analyses"""
    print("Starting Combined Network Statistics Analysis")
    print("=" * 50)
    
    # Create output directory first
    create_output_directory()
    print()
    
    # Initialize timestamp from data files
    initialize_timestamp()
    print()
    
    # Run all analysis functions
    analyze_delay_statistics()
    print()
    analyze_ran_statistics()
    print()
    analyze_throughput_statistics()
    
    print()
    print("=" * 50)
    print("All network statistics analyses completed successfully!")
    print(f"Check the '{OUTPUT_DIR}' directory for all generated PNG files.")
    print(f"Files saved with timestamp suffix: {TIMESTAMP_SUFFIX}")

if __name__ == "__main__":
    main()
