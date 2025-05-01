import pandas as pd
import mplfinance as mpf
import ta


def build_plot(df: pd.DataFrame, type: str = "candle", marker: pd.Timestamp = None) -> None:
    """
    Affiche un graphique basé sur les prix ask avec les EMA 5 et 13.

    Paramètres :
    - df : DataFrame pandas avec MultiIndex sur les colonnes
    - type : "line" ou "candle"
    - marker : Timestamp pour tracer une ligne verticale rouge (facultatif)
    """
    if type not in {"line", "candle"}:
        raise ValueError("Le paramètre 'type' doit être 'line' ou 'candle'")

    # Extraire les colonnes OHLC du ask
    df_plot = df[[('ask', 'Open'), ('ask', 'High'), ('ask', 'Low'), ('ask', 'Close')]].copy()
    df_plot.columns = ['Open', 'High', 'Low', 'Close']  # Flatten

    # Calcul des EMA
    df_plot['EMA_5'] = ta.trend.ema_indicator(close=df_plot['Close'], window=5)
    df_plot['EMA_13'] = ta.trend.ema_indicator(close=df_plot['Close'], window=13)

    # Préparation des courbes EMA
    apds = [
        mpf.make_addplot(df_plot['EMA_5'], color='blue', linestyle='dashed', width=1),
        mpf.make_addplot(df_plot['EMA_13'], color='orange', linestyle='dashed', width=2)
    ]

    # === Calcul du zoom vertical automatique ===
    min_price = df_plot['Low'].min()
    max_price = df_plot['High'].max()
    padding = (max_price - min_price) * 0.05  # 5% de marge visuelle
    ylim = (min_price - padding, max_price + padding)

    # === Construction du dictionnaire d'options ===
    kwargs = {
        'type': type,
        'style': 'yahoo',
        'addplot': apds,
        'title': f"{type.capitalize()} + EMA 5/13",
        'ylabel': 'Prix',
        'ylim': ylim,
        'tight_layout': True
    }

    if marker:
        kwargs['vlines'] = dict(vlines=[marker], colors='red', linewidths=1)

    # Affichage du graphique
    mpf.plot(df_plot, **kwargs)
