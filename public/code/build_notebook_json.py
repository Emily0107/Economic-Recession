import json

def markdown_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    }

# 1. Imports and Setup
setup_code = """# Install necessary libraries if not present
# !pip install yfinance fredapi scikit-learn plotly

import yfinance as yf
import pandas as pd
from fredapi import Fred
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import math
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler

# Define Global Colors for consistent plotting
COLOR_MAP = {
    'Unemployment': 'blue',
    'Inflation': 'red',
    'Interest': 'green',
    'SP500': 'orange',
    'Oil': 'black',
    'VIX': 'purple',
    'Gold': 'gold'
}

# API key from FRED to extract data
fred = Fred(api_key="65796ccf4eea28ff944ebb1cf7ea91de")"""

# 2. Data Loading
data_loading_code = """# Load data from FRED
unemployment = fred.get_series("UNRATE").to_frame(name="Unemployment")
inflation = fred.get_series("FPCPITOTLZGUSA").to_frame(name="Inflation")
interest = fred.get_series("DFF").to_frame(name="Interest")
oil = fred.get_series("DCOILWTICO").to_frame(name="Oil")

# Load data starting from 1968
unemployment = unemployment[unemployment.index >= "1968-01-01"]
inflation = inflation[inflation.index >= "1968-01-01"]
interest = interest[interest.index >= "1968-01-01"]

# Load data from Yahoo Finance
sp500 = yf.download("^GSPC", start="1968-01-01")['Close']
vix = yf.download("^VIX", start="1990-01-01")['Close']
gold = yf.download("^XAU", start="1990-01-01")['Close']"""

# 3. Resampling
resampling_code = """# Convert all data into monthly for consistency
unemployment_monthly = unemployment.resample("ME").last()
inflation_monthly = inflation.resample("ME").ffill()
interest_monthly = interest.resample("ME").last()
oil_monthly = oil.resample("ME").last()
sp500_monthly = sp500.resample("ME").last()
vix_monthly = vix.resample("ME").last()
gold_monthly = gold.resample("ME").last()

# Load recession indicator
recession = fred.get_series("USREC").to_frame(name="Recession")
recession = recession[recession.index >= "1968-01-01"]
recession = recession.resample("ME").last()"""

# 4. Dataframes 1968 & 1990
df_creation_code = """# ── Create df_1968 ───────────────────────────────────────────
df_1968 = pd.concat([
    unemployment_monthly,
    inflation_monthly,
    interest_monthly,
    sp500_monthly.to_frame(name="SP500")
], axis=1).merge(recession, left_index=True, right_index=True, how="left").dropna()

# ── Create df_1990 ───────────────────────────────────────────
df_1990 = pd.concat([
    oil_monthly,
    vix_monthly.to_frame(name="VIX"),
    gold_monthly.to_frame(name="Gold")
], axis=1).merge(recession, left_index=True, right_index=True, how="left")
# restrict to 1988 onward for proper 24m lookbacks
df_1990 = df_1990.loc["1988":].dropna()"""

# 5. Line Graph 1968
graph_1968_code = """# ── Normalize df_1968 for plotting ───────────────────────────────────────────
scaled_1968 = df_1968.copy()
indicators_1968 = ["Unemployment", "Inflation", "Interest", "SP500"]

for col in indicators_1968:
    col_min = scaled_1968[col].min()
    col_max = scaled_1968[col].max()
    scaled_1968[col] = (scaled_1968[col] - col_min) / (col_max - col_min)

# ── Line graph comparison ─────────────────────────────────────────────────────
plt.figure(figsize=(14, 8))

for col in indicators_1968:
    plt.plot(scaled_1968.index, scaled_1968[col], label=col, color=COLOR_MAP.get(col, 'blue'))

# Highlight recession periods
start = None
for date in scaled_1968.index:
    if scaled_1968.loc[date, "Recession"] == 1 and start is None:
        start = date
    elif scaled_1968.loc[date, "Recession"] == 0 and start is not None:
        plt.axvspan(start, date, alpha=0.15, color='gray')
        start = None

if start is not None:
    plt.axvspan(start, scaled_1968.index[-1], alpha=0.15, color='gray')

plt.axhline(0.5, linestyle="--", color='black')  # midpoint line at 0.5 for normalized data

plt.legend(fontsize=10)
plt.title("Normalized Unemployment, Inflation, Interest and SP500 Indicators with Recession Periods Highlighted", fontsize=14)
plt.xlabel("Date")
plt.ylabel("Normalized Value [0–1]")
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("line_graph_1968.png")
plt.show()"""

