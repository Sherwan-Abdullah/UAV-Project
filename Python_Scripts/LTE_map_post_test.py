import pandas as pd
import geopandas as gpd
import folium
import branca

# Load LTE data
df = pd.read_csv('lte_data.txt')
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

# Define metrics and their legend positions
metrics = [
    ('RSRP', 'RSRP (dBm)', 'top-left'),
    ('RSRQ', 'RSRQ (dB)', 'top-right'),
    ('RSSI', 'RSSI (dBm)', 'bottom-left'),
    ('SINR', 'SINR (dB)', 'bottom-right')
]

# Generate individual maps
map_files = []
for metric, title, position in metrics:
    colormap = branca.colormap.LinearColormap(
        ['red', 'yellow', 'green'],
        vmin=gdf[metric].min(),
        vmax=gdf[metric].max()
    )

    m = folium.Map(location=[gdf['latitude'].mean(), gdf['longitude'].mean()], zoom_start=17)

    # Add markers
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color=colormap(row[metric]),
            fill=True,
            fill_color=colormap(row[metric]),
            fill_opacity=1.0
        ).add_to(m)

    colormap.caption = title
    m.add_child(colormap)

    # Save each map
    map_filename = f"{metric.lower()}_map.html"
    m.save(map_filename)
    map_files.append((map_filename, title, position))

# Combine all maps into one HTML file
with open('lte_radio_maps_2x2.html', 'w') as f:
    f.write("""
    <html>
    <head>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                overflow: hidden;
                width: 100%;
                height: 100%;
            }
            .grid-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                grid-template-rows: 1fr 1fr;
                width: 100vw;
                height: 100vh;
                box-sizing: border-box;
            }
            .grid-item {
                position: relative;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }
            .map-frame {
                width: 90%;
                height: 90%;
                border: 3pt solid black;
                box-sizing: border-box;
            }
            .caption {
                position: absolute;
                writing-mode: vertical-rl;
                transform: rotate(180deg);
                font-weight: bold;
                background: rgba(255,255,255,0.8);
                padding: 5px;
                z-index: 999;
            }
            .top-left    { top: 10px; left: 10px; }
            .top-right   { top: 10px; right: 10px; }
            .bottom-left { bottom: 10px; left: 10px; }
            .bottom-right{ bottom: 10px; right: 10px; }
        </style>
    </head>
    <body>
        <div class="grid-container">
    """)

    for map_file, title, pos in map_files:
        f.write(f"""
            <div class="grid-item">
                <div class="caption {pos}">{title}</div>
                <iframe class="map-frame" src="{map_file}"></iframe>
            </div>
        """)

    f.write("""
        </div>
    </body>
    </html>
    """)

print("✅ All maps saved in 'lte_radio_maps_2x2.html'")
