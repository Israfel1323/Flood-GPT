import pandas as pd
import xgboost as xgb
import pickle
import os

# 🔥 Go UP one level from model → backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Correct dataset path
dataset_path = os.path.join(BASE_DIR, "data", "dataset.csv")

# Load dataset
df = pd.read_csv(dataset_path)

print("Dataset Loaded Successfully")
print(df.head())

# Features
X = df[["latitude", "longitude", "rainfall", "temperature", "humidity", "ndvi", "sar_water"]]

# Target
y = df["flood"]

# Train model
model = xgb.XGBClassifier()
model.fit(X, y)

# Save model in backend/model
model_dir = os.path.join(BASE_DIR, "model")
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "flood_model.pkl")

with open(model_path, "wb") as f:
    pickle.dump(model, f)

print("\n✅ Model saved at:", model_path)