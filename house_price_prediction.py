# ============================================================
#   HOUSE PRICE PREDICTION SYSTEM
#   Mini Project | Machine Learning | Computer Engineering
#   Run: python house_price_prediction.py
# ============================================================

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import pickle
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────────────────────
# 1. DATASET  (Built-in — no download required)
# ──────────────────────────────────────────────────────────────

np.random.seed(42)
n = 300

data = {
    'area_sqft':      np.random.randint(600, 4500, n),
    'bedrooms':       np.random.randint(1, 6, n),
    'bathrooms':      np.random.randint(1, 4, n),
    'age_years':      np.random.randint(0, 50, n),
    'garage':         np.random.randint(0, 2, n),
    'location_score': np.random.uniform(1, 10, n),
    'quality_score':  np.random.uniform(1, 10, n),
}

df = pd.DataFrame(data)
df['price'] = (
    df['area_sqft']       * 150  +
    df['bedrooms']        * 15000 +
    df['bathrooms']       * 10000 -
    df['age_years']       * 1200  +
    df['garage']          * 20000 +
    df['location_score']  * 18000 +
    df['quality_score']   * 12000 +
    np.random.normal(0, 15000, n)
).clip(50000, None).round(-3)

# ──────────────────────────────────────────────────────────────
# 2. PREPROCESSING
# ──────────────────────────────────────────────────────────────

print("\n" + "="*55)
print("   HOUSE PRICE PREDICTION SYSTEM")
print("="*55)

print("\n[1] Dataset Info:")
print(f"    Records  : {len(df)}")
print(f"    Features : {df.shape[1]-1}")
print(f"    Missing  : {df.isnull().sum().sum()}")
print(f"    Price    : ${df['price'].min():,.0f}  to  ${df['price'].max():,.0f}")

X = df.drop('price', axis=1)
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

# ──────────────────────────────────────────────────────────────
# 3. MODEL TRAINING
# ──────────────────────────────────────────────────────────────

lr  = LinearRegression()
rf  = RandomForestRegressor(n_estimators=100, random_state=42)

lr.fit(X_train_s, y_train)
rf.fit(X_train,   y_train)

lr_pred = lr.predict(X_test_s)
rf_pred = rf.predict(X_test)

print("\n[2] Model Results:")
print("-"*45)
for name, pred in [("Linear Regression", lr_pred), ("Random Forest", rf_pred)]:
    r2   = r2_score(y_test, pred)
    mae  = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    print(f"\n    {name}")
    print(f"    R2 Score : {r2:.4f}  ({r2*100:.1f}%)")
    print(f"    MAE      : ${mae:,.0f}")
    print(f"    RMSE     : ${rmse:,.0f}")

rf_r2 = r2_score(y_test, rf_pred)
print(f"\n    Best Model: Random Forest  (R2 = {rf_r2:.4f})")

# Save for Streamlit
pickle.dump(rf,     open('rf_model.pkl', 'wb'))
pickle.dump(scaler, open('scaler.pkl',   'wb'))

# ──────────────────────────────────────────────────────────────
# 4. FEATURE IMPORTANCE
# ──────────────────────────────────────────────────────────────

print("\n[3] Feature Importance (Random Forest):")
imps = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
for f, v in imps.items():
    bar = "*" * int(v * 60)
    print(f"    {f:<18} {bar}  {v:.3f}")

# ──────────────────────────────────────────────────────────────
# 5. USER INPUT PREDICTION
# ──────────────────────────────────────────────────────────────

print("\n" + "="*55)
print("   HOUSE PRICE PREDICTOR")
print("="*55)

try:
    area   = float(input("\n  Area in sq ft      (e.g. 1500) : "))
    beds   = float(input("  Bedrooms           (1-5)       : "))
    baths  = float(input("  Bathrooms          (1-3)       : "))
    age    = float(input("  Age in years       (0-50)      : "))
    garage = float(input("  Garage? 1=Yes 0=No             : "))
    loc    = float(input("  Location score     (1-10)      : "))
    qual   = float(input("  Quality score      (1-10)      : "))

    inp   = np.array([[area, beds, baths, age, garage, loc, qual]])
    price = rf.predict(inp)[0]

    print("\n" + "="*55)
    print(f"  PREDICTED PRICE : ${price:,.0f}")
    print(f"  Model Accuracy  : {rf_r2*100:.1f}%  (R2 Score)")
    print("="*55)

except (ValueError, KeyboardInterrupt):
    print("\n  [Using sample house for demo]")
    sample = np.array([[1500, 3, 2, 10, 1, 7.5, 8.0]])
    price  = rf.predict(sample)[0]
    print(f"  Sample: 1500sqft | 3bed | 2bath | 10yr | loc=7.5 | qual=8")
    print(f"  Predicted Price: ${price:,.0f}")

print("\n  Done! Models saved: rf_model.pkl, scaler.pkl\n")
