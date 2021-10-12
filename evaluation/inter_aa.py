import pandas as pd
from sklearn.metrics import cohen_kappa_score
import numpy as np

GROUPS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]

def read_files(path="../data/group-wise/"):
    '''import all 22 files to a dictionary'''
    df_dict={}
    sheets = [item+str(num) for item in GROUPS for num in [1, 2]]
    
    for i, sheet in enumerate(sheets):
        frame = pd.read_csv(path+sheet+".csv", sep="\t", encoding="utf=8")
        df_dict[sheet] = frame

    return df_dict
    

def individual_IAA(df_dict, group:str):
    '''inter-annotator agreement between two judges'''
    assert group.lower() in [item[0] for item in df_dict.keys()]
    
    candidate = []
    for num in [1, 2]:
        num = str(num)
        candid = df_dict[group+num].Ref_rating\
                .append(df_dict[group+num].MT_Z_rating)\
                .append(df_dict[group+num].MT_Y_rating).tolist()
        
        candidate.append(candid)
    
    return round(cohen_kappa_score(candidate[0], candidate[1]), 4)


def final_IAA(df_dict:pd.DataFrame):
    kappa_dict = {}
    for group in GROUPS:
        score = individual_IAA(df_dict, group)
        kappa_dict[group] = score

    return kappa_dict


if __name__ == '__main__':
    file_dicts = read_files()  # group, dfs
    
    print("Testing - Group A: ", individual_IAA(file_dicts, "a"))
    print("Group-wise Scores: ", final_IAA(file_dicts))
    
    kappa_dict = final_IAA(file_dicts)
    print("Avg= ", np.mean([score for _, score in kappa_dict.items()]))
    print("Min= ", np.min([score for _, score in kappa_dict.items()]))
    print("Max= ", np.max([score for _, score in kappa_dict.items()]))

