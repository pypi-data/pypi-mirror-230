import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Shapre Ratio


def sharpe_ratio(df, rf=0.03, interval='w'):
    match interval:
        case 'm':
            divsor = 12
        case 'y':
            divsor = 1
        case 'd':
            divsor = 252
        case _:
            divsor = 52
    risk_free_return = rf/divsor

    sharpe = []
    for col in df.columns:
        sharpe.append((df[col].describe().T['mean'] -
                      risk_free_return) / df[col].describe().T['std'])
    return sharpe


def pf_return(df, pfw='equal'):
    # Initial pf_return
    pf_ret = []
    if pfw == 'equal':
        pf_wt = 1/len(df.index)
        pf_ret = pf_wt * df.sum(axis=1)
        return pf_ret
    else:
        if sum(pfw.values()) == 1:
            tcWeight = list(pfw.values())
            for i in range(len(df.index)):
                pf_ret.append(sum(tcWeight * np.array(df.iloc[i])))
        else:
            print('err')
        return pf_ret
