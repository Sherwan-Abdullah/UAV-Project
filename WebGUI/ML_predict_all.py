import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.multioutput import MultiOutputRegressor
import warnings

warnings.filterwarnings('ignore')

class GPSKolmogorovExtrapolator:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.scaler = StandardScaler()

    def gps_to_utm_approx(self, lat, lon, ref_lat=None, ref_lon=None):
        if ref_lat is None: ref_lat = np.mean(lat)
        if ref_lon is None: ref_lon = np.mean(lon)
        R = 6378137.0
        lat_rad, lon_rad = np.radians(lat), np.radians(lon)
        ref_lat_rad, ref_lon_rad = np.radians(ref_lat), np.radians(ref_lon)
        x = R * (lon_rad - ref_lon_rad) * np.cos(ref_lat_rad)
        y = R * (lat_rad - ref_lat_rad)
        return x, y

    def create_altitude_aware_features(self, x, y, alt, target_alt):
        features = [x, y, alt]
        alt_diff = np.abs(alt - target_alt)
        features.append(alt_diff)
        features.append(alt_diff**2)
        alt_normalized = (alt - np.mean(alt)) / (np.std(alt) + 1e-6)
        features.append(alt_normalized)
        features.append(x * alt / 1000.0)
        features.append(y * alt / 1000.0)
        horiz_dist = np.sqrt(x**2 + y**2)
        features.append(horiz_dist)
        features.append(horiz_dist * alt / 10000.0)
        features.extend([(alt < 280).astype(float), ((alt >= 280) & (alt < 340)).astype(float), (alt >= 340).astype(float)])
        return np.column_stack(features)

    def compute_altitude_weights(self, alt_train, target_altitude, bandwidth=30.0):
        alt_distance = np.abs(alt_train - target_altitude)
        weights = np.exp(-(alt_distance**2) / (2 * bandwidth**2))
        weights = weights / np.sum(weights) * len(weights)
        return np.maximum(weights, 0.1)

    def predict_gps_models(self, training_data, prediction_data, target_altitude, targets):
        train_clean = training_data.dropna(subset=['latitude', 'longitude', 'Altitude'] + targets)
        train_clean = train_clean[train_clean['RSRP'] <= -50]
        pred_clean = prediction_data.dropna(subset=['latitude', 'longitude'] + targets)
        
        y_train = train_clean[targets].values
        ref_lat, ref_lon = np.mean(train_clean['latitude']), np.mean(train_clean['longitude'])
        
        xt, yt = self.gps_to_utm_approx(train_clean['latitude'].values, train_clean['longitude'].values)
        xp, yp = self.gps_to_utm_approx(pred_clean['latitude'].values, pred_clean['longitude'].values, ref_lat, ref_lon)
        
        Xt = self.create_altitude_aware_features(xt, yt, train_clean['Altitude'].values, target_altitude)
        Xp = self.create_altitude_aware_features(xp, yp, np.full(len(pred_clean), target_altitude), target_altitude)
        
        Xt_s = self.scaler.fit_transform(Xt)
        Xp_s = self.scaler.transform(Xp)
        w = self.compute_altitude_weights(train_clean['Altitude'].values, target_altitude)
        
        results = {}
        models = {
            'Random Forest (RF)': RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1),
            'Gradient Boosting (GB)': GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=5, random_state=42),
            'Multi-Layer Perceptron (MLP)': MLPRegressor(hidden_layer_sizes=(128, 64), max_iter=500, random_state=42, early_stopping=True)
        }
        
        for name, model in models.items():
            multi_model = MultiOutputRegressor(model)
            if 'MLP' not in name:
                multi_model.fit(Xt_s, y_train, sample_weight=w)
            else:
                multi_model.fit(Xt_s, y_train)
            results[name] = multi_model.predict(Xp_s)
            
        return {'predictions': results, 'actual': pred_clean[targets].values}

