import pandas as pd
import matplotlib.pyplot as plt
import math

# Load the dataset
data = pd.read_csv("iperf3_result.txt", skiprows=1)
data.columns = ["date_time", "UL_speed", "DL_speed"]  # Rename columns
data = data.dropna(subset=["UL_speed", "DL_speed"])  # Remove rows with missing values

# Define a function to categorize speeds into bins of variable Mbps
bin_wide = 5
def bin_speed(value):
    return math.ceil(value / bin_wide) * bin_wide

# Apply binning to UL_speed and DL_speed
data["UL_range"] = data["UL_speed"].apply(bin_speed)
data["DL_range"] = data["DL_speed"].apply(bin_speed)

# Get all unique bins from both UL and DL speeds
all_bins = sorted(set(data["UL_range"]).union(set(data["DL_range"])))

# Calculate the cumulative frequency distribution
ul_counts = data["UL_range"].value_counts().sort_index().reindex(all_bins, fill_value=0)
dl_counts = data["DL_range"].value_counts().sort_index().reindex(all_bins, fill_value=0)

# Compute cumulative sum and normalize
ul_cdf = ul_counts.cumsum() / len(data)
dl_cdf = dl_counts.cumsum() / len(data)

# Create a step plot
plt.figure(figsize=(10, 6))

# Step plot for UL_speed CDF
plt.step(all_bins, ul_cdf, where="post", label="UL_speed CDF", color='red')

# Step plot for DL_speed CDF
plt.step(all_bins, dl_cdf, where="post", label="DL_speed CDF", color='blue')

# Customize the plot
plt.title("CDF of UL and DL speeds")
plt.xlabel("Speed Ranges (Mbps)")
plt.ylabel("CDF")
plt.legend(loc="lower right")
plt.grid(True, linestyle='--', alpha=0.7)

# Save and show the plot
plt.savefig('CDF_speed.png', dpi=300)
plt.show()
