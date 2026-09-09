import json, pandas as pd, numpy as np
from systems import system_of, RULES
from prep_site import GENES, TISSUE_RU
SYS=[r[0] for r in RULES]+['Прочее']
MOD={'DNASE':'Открытость ДНК (DNase)','ATAC':'Открытость ДНК (ATAC)','CHIP_HISTONE':'Гистоновые метки','CHIP_TF':'Белки-регуляторы','CAGE':'Старт транскрипции','RNA_SEQ':'Уровень РНК'}
out={'systems':SYS,'modalities':MOD,'genes':{}}
LAB={};EXTRA={}
for gid,ch,pos,ref,alt,targets in GENES:
    df=pd.read_parquet(f'data/tissues/{gid}.parquet')
    df=df[df.scorer.isin(MOD)]
    df=df[(df.scorer!='RNA_SEQ')|(df.target==targets[0])]
    df['sys']=[system_of(n) for n in df.biosample_name]
    tracks={}
    for sc in MOD:
        d=df[df.scorer==sc].copy()
        # for CAGE: strand duplicates -> keep max abs per biosample; histone: keep track with mark
        d['label']=d.biosample_name.map(lambda n: TISSUE_RU.get(n,n))
        if sc=='CAGE':
            d=d.reindex(d.effect.abs().sort_values(ascending=False).index).drop_duplicates('biosample_name')
        recs=[]
        for r in d.itertuples():
            extra=r.histone_mark if sc=='CHIP_HISTONE' else (r.transcription_factor if sc=='CHIP_TF' else '')
            lab=r.label
            if lab not in LAB: LAB[lab]=len(LAB)
            if extra not in EXTRA: EXTRA[extra]=len(EXTRA)
            recs.append([SYS.index(r.sys), LAB[lab], round(float(r.effect),3), round(float(r.q),2) if r.q==r.q else -1, EXTRA[extra], 1 if r.biosample_type=='cell_line' else 0])
        tracks[sc]=recs
    # summary per system per modality: max |effect| and mean
    summ={}
    for sc in MOD:
        d=df[df.scorer==sc]
        g=d.groupby('sys').effect.agg(lambda x: float(x.loc[x.abs().idxmax()]))
        summ[sc]={k:round(float(v),3) for k,v in g.items()}
    out['genes'][gid]={'chrom':ch,'pos':pos,'ref':ref,'alt':alt,'target':targets[0],'tracks':tracks,'summary':summ}
    top={sc:max(summ[sc].items(),key=lambda kv:abs(kv[1])) for sc in MOD}
    print(gid,{MOD[k][:12]:v for k,v in top.items()})
out['labels']=list(LAB);out['extras']=list(EXTRA)
json.dump(out,open('tissues_data.json','w'),ensure_ascii=False,separators=(',',':'))
import os;print(os.path.getsize('tissues_data.json')//1024,'KB')
