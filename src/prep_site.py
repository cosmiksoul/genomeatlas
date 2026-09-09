"""Build site_data.json from pulled Atlas data + Ensembl gene structures."""
import json, os, time
import numpy as np, pandas as pd, requests

GENES = [
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
WIN = 5000; ZOOM = 150

# ---- Ensembl: canonical transcript exons for genes overlapping window ----
ENS = 'https://rest.ensembl.org'
def ensembl_structs(ch, pos):
    cache = f'data/ens_{ch}_{pos}.json'
    if os.path.exists(cache):
        return json.load(open(cache))
    r = requests.get(f'{ENS}/overlap/region/human/{ch[3:]}:{pos-WIN}-{pos+WIN}?feature=gene', headers={'Content-Type': 'application/json'}, timeout=30).json()
    out = []
    for g in r:
        if g.get('biotype') != 'protein_coding' and not g.get('external_name', '').startswith(('OR', 'TAS2R')):
            continue
        time.sleep(0.3)
        d = requests.get(f"{ENS}/lookup/id/{g['id']}?expand=1", headers={'Content-Type': 'application/json'}, timeout=30).json()
        tr = [t for t in d.get('Transcript', []) if t.get('is_canonical')] or d.get('Transcript', [])[:1]
        exons = [(e['start'], e['end']) for e in tr[0]['Exon']] if tr else []
        cds = None
        if tr and tr[0].get('Translation'):
            cds = (tr[0]['Translation']['start'], tr[0]['Translation']['end'])
        out.append({'name': d.get('display_name', g['id']), 'start': d['start'], 'end': d['end'], 'strand': d['strand'], 'exons': sorted(exons), 'cds': cds})
    json.dump(out, open(cache, 'w'))
    return out

FEATURE_GROUPS = {
 'Белок (аминокислота)': ['alphamissense'],
 'Белок (обрыв/старт/стоп)': ['protein_termination', 'start_lost', 'stop_lost'],
 'Сплайсинг': ['merged_splicing'],
 'Консервативность': ['cactus_241_way', 'phastcons_470_way'],
 'Открытость хроматина': ['max_abs_atac', 'max_abs_dnase', 'max_abs_chip_histone'],
 'Белки-регуляторы': ['max_abs_chip_tf'],
 'Старт транскрипции': ['max_abs_cage', 'max_abs_procap'],
 'Уровень РНК': ['max_abs_rna_seq', 'max_abs_polyadenylation'],
 '3D-контакты ДНК': ['max_abs_contact_maps'],
}

TISSUE_RU = {
 'liver': 'Печень', 'right lobe of liver': 'Печень (правая доля)', 'left lobe of liver': 'Печень (левая доля)', 'colonic mucosa': 'Слизистая толстой кишки',
 'left colon': 'Толстая кишка (левая)', 'mucosa of descending colon': 'Слизистая нисходящей кишки', 'transverse colon': 'Поперечная кишка', 'sigmoid colon': 'Сигмовидная кишка',
 'small intestine': 'Тонкий кишечник', 'ileum': 'Подвздошная кишка', 'duodenum': 'Двенадцатиперстная кишка', 'stomach': 'Желудок', 'esophagus mucosa': 'Слизистая пищевода',
 'gastrocnemius medialis': 'Икроножная мышца', 'skeletal muscle myoblast': 'Миобласты скелетной мышцы', 'skeletal muscle tissue': 'Скелетная мышца', 'muscle of leg': 'Мышца ноги', 'psoas muscle': 'Поясничная мышца',
 'urinary bladder': 'Мочевой пузырь', 'heart left ventricle': 'Сердце (левый желудочек)', 'right atrium auricular region': 'Сердце (правое предсердие)', 'lung': 'Лёгкое', 'upper lobe of left lung': 'Лёгкое (верхняя доля)',
 'brain': 'Мозг', 'cerebellum': 'Мозжечок', 'frontal cortex': 'Лобная кора', 'hippocampus': 'Гиппокамп', 'hypothalamus': 'Гипоталамус', 'spinal cord': 'Спинной мозг', 'tibial nerve': 'Большеберцовый нерв',
 'kidney': 'Почка', 'renal cortical epithelial cell': 'Эпителий коры почки', 'adrenal gland': 'Надпочечник', 'thyroid gland': 'Щитовидная железа', 'pancreas': 'Поджелудочная', 'body of pancreas': 'Поджелудочная',
 'spleen': 'Селезёнка', 'venous blood': 'Венозная кровь', 'natural killer cell': 'NK-клетки', 'immature natural killer cell': 'Незрелые NK-клетки', 'naive B cell': 'Наивные B-клетки', 'T-cell': 'T-клетки', 'CD4-positive, alpha-beta T cell': 'CD4 T-клетки', 'CD8-positive, alpha-beta T cell': 'CD8 T-клетки', 'B cell': 'B-клетки', 'peripheral blood mononuclear cell': 'Мононуклеары крови', 'monocyte': 'Моноциты', 'neutrophil': 'Нейтрофилы',
 'skin of body': 'Кожа', 'suprapubic skin': 'Кожа (лобковая)', 'lower leg skin': 'Кожа голени', 'keratinocyte': 'Кератиноциты', 'foreskin melanocyte': 'Меланоциты', 'melanocyte of skin': 'Меланоциты кожи', 'fibroblast of skin of abdomen': 'Фибробласты кожи',
 'omental fat pad': 'Сальник (жировая ткань)', 'mesenteric fat pad': 'Брыжеечный жир', 'subcutaneous adipose tissue': 'Подкожный жир', 'adipose tissue': 'Жировая ткань',
 'luminal epithelial cell of mammary gland': 'Эпителий молочной железы', 'breast epithelium': 'Эпителий груди', 'mammary gland': 'Молочная железа',
 'tracheal epithelial cell': 'Эпителий трахеи', 'nasal cavity respiratory epithelium epithelial cell of viscerocranial mucosa': 'Эпителий носовой полости', 'bronchial epithelial cell': 'Эпителий бронхов',
 'ovary': 'Яичник', 'uterus': 'Матка', 'testis': 'Яичко', 'prostate gland': 'Простата', 'vagina': 'Влагалище', 'placenta': 'Плацента',
 'ascending aorta': 'Аорта', 'coronary artery': 'Коронарная артерия', 'tibial artery': 'Большеберцовая артерия', 'thoracic aorta': 'Грудная аорта',
 'HepG2': 'HepG2 (линия клеток печени)', 'K562': 'K562 (линия клеток крови)', 'GM12878': 'GM12878 (лимфобласты)', 'IMR-90': 'IMR-90 (фибробласты лёгкого)', 'H1': 'H1 (стволовые клетки)',
}

TISSUE_RU.update({
 'A172':'A172 (глиобластома, линия)','AG04450':'AG04450 (фибробласты лёгкого)','BE2C':'BE2C (нейробластома, линия)','BJ':'BJ (фибробласты кожи)','BLaER1':'BLaER1 (лейкоз, линия)','Caki2':'Caki2 (рак почки, линия)','GM23248':'GM23248 (фибробласты кожи)','GM23338':'GM23338 (iPS-клетки)','H4':'H4 (нейроглиома, линия)','HT-29':'HT-29 (рак толстой кишки, линия)','Jurkat, Clone E6-1':'Jurkat (T-лейкоз, линия)','M059J':'M059J (глиобластома, линия)','NCI-H460':'NCI-H460 (рак лёгкого, линия)','PC-3':'PC-3 (рак простаты, линия)','PC-9':'PC-9 (рак лёгкого, линия)','PFSK-1':'PFSK-1 (опухоль мозга, линия)','RPMI7951':'RPMI7951 (меланома, линия)','SK-MEL-5':'SK-MEL-5 (меланома, линия)','SK-N-SH':'SK-N-SH (нейробластома, линия)','U-87 MG':'U-87 MG (глиобластома, линия)',
 'CD4-positive, CD25-positive, alpha-beta regulatory T cell':'Регуляторные T-клетки','CD8-positive, alpha-beta memory T cell':'CD8 T-клетки памяти','IgD-negative memory B cell':'B-клетки памяти','naive thymus-derived CD8-positive, alpha-beta T cell':'Наивные CD8 T-клетки','common myeloid progenitor, CD34-positive':'Миелоидные предшественники (CD34+)','hematopoietic multipotent progenitor cell':'Кроветворные предшественники',
 "Peyer's patch":'Пейеровы бляшки (кишечник)','large intestine':'Толстая кишка','aorta':'Аорта','mucosa of gallbladder':'Слизистая желчного пузыря','hepatocyte':'Гепатоциты (клетки печени)','airway epithelial cell':'Эпителий дыхательных путей','anterior lingual gland':'Железа языка','astrocyte':'Астроциты (мозг)','bronchial smooth muscle cell':'Гладкие мышцы бронхов','endocrine pancreas':'Островки поджелудочной','endothelial cell of umbilical vein':'Эндотелий пупочной вены','esophagus squamous epithelium':'Эпителий пищевода','fibroblast of lung':'Фибробласты лёгкого','fibroblast of skin of back':'Фибробласты кожи спины','fibroblast of skin of scalp':'Фибробласты кожи головы','forelimb muscle':'Мышца руки','hindlimb muscle':'Мышца ноги','muscle of arm':'Мышца плеча','muscle of back':'Мышца спины','muscle of trunk':'Мышца туловища','myocyte':'Миоциты (мышечные клетки)','myotube':'Миотрубочки (мышца)','hair follicular keratinocyte':'Кератиноциты волосяного фолликула','heart':'Сердце','kidney epithelial cell':'Эпителий почки','left lung':'Лёгкое (левое)','lower lobe of left lung':'Лёгкое (нижняя доля, левое)','lower lobe of right lung':'Лёгкое (нижняя доля, правое)','upper lobe of right lung':'Лёгкое (верхняя доля, правое)','mammary epithelial cell':'Эпителий молочной железы','mammary stem cell':'Стволовые клетки молочной железы','myoepithelial cell of mammary gland':'Миоэпителий молочной железы','mesenchymal stem cell':'Мезенхимальные стволовые клетки','mesenchymal stem cell of the bone marrow':'Стволовые клетки костного мозга','smooth muscle cell':'Гладкомышечные клетки','tongue':'Язык',
})

def tissue_ru(name):
    if name in TISSUE_RU: return TISSUE_RU[name]
    return name

site = {'win': WIN, 'zoom': ZOOM, 'genes': {}}
for gid, ch, pos, ref, alt, targets in GENES:
    reg = pd.read_parquet(f'data/{gid}_region.parquet')
    fam = json.load(open(f'data/{gid}_famous.json'))
    structs = ensembl_structs(ch, pos)
    # per-position max quantile & max avi
    per_pos = reg.groupby('pos').agg(q=('q', 'max'), avi=('avi', 'max')).reindex(range(pos - WIN, pos + WIN)).fillna(0)
    strip_q = (per_pos.q.values * 99).round().astype(int).tolist()
    # zoom matrix
    z = reg[(reg.pos >= pos - ZOOM) & (reg.pos <= pos + ZOOM)]
    zoom = [[int(r.pos - pos), r.alt, round(float(r.avi), 3), round(float(r.q), 4)] for r in z.itertuples()]
    refbase = {int(r.pos - pos): r.ref for r in z.itertuples()}
    # feature groups for famous variant
    fi = fam['feature_importance']; groups = {k: float(sum(fi.get(f, 0) for f in v)) for k, v in FEATURE_GROUPS.items()}
    tot = sum(groups.values()) or 1
    groups = {k: round(v / tot, 4) for k, v in groups.items()}
    # tissues: main target gene, tissue-type tracks first
    rna = pd.DataFrame(fam['rna_seq']); main = targets[0]
    rna = rna[rna.gene == main].copy()
    rna['label'] = rna.biosample.map(tissue_ru)
    rna = rna.reindex(rna.effect.abs().sort_values(ascending=False).index).drop_duplicates('label').head(14)
    tissues = [{'t': r.label, 'raw': r.biosample, 'e': round(float(r.effect), 4), 'q': None if r.q is None or (isinstance(r.q, float) and np.isnan(r.q)) else round(float(r.q), 3)} for r in rna.itertuples()]
    # stats
    share99 = float((reg.q > 0.99).mean()); share95 = float((reg.q > 0.95).mean())
    above = float((reg.avi > fam['avi']).mean())
    site['genes'][gid] = {
        'chrom': ch, 'pos': pos, 'ref': ref, 'alt': alt, 'targets': targets,
        'famous': {'avi': round(fam['avi'], 3), 'q': round(fam['q'], 4), 'groups': groups, 'share_above': round(above, 4)},
        'strip_q': strip_q, 'zoom': zoom, 'zoom_ref': refbase,
        'structs': structs, 'tissues': tissues,
        'share99': round(share99, 4), 'share95': round(share95, 4), 'n': int(len(reg)),
        'avi_hist': np.histogram(reg.avi, bins=np.linspace(-0.6, 2.4, 31))[0].tolist(),
    }
    print(gid, f'share99={share99:.1%} above_famous={above:.1%} structs={[s["name"] for s in structs]}')

json.dump(site, open('site_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('size', os.path.getsize('site_data.json') // 1024, 'KB')

TISSUE_RU.update({
 "Ammon's horn":'Аммонов рог (гиппокамп)','CD14-positive monocyte':'CD14 моноциты','Caco-2':'Caco-2 (модель кишечного эпителия)','Calu3':'Calu3 (линия, лёгкое)','HCT116':'HCT116 (рак толстой кишки, линия)','HEK293':'HEK293 (эмбриональная почка, линия)','HEK293T':'HEK293T (линия)','HL-60':'HL-60 (лейкоз, линия)','HeLa-S3':'HeLa (линия)','LoVo':'LoVo (рак толстой кишки, линия)','MCF-7':'MCF-7 (рак груди, линия)','MCF 10A':'MCF 10A (эпителий груди, линия)','Panc1':'Panc1 (рак поджелудочной, линия)','SW480':'SW480 (рак толстой кишки, линия)','THP-1':'THP-1 (моноциты, линия)','VCaP':'VCaP (рак простаты, линия)','A549':'A549 (рак лёгкого, линия)',
 'Right ventricle myocardium inferior':'Миокард правого желудочка','Right ventricle myocardium superior':'Миокард правого желудочка (верх)','left ventricle myocardium inferior':'Миокард левого желудочка','left ventricle myocardium superior':'Миокард левого желудочка (верх)','right cardiac atrium':'Правое предсердие','pulmonary valve':'Лёгочный клапан','mesothelial cell of epicardium':'Мезотелий эпикарда','artery':'Артерия','thoracic aorta':'Грудная аорта','umbilical cord':'Пуповина',
 'T-helper 17 cell':'Th17-клетки','gamma-delta T cell':'γδ-T-клетки','central memory CD8-positive, alpha-beta T cell':'CD8 T-клетки памяти','effector memory CD8-positive, alpha-beta T cell':'CD8 эффекторные T-клетки','naive thymus-derived CD4-positive, alpha-beta T cell':'Наивные CD4 T-клетки','memory B cell':'B-клетки памяти','immature conventional dendritic cell':'Дендритные клетки','plasmacytoid dendritic cell':'Плазмоцитоидные дендритные клетки','bone marrow':'Костный мозг','bone marrow cell':'Клетки костного мозга','lymph node':'Лимфоузел','thymus':'Тимус',
 'adipocyte of omentum tissue':'Адипоциты сальника','fat cell':'Жировые клетки','chondrocyte':'Хондроциты (хрящ)','cruciate ligament of knee':'Крестообразная связка','synovial cell':'Синовиальные клетки','nucleus pulposus cell of intervertebral disc':'Клетки межпозвонкового диска','fibroblast of dermis':'Фибробласты дермы','fibroblast of gingiva':'Фибробласты десны','lung fibroblast':'Фибробласты лёгкого','nail plate':'Ногтевая пластина','skin of palm of manus':'Кожа ладони','foreskin keratinocyte':'Кератиноциты','light melanocyte':'Меланоциты (светлые)',
 'angular gyrus':'Угловая извилина','cingulate gyrus':'Поясная извилина','middle temporal gyrus':'Средняя височная извилина','paracentral gyrus':'Парацентральная извилина','postcentral gyrus':'Постцентральная извилина','temporal lobe':'Височная доля','occipital pole':'Затылочный полюс','dorsolateral prefrontal cortex':'Префронтальная кора','cerebellar cortex':'Кора мозжечка','caudate nucleus':'Хвостатое ядро','nucleus accumbens':'Прилежащее ядро','globus pallidus':'Бледный шар','substantia nigra':'Чёрная субстанция','corpus callosum':'Мозолистое тело','layer of hippocampus':'Гиппокамп','pons':'Мост мозга','pineal body':'Эпифиз','meninx':'Мозговая оболочка','cerebrospinal fluid':'Спинномозговая жидкость','cranial nerve II':'Зрительный нерв','motor neuron':'Мотонейроны','neuron':'Нейроны','neuronal stem cell':'Нейральные стволовые клетки','neurosphere':'Нейросферы','brain pericyte':'Перициты мозга','central nervous system pericyte':'Перициты ЦНС','olfactory region':'Обонятельная область','retina':'Сетчатка','retinal pigment epithelial cell':'Пигментный эпителий сетчатки','camera-type eye':'Глаз','vitreous humor':'Стекловидное тело',
 'inferior rectus extraocular muscle':'Глазодвигательная мышца','lateral rectus extra-ocular muscle':'Глазодвигательная мышца (латеральная)','medial rectus extraocular muscle':'Глазодвигательная мышца (медиальная)','superior rectus extraocular muscle':'Глазодвигательная мышца (верхняя)','cell of skeletal muscle':'Клетки скелетной мышцы','skeletal muscle cell':'Клетки скелетной мышцы','skeletal muscle satellite cell':'Сателлитные клетки мышцы','left forelimb':'Мышца руки (эмбрион)','smooth muscle tissue':'Гладкая мышечная ткань','enteric smooth muscle cell':'Гладкие мышцы кишечника','muscle layer of duodenum':'Мышечный слой 12-перстной кишки',
 'colon':'Толстая кишка','duodenal mucosa':'Слизистая 12-перстной кишки','mucosa of rectum':'Слизистая прямой кишки','intestinal epithelial cell':'Эпителий кишечника','vermiform appendix':'Аппендикс','esophagus':'Пищевод','epithelial cell of esophagus':'Эпителий пищевода','gallbladder':'Желчный пузырь','bile duct':'Желчный проток','parotid gland':'Околоушная железа','submandibular gland':'Подчелюстная железа','saliva-secreting gland':'Слюнная железа','fungiform papilla':'Грибовидные сосочки языка','trachea':'Трахея',
 'epididymis':'Придаток яичка','seminal vesicle':'Семенной пузырёк','vas deferens':'Семявыносящий проток','penis':'Половой член','epithelial cell of prostate':'Эпителий простаты','amniotic epithelial cell':'Амниотический эпителий',
 'ectodermal cell':'Эктодермальные клетки','mesodermal cell':'Мезодермальные клетки','mesendoderm':'Мезэндодерма','nephron progenitor cell':'Предшественники нефрона','H7':'H7 (эмбриональные стволовые)','HUES6':'HUES6 (эмбриональные стволовые)','WTC11':'WTC11 (iPS-клетки)','iPS DF 19.11':'iPS-клетки','iPS DF 6.9':'iPS-клетки','iPS-15b':'iPS-клетки','iPS-20b':'iPS-клетки',
})
