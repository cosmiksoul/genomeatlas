"""Pull AlphaGenome Atlas data for the 10 'genes you've heard of'.
Output: data/<GENE>_region.parquet (all SNVs in window: AVI, quantile, 18 feature importances)
        data/<GENE>_famous.json  (famous variant: AVI, quantile, feature importance, RNA_SEQ per tissue for target genes)
"""
import json, time, os, sys
import numpy as np, pandas as pd
from alphagenome.atlas import atlas
from alphagenome.data import genome

import os; KEY = os.environ.get('ALPHAGENOME_API_KEY') or open('.env').read().split('=')[1].strip()
WIN = int(sys.argv[1]) if len(sys.argv) > 1 else 5000   # half-window in bp

GENES = [
 # id, chrom, pos, ref, alt (hg38 forward strand), target genes for expression
 ('LCT',     'chr2',  135851076, 'G', 'A', ['LCT', 'MCM6']),
 ('CYP1A2',  'chr15', 74749576,  'C', 'A', ['CYP1A2']),
 ('ALDH2',   'chr12', 111803962, 'G', 'A', ['ALDH2']),
 ('ACTN3',   'chr11', 66560624,  'C', 'T', ['ACTN3']),
 ('HERC2',   'chr15', 28120472,  'A', 'G', ['OCA2', 'HERC2']),
 ('TAS2R38', 'chr7',  141973545, 'C', 'G', ['TAS2R38']),
 ('MC1R',    'chr16', 89919709,  'C', 'T', ['MC1R']),
 ('ABCC11',  'chr16', 48224287,  'C', 'T', ['ABCC11']),
 ('OR6A2',   'chr11', 6868417,   'C', 'A', ['OR6A2', 'OR10A2']),
 ('FUT2',    'chr19', 48703417,  'G', 'A', ['FUT2']),
]

os.makedirs('data', exist_ok=True)
client = atlas.create(KEY, timeout=600)

def with_retry(fn, tries=6):
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            msg = str(e)
            if 'RESOURCE_EXHAUSTED' in msg or 'Quota' in msg:
                wait = 65
                print(f'  quota hit, sleeping {wait}s', flush=True); time.sleep(wait)
            else:
                raise
    raise RuntimeError('retries exhausted')

for gid, ch, pos, ref, alt, targets in GENES:
    out_region = f'data/{gid}_region.parquet'
    if not os.path.exists(out_region):
        print(f'[{gid}] region ±{WIN}', flush=True)
        iv = genome.Interval(chromosome=ch, start=pos - WIN, end=pos + WIN)
        t = time.time()
        res = with_retry(lambda: client.query_interval(iv, requested_scorers=['AVI_SCORE', 'AVI_SCORE_FEATURE_IMPORTANCE'], progress_bar=False, max_workers=2))
        avi, fi = res['AVI_SCORE'], res['AVI_SCORE_FEATURE_IMPORTANCE']
        df = pd.DataFrame({'variant': [str(v) for v in avi.obs['variant']], 'avi': np.asarray(avi.X).ravel(), 'q': np.asarray(avi.layers['quantiles']).ravel()})
        fdf = pd.DataFrame(np.asarray(fi.X), columns=[n.lower() for n in fi.var['name']]); fdf['variant'] = [str(v) for v in fi.obs['variant']]
        df = df.merge(fdf, on='variant', how='left')
        parts = df['variant'].str.split(':', expand=True)
        df['pos'] = parts[1].astype(int); df['ref'] = parts[2].str[0]; df['alt'] = parts[2].str[-1]
        df = df.sort_values(['pos', 'alt']).reset_index(drop=True)
        df.to_parquet(out_region, index=False)
        print(f'  {len(df)} SNVs in {time.time()-t:.1f}s; AVI q>0.99: {(df.q>0.99).mean():.3%}', flush=True)
        time.sleep(8)

    out_f = f'data/{gid}_famous.json'
    if not os.path.exists(out_f):
        print(f'[{gid}] famous variant', flush=True)
        v = genome.Variant(chromosome=ch, position=pos, reference_bases=ref, alternate_bases=alt)
        res = with_retry(lambda: client.query_variant(v, requested_scorers=['AVI_SCORE', 'AVI_SCORE_FEATURE_IMPORTANCE', 'RNA_SEQ', 'SPLICE_SITES'], gene_names=targets))
        rec = {'variant': f'{ch}:{pos}:{ref}>{alt}', 'targets': targets,
               'avi': float(res['AVI_SCORE'].X[0, 0]), 'q': float(res['AVI_SCORE'].layers['quantiles'][0, 0]),
               'feature_importance': {n.lower(): float(x) for n, x in zip(res['AVI_SCORE_FEATURE_IMPORTANCE'].var['name'], np.asarray(res['AVI_SCORE_FEATURE_IMPORTANCE'].X).ravel())}}
        if 'RNA_SEQ' in res:
            ad = res['RNA_SEQ']
            rows = []
            for i, g in enumerate(ad.obs['gene_name']):
                for j, (name, bio, gt, src) in enumerate(zip(ad.var['name'], ad.var['biosample_name'], ad.var['gtex_tissue'], ad.var['data_source'])):
                    rows.append({'gene': g, 'track': name, 'biosample': bio, 'gtex': None if pd.isna(gt) else gt, 'source': src,
                                 'effect': float(ad.X[i, j]), 'q': float(ad.layers['quantiles'][i, j]) if 'quantiles' in ad.layers else None})
            rec['rna_seq'] = rows
        if 'SPLICE_SITES' in res:
            ad = res['SPLICE_SITES']; rec['splice_sites'] = {n: float(x) for n, x in zip(ad.var['name'], np.asarray(ad.X).ravel())}
        json.dump(rec, open(out_f, 'w'), ensure_ascii=False)
        print(f'  AVI={rec["avi"]:.3f} q={rec["q"]:.4f}', flush=True)
        time.sleep(3)
print('done')
