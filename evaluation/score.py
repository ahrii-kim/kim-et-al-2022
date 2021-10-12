import pandas as pd
import numpy as np
from scipy.stats import binom_test
from sklearn.metrics import cohen_kappa_score

from ko_mecab import mecab
import sacrebleu

BTS = "../data/before_test_set.csv"
ATS = "../data/after_test_set.csv"
GOOGLE = "../data/scores_google.csv"
TER_Y = "../data/score_y.csv"
TER_Z = "../data/score_z.csv"


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


def get_sacrebleu(df:pd.DataFrame, mt1:str, mt2:str):
    reference = df.Ref.tolist()
    hypothesis_y = df[mt1].tolist()
    hypothesis_z = df[mt2].tolist()

    reference = [' '.join(mecab(s)).replace("▃", "").replace("  ", " ") for s in reference]
    hypothesis_y = [' '.join(mecab(s)).replace("▃", "").replace("  ", " ") for s in hypothesis_y]
    hypothesis_z = [' '.join(mecab(s)).replace("▃", "").replace("  ", " ") for s in hypothesis_z]

    score_dic = {} 
    for system in [hypothesis_y, hypothesis_z]:
        
        bleu = sacrebleu.corpus_bleu(system, [reference])
        ter = sacrebleu.corpus_ter(system, [reference])
        !--force
        chrf = sacrebleu.corpus_chrf(system, [reference])
        
        if system == hypothesis_y:
            print("[ {} ]".format(mt1))
        else:
            print("[ {} ]".format(mt2))

        score_dic['bleu'] = bleu.score
        score_dic['ter'] = ter.score
        score_dic['chrf'] = chrf.score

        print("BLEU: ", bleu.score)
        print("TER: ", ter.score)
        print("chrF", chrf.score)
        print()
        return score_dic 


if __name__ == '__main__':
    bts = pd.read_csv(BTS, sep="\t", encoding="utf-8")
    ats = pd.read_csv(ATS, sep="\t", encoding="utf-8")

    del bts["Unnamed: 0"]
    del ats["Unnamed: 0"]

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

    ### Sacrebleu - BLEU, TER, chrF2 - BTS
    print()
    print("[BTS]\n", get_sacrebleu(bts), "MT_Y", "MT_Z")

    ### Sacrebleu - BLEU, TER, chrF2 - ATS
    print()
    print("[ATS]\n", get_sacrebleu(ats), "MT_Y", "MT_Z")

    ### Google Translate
    df_gt = pd.read_csv(GOOGLE, sep="\t", encoding="utf-8")
    del df_gt["Unnamed: 0"]

    print()
    print("[Google Translate (BTS & ATS)]\n", get_sacrebleu(df_gt), "Google Before", "Google After")

    ### Qualitative Analysis with TER
    mty = pd.read_csv(TER_Y, sep="\t", encoding="utf-8")
    mtz = pd.read_csv(TER_Z, sep="\t", encoding="utf-8")

    print("System Y:\n", mty[mty.TER >= 0.8])
    print("System Z:\n", mtz[mtz.TER >= 0.8])

    print(bts[bts["Segment ID"] == 346])
    print(ats[ats["Segment ID"] == 346])