def main():
    data_file = 'lte_data.txt'
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found.")
        return

    targets = ['RSRP', 'RSRQ', 'RSSI', 'SINR']
    df = pd.read_csv(data_file).dropna(subset=['latitude', 'longitude', 'Altitude'] + targets)
    df = df[df['RSRP'] <= -50]
    total_samples_count = len(df)

    comparison = {t: {m: {} for m in ['Random Forest (RF)', 'Gradient Boosting (GB)', 'Multi-Layer Perceptron (MLP)']} for t in targets}

    # --- PART 1: LOAO METHOD ---
    print("Processing LOAO Method...")
    alts = sorted(df['Altitude'].unique())
    loao_raw = {t: {m: {'rmse': [], 'mae': []} for m in comparison[targets[0]]} for t in targets}

    for target_alt in alts:
        train_df, test_df = df[df['Altitude'] != target_alt], df[df['Altitude'] == target_alt]
        if train_df.empty or test_df.empty: continue

        ext = GPSKolmogorovExtrapolator(train_df)
        out = ext.predict_gps_models(train_df, test_df, target_alt, targets)
        
        for model_name, preds in out['predictions'].items():
            for i, target_name in enumerate(targets):
                y_true, y_pred = out['actual'][:, i], preds[:, i]
                loao_raw[target_name][model_name]['rmse'].append(np.sqrt(mean_squared_error(y_true, y_pred)))
                loao_raw[target_name][model_name]['mae'].append(mean_absolute_error(y_true, y_pred))

    for t in targets:
        for m in comparison[t]:
            comparison[t][m]['LOAO_RMSE'] = np.mean(loao_raw[t][m]['rmse'])
            comparison[t][m]['LOAO_MAE'] = np.mean(loao_raw[t][m]['mae'])

    # --- PART 2: GENERIC 80-20 METHOD ---
    print("Processing Generic 80-20 Method...")
    X_train, X_test, y_train, y_test = train_test_split(df[['Altitude', 'latitude', 'longitude']], df[targets], test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_tr_s, X_te_s = scaler.fit_transform(X_train), scaler.transform(X_test)

    generic_models = {
        'Random Forest (RF)': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting (GB)': GradientBoostingRegressor(random_state=42),
        'Multi-Layer Perceptron (MLP)': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
    }

    for name, model in generic_models.items():
        multi_model = MultiOutputRegressor(model)
        X_tr_in, X_te_in = (X_tr_s, X_te_s) if 'MLP' in name else (X_train, X_test)
        multi_model.fit(X_tr_in, y_train)
        preds = multi_model.predict(X_te_in)
        
        for i, target_name in enumerate(targets):
            comparison[target_name][name]['GEN_RMSE'] = np.sqrt(mean_squared_error(y_test.iloc[:, i], preds[:, i]))
            comparison[target_name][name]['GEN_MAE'] = mean_absolute_error(y_test.iloc[:, i], preds[:, i])

    # --- FINAL OUTPUT CONSTRUCTION ---
    output = []
    
    # Add the sample count line to the output list so it's written to the file
    output.append(f"total data samples count = {total_samples_count}\n")
    
    line_len = 105
    output.append("-" * line_len)
    output.append(f"{'RAN Metric':<12} {'Machine Learning Model':<30} {'RMSE (dBm)':^28} {'MAE (dBm)':^28}")
    output.append(f"{' ':<43} {'LOAO':^14} {'Generic':^14} {'LOAO':^14} {'Generic':^14}")
    output.append("-" * line_len)

    for target_name in targets:
        for m_idx, model_name in enumerate(comparison[target_name]):
            m_data = comparison[target_name][model_name]
            metric_label = target_name if m_idx == 1 else ""
            
            row = f"{metric_label:<12} {model_name:<30} "
            row += f"{m_data['LOAO_RMSE']:^14.2f} {m_data['GEN_RMSE']:^14.2f} "
            row += f"{m_data['LOAO_MAE']:^14.2f} {m_data['GEN_MAE']:^14.2f}"
            output.append(row)
        output.append("-" * line_len)

    final_table = "\n".join(output)
    
    # Print and save
    print(final_table)
    with open('ML_prediction.txt', 'w') as f:
        f.write(final_table)

if __name__ == '__main__':
    main()
