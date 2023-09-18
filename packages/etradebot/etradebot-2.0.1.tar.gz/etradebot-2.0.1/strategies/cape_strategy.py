import pandas as pd
import model.investor_views as views
from model.model import Model
from api.api import DataAPI


def get_cape_forecast(filepath, min_long_return=0.15, max_short_return=0.0):
    """
    :description: Get equity ETF data and filter ETFs by expected return

    :param filepath: Filepath to cape forecasts
    :type filepath: str, required
    :param min_long_return: Minimum required long return, default is 0.15
    :type min_long_return: float, optional
    :param max_short_return: Maximum tolerable short return, default is 0.0
    :type max_short_return: float, optional
    :return: Selected equity ETFs
    :rtype: pd.DataFrame
    """
    equity_etf_csv = pd.read_csv(r'{}'.format(filepath))

    df = equity_etf_csv[
        (equity_etf_csv['FWD_RETURN_FORECAST'] >= min_long_return) |
        (equity_etf_csv['FWD_RETURN_FORECAST'] <= max_short_return)
        ]

    return df


def strategy():
    """
    :description: Strategy to be run by the backtester

    :return: Portfolio weights
    :rtype: pd.Series
    """
    etf_path = 'C:/Code/Python/cape/data/etf_cape_return_forecast.csv'
    selected_equity_etfs = get_cape_forecast(etf_path)
    symbols = list(selected_equity_etfs.TICKER)

    bounds_df = pd.read_csv('../data/bounds.csv')
    bounds = []

    for ticker in symbols:
        if ticker in bounds_df['TICKER'].values:
            min_bound = bounds_df.loc[bounds_df['TICKER'] == ticker, 'MIN'].values[0]
            max_bound = bounds_df.loc[bounds_df['TICKER'] == ticker, 'MAX'].values[0]
            bounds.append((min_bound, max_bound))
        else:
            bounds.append((-0.30, 1.00))  # default bounds if ticker not in bounds.csv

    api = DataAPI(
        symbols,
        num_years=100,  # years
        period='max',  # '1d', '5d', '7d', '60d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
        api_source='bloomberg',  # yahoo or bloomberg
    )

    model = Model(
        symbols,
        bounds=bounds,  # percent
        gamma=0.0,  # decimal
        min_weight=0.05,  # percent
        margin_rate=0.132,  # percent
        long_weight=1.3,  # percent
        short_weight=0.3,  # percent, must be positive
        frequency=252,  # periods per year
    )

    historical_prices = api.get_historical_prices()
    risk_free_rate = api.get_risk_free_rate(prints=True)
    market_caps = api.get_market_caps(prints=True)

    vif_symbols = model.vif_filter(historical_prices, market_caps, threshold=50, prints=True)
    investor_views, confidences = views.investor_views_confidences(selected_equity_etfs, vif_symbols, prints=True)

    market_symbol, market_name, market_prices = api.get_market_prices(historical_prices, symbols, prints=True)
    market_implied_risk_aversion = model.market_implied_risk_aversion(market_prices, risk_free_rate, prints=False)
    covariance_matrix = model.calculate_covariance_matrix(historical_prices, symbols, prints=False)
    posterior_covariance_matrix, posterior_expected_returns = model.calculate_black_litterman(
        covariance_matrix,
        market_prices,
        risk_free_rate,
        market_caps,
        symbols,
        investor_views,
        confidences,
        prints=True
    )
    max_sharpe_weights, max_sharpe_results = model.maximum_sharpe_portfolio(
        posterior_expected_returns, posterior_covariance_matrix, risk_free_rate, prints=True
    )

    return max_sharpe_weights