# 6. Line Graph 1990
graph_1990_code = """# ── Normalize df_1990 for plotting ───────────────────────────────────────────
scaled_1990 = df_1990.copy()
indicators_1990 = ["Oil", "VIX", "Gold"]

for col in indicators_1990:
    col_min = scaled_1990[col].min()
    col_max = scaled_1990[col].max()
    scaled_1990[col] = (scaled_1990[col] - col_min) / (col_max - col_min)

# ── Line graph comparison ─────────────────────────────────────────────────────
plt.figure(figsize=(14, 8))

for col in indicators_1990:
    plt.plot(scaled_1990.index, scaled_1990[col], label=col, color=COLOR_MAP.get(col, 'black'))

# Highlight recession periods
start = None
for date in scaled_1990.index:
    if scaled_1990.loc[date, "Recession"] == 1 and start is None:
        start = date
    elif scaled_1990.loc[date, "Recession"] == 0 and start is not None:
        plt.axvspan(start, date, alpha=0.15, color='gray')
        start = None

if start is not None:
    plt.axvspan(start, scaled_1990.index[-1], alpha=0.15, color='gray')

plt.axhline(0.5, linestyle="--", color='black')  # midpoint line at 0.5 for normalized data

plt.legend(fontsize=10)
plt.title("Normalized Oil, VIX and Gold Indicators with Recession Periods Highlighted", fontsize=14)
plt.xlabel("Date")
plt.ylabel("Normalized Value [0–1]")
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("line_graph_1990.png")
plt.show()"""

# 7. Zoom Functions
zoom_func_code = """def get_recession_periods(df, recession_col='Recession'):
    periods = []
    start = None
    for date in df.index:
        if df.loc[date, recession_col] == 1 and start is None:
            start = date
        elif df.loc[date, recession_col] == 0 and start is not None:
            periods.append((start, date))
            start = None
    if start is not None:
        periods.append((start, df.index[-1]))
    return periods

def plot_zoom_before_recessions(df, indicator_cols, filename, recession_col='Recession', months_before=24):
    periods = get_recession_periods(df, recession_col)
    
    # Exclude 2020 recession for 1968 group in original notebook, but here we can just plot all if not specified.
    # We will plot up to 6 recessions to fit nicely in a 3x2 grid.
    if len(periods) > 6:
        periods = periods[-6:]
        
    n_recessions = len(periods)
    cols_grid = 2
    rows_grid = math.ceil(n_recessions / cols_grid)
    
    fig, axes = plt.subplots(rows_grid, cols_grid, figsize=(15, 4*rows_grid))
    if n_recessions == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
        
    for i, (start_date, end_date) in enumerate(periods):
        ax = axes[i]
        
        start_idx = df.index.get_indexer([start_date], method='bfill')[0]
        window_start_idx = max(0, start_idx - months_before)
        window_start_date = df.index[window_start_idx]
        
        plot_df = df.loc[window_start_date:end_date]
        
        for col in indicator_cols:
            ax.plot(plot_df.index, plot_df[col], label=col, color=COLOR_MAP.get(col, 'blue'))
            
        ax.axvspan(start_date, end_date, color='gray', alpha=0.2)
        ax.axvline(start_date, color='red', linestyle='--', label='Recession Start')
        ax.set_title(f"Recession starting {start_date.strftime('%Y-%m')}")
        ax.legend()
        
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
        
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

# ── Generate Zoom-In Views ───────────────────────────────────────────────────
# For 1968 group
plot_zoom_before_recessions(df_1968, ["Unemployment", "Inflation", "Interest", "SP500"], "close_up_view_1968.png")

# For 1990 group
plot_zoom_before_recessions(df_1990, ["Oil", "VIX", "Gold"], "close_up_view_1990.png")"""

