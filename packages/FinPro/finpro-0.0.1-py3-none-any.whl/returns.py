import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Computer the log returns


def log_return(df, tickers):
    for ticker in tickers.keys():
        df[ticker+'_Ret'] = np.log(df[ticker]/df[ticker].shift(1))

    ret_cols = [col for col in df.columns if 'Ret' in col]

    # Drop the row where the return value is nan
    rIdx = df[df[ret_cols[0]].isna()].index
    df.drop(index=rIdx, inplace=True)

    return df


def cum_return(df):
    for col in [col for col in df.columns if 'Ret' in col and 'Cum' not in col]:
        df[col+'_Cum'] = np.cumsum(df[col])

    return df


def ret_line_plot(df, tickers):

    for ticker in tickers.keys():
        Max_Hist_Price = round(df[ticker].max(), 2)
        Max_Hist_Price_Date = df[df[ticker] == df[ticker].max()].index[0]
        Min_Hist_Price = round(df[ticker].min(), 2)
        Min_Hist_Price_Date = df[df[ticker] == df[ticker].min()].index[0]
        Max_Return = round(df[ticker+'_Ret'].max(), 2)
        Max_Return_Date = df[df[ticker+'_Ret']
                             == df[ticker+'_Ret'].max()].index[0]
        Min_Return = round(df[ticker+'_Ret'].min(), 2)
        Min_Return_Date = df[df[ticker+'_Ret']
                             == df[ticker+'_Ret'].min()].index[0]

        print('{0}: \n  Max_Hist_Price : {1} on {2}, Min_Hist_Price : {3} on {4} \n  Max_Return: {5} on {6}, Min_Return: {7} on {8} '.format(
            ticker,
            Max_Hist_Price,
            Max_Hist_Price_Date,
            Min_Hist_Price,
            Min_Hist_Price_Date,
            Max_Return,
            Max_Return_Date,
            Min_Return,
            Min_Return_Date
        )
        )

        ax = df.plot(y=ticker, legend=False, figsize=(10, 3), color='darkblue')
        ax2 = ax.twinx()
        df.plot(y=ticker+'_Ret', ax=ax2, legend=False, color="lightgreen")
        ax.figure.legend()

        # Annotation
        # Max historical price
        text = str(Max_Hist_Price_Date) + ',' + str(Max_Hist_Price)
        x = df[df[ticker] == df[ticker].max()].index
        y = df[ticker].max()
        xytext = (x, y)
        ax.annotate(
            text,
            xy=(x, y),
            xytext=xytext,
            color='red',
            weight='bold',
            arrowprops=dict(facecolor='red', shrink=0.01,
                            headwidth=8, headlength=12),
        )
        # Min historical price
        text = str(Min_Hist_Price_Date) + ',' + str(Min_Hist_Price)
        x = df[df[ticker] == df[ticker].min()].index
        y = df[ticker].min()
        xytext = (x, y)
        ax.annotate(
            text,
            xy=(x, y),
            xytext=xytext,
            color='red',
            weight='bold',
            arrowprops=dict(facecolor='red', shrink=0.01,
                            headwidth=8, headlength=12),
        )

        # Max Return
        text = str(Max_Return_Date) + ',' + str(Max_Return)
        x = df[df[ticker+'_Ret'] == df[ticker+'_Ret'].max()].index
        y = df[ticker+'_Ret'].max()
        xytext = (x, y)
        ax2.annotate(
            text,
            xy=(x, y),
            xytext=xytext,
            color='red',
            weight='bold',
            arrowprops=dict(facecolor='red', shrink=0.01,
                            headwidth=8, headlength=12),
        )
        # Min Return
        text = str(Min_Return_Date) + ',' + str(Min_Return)
        x = df[df[ticker+'_Ret'] == df[ticker+'_Ret'].min()].index
        y = df[ticker+'_Ret'].min()
        xytext = (x, y)
        ax2.annotate(
            text,
            xy=(x, y),
            xytext=xytext,
            color='red',
            weight='bold',
            arrowprops=dict(facecolor='red', shrink=0.01,
                            headwidth=8, headlength=12),
        )


# Plot cumulative returns
def cum_return_plot(df, palette=None):
    plt.figure(figsize=(15, 8))
    plt.grid()
    d = df
    ax = sns.lineplot(d, palette=palette)

    # Annotations
    for col in df.columns:
        max_cum = df[col].max()
        max_cum_date = df[df[col] == max_cum].index[0]
        min_cum = df[col].min()
        min_cum_date = df[df[col] == min_cum].index[0]

        # Max Cum Return
        text = '{0}, {1}%' .format(
            str(max_cum_date), str(round(max_cum*100, 2)))
        x = max_cum_date
        y = max_cum
        xytext = (x, y)
        ax.annotate(
            text,
            xy=(x, y),
            xytext=xytext,
            color='green',
            weight='bold',
        )
        # Min Cum Return
        text = '{0}, {1}%' .format(
            str(min_cum_date), str(round(min_cum*100, 2)))
        x = min_cum_date
        y = min_cum
        xytext = (x, y)
        ax.annotate(
            text,
            xy=(x, y),
            xytext=xytext,
            color='red',
            # weight='bold',
        )

    plt.show()
