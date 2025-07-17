import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
os.makedirs("plots", exist_ok=True)
plt.style.use('dark_background')

# --- Tickers from diverse sectors ---
tickers = [
    'AAPL', 'MSFT', 'GOOGL', 'NVDA',
    'XOM', 'CVX', 'KO', 'PG',
    'JNJ', 'PFE', 'JPM', 'V',
    'MA', 'CAT', 'GE', 'SPY',
    'QQQ', 'VTI', 'GLD', 'BTC-USD'
]

sector_map = {
    'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'NVDA': 'Technology',
    'XOM': 'Energy', 'CVX': 'Energy',
    'KO': 'Consumer', 'PG': 'Consumer',
    'JNJ': 'Healthcare', 'PFE': 'Healthcare',
    'JPM': 'Financials', 'V': 'Financials',
    'MA': 'Industrials', 'CAT': 'Industrials', 'GE': 'Industrials',
    'SPY': 'ETF', 'QQQ': 'ETF', 'VTI': 'ETF',
    'GLD': 'Alternatives', 'BTC-USD': 'Alternatives'
}

# --- Download historical data ---
batches = [tickers[i:i + 4] for i in range(0, len(tickers), 4)]
all_data = []

for batch in batches:
    df = yf.download(batch, start='2019-01-01', end='2024-12-31', auto_adjust=True)
    close_prices = df['Close'] if isinstance(df.columns, pd.MultiIndex) else pd.DataFrame(df['Close'])
    all_data.append(close_prices)

data = pd.concat(all_data, axis=1)
data = data.ffill().dropna(axis=1, thresh=len(data) * 0.95)

returns = data.pct_change().dropna()
mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252

# --- Correlation Heatmap ---
correlation_matrix = returns.corr()

plt.figure(figsize=(14, 12))
sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap='coolwarm',  # diverging: blue = low correlation, red = high
    fmt=".2f",
    linewidths=0.5,
    square=True,
    cbar_kws={'label': 'Correlation'},
    annot_kws={"size": 9}
)
plt.title("Asset Correlation Heatmap (Daily Returns)", fontsize=16, color='white', pad=15)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig("plots/asset_correlation_heatmap_dark.png", facecolor='black')
plt.show()


# --- Define constraints ---
constraints = {
    'unconstrained': {'asset_max': 1.00, 'sector_max': 1.00, 'alt_max': 1.00},
    'conservative': {'asset_max': 0.15, 'sector_max': 0.25, 'alt_max': 0.10},
    'aggressive': {'asset_max': 0.25, 'sector_max': 0.35, 'alt_max': 0.20}
}

# --- Efficient Frontier simulation ---
num_portfolios = 10000
results_all = {}
weights_all = {}
np.random.seed(33)

mean_arr = mean_returns.values
cov_arr = cov_matrix.values
asset_names = data.columns.tolist()

for label, limit in constraints.items():
    results = []
    weights_record = []

    for _ in range(num_portfolios):
        valid = False
        attempts = 0

        while not valid and attempts < 1000:
            w = np.random.random(len(asset_names))
            w /= w.sum()
            w_series = pd.Series(w, index=asset_names)

            if (w_series > limit['asset_max']).any():
                attempts += 1
                continue

            sector_w = {}
            for ticker, weight in w_series.items():
                sector = sector_map[ticker]
                sector_w[sector] = sector_w.get(sector, 0) + weight

            if any(val > limit['sector_max'] for val in sector_w.values()):
                attempts += 1
                continue

            if sector_w.get('Alternatives', 0) > limit['alt_max']:
                attempts += 1
                continue

            valid = True

        if not valid:
            continue

        port_return = np.dot(w, mean_arr)
        port_vol = np.sqrt(np.dot(w.T, np.dot(cov_arr, w)))
        sharpe = port_return / port_vol

        results.append((port_return, port_vol, sharpe))
        weights_record.append(w)

    df = pd.DataFrame(results, columns=['Return', 'Volatility', 'Sharpe Ratio'])
    w_df = pd.DataFrame(weights_record, columns=asset_names)

    results_all[label] = df
    weights_all[label] = w_df

# --- Plot Efficient Frontier Comparison ---
plt.figure(figsize=(12, 8))
colors = {'unconstrained': '#00BFFF', 'conservative': '#8A2BE2', 'aggressive': '#7FFFD4'}

for label, df in results_all.items():
    plt.scatter(df['Volatility'], df['Return'], alpha=0.3, s=10, label=label.capitalize(), color=colors[label])
    max_idx = df['Sharpe Ratio'].idxmax()
    opt = df.loc[max_idx]
    plt.scatter(opt['Volatility'], opt['Return'], c=colors[label], s=100, edgecolor='white', label=f"{label.capitalize()} Max Sharpe")

plt.title("Efficient Frontier Comparison (Unconstrained vs Constrained)")
plt.xlabel("Volatility (Risk)")
plt.ylabel("Expected Return")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("plots/frontier_comparison_dark.png")
plt.show()


# --- Pie Charts for Sector Allocation ---
for label in constraints:
    opt_w = weights_all[label].iloc[results_all[label]['Sharpe Ratio'].idxmax()]
    sector_weights = {}
    for asset, weight in opt_w.items():
        sector = sector_map[asset]
        sector_weights[sector] = sector_weights.get(sector, 0) + weight

    plt.figure(figsize=(9, 9))
    color_palette = plt.cm.cool(np.linspace(0.2, 0.9, len(sector_weights)))
    wedges, texts, autotexts = plt.pie(
        sector_weights.values(),
        labels=sector_weights.keys(),
        autopct='%1.1f%%',
        startangle=140,
        colors=color_palette,
        textprops={'color': 'white', 'fontsize': 12},
        wedgeprops={'linewidth': 1, 'edgecolor': 'black'}
    )

    plt.setp(autotexts, size=12, weight="bold")
    plt.title(f"{label.capitalize()} Portfolio — Sector Allocation", fontsize=16, weight='bold', color='white', pad=20)
    plt.tight_layout()
    plt.savefig(f"plots/{label}_sector_pie_dark.png", facecolor='black')
    plt.show()


# --- Side-by-side bar plot of weights ---
top_weights = {label: weights_all[label].iloc[results_all[label]['Sharpe Ratio'].idxmax()] for label in constraints}
weights_df = pd.DataFrame(top_weights)

weights_df.plot(kind='barh', figsize=(12, 10), color=[colors[col] for col in weights_df.columns])
plt.title("Optimal Portfolio Weights by Constraint")
plt.xlabel("Weight")
plt.grid(True, axis='x')
plt.tight_layout()
plt.savefig("plots/side_by_side_weights_dark.png")
plt.show()