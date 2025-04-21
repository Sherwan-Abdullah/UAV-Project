import pandas as pd
import geopandas as gpd
import folium
import branca
import os
import matplotlib.pyplot as plt

# Load your data
df = pd.read_csv('lte_data.txt')

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

# Define a function to map the colors as per the given conditions for 'RSRP'
def color_map(value):
    if -85 <= value <= 0:
        return 'green'
    elif -100 <= value < -85:
        return 'yellow'
    else:
        return 'red'

# Apply the function to your data
gdf['color'] = gdf['RSRP'].apply(color_map)

# Define a function to map the colors for 'RSRQ'
def color_map_rsrq(value):
    if -12 <= value <= 0:
        return 'green'
    elif -18 <= value < -12:
        return 'yellow'
    else:
        return 'red'

# Apply the function to your data
gdf['color_rsrq'] = gdf['RSRQ'].apply(color_map_rsrq)

# Define a function to map the colors as per the given conditions for 'RSSI'
def color_map_rssi(value):
    if -65 <= value <= 0:
        return 'green'
    elif -75 <= value < -65:
        return 'yellow'
    else:
        return 'red'

# Apply the function to your data
gdf['color_rssi'] = gdf['RSSI'].apply(color_map_rssi)

# Define a function to map the colors for 'SINR'
def color_map_sinr(value):
    if 15 <= value <= 40:
        return 'green'
    elif 5 <= value < 15:
        return 'yellow'
    else:
        return 'red'

# Apply the function to your data
gdf['color_sinr'] = gdf['SINR'].apply(color_map_sinr)

# Create the first map RSRP
m1 = folium.Map(location=[gdf['latitude'].mean(), gdf['longitude'].mean()], zoom_start=17)
for idx, row in gdf.iterrows():
    folium.CircleMarker([row['latitude'], row['longitude']], radius=5, color=row['color'], fill=True, fill_color=row['color'], fill_opacity=1.0).add_to(m1)

# Create the second map RSRQ
m2 = folium.Map(location=[gdf['latitude'].mean(), gdf['longitude'].mean()], zoom_start=17)
for idx, row in gdf.iterrows():
    folium.CircleMarker([row['latitude'], row['longitude']], radius=5, color=row['color_rsrq'], fill=True, fill_color=row['color_rsrq'], fill_opacity=1.0).add_to(m2)

# Create the third map RSSI
m3 = folium.Map(location=[gdf['latitude'].mean(), gdf['longitude'].mean()], zoom_start=17)
for idx, row in gdf.iterrows():
    folium.CircleMarker([row['latitude'], row['longitude']], radius=5, color=row['color_rssi'], fill=True, fill_color=row['color_rssi'], fill_opacity=1.0).add_to(m3)

# Create the fourth map SINR
m4 = folium.Map(location=[gdf['latitude'].mean(), gdf['longitude'].mean()], zoom_start=17)
for idx, row in gdf.iterrows():
    folium.CircleMarker([row['latitude'], row['longitude']], radius=5, color=row['color_sinr'], fill=True, fill_color=row['color_sinr'], fill_opacity=1.0).add_to(m4)

# Get the last RSRP and RSRQ values
last_rsrp = gdf['RSRP'].iloc[-1]
last_rsrq = gdf['RSRQ'].iloc[-1]
last_rssi = gdf['RSSI'].iloc[-1]
last_sinr = gdf['SINR'].iloc[-1]

# Create a new figure for the table
fig, ax = plt.subplots()
ax.axis('off')

# Create a table and add it to the figure
table_data = [
    ["RSRP", last_rsrp, "dBm"],
    ["RSRQ", last_rsrq, "dB"],
    ["RSSI", last_rssi, "dB"],
    ["SINR", last_sinr, "dB"]
]
table = plt.table(cellText=table_data, loc='upper left', cellLoc='center', bbox=[0, 0, 1, 1])

# Apply styles to the table
table.auto_set_font_size(False)
table.set_fontsize(40)
table.scale(1, 1.5)

# Color the cells
table.get_celld()[(0, 1)].set_facecolor(color_map(last_rsrp))
table.get_celld()[(1, 1)].set_facecolor(color_map_rsrq(last_rsrq))
table.get_celld()[(2, 1)].set_facecolor(color_map_rssi(last_rssi))
table.get_celld()[(3, 1)].set_facecolor(color_map_sinr(last_sinr))

# Save the table as an image
plt.savefig('table.png')

# Create a Figure for HTML display
fig = branca.element.Figure()

# Create HTML subplots
fig1 = fig.add_subplot(2, 3, 1)
fig2 = fig.add_subplot(2, 3, 2)
fig3 = fig.add_subplot(2, 3, 3)
fig4 = fig.add_subplot(2, 3, 4)
fig5 = fig.add_subplot(2, 3, 5)

# Add maps to the HTML figure
m1.add_to(fig1)
m2.add_to(fig2)
m3.add_to(fig4)
m4.add_to(fig5)

# Add the table image
fig3.html.add_child(branca.element.Element('<img src="table.png" alt="table" width="100%">'))

# Save the final HTML output
fig.save('lte_radio_maps_after.html')
