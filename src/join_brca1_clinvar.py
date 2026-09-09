"""ClinVar esummary → per-allele таблица → join с Atlas (data/brca1/*.parquet). Выход: data/brca1_clinvar_joined.parquet"""
import json, re, glob, pandas as pd
out = json.load(open('data/brca1_clinvar_esummary.json')); rows = []
for v in out:
    vs = v.get('variation_set', [{}])[0]; m = re.match(r'NC_000017\.11:(\d+):([ACGT]):([ACGT])$', vs.get('canonical_spdi', ''))
    if not m: continue
    gc = v.get('germline_classification', {}); name = vs.get('variation_name', ''); prot = re.search(r'\((p\.[^)]+)\)', name)
    rows.append({'cvid': v['uid'], 'pos': int(m.group(1)) + 1, 'ref': m.group(2), 'alt': m.group(3), 'desc': gc.get('description', ''), 'review': gc.get('review_status', ''),
                 'name': name, 'cdna': vs.get('cdna_change', ''), 'prot': prot.group(1) if prot else ''})
cv = pd.DataFrame(rows)
def cls(d):
    d = d.lower()
    if 'conflicting' in d: return 'conflict'
    if 'pathogenic' in d and 'benign' not in d: return 'P'
    if 'benign' in d and 'pathogenic' not in d: return 'B'
    if 'uncertain' in d: return 'VUS'
    return 'other'
def conseq(name, prot):
    if 'c.-' in name or 'c.*' in name: return 'UTR'
    m = re.search(r'c\.\d+([+-])(\d+)', name)
    if m: return 'splice_site' if int(m.group(2)) <= 2 else 'intron'
    if 'Ter' in prot: return 'nonsense'
    if '=' in prot: return 'synonymous'
    if prot.startswith('p.'): return 'missense'
    return 'other'
cv['cls'] = cv.desc.map(cls); cv['cons'] = [conseq(n, p) for n, p in zip(cv.name, cv.prot)]
cv['variant'] = 'chr17:' + cv.pos.astype(str) + ':' + cv.ref + '>' + cv.alt
atl = pd.concat([pd.read_parquet(f) for f in glob.glob('data/brca1/*.parquet')]).drop_duplicates('variant')
j = cv.merge(atl, on='variant', how='inner', suffixes=('', '_a'))
j.to_parquet('data/brca1_clinvar_joined.parquet', index=False); print('joined', len(j), j.cls.value_counts().to_dict())
