import pandas as pd
import numpy as np
from scipy.stats import binom_test
from sklearn.metrics import cohen_kappa_score

from ko_mecab import mecab

BTS = "../data/before_test_set.csv"
ATS = "../data/after_test_set.csv"
GOOGLE = "../data/scores_google.csv"


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


if __name == '__main__':
    bts = pd.read_csv(BTS, sep="\t", encoding="utf-8")
    ats = pd.read_csv(ATS, sep="\t", encoding="utf-8")

    del before["Unnamed: 0"]
    del after["Unnamed: 0"]

    ###  Sign Test Result (n=437)
    print(result_bts = get_result(bts))
    print(result_ats = get_result(ats))

    ### Absolute Score Result (n=437)
    print()
    print("=== Absolute Score ===")
    print(absolute_score(bts, "Ref"))
    print(absolute_score(ats, "Ref"))

    ### Sign Test Result (n=148)
    bts_small = bts[bts["Error"] == "T"]
    ats_small = ats[ats["Error"] == "T"]

    print(result_bts_small = get_result(bts_small))
    print(result_ats_small = get_result(ats_small))

    ### Absolute Score Result (n=148)
    print()
    print("=== Absolute Score ===")
    print(absolute_score(bts_small, "Ref"))
    print(absolute_score(ats_small, "Ref"))    
