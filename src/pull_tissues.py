import json, time, os
import numpy as np, pandas as pd
from alphagenome.atlas import atlas
from alphagenome.data import genome
from prep_site import GENES
import os; KEY = os.environ.get('ALPHAGENOME_API_KEY') or open('.env').read().split('=')[1].strip()
client=atlas.create(KEY,timeout=600)
SC=['RNA_SEQ','ATAC','DNASE','CHIP_HISTONE','CHIP_TF','CAGE','PROCAP','SPLICE_SITE_USAGE']
os.makedirs('data/tissues',exist_ok=True)
for gid,ch,pos,ref,alt,targets in GENES:
    out=f'data/tissues/{gid}.parquet'
    if os.path.exists(out): continue
    v=genome.Variant(chromosome=ch,position=pos,reference_bases=ref,alternate_bases=alt)
    for i in range(5):
        try: res=client.query_variant(v,requested_scorers=SC,gene_names=targets); break
        except Exception as e:
            if 'RESOURCE_EXHAUSTED' in str(e): print('quota, wait');time.sleep(65)
            else: raise
    rows=[]
    for sc,ad in res.items():
        var=ad.var
        for i in range(ad.n_obs):
            gene=ad.obs['gene_name'].iloc[i] if 'gene_name' in ad.obs else None
            for j in range(ad.n_vars):
                r={'gene':gid,'scorer':sc,'target':gene,'track':var['name'].iloc[j],'strand':var['strand'].iloc[j] if 'strand' in var else None,
                   'effect':float(ad.X[i,j]),'q':float(ad.layers['quantiles'][i,j]) if 'quantiles' in ad.layers else None}
                for c in ['ontology_curie','biosample_name','biosample_type','biosample_life_stage','gtex_tissue','data_source','Assay title','histone_mark','transcription_factor']:
                    if c in var: 
                        val=var[c].iloc[j]; r[c]=None if (isinstance(val,float) and np.isnan(val)) else val
                rows.append(r)
    df=pd.DataFrame(rows); df.to_parquet(out,index=False)
    print(gid,len(df),df.groupby('scorer').size().to_dict(),flush=True); time.sleep(3)
