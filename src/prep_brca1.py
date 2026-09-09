import pandas as pd,numpy as np,json
from sklearn.metrics import roc_auc_score
j=pd.read_parquet('data/brca1_clinvar_joined.parquet'); G=json.load(open('data/brca1_gene.json'))
j=j[j.cls.isin(['P','B','VUS','conflict'])].copy()
j['stars']=j.review.map(lambda r: 3 if 'expert' in r else 2 if 'multiple' in r and 'no conflicts' in r else 1 if 'criteria provided' in r else 0)
j['short']=j.name.str.replace(r'^NM_007294\.4\(BRCA1\):','',regex=True)
ex=sorted(G['exons'],reverse=True)
def exon_of(p):
    for i,(a,b) in enumerate(ex):
        if a<=p<=b: return i+1
    return 0
j['exon']=j.pos.map(exon_of)
pts=[[int(r.pos),r.cls,r.cons,round(float(r.q),5),round(float(r.avi),3),r.short,int(r.stars),int(r.exon)] for r in j.itertuples()]
pb=j[j.cls.isin(['P','B'])]; ep=pb[pb.stars==3]
def auc(d): return round(float(roc_auc_score(d.cls=='P',d.q)),4) if d.cls.nunique()==2 else None
stats={'n':{k:int(v) for k,v in j.cls.value_counts().items()},
 'auc_all':auc(pb),'auc_expert':auc(ep),'n_expert':{k:int(v) for k,v in ep.cls.value_counts().items()},
 'auc_by_cons':{c:auc(pb[pb.cons==c]) for c in ['missense','intron','synonymous','nonsense','splice_site','UTR']},
 'n_by_cons':{c:{k:int(v) for k,v in pb[pb.cons==c].cls.value_counts().items()} for c in ['missense','intron','synonymous','nonsense','splice_site','UTR']},
 'median_q':{k:round(float(v),4) for k,v in j.groupby('cls').q.median().items()},
 'expert_minP_q':round(float(ep[ep.cls=='P'].q.min()),4),
 'vus':{'n':int((j.cls=='VUS').sum()),'ge99':int(((j.cls=='VUS')&(j.q>=.99)).sum()),'ge995':int(((j.cls=='VUS')&(j.q>=.995)).sum()),'lt90':int(((j.cls=='VUS')&(j.q<.9)).sum()),'lt50':int(((j.cls=='VUS')&(j.q<.5)).sum()),'missense':int(((j.cls=='VUS')&(j.cons=='missense')).sum())},
 'conflict_ge99':round(float((j[j.cls=='conflict'].q>=.99).mean()),3),
}
# threshold curve
ths=[round(float(1-10**(-e)),5) for e in np.linspace(1,4.3,120)]
curve=[[t,round(float((pb[pb.cls=='P'].q>=t).mean()),4),round(float((pb[pb.cls=='B'].q<t).mean()),4),int(((j.cls=='VUS')&(j.q>=t)).sum())] for t in ths]
# exon table
et=j[j.cls.isin(['P','B','VUS'])].groupby(['exon','cls']).size().unstack(fill_value=0).reindex(range(0,24),fill_value=0)
exons=[{'i':i+1,'start':a,'end':b,'P':int(et.loc[i+1,'P']) if i+1 in et.index else 0,'B':int(et.loc[i+1,'B']) if i+1 in et.index else 0,'VUS':int(et.loc[i+1,'VUS']) if i+1 in et.index else 0} for i,(a,b) in enumerate(ex)]
site={'gene':{'start':G['start'],'end':G['end'],'cds':G['cds'],'exons':exons},'points':pts,'stats':stats,'curve':curve,
 'examples':{
  'vus_top':[[r.short,round(float(r.q),4),int(r.stars)] for r in j[j.cls=='VUS'].sort_values('q',ascending=False).head(8).itertuples()],
  'vus_bottom':[[r.short,round(float(r.q),4),int(r.stars)] for r in j[j.cls=='VUS'].sort_values('q').head(8).itertuples()],
  'expert_benign_high':[[r.short,r.cons,round(float(r.q),4)] for r in ep[ep.cls=='B'].drop_duplicates('short').sort_values('q',ascending=False).head(5).itertuples()],
  'expert_path_low':[[r.short,r.cons,round(float(r.q),4)] for r in ep[ep.cls=='P'].sort_values('q').head(5).itertuples()],
  'path_low_any':[[r.short,r.cons,round(float(r.q),4),int(r.stars)] for r in pb[pb.cls=='P'].sort_values('q').head(5).itertuples()],
 }}
json.dump(site,open('brca1_data.json','w'),ensure_ascii=False,separators=(',',':'))
import os;print(os.path.getsize('brca1_data.json')//1024,'KB'); print(json.dumps(stats,ensure_ascii=False)[:1200])
print(site['examples'])
