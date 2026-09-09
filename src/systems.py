import re
# organ-system mapping for biosample names (ENCODE/GTEx/FANTOM/4DN). Order matters: first match wins.
RULES = [
( 'ЖКТ', r'saliv|parotid|submandibular|lingual|tongue|mouth|gingiv|throat|fungiform|colon|intestin|rectum|ileum|duoden|jejun|stomach|gastr|esophag|oesophag|Peyer|caecum|cecum|colorect|LoVo|Caco|HT-29|HCT|SW480|SW620|DLD|RKO|LS174|COLO|gallbladder|bile|appendix|mucosa of'),
 ('Печень и поджелудочная', r'liver|hepat|HepG2|Hep 3B|Huh|pancrea|islet|Panc|HPDE'),
 ('Кровь и иммунитет', r'T-helper|reticulocyte|mononuclear|Langerhans|NAMALWA|KOPT|DND-41|KBM-7|HS-5|HS-27A|HG0|GM0[0-9]|blood|lymph|leuk|myelo|monocyt|macrophag|neutrophil|eosinophil|basophil|T cell|T-cell|B cell|B-cell|NK|natural killer|thymus|spleen|tonsil|bone marrow|erythro|K562|GM1|GM2|Jurkat|HL-60|Karpas|MM\.1S|OCI-LY|Loucy|KMS|HAP-1|THP-1|Raji|Daudi|BLaER|plasma|megakary|dendritic|mast cell|hematopoie|CD34|CD4|CD8|CD14|CD19|CD20|immune|Kasumi|DOHH|NB4|SU-DHL|Ramos|RPMI|U937|CMK'),
 ('Мозг, нервы и глаза', r'occipital|meninx|gyrus|lobe|Ammon|Purkinje|Schwann|oligodendro|corpus callosum|diencephal|insula|globus|locus|mening|leptomening|D721|H54|NT2|UCSF-4|eye|retin|lens|corneal|iris|ciliary|vitreous|trabecular|WERI|brain|cerebr|cortex|hippocamp|hypothalam|thalam|amygdal|putamen|caudate|nucleus accumbens|substantia|cerebell|spinal|nerve|neur|astrocyt|glia|glio|SK-N|BE2C|PFSK|H4$|M059|U-87|A172|Daoy|D341|SH-SY5Y|retina|pituitar|pons|medulla|ganglion|olfactory|choroid|dura'),
 ('Мышцы и сердце', r'valve|vena cava|diaphragm|limb|LHCN|SJCRH|femur|muscle|myo|heart|cardi|atrium|ventric|aorta|artery|arter|vein|vascul|endotheli|HUVEC|pericyte|coronary|tibial|gastrocnem|psoas|skeletal|RD$|A673|smooth'),
 ('Лёгкие и дыхание', r'pneumocyte|HCEC|ACC112|lung|bronch|trache|airway|alveol|nasal|pulmon|IMR-90|A549|NCI-H|PC-9|Calu|WI38|WI-38|AG04450|respirat'),
 ('Кожа и пигмент', r'skin|derm|keratin|melano|SK-MEL|hair|follic|foreskin|BJ$|fibroblast of skin|scalp|epiderm|A375|RPMI7951|Malme|COLO 8|SK-MEL'),
 ('Почки и мочевыделение', r'HK-2|RCC|G401|mesangial|urethra|kidney|renal|nephr|HEK293|Caki|ureter|bladder|urothel|786-O|A498|ACHN|glomerul|podocyt|proximal tubule'),
 ('Репродуктивная система', r'gonad|Sertoli|penis|vas deferens|RWPE|DU 145|C4-2B|HTR-8|amniotic|ovar|uter|endometr|cervi|vagin|placent|prostat|testi|breast|mammary|MCF|T47D|HCC1|MDA-MB|BT-|SK-BR|LNCaP|PC-3|22Rv1|VCaP|trophoblast|HeLa|Ishikawa|OVCAR|SK-OV|Caov|amnion|chorion|umbilical|decidua|seminal|epididym|fallopian|myometr|foreskin'),
 ('Эндокринная система', r'thyroid|adrenal|pituit|parathyr|pineal|endocrin'),
 ('Жир и соединительная ткань', r'adipocyt|preadipocyt|AG0|AG1|AG2|HFF|MG63|annulus|pulposus|mesothel|keratocyte|Malassez|nail|mole|sebaceous|adipos|fat|fibroblast|mesenchym|stromal|chondro|osteo|bone|cartilag|tendon|ligament|synovi|SJSA|U2OS|Saos|MG-63|HT1080|omental|mesenter|subcutaneous'),
 ('Стволовые и эмбриональные', r'ES-I3|EH$|EL$|ELF-1|ELR|L1-S8|adult organism|stem|embryo|iPS|H1$|H9$|H7$|HUES|ES cell|ESC|progenitor|blastocyst|fetal|fetus|germ|trophoblast|neural crest|mesoderm|endoderm|ectoderm|GM23338|WTC|PGP1'),
]
def system_of(name, curie=None):
    n = name or ''
    for sysname, rx in RULES:
        if re.search(rx, n, re.I):
            return sysname
    return 'Прочее'
