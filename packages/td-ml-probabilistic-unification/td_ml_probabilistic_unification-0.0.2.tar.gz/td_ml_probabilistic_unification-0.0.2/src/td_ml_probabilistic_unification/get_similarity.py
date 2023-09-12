import pandas as pd
import numpy as np
import re
from similarity.jarowinkler import JaroWinkler
from similarity.cosine import Cosine
cosine = Cosine(2)
from  fuzzywuzzy import fuzz

from similarity.normalized_levenshtein import NormalizedLevenshtein
normalized_levenshtein = NormalizedLevenshtein()
jarowinkler = JaroWinkler()


def get_email_d(c,d):
    if c==None or d==None or c=='' or d=='':
        return np.nan
    c=str(c).split('@')[0].lower().strip()
    d=str(d).split('@')[0].lower().strip()
   
    return 1 - np.round(normalized_levenshtein.distance(c,d),2)
           
def get_phone_d(c,d):
    if c==None or d==None or c=='' or d=='':
        return np.nan
    c=re.sub("\D", "",str(c).strip())
    d=re.sub("\D", "",str(d).strip()) 
    return 1 - np.round(normalized_levenshtein.distance(c,d),2)

def get_cosine(c,d):
    if c==None or d==None or c=='' or d=='':
        return np.nan
    c=str(c).lower().strip()
    d=str(d).lower().strip()
    a=cosine.get_profile(c)
    b=cosine.get_profile(d)

    return np.round(cosine.similarity_profiles(a,b),2)

def get_jarowinkler(c,d):
    if c==None or d==None:
        return np.nan
    else:
        c=re.sub('[^A-Za-z0-9]+', ' ',str(c)).lower().strip()
        d=re.sub('[^A-Za-z0-9]+', ' ',str(d)).lower().strip()
        if c==None or d==None or c=='' or d=='':
            return np.nan
    return jarowinkler.similarity(c,d)

def get_fuzzy(c,d):
    if c==None or d==None:
        return np.nan
    else:
        c=re.sub('[^A-Za-z0-9]+', ' ',str(c)).lower().strip()
        d=re.sub('[^A-Za-z0-9]+', ' ',str(d)).lower().strip()
        if c==None or d==None or c=='' or d=='' :
            return np.nan
    return np.round(fuzz.token_sort_ratio(c,d)/100,2)



def get_similarities(sim_data,feature_dict,string_type='jarowinkler'):
    
    sim_feat_list=[]
    col_names=[]
    weights=[]
    
    for feature in feature_dict:

        name=feature['name']
        col_names.append(name)
        type=feature['type']
        weights.append(float(feature['weight']))
        sim_feat_list.append(name+'_sim')
                       
        if type=='email':
            sim_data[name+'_sim']=sim_data[[name+'_2',name+'_1']].apply(lambda x: get_email_d(*x),axis=1)


        elif type=='phone':
            sim_data[name+'_sim']=sim_data[[name+'_2',name+'_1']].apply(lambda x: get_phone_d(*x),axis=1)

        elif type=='string':
            
            if string_type=='jarowinkler':
                sim_data[name+'_sim']=sim_data[[name+'_2',name+'_1']].apply(lambda x: get_jarowinkler(*x),axis=1)
            elif string_type=='cosine':
                sim_data[name+'_sim']=sim_data[[name+'_2',name+'_1']].apply(lambda x: get_cosine(*x),axis=1)
            else:
                sim_data[name+'_sim']=sim_data[[name+'_2',name+'_1']].apply(lambda x: get_fuzzy(*x),axis=1)
    
    return sim_data, sim_feat_list,col_names,weights