from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
from fredapi import Fred
from datetime import datetime, timedelta
import os
import traceback
import requests

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Load model artifacts
model    = joblib.load("model_D.pkl")
scaler   = joblib.load("scaler_D.pkl")
features = joblib.load("features_D.pkl")

# Environment variables
FRED_API_KEY        = os.getenv("FRED_API_KEY")
ALPHA_VANTAGE_KEY   = os.getenv("ALPHA_VANTAGE_KEY")

if not FRED_API_KEY:
    raise ValueError("FRED_API_KEY not set")

if not ALPHA_VANTAGE_KEY:
    raise ValueError("ALPHA_VANTAGE_KEY not set")

LAGS = [3, 6, 9, 12]


# ─────────────────────────────────────────────
# FETCH SP500 (Alpha Vantage)
# ─────────────────────────────────────────────
def fetch_sp500(start_str, end_str):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_MONTHLY",
        "symbol": "SPY",
        "apikey": ALPHA_VANTAGE_KEY
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if "Monthly Time Series" not in data:
        raise ValueError(f"Alpha Vantage error: {data}")

    ts = data["Monthly Time Series"]

    df = pd.DataFrame.from_dict(ts, orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    df["close"] = df["4. close"].astype(float)

    df = df.loc[start_str:end_str]

    if df.empty:
        raise ValueError("Alpha Vantage returned empty SP500 data")

    return df["close"].rename("SP500")


# ─────────────────────────────────────────────
# FETCH ALL DATA
# ─────────────────────────────────────────────
def fetch_latest_data():
    try:
        fred  = Fred(api_key=FRED_API_KEY)
        end   = datetime.today()
        start = end - timedelta(days=1200)

        start_str = start.strftime("%Y-%m-%d")
        end_str   = end.strftime("%Y-%m-%d")

        # FRED data
        unemployment = fred.get_series("UNRATE", start_str, end_str)
        inflation    = fred.get_series("FPCPITOTLZGUSA", start_str, end_str)
        interest     = fred.get_series("DFF", start_str, end_str)

        if unemployment.empty:
            raise ValueError("UNRATE empty")
        if inflation.empty:
            raise ValueError("Inflation empty")
        if interest.empty:
            raise ValueError("Interest empty")

        unemployment.index = pd.to_datetime(unemployment.index)
        inflation.index    = pd.to_datetime(inflation.index)
        interest.index     = pd.to_datetime(interest.index)

        unemployment = unemployment.resample("MS").last().rename("Unemployment")
        inflation    = inflation.resample("MS").ffill().rename("Inflation")
        interest     = interest.resample("MS").last().rename("Interest")

        # SP500 via Alpha Vantage
        sp500 = fetch_sp500(start_str, end_str)
        sp500 = sp500.resample("MS").last()

        # Align indices
        all_months = unemployment.index.union(inflation.index) \
                                      .union(interest.index) \
                                      .union(sp500.index)

        unemployment = unemployment.reindex(all_months)
        inflation    = inflation.reindex(all_months).ffill()
        interest     = interest.reindex(all_months)
        sp500        = sp500.reindex(all_months)

        df = pd.DataFrame({
            "Unemployment": unemployment,
            "Inflation":    inflation,
            "Interest":     interest,
            "SP500":        sp500,
        }, index=all_months)

        df = df.dropna()

        if df.empty:
            raise ValueError("Final dataset empty")

        return df

    except Exception as e:
        raise ValueError(f"fetch_latest_data failed: {str(e)}")


# ─────────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────────
def build_features(df):
    out = df.copy()

    for col in ["Unemployment", "Inflation", "Interest", "SP500"]:
        for lag in LAGS:
            out[f"{col}_lag{lag}"] = out[col].shift(lag)

        out[f"{col}_roll3_mean"] = out[col].rolling(3).mean()
        out[f"{col}_roll6_mean"] = out[col].rolling(6).mean()
        out[f"{col}_roll3_std"]  = out[col].rolling(3).std()

        out[f"{col}_mom1"]  = out[col].diff(1)
        out[f"{col}_mom3"]  = out[col].diff(3)
        out[f"{col}_mom12"] = out[col].diff(12)

    out = out.dropna()

    if out.empty:
        raise ValueError("Feature dataframe empty")

    return out


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug")
def debug():
    try:
        df       = fetch_latest_data()
        featured = build_features(df)

        return {
            "raw_rows": len(df),
            "featured_rows": len(featured),
            "features_expected": len(features),
            "features_in_df": len([c for c in features if c in featured.columns]),
            "missing_features": [c for c in features if c not in featured.columns],
            "last_date": str(df.index[-1])
        }

    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/predict")
def predict():
    try:
        raw      = fetch_latest_data()
        featured = build_features(raw)

        missing = [c for c in features if c not in featured.columns]
        if missing:
            raise HTTPException(status_code=500,
                detail=f"Missing features: {missing}")

        latest = featured.iloc[[-1]]
        date   = latest.index[0].strftime("%Y-%m")

        X    = scaler.transform(latest[features].values)
        prob = float(model.predict_proba(X)[0][1])
        pred = int(model.predict(X)[0])

        return {
            "month":             date,
            "recession_prob":    round(prob, 4),
            "recession_predict": bool(pred),
            "signal":            "HIGH" if prob >= 0.5 else "LOW"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,
            detail=f"{str(e)} | {traceback.format_exc()}")