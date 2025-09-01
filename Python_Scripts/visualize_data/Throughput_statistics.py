import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define bin width
bin_size = 1

# Load the dataset from the file 'iperf3_result.txt'.
# We skip the second row (index 1) because it contains invalid data ',0,0'.
df = pd.read_csv('iperf3_data.txt', skiprows=[1])

# The 'date time' column is not used for this analysis. We focus on 'UL_speed' and 'DL_speed'.
# We convert these columns to numeric types. 'coerce' will replace any non-numeric values with NaN.
df['UL_speed'] = pd.to_numeric(df['UL_speed'], errors='coerce')
df['DL_speed'] = pd.to_numeric(df['DL_speed'], errors='coerce')

# We remove any rows that have NaN in 'UL_speed' or 'DL_speed' columns.
df.dropna(subset=['UL_speed', 'DL_speed'], inplace=True)

# We determine the maximum speed to set the upper limit for our bins.
max_speed = max(df['UL_speed'].max(), df['DL_speed'].max())

# We create bins using the bin_size variable.
bins = np.arange(0, max_speed + bin_size, bin_size)

# We calculate the histogram for UL_speed. This counts the number of occurrences in each bin.
ul_counts, ul_bins = np.histogram(df['UL_speed'], bins=bins)
# We then compute the Cumulative Distribution Function (CDF) for UL_speed.
ul_cdf = np.cumsum(ul_counts) / sum(ul_counts)

# We do the same for DL_speed.
dl_counts, dl_bins = np.histogram(df['DL_speed'], bins=bins)
dl_cdf = np.cumsum(dl_counts) / sum(dl_counts)

# Now we plot the CDFs as step line charts.
plt.figure(figsize=(10, 6))

# Create step line for UL_speed
plt.step(ul_bins[:-1], ul_cdf, where='post', label='UL_speed CDF')

# Create step line for DL_speed
plt.step(dl_bins[:-1], dl_cdf, where='post', label='DL_speed CDF')


# We set the title and labels for the plot for better understanding.
plt.title(f'CDF of Throughput (bin size: {bin_size})')
plt.xlabel('Throughput (Mbps)')
plt.ylabel('Cumulative Distribution Function')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.xticks(rotation=90)
#plt.yticks(np.arange(0, 1.1, 0.1))
plt.tight_layout()

# Finally, we display the plot.
plt.savefig(f'speed_cdf_{bin_size}_Mbps.png')
