import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define bin width
bin_width = 1

# Read the data from the file
df = pd.read_csv('nping_data.txt', sep=',')

# Convert 'Max' column to numeric, handling potential errors
df['Max_RTT_ms'] = pd.to_numeric(df['Max_RTT_ms'], errors='coerce')

# Drop rows with NaN values in 'Max' after conversion
df.dropna(subset=['Max_RTT_ms'], inplace=True)

# Set min_max to 0 to ensure the first bin starts from 0
min_max = 0
max_max = np.ceil(df['Max_RTT_ms'].max())

# Create bins
# Ensure max_max is large enough to include the last bin completely.
# For example, if max_max is 353 and bin_width is 100, bins should go up to 400.
# So, max_max + bin_width will make sure the last bin is included.
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
# Use 'Bin_Center' for x-axis and 'align='center''
plt.bar(pdf_df['Bin_Center'], pdf_df['PDF'], width=bin_width, align='center', edgecolor='black')
plt.xlabel('Latency (ms)', fontsize=18)
plt.ylabel('Probability Density Function', fontsize=18)
plt.title(f'PDF of Latency (Bin Width: {bin_width} ms)', fontsize = 20)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

# Set x-axis limits to start from 0 and extend slightly beyond the max value
plt.xlim(left=0, right=max_max + bin_width / 2)

# Save the plot to a file
plt.savefig(f'pdf_of_delay_{bin_width}msec.png')
