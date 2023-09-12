import json
import os
import sys
import pandas as pd
import numpy as np
import datetime
from .data_loader import TDConnector


os.system(f"{sys.executable} -m pip install fancyimpute==0.7.0")
os.system(f"{sys.executable} -m pip install strsim==0.0.3")
os.system(f"{sys.executable} -m pip install networkx==2.5")
os.system(f"{sys.executable} -m pip install scipy==1.6.2")
#os.system(f"{sys.executable} -m pip install pandiet==0.1.6")
os.system(f"{sys.executable} -m pip install fuzzywuzzy==0.18.0")
#os.system(f"{sys.executable} -m pip install memory_profiler==0.60.0")
os.system(f"{sys.executable} -m pip install python-Levenshtein==0.21.1")


#####----Defining Variables-------#####
TD_SINK_DATABASE=os.environ.get('TD_SINK_DATABASE')
TD_API_KEY=os.environ.get('TD_API_KEY')
TD_API_SERVER=os.environ.get('TD_API_SERVER')

id_col=os.environ.get('id_col')
cluster_col_name=os.environ.get('cluster_col_name')
convergence_threshold=float(os.environ.get('convergence_threshold'))
cluster_threshold=float(os.environ.get('cluster_threshold'))
string_type=os.environ.get('string_type')
fill_missing=os.environ.get('fill_missing')
feature_dict=json.loads(os.environ.get('feature_dict'))
blocking_table=os.environ.get('blocking_table')
output_table=os.environ.get('output_table')

record_limit=int(os.environ.get('record_limit'))
lower_limit=int(os.environ.get('lower_limit'))
upper_limit=int(os.environ.get('upper_limit'))
range_index=os.environ.get('range_index')
paralelism = os.environ.get('paralelism')

input_table=blocking_table


#fill_missing=True
#print(feature_dict)
import get_similarity
import get_cluster

feature_cols="block_key, " + id_col
for feature in feature_dict:

        name=feature['name']
        feature_cols=feature_cols +  ","  + name

query= f"Select { feature_cols }  from {input_table} WHERE rnk > {lower_limit} and rnk <= {upper_limit}"
print(query)

def execute_main():

  dup_data = TDConnector.read(query,TD_SINK_DATABASE,input_table,TD_API_KEY,TD_API_SERVER)


#--- Generating all the combinations of pairs within each block
#--- and then dropping pair of same id e.g. when id=A , self pair would be id_1=A and id_2=A so its like A-A(which we dont need to calculate #    similarities )
  sim_data=pd.merge(dup_data,dup_data,on='block_key',suffixes=('_1','_2')).drop_duplicates()

#--- Dropping one of duplicate pairs e.g id_1=A and id_2= B ==> there will be two combinations A-B and B-A but we only need any one of them. so dropping one of them here
  sim_data=sim_data[sim_data[id_col+'_1']>sim_data[id_col+'_2']]

  sim_data, sim_feat_list,col_names,weights=get_similarity.get_similarities(sim_data,feature_dict,string_type)

#--- Multiplying Features similarities with weights defined in config file
#--- If a feature's value is null and there is no similarity score for that feature, weights will not be multiplied with that feature.
  sim_data[sim_feat_list]=sim_data[sim_feat_list]*weights
  sim_data['score']=sim_data[sim_feat_list].sum(axis=1)

#-- Creating clusters based on final similarities
#-- fill_missing ==> it is used to fill null values between pairs link (This is an extremely unusual occurrence.)
  df_clusters=get_cluster.clusters(sim_data,id_col,cluster_col_name,cluster_threshold,convergence_threshold,col_names,fill_missing)

  df=df_clusters[cluster_col_name].value_counts()
  final_df=df_clusters[df_clusters[cluster_col_name].isin(df[df > 1].index)]
  final_df=final_df.merge(dup_data,how='left',on=[id_col]).drop('block_key',axis=1).drop_duplicates()
  print(range_index,'range index with cluster_col_name ', cluster_col_name)
  final_df[cluster_col_name]=str(range_index) + '_' + final_df[cluster_col_name].astype('str')


  if paralelism == 'no' and len(final_df) > 0:
    TDConnector.write(final_df,TD_SINK_DATABASE, output_table,TD_API_KEY,TD_API_SERVER)
  elif len(final_df) > 0:
    TDConnector.insert_df(final_df,TD_SINK_DATABASE, output_table,TD_API_KEY,TD_API_SERVER)
