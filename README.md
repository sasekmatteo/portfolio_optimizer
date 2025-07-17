# Smart Portfolio Optimizer

A Python-based tool for exploring how different portfolio strategies perform based on real historical data. By simulating thousands of possible allocations, it helps visualize the trade-offs between risk and return, and shows how constraints like sector exposure or asset limits impact diversification.


---

## Behind the Project

In professional finance, portfolio optimization isn’t about guessing which stocks will go up, it’s about managing trade-offs between risk, return, and diversification under realistic constraints.

This project was my way of applying that principle on a small scale. I developed a Monte Carlo–based portfolio optimizer that simulates thousands of asset combinations using real historical data, incorporating constraints around individual assets, sector exposure, and alternative investments.

It was also an opportunity to integrate core topics from my university coursework Principles of Finance, Introduction to Data Science, and Statistics: Data Analysis and Probability into a practical tool that not only models portfolio performance, but also clearly visualizes the results and trade-offs involved.

I consider this project as a crucial first step towards better understanding how real investment decisions are made and strengthening my ability to communicate insights through data.

---

## Methodology Overview

This project fetches historical data for 20 diversified assets: tech stocks, energy, healthcare, ETFs, crypto, and more — and runs a **Monte Carlo simulation** to generate 10,000 random portfolios. It calculates:

- **Expected return**
- **Volatility (risk)**
- **Sharpe ratio** (return per unit of risk)

The optimizer models three portfolio strategies, each reflecting a different level of constraint and risk tolerance:

- **Unconstrained:** Pure performance-focused
- **Conservative:** Caps on individual assets and sectors
- **Aggressive:** More flexibility, but still realistic

---

## Key Features

- Real financial data from 2019–2024
- Monte Carlo simulation with thousands of portfolios
- Sector and asset allocation constraints
- Easy-to-read allocation charts (pie + bar)
- Clean, modular Python code ready for extension

---

## Visuals

###  Asset Correlation Heatmap  
Before running any simulations, I started by checking how the selected assets move relative to one another. This correlation heatmap helps assess the level of diversification across the portfolio by showing how closely assets move in relation to one another.

Each square represents the correlation between a pair of assets. A value near 1 (deep red) means they tend to move together, while values near 0 or negative (deep blue) indicate weaker or even opposite relationships. If the chart were mostly red, it would suggest that the assets behave similarly, reducing the benefits of diversification.

In this case, the chart shows a healthy range of correlations. While assets within the same sector (like tech stocks) show stronger relationships, there are plenty of weaker correlations across sectors. This confirms that the portfolio includes a good mix of assets that don't all move in sync, which is essential for managing risk effectively.


![Asset Correlation Heatmap](./plots/asset_correlation_heatmap_dark.png)

---

### Efficient Frontier Comparison
This plot visualizes the results of 10,000 randomly generated portfolios under each strategy: unconstrained, conservative, and aggressive. Each dot represents a portfolio with a specific expected return and volatility, and the larger highlighted points mark the ones with the highest Sharpe ratio within each strategy.

Rather than plotting a theoretical frontier, we simulate real-world portfolios to show how return and risk actually distribute when constraints are applied. The upper boundary of the cloud of points effectively traces the empirical efficient frontier, the limit of performance for a given level of risk.

This plot is especially useful to see how different constraints shift and compress the frontier. For example, the conservative strategy produces safer portfolios, but sacrifices some potential return, while the unconstrained one pushes further into high-risk, high-return territory.

![Efficient Frontier](./plots/frontier_comparison_dark.png)

---

###  Sector Allocation — Unconstrained  
This chart shows the sector composition of the optimal unconstrained portfolio, the one with the highest Sharpe ratio when the optimizer was given complete freedom.

Without any limits on how much can be invested in a single asset, sector, or asset class, the optimizer leans heavily into the sectors that historically performed best. Here, Technology (23.4%), Alternatives (22.9%), and Industrials (18.6%) take the lead, together making up nearly two-thirds of the portfolio. This is a classic example of return-chasing behavior when no real-world constraints are applied.

That said, we still see some natural diversification. Healthcare (14.5%), ETFs (10.6%), and even small allocations to Consumer and Energy remain in the mix. This diversification isn’t imposed by constraints; it naturally emerges from the optimizer’s attempt to maximize the Sharpe ratio. Even in a purely performance-driven setup, allocating across multiple sectors helps reduce risk and smooth out returns.

![Unconstrained Sector Pie](./plots/unconstrained_sector_pie_dark.png)

---

###  Sector Allocation — Conservative  
In the conservative allocation, the optimizer responded to tighter constraints by distributing weight more evenly across sectors. Technology, Industrials, and Consumer sectors remain prominent, but no single area dominates the portfolio. Alternatives are capped below 10%, and sectors like Energy and Healthcare receive modest but meaningful exposure.

This distribution reflects a common institutional mindset, one that favors risk management and avoids over-concentration. It’s the kind of allocation you’d expect from a long-term investor or retirement fund, where preserving capital and ensuring stable growth matter more than chasing maximum returns.

![Conservative Sector Pie](./plots/conservative_sector_pie_dark.png)

---

###  Sector Allocation — Aggressive  
In the aggressive allocation, we gave the optimizer more breathing room, slightly relaxed constraints allow it to chase higher returns while still maintaining basic diversification. The result is a noticeable tilt toward Technology (27.4%) and Alternatives (18.4%), both of which tend to offer greater upside potential but also come with higher volatility.

Industrials hold a strong presence as well, suggesting the optimizer sees value in sectors that blend cyclical growth with relative stability. Meanwhile, lower allocations in Financials and Energy reflect a tactical decision to minimize drag in pursuit of better Sharpe ratios.

This kind of portfolio could appeal to investors with a higher risk tolerance, those aiming for long-term growth, comfortable with drawdowns, and willing to ride out market swings in exchange for better performance.
![Aggressive Sector Pie](./plots/aggressive_sector_pie_dark.png)

---

###  Side-by-Side Portfolio Weights  
This horizontal bar chart compares the individual asset weights across the three strategies: unconstrained, conservative, and aggressive. Each bar shows how much of a given asset makes it into the final optimized portfolio under each set of constraints.

Some clear patterns emerge. For example, BTC-USD and GLD (crypto and gold) receive much higher weights in the unconstrained setup, where maximizing performance takes priority. In contrast, the conservative version distributes weights more evenly, avoiding concentration and adhering to stricter caps.

This visualization helps us analyze how constraint logic affects specific investment decisions. It makes it easy to spot which assets are consistently favored, which get trimmed under risk-aware strategies, and how the optimizer balances high-return opportunities against exposure limits.
![Side by Side Weights](./plots/side_by_side_weights_dark.png)

---

## Tech Stack

- Python (Pandas, NumPy, Matplotlib, Seaborn)
- Yahoo Finance API via `yfinance`
- PyCharm for development

---

## Contact

Feel free to reach out:

[LinkedIn](https://www.linkedin.com/in/matteo-sasek-martins)

[GitHub](https://github.com/sasekmatteo)


## How to Run

Clone the repo and run:

```bash
pip install -r requirements.txt
python main.py