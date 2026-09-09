import pandas as pd, numpy as np, json, re, glob
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from prep_site import GENES

# ---- SGE mapping (Findlay 2018 via MaveDB urn:mavedb:00000097-0-2) ----
G = json.load(open('data/brca1_gene.json')); ex = sorted(G['exons'], reverse=True)
cum = []; acc = 0
for a, b in ex: cum.append(acc); acc += b - a + 1
def g2c(pos):
    for (a, b), c0 in zip(ex, cum):
        if a <= pos <= b: return c0 + (b - pos) + 1
cds1 = g2c(43124096)
def c2g(n):
    cd = cds1 + n - 1
    for (a, b), c0 in zip(ex, cum):
        if c0 < cd <= c0 + (b - a + 1): return b - (cd - c0 - 1)
comp = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
sge0 = pd.read_csv('data/brca1_sge_scores.csv'); rows = []
for r in sge0.itertuples():
    m = re.match(r'NM_007294\.3:c\.(\d+)([+-]\d+)?([ACGT])>([ACGT])$', r.hgvs_nt)
    if not m: continue
    g = c2g(int(m.group(1)))
    if g is None: continue
    g -= int(m.group(2)) if m.group(2) else 0
    kind = 'splice/intron' if m.group(2) else 'coding'
    rows.append({'hgvs': r.hgvs_nt.replace('NM_007294.3:', ''), 'score': r.score, 'kind': kind, 'variant': f'chr17:{g}:{comp[m.group(3)]}>{comp[m.group(4)]}'})
sge = pd.DataFrame(rows).dropna(subset=['score'])
atl = pd.concat([pd.read_parquet(f) for f in glob.glob('data/brca1/*.parquet')]).drop_duplicates('variant')
sge = sge.merge(atl[['variant', 'avi', 'q', 'pos']], on='variant')
_cv = pd.read_parquet('data/brca1_clinvar_joined.parquet')[['variant', 'cons']].drop_duplicates('variant')
sge = sge.merge(_cv, on='variant', how='left'); sge['kind'] = sge.cons.fillna(sge.kind); sge = sge.drop(columns=['cons'])
sge['cls'] = np.where(sge.score < -1.328, 'nonfunc', np.where(sge.score > -0.748, 'func', 'inter'))
sge.to_parquet('data/brca1_sge_joined.parquet', index=False)

gn = pd.read_parquet('data/gnomad_brca1.parquet'); cv = pd.read_parquet('data/brca1_clinvar_joined.parquet')
obs = set(gn.variant); cvs = set(cv.variant); exp = set(cv[cv.review.str.contains('expert')].variant); sg = set(sge.variant)
N = len(atl)
d = sge[sge.cls != 'inter']
auc_all = roc_auc_score(d.cls == 'nonfunc', d.q)
dm = d[d.kind == 'missense']; auc_mis = roc_auc_score(dm.cls == 'nonfunc', dm.q)
rho = spearmanr(sge.q, sge.score).statistic
# SGE vs clinvar verdict agreement for the same variants
jj = sge.merge(cv[['variant', 'cls', 'review']].rename(columns={'cls': 'cv'}), on='variant', how='left')
sge_cv = jj[jj.cv.isin(['P', 'B']) & (jj.cls != 'inter')]
agree = ((sge_cv.cv == 'P') == (sge_cv.cls == 'nonfunc')).mean()
atl['qb'] = pd.cut(atl.q, [0, .5, .9, .99, .999, 1.0001], labels=['<0.5', '0.5–0.9', '0.9–0.99', '0.99–0.999', '>0.999'])
obs_by_q = atl.groupby('qb', observed=True).variant.apply(lambda v: float(v.isin(obs).mean())).to_dict()
n_by_q = atl.groupby('qb', observed=True).size().to_dict()
funnel = {
 'possible': N, 'observed': len(obs), 'clinvar': len(cvs), 'classified': int(cv.cls.isin(['P', 'B', 'VUS', 'conflict']).sum()),
 'expert': len(exp), 'sge': len(sg), 'sge_observed': len(sg & obs), 'sge_clinvar': len(sg & cvs), 'clinvar_unobserved': len(cvs - obs),
 'top1': int((atl.q >= .99).sum()), 'top1_observed': int(atl[atl.q >= .99].variant.isin(obs).sum()), 'top1_clinvar': int(atl[atl.q >= .99].variant.isin(cvs).sum()), 'top1_expert': int(atl[atl.q >= .99].variant.isin(exp).sum()), 'top1_sge': int(atl[atl.q >= .99].variant.isin(sg).sum()),
 'singleton_share': float((gn.ac == 1).mean()),
 'obs_by_q': {str(k): round(v, 4) for k, v in obs_by_q.items()}, 'n_by_q': {str(k): int(v) for k, v in n_by_q.items()},
}
genes = []
for gid, *_ in GENES:
    a = pd.read_parquet(f'data/{gid}_region.parquet'); g = pd.read_parquet(f'data/gnomad_{gid}.parquet'); o = set(g.variant)
    genes.append({'gene': gid, 'n': len(a), 'observed': round(float(a.variant.isin(o).mean()), 4), 'top1_n': int((a.q >= .99).sum()), 'top1_observed': round(float(a[a.q >= .99].variant.isin(o).mean()), 4)})
sge_stats = {'n': len(sge), 'auc': round(auc_all, 4), 'auc_missense': round(auc_mis, 4), 'n_missense': int(len(dm)), 'rho': round(float(rho), 3),
             'cls': {k: int(v) for k, v in sge.cls.value_counts().items()}, 'kind': {k: int(v) for k, v in sge.kind.value_counts().items()},
             'nonfunc_below99': round(float((sge[sge.cls == 'nonfunc'].q < .99).mean()), 4), 'func_above999': round(float((sge[sge.cls == 'func'].q >= .999).mean()), 4),
             'with_clinvar_PB': int(len(sge_cv)), 'sge_clinvar_agree': round(float(agree), 4),
             'median_q': {k: round(float(v), 4) for k, v in sge.groupby('cls').q.median().items()}}
pts = [[round(float(r.score), 3), round(float(r.q), 4), r.kind, r.hgvs, r.cls] for r in sge.itertuples()]
# examples: worst disagreements
ex_nf_low = sge[sge.cls == 'nonfunc'].sort_values('q').head(6)[['hgvs', 'kind', 'score', 'q']].round(3).values.tolist()
ex_f_high = sge[sge.cls == 'func'].sort_values('q', ascending=False).head(6)[['hgvs', 'kind', 'score', 'q']].round(4).values.tolist()
json.dump({'funnel': funnel, 'genes': genes, 'sge': sge_stats, 'sge_points': pts, 'ex_nf_low': ex_nf_low, 'ex_f_high': ex_f_high}, open('finale_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(json.dumps(funnel, ensure_ascii=False, indent=1)); print(json.dumps(sge_stats, ensure_ascii=False, indent=1)); print(pd.DataFrame(genes).to_string()); print(ex_nf_low); print(ex_f_high)
