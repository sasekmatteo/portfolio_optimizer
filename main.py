import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
os.makedirs("plots", exist_ok=True)
plt.style.use('dark_background')

# Tickers from diverse sectors

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

# Download historical data

batches = [tickers[i:i + 4] for i in range(0, len(tickers), 4)]
all_data = []

for batch in batches:
    batch_data = yf.download(batch, start='2019-01-01', end='2024-12-31', auto_adjust=True)
    close_prices = batch_data['Close'] if isinstance(batch_data.columns, pd.MultiIndex) else pd.DataFrame(batch_data['Close'])
    all_data.append(close_prices)

price_data = pd.concat(all_data, axis=1)
price_data = price_data.ffill().dropna(axis=1, thresh=len(price_data) * 0.95)

returns = price_data.pct_change().dropna()
mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252

# Correlation Heatmap

correlation_matrix = returns.corr()

plt.figure(figsize=(14, 12))
sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap='coolwarm',
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

# Define constraints

constraints = {
    'unconstrained': {'asset_max': 1.00, 'sector_max': 1.00, 'alt_max': 1.00},
    'conservative': {'asset_max': 0.15, 'sector_max': 0.25, 'alt_max': 0.10},
    'aggressive': {'asset_max': 0.25, 'sector_max': 0.35, 'alt_max': 0.20}
}

# Efficient Frontier simulation

num_portfolios = 10000
all_metrics_by_strategy = {}
all_weights_by_strategy = {}
np.random.seed(33)

mean_arr = mean_returns.values
cov_arr = cov_matrix.values
asset_names = price_data.columns.tolist()

for strategy, constraint in constraints.items():
    simulation_metrics = []
    portfolio_weights = []

    for _ in range(num_portfolios):
        valid = False
        attempts = 0

        while not valid and attempts < 1000:
            random_weights = np.random.random(len(asset_names))
            random_weights /= random_weights.sum()
            weights_series = pd.Series(random_weights, index=asset_names)

            if (weights_series > constraint['asset_max']).any():
                attempts += 1
                continue

            sector_weights = {}
            for ticker, weight in weights_series.items():
                sector = sector_map[ticker]
                sector_weights[sector] = sector_weights.get(sector, 0) + weight

            if any(val > constraint['sector_max'] for val in sector_weights.values()):
                attempts += 1
                continue

            if sector_weights.get('Alternatives', 0) > constraint['alt_max']:
                attempts += 1
                continue

            valid = True

        if not valid:
            continue

        expected_return = np.dot(random_weights, mean_arr)
        risk = np.sqrt(np.dot(random_weights.T, np.dot(cov_arr, random_weights)))
        sharpe_ratio = expected_return / risk if risk > 0 else 0

        simulation_metrics.append((expected_return, risk, sharpe_ratio))
        portfolio_weights.append(random_weights)

    strategy_results_df = pd.DataFrame(simulation_metrics, columns=['Return', 'Volatility', 'Sharpe Ratio'])
    portfolio_weights_df = pd.DataFrame(portfolio_weights, columns=asset_names)

    all_metrics_by_strategy[strategy] = strategy_results_df
    all_weights_by_strategy[strategy] = portfolio_weights_df

# Plot Efficient Frontier Comparison

plt.figure(figsize=(12, 8))
colors = {'unconstrained': '#00BFFF', 'conservative': '#8A2BE2', 'aggressive': '#7FFFD4'}

for strategy, metrics_df in all_metrics_by_strategy.items():
    plt.scatter(metrics_df['Volatility'], metrics_df['Return'], alpha=0.3, s=10, label=strategy.capitalize(), color=colors[strategy])
    max_sharpe_idx = metrics_df['Sharpe Ratio'].idxmax()
    max_sharpe_point = metrics_df.loc[max_sharpe_idx]
    plt.scatter(max_sharpe_point['Volatility'], max_sharpe_point['Return'], c=colors[strategy], s=100, edgecolor='white', label=f"{strategy.capitalize()} Max Sharpe")

plt.title("Efficient Frontier Comparison (Unconstrained vs Constrained)")
plt.xlabel("Volatility (Risk)")
plt.ylabel("Expected Return")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("plots/frontier_comparison_dark.png")
plt.show()

# Pie Charts for Sector Allocation

for strategy in constraints:
    optimal_weights = all_weights_by_strategy[strategy].iloc[all_metrics_by_strategy[strategy]['Sharpe Ratio'].idxmax()]
    sector_weights = {}
    for asset, weight in optimal_weights.items():
        sector = sector_map[asset]
        sector_weights[sector] = sector_weights.get(sector, 0) + weight

    # Sort by weight (descending)
    sector_weights = dict(sorted(sector_weights.items(), key=lambda x: x[1], reverse=True))

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
    plt.title(f"{strategy.capitalize()} Portfolio — Sector Allocation", fontsize=16, weight='bold', color='white', pad=20)
    plt.tight_layout()
    plt.savefig(f"plots/{strategy}_sector_pie_dark.png", facecolor='black')
    plt.show()

# Side-by-side bar plot of weights

top_optimal_weights = {strategy: all_weights_by_strategy[strategy].iloc[all_metrics_by_strategy[strategy]['Sharpe Ratio'].idxmax()] for strategy in constraints}
weights_comparison_df = pd.DataFrame(top_optimal_weights)

weights_comparison_df.plot(kind='barh', figsize=(12, 10), color=[colors[col] for col in weights_comparison_df.columns])
plt.title("Optimal Portfolio Weights by Constraint")
plt.xlabel("Weight")
plt.grid(True, axis='x')
plt.tight_layout()
plt.savefig("plots/side_by_side_weights_dark.png")
plt.show()