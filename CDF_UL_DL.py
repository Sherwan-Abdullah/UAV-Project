import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv("iperf3_result.txt", skiprows=1)
data.columns = ["date_time", "UL_speed", "DL_speed"]  # Rename columns
data = data.dropna(subset=["UL_speed", "DL_speed"])  # Remove rows with missing values

# Define the bins and labels for your specified ranges
bins = [0, 2, 5, 10, 20, 35, 50, 75, 150]
labels = [str(num) for num in bins[1:]]
print (labels)

# Bin the UL_speed and DL_speed data
data["UL_range"] = pd.cut(data["UL_speed"], bins=bins, labels=labels, include_lowest=True)
data["DL_range"] = pd.cut(data["DL_speed"], bins=bins, labels=labels, include_lowest=True)

# Calculate the cumulative frequencies for each range
ul_cdf = data["UL_range"].value_counts(sort=False).cumsum() / len(data)
dl_cdf = data["DL_range"].value_counts(sort=False).cumsum() / len(data)

# Create a step chart
plt.figure(figsize=(10, 6))

# Step plot for UL_speed CDF
plt.step(labels, ul_cdf, where="post", label="UL_speed CDF", color = 'red')

# Step plot for DL_speed CDF
plt.step(labels, dl_cdf, where="post", label="DL_speed CDF", color = 'blue')

# Customize the plot
plt.title("CDF of UL and DL speeds")
plt.xlabel("Speed Ranges (Mbps)")
plt.ylabel("CDF")
plt.legend(loc="lower right")
plt.grid(True, linestyle='--', alpha=0.7)

# Show the plot
plt.savefig('CDF_speed', dpi=300)
