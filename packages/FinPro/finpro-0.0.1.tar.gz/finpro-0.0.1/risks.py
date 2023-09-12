import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from arch import arch_model
from scipy import stats

# Maximun Drawdown


def MDD(df, tickers, idx=[], plot=False):
    # Calculate Drawdown for each rows first, then MDD
    dd = {}
    MDD = {}

    for ticker in tickers.keys():
        # Calculate every row's Drawdown
        value_list = []
        for i in range(len(df[ticker])):
            if i == 0:
                value_list.append(0)
            else:
                value_list.append(
                    (min((df[ticker][i] - max(df[ticker][0:i])) / max(df[ticker][0:i]), 0)))

        # create a DataFrame for plotting
        dd[ticker+'_DD'] = value_list
        # Caluclar Maximum Drawdown for each tickers
        MDD[ticker] = np.min(value_list)

    df_dd = pd.DataFrame(dd, index=idx)

    # Date of MDD
    mddDate = {}
    for ticker in tickers.keys():
        # mddDate[ticker] = df_dd[df_dd[ticker+'_DD']==min(df_dd[ticker+'_DD'])]
        mddDate[ticker] = list(
            df_dd[ticker+'_DD']).index(min(df_dd[ticker+'_DD']))

    # Line Plot Function
    def mdd_line_plot(df, mdddate, mdd, tickers):
        plt.figure(figsize=(15, 8))
        plt.grid()
        ax = sns.lineplot(df)

        # Annotation
        for i in range(len(mdddate)):
            text = tickers[i] + ',' + str((mdd[i] * 100).round(2)) + \
                '%' + ',' + str(df_dd.index[mdddate[i]])
            x = df_dd.index[mdddate[i]]
            y = mdd[i]
            xytext = (x, y - 0.05)
            ax.annotate(
                text,
                xy=(x, y),
                xytext=xytext,
                color='red',
                weight='bold',
                arrowprops=dict(facecolor='red', shrink=0.01,
                                headwidth=8, headlength=12),
            )
            # txt = tickers[i] + ',' + str( (mdd[i] * 100).round(2) ) + '%' + ','  + str(df_dd.index[mdddate[i]])
            # ax.text(df_dd.index[mdddate[i]],mdd[i], txt, color ='blue' )

        plt.show()

    if plot == True:
        mdd_line_plot(df_dd, mdddate=list(mddDate.values()),
                      mdd=list(MDD.values()), tickers=list(MDD.keys()))
        return MDD, df_dd, mddDate
    else:
        return MDD.values(), df_dd, mddDate


# Calculate Beta
def beta(df, bmkcol):
    # Benchmark
    bmk_var = df[bmkcol].var()
    beta = (df.cov() / bmk_var)[bmkcol]

    return beta.values


# Monte Carlo VaR
# Decide the significant level and the relevant z-scores
def mcVar(df, siglvl='5%'):
    # Get each columns' name
    cols = df.columns

    # Initialize z-scores and significant levle multiplier which equals to the significant level
    z = 0
    sig_multiplier = 0

    # Set level of significant, it's one-sided.
    if siglvl == '5%':
        z = -1.645
        sig_multiplier = 0.05
    elif siglvl == '1%':
        z = -2.326
        sig_multiplier = 0.01

    # Computer the parameters for the GARCH, such as : Mean, Omega, Alpha, Beta
    # g_params = {} #Save each tickers' GARCH parameteres

    mcVaR = {}
    for col in cols:
        # Caculate GARCH Params
        list_for_fit = np.array(df[col])
        am = arch_model(list_for_fit)
        res = am.fit()

        # The Params:Mu, Omega, Alpha, Beta
        mu = res.params[0]
        o = res.params[1]
        a = res.params[2]
        b = res.params[3]

        # Ticker's Variance
        varr = list_for_fit.var()

        # uncontiditional GARCH VaR
        gvar_t1 = np.sqrt(
            o + a * np.square(list_for_fit[-1]) + b * varr) * (-1 * z)  # T+1 VaR

        # Generate 100k random number
        randz = stats.zscore(np.random.rand(100000))

        mc_list = list_for_fit.mean() - list_for_fit.std() * randz
        mc_list.sort()
        pos = int(np.floor(len(mc_list) * sig_multiplier))

        mcVaR[col] = mc_list[pos-1]

    return mcVaR.values()