# 8. Trajectory function
traj_func_code = """def indicator_trajectory(df, indicators, recession_col="Recession", months_before=24):
    recession_starts = []
    for i in range(1, len(df)):
        if df[recession_col].iloc[i] == 1 and df[recession_col].iloc[i-1] == 0:
            recession_starts.append(df.index[i])
            
    trajectories = {col: [] for col in indicators}
    
    for start_date in recession_starts:
        start_idx = df.index.get_indexer([start_date], method='bfill')[0]
        if start_idx >= months_before:
            window = df.iloc[start_idx - months_before : start_idx + 1]
            for col in indicators:
                trajectories[col].append(window[col].values)
                
    avg_trajectories = {}
    for col in indicators:
        avg_trajectories[col] = np.mean(trajectories[col], axis=0)
        
    time_index = np.arange(-months_before, 1)
    traj_df = pd.DataFrame(avg_trajectories, index=time_index)
    return traj_df"""

# 9. Trajectory 1968 Interactive
traj_1968_interact = """# ── Trajectory 1968 ───────────────────────────────────────────
scaled_1968 = df_1968.loc["1968":].copy()
scaler_1968 = StandardScaler()
indicators_1968 = ["Unemployment", "Inflation", "Interest", "SP500"]
scaled_1968[indicators_1968] = scaler_1968.fit_transform(scaled_1968[indicators_1968])

traj_1968 = indicator_trajectory(
    scaled_1968,
    indicators=indicators_1968,
    months_before=24
)

fig_1968 = go.Figure()

for col in traj_1968.columns:
    fig_1968.add_trace(go.Scatter(
        x=traj_1968.index,
        y=traj_1968[col],
        mode="lines",
        name=col,
        line=dict(color=COLOR_MAP.get(col, 'blue')),
        hovertemplate=f"<b>{col}</b><br>Month: %{{x}}<br>Z-score: %{{y:.2f}}<extra></extra>"
    ))

fig_1968.add_vline(
    x=0,
    line_dash="dash",
    line_color="black",
    annotation_text="Recession Start",
    annotation_position="top right"
)

fig_1968.update_layout(
    title="Average Indicator Trajectory Before Recession — Unemployment, Inflation, Interest, SP500 (1968–)",
    xaxis_title="Months Before Recession",
    yaxis_title="Standardized Value (Z-score)",
    hovermode="closest",
    legend_title="Indicator",
    template="plotly_white"
)

fig_1968.write_html("economic_chart_1968.html", include_plotlyjs="cdn", full_html=True)
fig_1968.show()"""

# 10. Trajectory 1968 Static
traj_1968_static = """# ── Trajectory 1968 (Static Graph) ───────────────────────────────────────────
plt.figure(figsize=(10, 6))

for col in traj_1968.columns:
    plt.plot(traj_1968.index, traj_1968[col], label=col, color=COLOR_MAP.get(col, 'blue'), linewidth=2)

plt.axvline(x=0, linestyle="--", color="black", label="Recession Start")

plt.title("Average Indicator Trajectory Before Recession — Unemployment, Inflation, Interest, SP500 (1968–)")
plt.xlabel("Months Before Recession")
plt.ylabel("Standardized Value (Z-score)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.7)

plt.tight_layout()
plt.savefig("average_line_graph_economic_indicator.png")
plt.show()"""


# 11. Trajectory 1990 Interactive
traj_1990_interact = """# ── Trajectory 1990 ───────────────────────────────────────────
scaled_1990 = df_1990.loc["1988":].copy()
scaler_1990 = StandardScaler()
# ensure SP500 is in df_1990 or drop it here
if "SP500" not in df_1990.columns:
    df_1990 = pd.concat([df_1990, sp500_monthly.to_frame("SP500")], axis=1).dropna()
    scaled_1990 = df_1990.loc["1988":].copy()

indicators_1990 = ["VIX", "Gold", "Oil"] # sticking to the 3 main ones
scaled_1990[indicators_1990] = scaler_1990.fit_transform(scaled_1990[indicators_1990])

traj_1990 = indicator_trajectory(
    scaled_1990,
    indicators=indicators_1990,
    months_before=24
)

fig_1990 = go.Figure()

for col in traj_1990.columns:
    fig_1990.add_trace(go.Scatter(
        x=traj_1990.index,
        y=traj_1990[col],
        mode="lines",
        name=col,
        line=dict(color=COLOR_MAP.get(col, 'black')),
        hovertemplate=f"<b>{col}</b><br>Month: %{{x}}<br>Z-score: %{{y:.2f}}<extra></extra>"
    ))

fig_1990.add_vline(
    x=0,
    line_dash="dash",
    line_color="black",
    annotation_text="Recession Start",
    annotation_position="top right"
)

fig_1990.update_layout(
    title="Average Indicator Trajectory Before Recession (Standardized)",
    xaxis_title="Months Before Recession",
    yaxis_title="Standardized Value (Z-score)",
    hovermode="closest",
    legend_title="Indicator",
    template="plotly_white"
)

fig_1990.write_html("financial_chart.html", include_plotlyjs="cdn", full_html=True)
fig_1990.show()"""

