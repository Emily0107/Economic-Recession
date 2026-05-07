# ML Inference Service

FastAPI service that serves real-time recession probability predictions using Model D
(Macro + S&P 500 — Logistic Regression).

## Indicators Used

| Indicator        | Source                    | Notes                              |
|------------------|---------------------------|------------------------------------|
| Unemployment     | FRED — UNRATE             | Monthly, resampled to month start  |
| Inflation        | FRED — FPCPITOTLZGUSA     | Annual, forward-filled monthly     |
| Interest Rate    | FRED — DFF                | Daily, resampled to month start    |
| S&P 500          | Alpha Vantage — SPY       | Monthly close, replaces yfinance   |

> **Why Alpha Vantage instead of yfinance?**
> `yfinance` relies on scraping Yahoo Finance's web interface, which blocks requests
> from cloud server IP addresses. Alpha Vantage provides a stable REST API suitable
> for production environments.

## Environment Variables

Create a `.env` file in this folder for local development that includes:
FRED_API_KEY=your_fred_api_key_here  
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here  

Get your free keys here:
- FRED: https://fred.stlouisfed.org/docs/api/api_key.html
- Alpha Vantage: https://www.alphavantage.co/support/#api-key

## Model Files

The following binary files are required but excluded from git (too large):
- `model_D.pkl` — trained Logistic Regression model
- `scaler_D.pkl` — fitted StandardScaler
- `features_D.pkl` — list of 44 feature column names

Download them by running Section 10 of the Google Colab notebook:
```python
from google.colab import files
files.download("model_D.pkl")
files.download("scaler_D.pkl")
files.download("features_D.pkl")
```
Place all three files in this `ml-service/` folder before deploying.

## Local Development

```bash
cd ml-service

# Install dependencies
pip install -r requirements.txt

# Run locally (reads from .env automatically if using python-dotenv)
uvicorn main:app --reload --port 8080
```

Test endpoints:
```bash
curl http://localhost:8080/health
curl http://localhost:8080/debug
curl http://localhost:8080/predict
```

## Deploy to Google Cloud Run

```bash
cd ml-service

gcloud run deploy recession-model \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 60 \
  --set-env-vars FRED_API_KEY=your_key_here,ALPHA_VANTAGE_KEY=your_key_here
```

## API Endpoints

| Endpoint   | Method | Description                                      |
|------------|--------|--------------------------------------------------|
| `/health`  | GET    | Returns `{"status": "ok"}` — use for uptime check |
| `/debug`   | GET    | Returns data row counts and feature diagnostics  |
| `/predict` | GET    | Returns current month recession probability      |

### `/predict` Response Example

```json
{
  "month": "2026-03",
  "recession_prob": 0.0004,
  "recession_predict": false,
  "signal": "LOW"
}
```

### Response Field Descriptions

| Field               | Type    | Description                                         |
|---------------------|---------|-----------------------------------------------------|
| `month`             | string  | Most recent month with complete data (YYYY-MM)      |
| `recession_prob`    | float   | Predicted recession probability (0.0 to 1.0)        |
| `recession_predict` | boolean | True if probability exceeds 50% threshold           |
| `signal`            | string  | `"HIGH"` if prob ≥ 0.5, `"LOW"` otherwise          |

> **Note on data lag:** The predicted month may be 1–2 months behind the current date.
> This is expected — FRED indicators such as unemployment and inflation are published
> with a delay. The model uses the most recent month where all indicators are available.

## Notes

- The model was trained on data from **1968–2008** covering 5 recessions
- Test period covers **2008–2024** (Great Recession + COVID)
- ROC-AUC on test set: **0.979**
- This is a research tool — not financial advice
