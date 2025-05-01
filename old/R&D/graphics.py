import mplfinance as mpf

def build_plot(df):
    # Préparation des données pour mplfinance
    df_mpf = df[['bid_Open', 'bid_High', 'bid_Low', 'bid_Close', 'ema_5', 'ema_13']].copy()
    df_mpf.columns = ['Open', 'High', 'Low', 'Close', 'EMA_5', 'EMA_13']

    # Couleurs personnalisées pour EMA5 et EMA20 inversées
    apds = [
        mpf.make_addplot(df_mpf['EMA_5'], color='orange', width=1, linestyle='--', label='EMA 5'),
        mpf.make_addplot(df_mpf['EMA_13'], color='blue', width=1, linestyle='-.', label='EMA 13')
    ]

    # Couleurs chandeliers
    mc = mpf.make_marketcolors(
        up='green', down='red',
        edge='inherit', wick='inherit', volume='in'
    )

    # Style affiné avec quadrillage
    s = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle='--',
        gridcolor='lightgray',
        y_on_right=False,
        rc={'xtick.minor.visible': True, 'ytick.minor.visible': True}
    )

    # Tracé du graphique
    mpf.plot(
        df_mpf,
        type='candle',
        style=s,
        title="EUR/USD - EMA 5 (orange) vs EMA 20 (bleu) - Bougies M1",
        ylabel='Prix',
        addplot=apds,
        volume=False,
        figsize=(12, 6),
        tight_layout=True,
        datetime_format='%H:%M',
        warn_too_much_data = 30000
    )
