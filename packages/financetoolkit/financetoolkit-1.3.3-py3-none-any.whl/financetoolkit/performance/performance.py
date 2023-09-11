"""Performance Model"""

import warnings

import numpy as np
import pandas as pd

# This is meant for calculations in which a Multi Index exists. This is the case
# when calculating a "within period" in which the first index represents the period
# (e.g. 2020Q1) and the second index the days within that period (January to March)
MULTI_PERIOD_INDEX_LEVELS = 2

# pylint: disable=isinstance-second-argument-not-valid-type


def get_covariance(
    returns: pd.Series | pd.DataFrame, benchmark_returns: pd.Series | pd.DataFrame
) -> pd.Series | pd.DataFrame:
    """
    Calculate the covariance of returns.

    A warnings filter is included given that the following error
    can occur:

    RuntimeWarning: Degrees of freedom <= 0 for slice
        return np.cov(a, b, ddof=ddof)[0, 1]

    Given that this is due to division by zero or NaN values, it does
    not have any impact on the result. The warning is therefore
    ignored.

    Args:
        returns (pd.Series | pd.DataFrame): _description_
        benchmark_returns (pd.Series | pd.DataFrame): _description_

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if isinstance(returns, pd.DataFrame):
            covariance = pd.Series(index=returns.columns)

            for column in returns.columns:
                covariance.loc[column] = returns[column].cov(benchmark_returns)

            return covariance

        if isinstance(returns, pd.Series | pd.core.window.rolling.Rolling):
            return returns.cov(benchmark_returns)

    return returns.cov(benchmark_returns)


def get_beta(
    returns: pd.Series | pd.DataFrame, benchmark_returns: pd.Series
) -> pd.Series | pd.DataFrame:
    """_summary_

    Args:
        returns (pd.Series | pd.DataFrame): _description_
        benchmark_returns (pd.Series | pd.DataFrame): _description_

    Returns:
        pd.Series | pd.DataFrame: _description_
    """
    if isinstance(returns, pd.DataFrame):
        if returns.index.nlevels == MULTI_PERIOD_INDEX_LEVELS:
            combination = pd.concat([returns, benchmark_returns], axis=1)

            # Calculate Sharpe ratio for each asset (ticker) in the DataFrame
            covariance = combination.groupby(level=0).apply(
                lambda x: get_covariance(x[returns.columns], x[benchmark_returns.name])
            )
            variance = benchmark_returns.groupby(level=0).apply(lambda x: x.var())

            return covariance.div(variance, axis=0)

        return get_covariance(returns, benchmark_returns) / benchmark_returns.var()

    if isinstance(returns, pd.Series):
        # Calculate Sharpe ratio for a single asset (ticker)
        return get_covariance(returns, benchmark_returns) / benchmark_returns.var()

    raise TypeError("Expects pd.DataFrame or pd.Series, no other value.")


def get_rolling_beta(
    returns: pd.Series | pd.DataFrame, benchmark_returns: pd.Series, window_size: int
) -> pd.Series | pd.DataFrame:
    """
    Calculate rolling beta.

    Args:
        returns (pd.Series | pd.DataFrame): Asset returns.
        benchmark_returns (pd.Series): Benchmark returns.
        window_size (int): Rolling window size.

    Returns:
        pd.Series | pd.DataFrame: Rolling beta values.
    """
    rolling_cov = pd.DataFrame(columns=returns.columns, dtype=np.float64)

    for column in returns.columns:
        rolling_cov.loc[:, column] = get_covariance(
            returns[column].rolling(window=window_size), benchmark_returns
        )

    rolling_var = benchmark_returns.rolling(window=window_size).var()

    rolling_beta = rolling_cov.div(rolling_var, axis=0)

    return rolling_beta


def get_capital_asset_pricing_model(
    risk_free_rate: pd.Series | float,
    beta: pd.Series | pd.DataFrame | float,
    benchmark_returns: pd.Series | float,
) -> pd.Series | pd.DataFrame:
    """
    CAPM, or the Capital Asset Pricing Model, is a financial model used to estimate the expected return on an investment,
    such as a stock or portfolio of stocks. It provides a framework for evaluating the risk and return trade-off of
    an asset or portfolio in relation to the overall market. CAPM is based on the following key components:

        - Risk-Free Rate (Rf): This is the theoretical return an investor could earn from an investment with no
        risk of financial loss. It is typically based on the yield of a government bond.
        - Market Risk Premium (Rm - Rf): This represents the additional return that investors expect to earn
        for taking on the risk of investing in the overall market as opposed to a risk-free asset. It
        is calculated as the difference between the expected return of the market (Rm) and the risk-free rate (Rf).
        - Beta (β): Beta is a measure of an asset's or portfolio's sensitivity to market movements. It
        quantifies how much an asset's returns are expected to move in relation to changes in the
        overall market. A beta of 1 indicates that the asset moves in line with the market, while a
        beta greater than 1 suggests higher volatility, and a beta less than 1 indicates lower volatility.

    The formula is as follows:

    Expected Return (ER) = Rf + β * (Rm - Rf)

    Args:
        risk_free_rate (pd.Series | float): the risk free rate.
        beta (pd.Series | pd.DataFrame | float): the beta.
        benchmark_returns (pd.Series | float): the benchmark returns.

    Returns:
        pd.Series | pd.DataFrame | float: the capital asset pricing model.
    """
    if isinstance(beta, pd.DataFrame):
        capital_asset_pricing_model = pd.DataFrame(
            columns=beta.columns, dtype=np.float64
        )
        for column in capital_asset_pricing_model.columns:
            capital_asset_pricing_model.loc[:, column] = risk_free_rate + beta[
                column
            ] * (benchmark_returns - risk_free_rate)
    if isinstance(beta, (pd.Series | float)):
        capital_asset_pricing_model = risk_free_rate + beta * (
            benchmark_returns - risk_free_rate
        )

    return capital_asset_pricing_model


def get_alpha(
    asset_returns: pd.Series | float,
    benchmark_returns: pd.Series | float,
) -> pd.Series | pd.DataFrame:
    """
    Calculate the Alpha.

    Args:
        excess_returns (pd.Series): A Series of returns with risk-free rate subtracted.

    Returns:
        pd.Series: A Series of Sharpe ratios with time as index and assets as columns.
    """
    if isinstance(asset_returns, pd.DataFrame):
        alpha = pd.DataFrame(columns=asset_returns.columns, dtype=np.float64)
        for column in alpha.columns:
            alpha.loc[:, column] = asset_returns[column] - benchmark_returns
    if isinstance(asset_returns, (pd.Series | float)):
        alpha = asset_returns - benchmark_returns

    return alpha


def get_jensens_alpha(
    asset_returns: pd.Series | float,
    risk_free_rate: pd.Series | float,
    beta: pd.Series | pd.DataFrame | float,
    benchmark_returns: pd.Series | float,
) -> pd.Series | pd.DataFrame:
    """
    Calculate Jensen's Alpha.

    Args:
        excess_returns (pd.Series): A Series of returns with risk-free rate subtracted.

    Returns:
        pd.Series: A Series of Sharpe ratios with time as index and assets as columns.
    """
    if isinstance(beta, pd.DataFrame) and isinstance(asset_returns, pd.DataFrame):
        jensens_alpha = pd.DataFrame(columns=beta.columns, dtype=np.float64)
        for column in jensens_alpha.columns:
            jensens_alpha.loc[:, column] = asset_returns[column] - (
                risk_free_rate + beta[column] * (benchmark_returns - risk_free_rate)
            )
    elif isinstance(beta, (pd.Series | float)) and isinstance(
        beta, (pd.Series | float)
    ):
        jensens_alpha = asset_returns - (
            risk_free_rate + beta * (benchmark_returns - risk_free_rate)
        )
    else:
        raise TypeError(
            "Expects pd.DataFrame for both Asset Returns and Beta or pd.Series / Float "
            "for both Asset Returns and Beta"
        )

    return jensens_alpha


def get_treynor_ratio(
    asset_returns: pd.Series | float,
    risk_free_rate: pd.Series | float,
    beta: pd.Series | pd.DataFrame | float,
) -> pd.Series:
    """
    Calculate the Treynor ratio of returns.

    Args:
        excess_returns (pd.Series): A Series of returns with risk-free rate subtracted.
        beta (float): The portfolio's beta (systematic risk).

    Returns:
        pd.Series: A Series of Treynor ratios with time as index and assets as columns.
    """
    if isinstance(beta, pd.DataFrame) and isinstance(asset_returns, pd.DataFrame):
        treynor_ratio = pd.DataFrame(columns=beta.columns, dtype=np.float64)
        for column in treynor_ratio.columns:
            treynor_ratio.loc[:, column] = (
                asset_returns[column] - risk_free_rate
            ) / beta[column]
    elif isinstance(beta, (pd.Series | float)) and isinstance(
        asset_returns, (pd.Series | float)
    ):
        treynor_ratio = (asset_returns - risk_free_rate) / beta
    else:
        raise TypeError(
            "Expects pd.DataFrame for both Asset Returns and Beta or pd.Series / Float "
            "for both Asset Returns and Beta"
        )

    return treynor_ratio


def get_sharpe_ratio(excess_returns: pd.Series | pd.DataFrame) -> pd.Series:
    """
    Calculate the Sharpe ratio of returns.

    Args:
        excess_returns (pd.Series): A Series of returns with risk-free rate subtracted.

    Returns:
        pd.Series: A Series of Sharpe ratios with time as index and assets as columns.
    """
    if isinstance(excess_returns, pd.DataFrame):
        if excess_returns.index.nlevels == MULTI_PERIOD_INDEX_LEVELS:
            # Calculate Sharpe ratio for each asset (ticker) in the DataFrame
            sharpe_ratios = excess_returns.groupby(level=0).apply(
                lambda x: x.mean() / x.std()
            )
            return sharpe_ratios

        return excess_returns / excess_returns.std()

    if isinstance(excess_returns, pd.Series):
        # Calculate Sharpe ratio for a single asset (ticker)
        return excess_returns / excess_returns.std()

    raise TypeError("Expects pd.DataFrame or pd.Series, no other value.")


def get_rolling_sharpe_ratio(
    excess_returns: pd.Series | pd.DataFrame,
    window_size: int,
) -> pd.Series:
    """
    Calculate the rolling Sharpe ratio of returns.

    Args:
        excess_returns (pd.Series | pd.DataFrame): A Series or DataFrame of returns with risk-free rate subtracted.
        window_size (int): The size of the rolling window in months. Default is 12.

    Returns:
        pd.Series: A Series of rolling Sharpe ratios with time as index and assets as columns.
    """
    sharpe_ratio = (
        excess_returns.rolling(window=window_size).mean()
        / excess_returns.rolling(window=window_size).std()
    )

    return sharpe_ratio


def get_sortino_ratio(excess_returns: pd.Series | pd.DataFrame) -> pd.Series:
    """
    Calculate the Sortino ratio of returns.

    Args:
        excess_returns (pd.Series | pd.DataFrame): A Series or DataFrame of returns with risk-free
        rate already subtracted.

    Returns:
        pd.Series: A Series of Sortino ratios with time as index and assets as columns.
    """
    if isinstance(excess_returns, pd.DataFrame):
        if excess_returns.index.nlevels == MULTI_PERIOD_INDEX_LEVELS:
            # Calculate Sortino ratio for each asset (ticker) in the DataFrame
            sortino_ratios = excess_returns.groupby(level=0).apply(
                lambda x: x.mean() / x[x < 0].std()
            )
            return sortino_ratios

        downside_returns = excess_returns[excess_returns < 0]
        downside_volatility = downside_returns.std()

        return excess_returns.mean() / downside_volatility

    if isinstance(excess_returns, pd.Series):
        # Calculate Sortino ratio for a single asset (ticker)
        downside_returns = excess_returns[excess_returns < 0]
        downside_volatility = downside_returns.std()
        return excess_returns.mean() / downside_volatility

    raise TypeError("Expects pd.DataFrame, pd.Series inputs, no other value.")


def get_ulcer_performance_index(
    excess_returns: pd.Series | pd.DataFrame, ulcer_index: pd.Series | pd.DataFrame
) -> pd.Series:
    """
    Calculate the Ulcer Performance Index (UPI) of returns.

    Args:
        excess_returns (pd.Series | pd.DataFrame): A Series of returns with risk-free rate subtracted.
        ulcer_index (pd.Series | pd.DataFrame): The corresponding

    Returns:
        pd.Series: A Series of Ulcer Performance Index values with time as index and assets as columns.
    """
    return (excess_returns / ulcer_index).dropna()


def get_m2_ratio(
    asset_returns: pd.Series | pd.DataFrame,
    risk_free_rate: pd.Series,
    asset_standard_deviation: pd.Series | pd.DataFrame,
) -> pd.Series:
    """
    Calculate the M2 Ratio (Modigliani-Modigliani Measure) of returns.

    Args:
        excess_returns (pd.Series | pd.DataFrame): A Series or DataFrame of returns with risk-free
        rate already subtracted.

    Returns:
        pd.Series: A Series of M2 ratios with time as index and assets as columns.
    """
    if isinstance(asset_returns, pd.DataFrame) and isinstance(
        asset_standard_deviation, pd.DataFrame
    ):
        m2_ratio = pd.DataFrame(columns=asset_returns.columns, dtype=np.float64)
        for column in m2_ratio.columns:
            m2_ratio.loc[:, column] = (
                asset_returns[column] - risk_free_rate
            ) / asset_standard_deviation[column]
    elif isinstance(asset_returns, (pd.Series | float)) and isinstance(
        asset_standard_deviation, (pd.Series | float)
    ):
        m2_ratio = (asset_returns - risk_free_rate) / asset_standard_deviation
    else:
        raise TypeError(
            "Expects pd.DataFrame for both Asset Returns and Asset Standard Deviations or pd.Series / Float "
            "for both Asset Returns and Asset Standed Deviations."
        )

    return m2_ratio


def get_tracking_error(
    asset_returns: pd.Series | pd.DataFrame, benchmark_returns: pd.Series
) -> pd.Series:
    """
    Calculate the Tracking Error of returns.

    Args:
        excess_returns (pd.Series | pd.DataFrame): A Series or DataFrame of returns with risk-free
        rate already subtracted.

    Returns:
        pd.Series: A Series of Sortino ratios with time as index and assets as columns.
    """
    if isinstance(asset_returns, pd.DataFrame):
        if asset_returns.index.nlevels == MULTI_PERIOD_INDEX_LEVELS:
            tracking_error = asset_returns.groupby(level=0).apply(
                lambda x: (x.sub(benchmark_returns, axis=0)).std()
            )

            return tracking_error

        tracking_error = pd.DataFrame(columns=asset_returns.columns, dtype=np.float64)
        for column in tracking_error.columns:
            tracking_error.loc[:, column] = (asset_returns - benchmark_returns).std()

    if isinstance(asset_returns, (pd.Series | float)):
        tracking_error = (asset_returns - benchmark_returns).std()

    return tracking_error


def get_information_ratio(
    asset_returns: pd.Series | pd.DataFrame, benchmark_returns: pd.Series
) -> pd.Series:
    """
    Calculate the Information Ratio of returns.

    Args:
        excess_returns (pd.Series | pd.DataFrame): A Series or DataFrame of returns with risk-free
        rate already subtracted.

    Returns:
        pd.Series: A Series of Sortino ratios with time as index and assets as columns.
    """
    if isinstance(asset_returns, pd.DataFrame):
        if asset_returns.index.nlevels == MULTI_PERIOD_INDEX_LEVELS:
            information_ratio = asset_returns.groupby(level=0).apply(
                lambda x: (
                    x.sub(benchmark_returns, axis=0).mean()
                    / (x.sub(benchmark_returns, axis=0)).std()
                )
            )

            return information_ratio

        information_ratio = pd.DataFrame(
            columns=asset_returns.columns, dtype=np.float64
        )
        for column in information_ratio.columns:
            difference = asset_returns[column] - benchmark_returns
            information_ratio.loc[:, column] = difference.mean() / difference.std()

    if isinstance(asset_returns, (pd.Series | float)):
        difference = asset_returns - benchmark_returns
        information_ratio = difference.mean() / difference.std()

    return information_ratio
