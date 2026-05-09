# Analyzing Early Economic and Financial Indicators for Recession in the U.S.

> **Group 5** — May Sabai, Emily Lu
> 
> **Live Website**: [https://economic-recession-app.uw.r.appspot.com/](https://economic-recession-app.uw.r.appspot.com/)

---

## What Is This Repo?

This repository contains the full end-to-end pipeline for a data science project that detects early warning signs of U.S. recessions using macroeconomic and financial indicators. It covers data collection from public APIs, exploratory data analysis, machine learning model training (Logistic Regression and Random Forest), a real-time ML inference service, and a published website presenting the findings.

---

## Repository Structure

```
Economic-Recession/
├── public/                  # Static assets served by the website
│   ├── code/                # Code files from Google Colab for EDA, ML, and compare similarity 
│   ├── css/                 # Global stylesheet (style.css)
│   ├── images/              # Charts and figures used across all pages
│   └── data/
│       └── predictions.json # Pre-computed model predictions (exported from Colab)
│
├── src/                     # TypeScript source for the Node.js web server
│   └── routes/
│   │   └── index.ts         # All website page routes
│   ├── .gitignore           # src-level gitignore
│   ├── app.ts               # Express app configuration and middleware setup
│   └── server.ts            # Server entry point, starts the HTTP listener
│
├── views/                   # EJS page templates
│   ├── partials/
│   │   ├── header.ejs       # Shared navigation header
│   │   └── footer.ejs       # Shared footer
│   ├── index.ejs            # Home page
│   ├── eda.ejs              # Exploratory Data Analysis page
│   ├── analysis_methods.ejs # Analysis methods and feature engineering page
│   ├── ml_models.ejs        # ML model results and comparison page
│   ├── ml_inference.ejs     # ML inference service page (live recession signal)
│   └── major_findings.ejs   # Key findings and conclusions
│
├── ml-service/              # Python FastAPI inference service (deployed to Cloud Run)
│   ├── main.py              # API endpoints: /health, /debug, /predict
│   ├── requirements.txt     # Python dependencies for the inference service
│   ├── Dockerfile           # Container definition for Cloud Run deployment
│   ├── .gcloudignore        # Files to exclude from Cloud Run build
│   ├── README.md            # ML service setup and deployment instructions
│   ├── model_D.pkl          # Trained Logistic Regression model (not in git)
│   ├── scaler_D.pkl         # Fitted StandardScaler (not in git)
│   └── features_D.pkl       # Feature column names list (not in git)
│
├── .gcloudignore            # Files excluded from App Engine deployment
├── .gitignore               # Excludes .pkl files and .env
├── app.yaml                 # Google App Engine deployment configuration
├── package.json             # Node.js dependencies and npm scripts
├── README.md                # This file
└── tsconfig.json            # TypeScript compiler configuration
```

---

## Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.11+
- Google Cloud CLI `gcloud` (for deployment only)

### Website (Local Development)

```bash
# Clone the repo
git clone https://github.com/your-username/Economic-Recession.git
cd Economic-Recession

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

Visit `http://localhost:8080`

### ML Inference Service (Local Testing)

```bash
cd ml-service

# Create a .env file with your API keys
echo "FRED_API_KEY=your_fred_key_here" > .env
echo "ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here" >> .env

# Install Python dependencies
pip install -r requirements.txt

# Download model files from Google Colab (see ml-service/README.md)
# Place model_D.pkl, scaler_D.pkl, features_D.pkl in ml-service/

# Run the API locally
uvicorn main:app --reload --port 8080
```

Test: `curl http://localhost:8080/predict`

### API Keys Required

| Key | Source | Used For |
|-----|--------|----------|
| `FRED_API_KEY` | https://fred.stlouisfed.org/docs/api/api_key.html | Unemployment, Inflation, Interest Rate data |
| `ALPHA_VANTAGE_KEY` | https://www.alphavantage.co/support/#api-key | S&P 500 monthly data (SPY ETF) |

---

## Full Pipeline

```
1. DATA COLLECTION
   └── Done in Google Colab notebook
       ├── FRED API  → Unemployment (UNRATE), Inflation (FPCPITOTLZGUSA),
       │               Interest Rate (DFF), Oil (DCOILWTICO), Recession label (USREC)
       └── Yahoo Finance (yfinance) → S&P 500 (^GSPC), VIX (^VIX), Gold (^XAU)

2. EXPLORATORY DATA ANALYSIS
   └── In Colab notebook
       ├── Z-score normalization for cross-indicator comparison
       ├── Correlation heatmap
       ├── Time-series line plots (normalized)
       ├── Average indicator trajectory before each recession
       └── Heatmaps of % changes 3/6/12/24 months before recession

3. RECESSION SIMILARITY ANALYSIS
   └── Colab notebook
       ├── Extracts 12-month trend windows for each indicator
       │   leading up to today and each of the 8 historical recessions
       ├── Normalises all series to [0, 1] for cross-indicator comparability
       ├── Metric 1 — Spearman Rank Correlation
       │     Measures whether current and historical series move in the
       │     same direction at the same time.
       ├── Metric 2 — Dynamic Time Warping (DTW)
       │     Measures shape similarity even when one series is slightly
       │     time-shifted. Smaller DTW distance → higher similarity.
       ├── Scores computed for every combination of recession ×
       │   indicator × time window (1M, 2M, 3M, 6M, 1Y, 2Y)
       └── Note: Inflation excluded due to incomplete post-2024 data
      
4. FEATURE ENGINEERING
   └── Colab notebook (build_features function)
       ├── Lag features: 3, 6, 9, 12 months
       ├── Rolling statistics: 3-month mean, 6-month mean, 3-month std
       └── Momentum: 1-month, 3-month, 12-month diff

5. MODEL TRAINING & EVALUATION
   └── Colab notebook
       ├──4 model configurations: A (Macro), B (Financial),
       │    C (Combined), D (Macro + SP500)
       ├── Time-based train/test split
       ├── StandardScaler fitted on training data only
       ├── Train Logistic Regression 
       └── Train Random Forest

6. MODEL EXPORT
   └── Colab → joblib.dump()
       ├── model_D.pkl   (best model: Logistic Regression, Model D (Macro + SP500))
       ├── scaler_D.pkl
       └── features_D.pkl

7. INFERENCE SERVICE DEPLOYMENT
   └── ml-service/ → Google Cloud Run
       ├── FastAPI wraps the saved model
       ├── Fetches live data from FRED + Alpha Vantage at request time
       └── Returns current month recession probability via /predict

8. WEBSITE DEPLOYMENT
   └── Economic-Recession/ → Google App Engine
       ├── Node.js + Express + EJS renders all pages
       └── /ml-inference route calls Cloud Run API client-side
       
```

---

## Key Processing Code

| File | Purpose |
|------|---------|
|`public/code/EDA.ipynb`| Contains the full exploratory data analysis (EDA) workflow, including data cleaning, statistical summaries, and visualization plots.|
|`public/code/Recessopm Similarity Analysis.ipynb`|Implements recession similarity analysis using Spearman Rank Correlation and Dynamic Time Warping (DTW) techniques.|
| `public/code/ML_Logistic_Regression_and_Random_Forest.ipynb` | Include data collection from FRED and Yahoo Finance APIs, feature engineering, model training, and model export to `.pkl` files and `predictions.json` |
| `ml-service/main.py` | Performs live inference by fetching real-time market and economic data, generating features, and runs model to produce predictions|
| `src/routes/index.ts` | Website routing; `/ml-inference` renders the live signal page |

---

## System Design

```
          User Browser
                │ HTTPS
                ▼
          Google App Engine (Node.js / Express)
          - Hosts website and routes
          - Serves static assets (CSS, images, predictions.json)
          - Renders live inference dashboard
                │
                │ API request
                ▼
          Google Cloud Run (FastAPI)
          - `/predict` endpoint
          - Fetches live economic and market data
          - Performs feature engineering
          - Runs trained ML models
                │
                ├── FRED API (macroeconomic indicators)
                └── Alpha Vantage API (S&P 500 market data)
```

### Scalability Discussion

**Website (App Engine):** Google App Engine automatically scales the Node.js server horizontally based on traffic. Most assets are served statically, minimizing backend computation and reducing latency.

**Inference Service (Cloud Run):** Google Cloud Run provides serverless autoscaling for the FastAPI inference service. Since predictions are stateless, multiple instances can run concurrently without shared coordination.

**Potential Bottleneck:** The current design makes a live API call to FRED and Alpha Vantage on every `/predict` request. Under high traffic, this could hit third-party rate limits. The mitigation would be to cache the prediction result for the current month (since FRED data only updates monthly), which would reduce external API calls to at most once per month per indicator.

---

## Inference Service

The ML inference service is a **FastAPI application** deployed on **Google Cloud Run** that provides real-time recession probability predictions.

**Location of Key Code**
| File | Purpose |
|------|---------|
| `ml-service/main.py` | FastAPI application: data fetching, feature engineering, model inference |
| `ml-service/Dockerfile` | Docker container definition for base image, dependency installation, startup command |
| `ml-service/.gcloudignore` | Files excluded from the Cloud Run build context |
| `ml-service/requirements.txt` | Python dependencies installed inside the Docker container |
| `public/code/ML_Logistic_Regression_and_Random_Forest.ipynb` (Section 6) | Model training code: fits Logistic Regression on historical data |
| `public/code/ML_Logistic_Regression_and_Random_Forest.ipynb` (Section 10) | Model export: saves `model_D.pkl`, `scaler_D.pkl`, `features_D.pkl` via `joblib` |

**Docker**
The service is containerised using Docker. The `Dockerfile` in `ml-service/` defines:
1. Base image: `python:3.11-slim`
2. Copies `requirements.txt` and installs all Python dependencies
3. Copies the three `.pkl` model artifact files into the container
4. Copies `main.py`
5. Starts the FastAPI server via `uvicorn` on port 8080

The built image is stored in **Google Artifact Registry** and pulled by Cloud Run on each deployment. The `.pkl` files are baked into the image at deploy time, they are not fetched at runtime.

**How it works:**
1. Fetches the last ~40 months of data from FRED (Unemployment, Inflation, Interest Rate) and Alpha Vantage (S&P 500 via SPY ETF)
2. Resamples all series to monthly frequency and aligns them on a shared index
3. Applies forward-fill for inflation (published annually) and drops incomplete months
4. Builds 44 derived features (lags, rolling statistics, momentum) using the same `build_features()` logic as training
5. Applies the saved `StandardScaler` to normalize features
6. Runs the saved Logistic Regression Model D and returns the probability

**Example response:**
```json
{
  "month": "2026-03",
  "recession_prob": 0.0004,
  "recession_predict": false,
  "signal": "LOW"
}
```

**Note on data lag:** The predicted month is typically 1–2 months behind the current date. This is expected because of FRED economic indicators are published with a delay. The service uses the most recent month for which all four indicators are available.

**Note on S&P 500 source:** `yfinance` is blocked by Yahoo Finance's servers in cloud environments. Alpha Vantage is used instead. SPY (S&P 500 ETF) closely tracks the ^GSPC index used during training.

---

## Data Stored in the Cloud

### Google App Engine (Website Hosting)

The Node.js website is deployed on Google App Engine (Standard Environment). App Engine stores and serves the application code and all static assets including:

- `public/data/predictions.json` — pre-computed recession probability curves for all 4 models across the 2008–2024 test period, exported from the Colab notebook and committed to the repo
- `public/images/` — all EDA, similarity comparison, and ML result charts generated in Colab and saved as PNG files
- `public/css/style.css` — global stylesheet

These files are static, they do not change unless a new version is deployed.

### Google Cloud Run (Inference Service)

The ML inference service container stores:

- `model_D.pkl` — the trained Logistic Regression model (baked into the container image at deploy time)
- `scaler_D.pkl` — the fitted StandardScaler
- `features_D.pkl` — the list of 44 feature column names

These files are embedded in the Docker container image stored in **Google Artifact Registry**, which Cloud Run pulls from on each deployment. They are not stored in a database since they are part of the container image itself.

### What Is NOT Stored

There is no persistent database in this project. All indicator data (unemployment, inflation, interest rates, S&P 500) is fetched live from FRED and Alpha Vantage APIs at prediction time. This keeps the architecture stateless and eliminates the need for database maintenance.

---

## Website

**[https://economic-recession.uc.r.appspot.com](https://economic-recession-app.uw.r.appspot.com/)**

| Page | Description |
|------|-------------|
| Home | Project summary, data sources, recession timeline |
| EDA | Exploratory data analysis with visualizations |
| Analysis Methods | Similarity comparison methodology |
| ML Models | Model results, confusion matrices, probability charts |
| ML Inference | Live recession signal|
| Major Findings | Key conclusions and takeaways |
