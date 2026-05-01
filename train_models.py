import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def train_and_evaluate():
    print("Loading dataset...")
    df = pd.read_csv('indian_housing_data.csv')
    
    X = df.drop('price_lakhs', axis=1)
    y = df['price_lakhs']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    }
    
    results = {}
    best_model_name = ""
    best_r2 = -float('inf')
    best_model = None
    
    print("Training models...")
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        r2 = r2_score(y_test, preds)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        
        results[name] = {
            'r2': r2,
            'mae': mae,
            'rmse': rmse
        }
        
        print(f"{name}: R2 = {r2:.4f}, MAE = {mae:.2f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_model = model

    print(f"\nBest Model: {best_model_name} (R2 = {best_r2:.4f})")
    
    # Feature Importances (from best model if tree-based, else RF fallback)
    feature_names = X.columns.tolist()
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_.tolist()
    else:
        # Fallback to Random Forest importances if Linear Regression is somehow best
        importances = models['Random Forest'].feature_importances_.tolist()
        
    model_data = {
        'models': models,
        'results': results,
        'best_model_name': best_model_name,
        'best_model': best_model,
        'scaler': scaler,
        'feature_names': feature_names,
        'feature_importances': importances,
        'dataset_size': len(df)
    }
    
    with open('model_data.pkl', 'wb') as f:
        pickle.dump(model_data, f)
        
    print("Saved models to model_data.pkl")

if __name__ == "__main__":
    train_and_evaluate()
