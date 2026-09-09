import json,time,os,numpy as np,pandas as pd
from alphagenome.atlas import atlas
from alphagenome.data import genome
import os; KEY = os.environ.get('ALPHAGENOME_API_KEY') or open('.env').read().split('=')[1].strip(); client=atlas.create(KEY,timeout=600)
G=json.load(open('data/brca1_gene.json')); s=G['start']-2000; e=G['end']+2000
os.makedirs('data/brca1',exist_ok=True)
for a in range(s,e,10000):
    b=min(a+10000,e); out=f'data/brca1/{a}.parquet'
    if os.path.exists(out): continue
    for i in range(6):
        try:
            res=client.query_interval(genome.Interval(chromosome='chr17',start=a,end=b),requested_scorers=['AVI_SCORE','AVI_SCORE_FEATURE_IMPORTANCE'],progress_bar=False,max_workers=2); break
        except Exception as ex:
            if 'RESOURCE_EXHAUSTED' in str(ex): print('quota wait',flush=True); time.sleep(65)
            else: raise
    avi,fi=res['AVI_SCORE'],res['AVI_SCORE_FEATURE_IMPORTANCE']
    df=pd.DataFrame({'variant':[str(v) for v in avi.obs['variant']],'avi':np.asarray(avi.X).ravel(),'q':np.asarray(avi.layers['quantiles']).ravel()})
    fdf=pd.DataFrame(np.asarray(fi.X),columns=[n.lower() for n in fi.var['name']]);fdf['variant']=[str(v) for v in fi.obs['variant']]
    df=df.merge(fdf,on='variant'); p=df.variant.str.split(':',expand=True); df['pos']=p[1].astype(int); df['ref']=p[2].str[0]; df['alt']=p[2].str[-1]
    df.to_parquet(out,index=False); print(a,len(df),flush=True); time.sleep(10)
print('done')
