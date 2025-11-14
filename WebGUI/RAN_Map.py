import os
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import folium
import branca

# Define the main output folder
main_output_folder = "spatiotemporal maps results"
os.makedirs(main_output_folder, exist_ok=True)

# Define the subfolder for individual metric HTML files
output_subfolder = os.path.join(main_output_folder, "output")
os.makedirs(output_subfolder, exist_ok=True)

# Load LTE data
df = pd.read_csv('lte_data.txt')

# Drop rows missing any of the required fields
required_columns = ['Altitude', 'longitude', 'latitude', 'CellID', 'RSRP', 'RSRQ', 'SINR', 'RSSI']
df.dropna(subset=required_columns, inplace=True)

print(f"Initial data loaded: {len(df)} rows")

# FILTER: Drop rows where RSRP > -50 or RSRQ > -3
initial_count = len(df)
df = df[(df['RSRP'] <= -50) & (df['RSRQ'] <= -3)]
filtered_count = initial_count - len(df)

print(f"Data filtering complete:")
print(f"  - Lines filtered out (RSRP > -50 or RSRQ > -3): {filtered_count}")
print(f"  - Valid lines remaining: {len(df)}")

# Check if we have any data left after filtering
if len(df) == 0:
    print("ERROR: No valid data remaining after filtering!")
    print("Cannot generate maps. Please check your data.")
    exit(1)

# Ensure 'longitude' and 'latitude' columns exist for GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

metrics = [
    ('RSRP', 'RSRP (dBm)'),
    ('RSRQ', 'RSRQ (dB)'),
    ('RSSI', 'RSSI (dBm)'),
    ('SINR', 'SINR (dB)')
]

plot_files = []
map_files = []

for metric, label in metrics:
    values = df[metric]
    
    print(f"\nGenerating maps for {label}:")
    print(f"  - Min: {values.min():.2f}, Max: {values.max():.2f}")
    print(f"  - Mean: {values.mean():.2f}, Median: {values.median():.2f}")

    # --- 3D Plotly Map ---
    fig = go.Figure(data=go.Scatter3d(
        x=df['longitude'],
        y=df['latitude'],
        z=df['Altitude'],
        mode='markers',
        marker=dict(
            size=4,
            color=values,
            colorscale='RdYlGn',
            colorbar=dict(
                title=label,
                thickness=10,
                len=0.5,
                y=0.5,
                ticks="outside"
            ),
            cmin=values.min(),
            cmax=values.max()
        ),
        text=[f"{metric}: {v:.2f}" for v in values],
        hoverinfo='text'
    ))
    fig.update_layout(
        title=f"{label} - 3D Scatter",
        margin=dict(l=0, r=0, b=0, t=40),
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude'
        )
    )
    plot_file = os.path.join(output_subfolder, f"{metric.lower()}_3d.html")
    fig.write_html(plot_file)
    plot_files.append(plot_file)
    print(f"  - 3D map saved: {plot_file}")

    # --- 2D Folium Map ---
    colormap = branca.colormap.LinearColormap(
        ['red', 'yellow', 'green'],
        vmin=values.min(),
        vmax=values.max()
    )
    # Set the colormap width to half (default is 350px, setting to 175px)
    colormap.width = 175
    
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=17)
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color=colormap(row[metric]),
            fill=True,
            fill_color=colormap(row[metric]),
            fill_opacity=1.0,
            tooltip=f'{metric}: {row[metric]:.2f}'
        ).add_to(m)
    colormap.caption = label
    m.add_child(colormap)
    map_file = os.path.join(output_subfolder, f"{metric.lower()}_map.html")
    m.save(map_file)
    map_files.append(map_file)
    print(f"  - 2D map saved: {map_file}")

# --- Save the Combined HTML in the Main Output Directory ---
html_output = os.path.join(main_output_folder, "lte_combined_visuals.html")
with open(html_output, 'w') as f:
    f.write("""
    <html>
    <head>
        <title>LTE Metrics Visualization</title>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                width: 100%;
                height: auto;
                overflow-y: auto;
            }
            .grid-container {
                display: grid;
                grid-template-columns: 50% 50%;
                grid-template-rows: repeat(4, 500px);
                width: 100%;
                gap: 20px;
            }
            .grid-item {
                border: 2px solid black;
                overflow: hidden;
            }
            iframe {
                width: 100%;
                height: 100%;
                border: none;
            }
            .title {
                text-align: center;
                font-weight: bold;
                padding: 10px;
                background-color: #f0f0f0;
            }
        </style>
    </head>
    <body>
        <div class="grid-container">
    """)

    for plot, map_, (metric, label) in zip(plot_files, map_files, metrics):
        relative_plot_path = os.path.relpath(plot, start=main_output_folder)
        relative_map_path = os.path.relpath(map_, start=main_output_folder)
        f.write(f"""
            <div class="grid-item">
                <div class="title">{label} - 3D Plot</div>
                <iframe src="{relative_plot_path}"></iframe>
            </div>
            <div class="grid-item">
                <div class="title">{label} - 2D Map</div>
                <iframe src="{relative_map_path}"></iframe>
            </div>
        """)

    f.write("""
        </div>
    </body>
    </html>
    """)

print(f"\n{'='*60}")
print(f"All visualizations have been successfully created!")
print(f"Combined view saved: {html_output}")
print(f"Individual maps saved in: {output_subfolder}")
print(f"{'='*60}")
