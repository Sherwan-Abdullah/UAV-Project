import pandas as pd
import matplotlib.pyplot as plt

# Load data
file_path = "lte_data.txt"
columns = ["Altitude", "RSRP"]
data = pd.read_csv(file_path, usecols=[0, 10])  # Assuming Altitude is first and RSRP is 11th

# Remove any rows with missing RSRP values
data = data.dropna()

# Group by altitude and compute statistics
stats = data.groupby("Altitude")["RSRP"].agg(["mean", "std"])

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(stats.index, stats["mean"], yerr=stats["std"], capsize=5, alpha=0.7, label="Mean RSRP")
ax.set_xlabel("Altitude")
ax.set_ylabel("RSRP")
ax.set_title("Average RSRP with Standard Deviation per Altitude")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.5)

# Save the plot
image_name = "rsrp_chart.png"
plt.savefig(image_name)

print(f"Chart saved as {image_name}")