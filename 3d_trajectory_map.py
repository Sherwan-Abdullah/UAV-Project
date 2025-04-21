import pandas as pd
import plotly.express as px

# --- Load the data from the file in the same directory ---
file_name = 'lte_data.txt'

# Read the CSV data using pandas
# Need to handle potential parsing errors and inconsistent columns if the file isn't perfectly clean
try:
    # Read directly from the file name, skipping bad lines if necessary
    df = pd.read_csv(file_name, on_bad_lines='skip')

    # --- Data Cleaning and Preparation ---
    # Select necessary columns
    df_filtered = df[['Altitude', 'latitude', 'longitude', 'RSRP']].copy()

    # Convert columns to numeric, coercing errors to NaN
    df_filtered['Altitude'] = pd.to_numeric(df_filtered['Altitude'], errors='coerce')
    df_filtered['latitude'] = pd.to_numeric(df_filtered['latitude'], errors='coerce')
    df_filtered['longitude'] = pd.to_numeric(df_filtered['longitude'], errors='coerce')
    df_filtered['RSRP'] = pd.to_numeric(df_filtered['RSRP'], errors='coerce')

    # Drop rows with NaN values in essential columns
    df_filtered.dropna(subset=['Altitude', 'latitude', 'longitude', 'RSRP'], inplace=True)

    # --- Define color mapping function and create a label column ---
    def map_rsrp_to_color_and_label(rsrp):
        if -85 <= rsrp <= -10:
            return 'green', '-85 <= RSRP'
        elif -100 <= rsrp < -85:
            return 'yellow', '-100 <= RSRP <= -85'
        else:
            return 'red', 'RSRP <= -100'

    # Apply the function to create both 'color' and 'label' columns
    df_filtered[['color', 'signal_power_in_dBm']] = df_filtered['RSRP'].apply(lambda x: pd.Series(map_rsrp_to_color_and_label(x)))

    # --- Create the 3D Scatter Plot ---
    fig = px.scatter_3d(df_filtered,
                        x='longitude',
                        y='latitude',
                        z='Altitude',
                        color='signal_power_in_dBm',  # Use the label column for color mapping
                        color_discrete_map={ # Enforce the specific colors for the labels
                            '-85 <= RSRP': 'green',
                            '-100 <= RSRP <= -85': 'yellow',
                            'RSRP <= -100': 'red',
                            
                        },
                        hover_name=df_filtered.index, # Optional: show index on hover
                        hover_data={'RSRP': True, # Show RSRP value on hover
                                    'Altitude': True,
                                    'latitude': True,
                                    'longitude': True,
                                    'signal_power_in_dBm': True, # Show the signal quality label on hover
                                    'color': False # Hide the color name itself if desired
                                   },
                        title="3D RSRP Trajectory Map")

    # Adjust marker size if desired
    fig.update_traces(marker=dict(size=3))

    # Adjust layout for better viewing
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=40)) # Adjust margins

    # --- Save the plot as an HTML file ---
    output_html_file = "rsrp_3d_map.html"
    fig.write_html(output_html_file)
    print(f"Map saved successfully as {output_html_file}")

    # --- Optionally, still show the plot in a browser window if running interactively ---
    # fig.show() # You can uncomment this if you also want to see it immediately

except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found in the same directory as the script.")
except Exception as e:
    print(f"An error occurred during data processing or plotting: {e}")
    print("Please ensure the 'lte_data.txt' file is correctly formatted CSV and in the same folder.")