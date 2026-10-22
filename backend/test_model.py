import pandas as pd
import xgboost as xgb
import pickle

# Load dataset
df = pd.read_csv("backend/data/dataset.csv")

print("Dataset Loaded Successfully")
print(df.head())

# Features and target
X = df[["latitude", "longitude", "rainfall", "temperature", "humidity", "ndvi", "sar_water"]]
y = df["flood"]

# Train model
model = xgb.XGBClassifier()
model.fit(X, y)

# Save model
import os
os.makedirs("backend/model", exist_ok=True)

with open("backend/model/flood_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\nModel saved to backend/model/flood_model.pkl")