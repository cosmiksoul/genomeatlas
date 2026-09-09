"""Внешние источники для историй 03 и 04 (BRCA1): Ensembl (структура гена), ClinVar (E-utilities), gnomAD (GraphQL), MaveDB (SGE Findlay 2018).
Запускать до prep_brca1.py / prep_finale.py. Все запросы — публичные API без ключей."""
import requests, json, time, os, io, re
import pandas as pd
from prep_site import GENES
H = {'Content-Type': 'application/json'}
os.makedirs('data', exist_ok=True)

# 1. Ensembl: BRCA1, канонический транскрипт
if not os.path.exists('data/brca1_gene.json'):
    g = requests.get('https://rest.ensembl.org/lookup/symbol/homo_sapiens/BRCA1?expand=1', headers=H, timeout=60).json()
    can = [t for t in g['Transcript'] if t.get('is_canonical')][0]
    json.dump({'start': g['start'], 'end': g['end'], 'strand': g['strand'], 'exons': [(e['start'], e['end']) for e in can['Exon']],
               'cds': (can['Translation']['start'], can['Translation']['end'])}, open('data/brca1_gene.json', 'w'))
    print('ensembl ok', can['id'])
G = json.load(open('data/brca1_gene.json'))

# 2. ClinVar: все SNV по BRCA1 через esearch + esummary (per-allele canonical SPDI)
if not os.path.exists('data/brca1_clinvar_esummary.json'):
    E = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    term = 'BRCA1[gene] AND "single nucleotide variant"[Type]'
    n = int(requests.get(E + 'esearch.fcgi', params={'db': 'clinvar', 'term': term, 'retmax': 0, 'retmode': 'json'}, timeout=60).json()['esearchresult']['count'])
    ids = requests.get(E + 'esearch.fcgi', params={'db': 'clinvar', 'term': term, 'retmax': n, 'retmode': 'json'}, timeout=120).json()['esearchresult']['idlist']
    out = []
    for i in range(0, len(ids), 400):
        s = requests.get(E + 'esummary.fcgi', params={'db': 'clinvar', 'id': ','.join(ids[i:i + 400]), 'retmode': 'json'}, timeout=120).json()
        out += [v for k, v in s['result'].items() if k != 'uids']; time.sleep(0.4)
    json.dump(out, open('data/brca1_clinvar_esummary.json', 'w'))
    print('clinvar ok', len(out))

# 3. gnomAD v4: все SNV в регионе (BRCA1 ±2 кб и окна ±5 кб десяти генов)
def gnomad(ch, a, b):
    rows = []
    for s in range(a, b, 20000):
        e = min(s + 20000, b)
        q = '{ region(chrom:"%s", start:%d, stop:%d, reference_genome:GRCh38){ variants(dataset:gnomad_r4){ pos ref alt genome{ac an} exome{ac an} } } }' % (ch, s, e)
        for _ in range(4):
            d = requests.post('https://gnomad.broadinstitute.org/api', json={'query': q}, timeout=180).json()
            if d.get('data', {}).get('region'): break
            time.sleep(5)
        for v in d['data']['region']['variants']:
            if len(v['ref']) != 1 or len(v['alt']) != 1: continue
            ac = (v['genome'] or {}).get('ac', 0) + (v['exome'] or {}).get('ac', 0); an = max((v['genome'] or {}).get('an', 0), (v['exome'] or {}).get('an', 0))
            rows.append({'variant': f"chr{ch}:{v['pos']}:{v['ref']}>{v['alt']}", 'ac': ac, 'an': an})
        time.sleep(1)
    return pd.DataFrame(rows)
if not os.path.exists('data/gnomad_brca1.parquet'):
    gnomad('17', G['start'] - 2000, G['end'] + 2000).to_parquet('data/gnomad_brca1.parquet'); print('gnomad brca1 ok')
for gid, ch, pos, *_ in GENES:
    f = f'data/gnomad_{gid}.parquet'
    if not os.path.exists(f): gnomad(ch[3:], pos - 5000, pos + 5000).to_parquet(f); print('gnomad', gid)

# 4. MaveDB: нормализованные оценки SGE (Findlay 2018), meta-analysis score set
if not os.path.exists('data/brca1_sge_scores.csv'):
    urn = 'urn:mavedb:00000097-0-2'
    s = requests.get(f'https://api.mavedb.org/api/v1/score-sets/{urn}/scores', timeout=120)
    pd.read_csv(io.StringIO(s.text)).to_csv('data/brca1_sge_scores.csv', index=False); print('mavedb ok')
print('done')