# 12. Trajectory 1990 Static
traj_1990_static = """# ── Trajectory 1990 (Static Graph) ───────────────────────────────────────────
plt.figure(figsize=(10, 6))

for col in traj_1990.columns:
    plt.plot(traj_1990.index, traj_1990[col], label=col, color=COLOR_MAP.get(col, 'black'), linewidth=2)

plt.axvline(x=0, linestyle="--", color="black", label="Recession Start")

plt.title("Average Indicator Trajectory Before Recession (Standardized)")
plt.xlabel("Months Before Recession")
plt.ylabel("Standardized Value (Z-score)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.7)

plt.tight_layout()
plt.savefig("average_line_graph_financial_indicator.png")
plt.show()"""

# 13. Individual changes function + 1968 plots
indiv_change_code = """def compute_recession_change(df, indicators, recession_col="Recession", months_before=24):
    recession_starts = []
    for i in range(1, len(df)):
        if df[recession_col].iloc[i] == 1 and df[recession_col].iloc[i-1] == 0:
            recession_starts.append(df.index[i])
            
    changes = {col: [] for col in indicators}
    
    for start_date in recession_starts:
        start_idx = df.index.get_indexer([start_date], method='bfill')[0]
        if start_idx >= months_before:
            val_before = df.iloc[start_idx - months_before][indicators].values
            val_start = df.iloc[start_idx][indicators].values
            # calculate percentage change
            pct_change = (val_start - val_before) / np.abs(val_before) * 100
            for j, col in enumerate(indicators):
                changes[col].append(pct_change[j])
                
    return pd.DataFrame(changes, index=[date.strftime('%Y-%m') for date in recession_starts])

# Calculate for 1968
windows = [1, 3, 6, 12, 24]
heatmaps_1968 = {}

for w in windows:
    heatmaps_1968[w] = compute_recession_change(df_1968, ["Unemployment", "Inflation", "Interest", "SP500"], months_before=w)

# Plot Heatmap 1968
fig, axes = plt.subplots(3, 2, figsize=(14, 10))
axes = axes.flatten()

for i, w in enumerate(windows):
    sns.heatmap(heatmaps_1968[w].T, annot=True, cmap="RdBu_r", center=0, ax=axes[i], fmt=".1f")
    axes[i].set_title(f"{w}-Month Change Before Recession")
fig.delaxes(axes[-1])
plt.tight_layout()
plt.savefig("indicators_changes_heatmap_1970.png")
plt.show()

# Plot Bubble 1968
fig, axes = plt.subplots(3, 2, figsize=(14, 12))
axes = axes.flatten()

for i, w in enumerate(windows):
    ax = axes[i]
    df_w = heatmaps_1968[w]
    
    for j, col in enumerate(df_w.columns):
        x = range(len(df_w.index))
        y = [j] * len(df_w.index)
        sizes = np.abs(df_w[col]) * 20
        colors = ['green' if val > 0 else 'red' for val in df_w[col]]
        
        ax.scatter(x, y, s=sizes, c=colors, alpha=0.6, edgecolors='black')
        
    ax.set_yticks(range(len(df_w.columns)))
    ax.set_yticklabels(df_w.columns)
    ax.set_xticks(range(len(df_w.index)))
    ax.set_xticklabels(df_w.index, rotation=45)
    ax.set_title(f"{w}-Month Change Bubble Plot")
fig.delaxes(axes[-1])
plt.tight_layout()
plt.savefig("indicator_changes_bubble_1970.png")
plt.show()"""

