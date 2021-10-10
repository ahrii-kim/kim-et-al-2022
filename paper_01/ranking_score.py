import pandas as pd
import numpy as np
from scipy.stats import binom_test
from sklearn.metrics import cohen_kappa_score




def significance_test(df:pd.DataFrame, system:str):
    '''
    The Significance Test compares MT and HT rankings.
    '''
    mt_better= 0 # MT better
    ht_better = 0 # HT better
    tie = 0 # Ties
    
    for row in df.iterrows():
        ref = row[1]['Ref_rating']  # reference
        sys = row[1][system+"_rating"]

        if(ref > sys):
            mt_better+=1
        elif(ref < sys):
            ht_better+=1
        else:
            tie+=1
    
    x = round(mt_better + 0.5*tie)
    n = mt_better + ht_better + tie
    p_value = binom_test(x, n, alternative='two-sided')
  
    return {system:(mt_better, ht_better, tie, p_value)}

    

def absolute_score(df:pd.DataFrame, system:str):
    '''
    The absolute ranking score from TAUS
    '''
    first, second, third = df[system+"_rating"].value_counts().sort_index()
    score = (first*3 + second*2 + third*1) / np.sum([first, second, third])
    
    return {system:(score, first, second, third)}


def get_result(df:pd.DataFrame):
    system_y = "MT_Y"
    system_z = "MT_Z"

    sign_y = significance_test(df, system_y)
    sign_z = significance_test(df, system_z)

    result = pd.DataFrame({system_y:sign_y[system_y], system_z:sign_z[system_z]})
    result.index = ["MT_better", "HT_better", "Tie", "P-value"]
    result.loc["Valid"] = [str(result.loc["P-value"][0] < 0.001), str(result.loc["P-value"][1] < 0.001)]
    result.loc["Ab_score"] = [absolute_score(df, system_y)[system_y][0], absolute_score(df, system_z)[system_z][0]]
    
    return result