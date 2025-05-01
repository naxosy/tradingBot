import pandas as pd
import mplfinance as mpf
import ta


def build_plot(df: pd.DataFrame, type: str = "candle", marker: pd.Timestamp = None) -> None:
    """
    Affiche un graphique basé sur les prix bid avec les EMA 5 et 13.

    Paramètres :
    - df : DataFrame pandas avec MultiIndex sur les colonnes
    - type : "line" ou "candle" (type de graphique)
    """
    # Vérification du paramètre type
    if type not in {"line", "candle"}:
        raise ValueError("Le paramètre 'type' doit être 'line' ou 'candle'")


    # Extraire les colonnes OHLC du bid
    df_plot = df[[('ask', 'Open'), ('ask', 'High'), ('ask', 'Low'), ('ask', 'Close')]].copy()
    df_plot.columns = ['Open', 'High', 'Low', 'Close']  # Aplatir pour mplfinance

    # Calcul des EMA
    df_plot['EMA_5'] = ta.trend.ema_indicator(close=df_plot['Close'], window=5)
    df_plot['EMA_13'] = ta.trend.ema_indicator(close=df_plot['Close'], window=13)

    # Préparation des courbes EMA à ajouter
    apds = [
        mpf.make_addplot(df_plot['EMA_5'], color='blue', linestyle='dashed', width=1),
        mpf.make_addplot(df_plot['EMA_13'], color='orange', linestyle='dashed', width=2)
    ]

    marqueur = marqueur = pd.Timestamp("2025-04-21 14:16:00")
    # Affichage

    if not marker :
        mpf.plot(
            df_plot,
            type=type,
            style='yahoo',
            addplot=apds,
            title=f"{type.capitalize()} + EMA 5/13",
            ylabel='Prix'
        )
    else :
        mpf.plot(
            df_plot,
            type=type,
            style='yahoo',
            addplot=apds,
            title=f"{type.capitalize()} + EMA 5/13",
            ylabel='Prix',
            vlines=[marker]
        )