# 14. 1990 individual changes
indiv_change_1990_code = """# Calculate for 1990
heatmaps_1990 = {}

# Make sure df_1990 has SP500 for this analysis as per some requests, or just stick to df_1990
df_1990_combined = df_1990.copy()
if "SP500" not in df_1990_combined.columns:
    df_1990_combined = pd.concat([df_1990_combined, sp500_monthly.to_frame("SP500")], axis=1).dropna()

for w in windows:
    heatmaps_1990[w] = compute_recession_change(df_1990_combined, ["SP500", "VIX", "Gold", "Oil"], months_before=w)

# Plot Heatmap 1990
fig, axes = plt.subplots(3, 2, figsize=(14, 10))
axes = axes.flatten()

for i, w in enumerate(windows):
    sns.heatmap(heatmaps_1990[w].T, annot=True, cmap="RdBu_r", center=0, ax=axes[i], fmt=".1f")
    axes[i].set_title(f"{w}-Month Change Before Recession")
fig.delaxes(axes[-1])
plt.tight_layout()
plt.savefig("indicator_changes_heatmap_1990.png")
plt.show()

# Plot Bubble 1990
fig, axes = plt.subplots(3, 2, figsize=(14, 12))
axes = axes.flatten()

for i, w in enumerate(windows):
    ax = axes[i]
    df_w = heatmaps_1990[w]
    
    for j, col in enumerate(df_w.columns):
        x = range(len(df_w.index))
        y = [j] * len(df_w.index)
        sizes = np.abs(df_w[col]) * 20
        colors = ['green' if val > 0 else 'red' for val in df_w[col]]
        
        ax.scatter(x, y, s=sizes, c=colors, alpha=0.6, edgecolors='black')
        
    ax.set_yticks(range(len(df_w.columns)))
    ax.set_yticklabels(df_w.columns)
    ax.set_xticks(range(len(df_w.index)))
    ax.set_xticklabels(df_w.index, rotation=45)
    ax.set_title(f"{w}-Month Change Bubble Plot")
fig.delaxes(axes[-1])
plt.tight_layout()
plt.savefig("indicator_change_bubble_1990.png")
plt.show()"""

# 15. Correlation Map
corr_code = """# ── Correlation Map for All Indicators ───────────────────────────────────────────
combined_df = pd.concat([
    df_1968[["Unemployment", "Inflation", "Interest", "SP500"]],
    df_1990[["VIX", "Gold", "Oil"]]
], axis=1).dropna()

combined_corr = combined_df.corr()

plt.figure(figsize=(8, 6))
sns.heatmap(combined_corr, annot=True, cmap="coolwarm", center=0, fmt=".2f")
plt.title("Correlation Heatmap of Economic and Financial Indicators")
plt.tight_layout()
plt.savefig("correlation-of-financial-economic-indicator.png")
plt.show()"""

notebook = {
    "cells": [
        markdown_cell("# Exploratory Data Analysis"),
        code_cell(setup_code),
        markdown_cell("## 1. Data Loading"),
        code_cell(data_loading_code),
        code_cell(resampling_code),
        code_cell(df_creation_code),
        markdown_cell("## 2. Overall Normalized Trends (Line Graphs)"),
        code_cell(graph_1968_code),
        code_cell(graph_1990_code),
        markdown_cell("## 3. Zoom-In View (24 months before recessions)"),
        code_cell(zoom_func_code),
        markdown_cell("## 4. Average Indicator Trajectory Before Recession"),
        code_cell(traj_func_code),
        code_cell(traj_1968_interact),
        code_cell(traj_1968_static),
        code_cell(traj_1990_interact),
        code_cell(traj_1990_static),
        markdown_cell("## 5. Individual Indicator Changes Before Recession"),
        code_cell(indiv_change_code),
        code_cell(indiv_change_1990_code),
        markdown_cell("## 6. Correlation between Indicators"),
        code_cell(corr_code)
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open("EDA.ipynb", "w") as f:
    json.dump(notebook, f, indent=2)

print("Successfully generated EDA.ipynb")
