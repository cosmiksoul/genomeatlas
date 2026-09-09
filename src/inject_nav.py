# -*- coding: utf-8 -*-
"""Сквозное меню проекта для всех страниц + index.html."""
import re

PAGES = [
 ('index.html',   'index',   'Карта невозможного'),
 ('genes.html',   'genes',   'Гены, о которых вы слышали'),
 ('tissues.html', 'tissues', 'Одна мутация, сорок тканей'),
 ('brca1.html',   'brca1',   'Одиннадцать тысяч приговоров'),
 ('finale.html',  'finale',  'Чего никто не видел'),
]
FAVICON = '<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 16 16%22><rect width=%2216%22 height=%2216%22 fill=%22%23f5f2ec%22/><circle cx=%228%22 cy=%228%22 r=%224.5%22 fill=%22%23c4901e%22/></svg>">\n'
NAV_CSS = '''
<style>
  .pnav{display:flex;align-items:center;gap:0;border-bottom:1px solid var(--line,#d8d3c7);background:var(--paper,#f5f2ec);font:12px/1 var(--mono,Menlo,monospace);letter-spacing:.08em;text-transform:uppercase}
  .pnav .brand{padding:16px clamp(20px,6vw,90px) 16px;color:var(--ink,#17160f);text-decoration:none;font-weight:600;border-right:1px solid var(--line,#d8d3c7);white-space:nowrap}
  .pnav .brand i{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent,#c4901e);margin-right:10px;vertical-align:1px}
  .pnav a.item{padding:16px 22px;color:var(--ink-2,#5a574d);text-decoration:none;border-right:1px solid var(--line,#d8d3c7);display:flex;gap:10px;align-items:baseline;white-space:nowrap}
  .pnav a.item b{font-weight:400;color:var(--ink-3,#9a968a)}
  .pnav a.item:hover{color:var(--ink,#17160f);background:var(--paper-2,#ece8df)}
  .pnav a.item.on{color:var(--ink,#17160f);box-shadow:inset 0 -2px 0 var(--accent,#c4901e)}
  .pnav .sp{flex:1}
  .pnav .meta{padding:16px clamp(20px,6vw,90px) 16px 22px;color:var(--ink-3,#9a968a);white-space:nowrap}
  @media (max-width:900px){.pnav{flex-wrap:wrap}.pnav .meta{display:none}.pnav a.item{padding:12px 14px}.pnav .brand{padding:12px 20px;border-right:0;width:100%;border-bottom:1px solid var(--line,#d8d3c7)}}
</style>
'''
def nav_html(cur):
    items = ''.join(f'<a class="item{" on" if key==cur else ""}" href="{f}"><b>{i:02d}</b>{t}</a>' for i, (f, key, t) in enumerate(PAGES[1:], 1))
    return f'<nav class="pnav"><a class="brand" href="index.html"><i></i>Карта невозможного</a>{items}<span class="sp"></span><span class="meta">AlphaGenome Atlas · 2026</span></nav>'

def inject(path, key):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<nav class="pnav">.*?</nav>', '', s, count=1, flags=re.S)
    s = re.sub(r'<style>\n  \.pnav\{.*?</style>\n', '', s, count=1, flags=re.S)
    # старые мастхеды
    s = re.sub(r'<div class="masthead">.*?</div>\n', '', s, count=1, flags=re.S)
    if '<link rel="icon"' not in s:
        s = s.replace('</head>', FAVICON + '</head>', 1)
    s = s.replace('</head>', NAV_CSS + '</head>', 1)
    s = s.replace('<body>', '<body>\n' + nav_html(key), 1)
    open(path, 'w', encoding='utf-8').write(s)

INDEX = '''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Карта невозможного — AlphaGenome Atlas популярным языком</title>
<meta name="description" content="Четыре интерактивные истории о том, как нейросеть DeepMind предсказала эффект девяти миллиардов возможных опечаток в ДНК человека — и какую часть этого можно проверить.">
<meta property="og:title" content="Карта невозможного">
<meta property="og:description" content="AlphaGenome Atlas популярным языком: девять миллиардов опечаток в ДНК, десять «застольных» генов, ген BRCA1 против консилиума врачей — и честный финал о границах проверяемого.">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<style>
  :root{--paper:#f5f2ec;--paper-2:#ece8df;--ink:#17160f;--ink-2:#5a574d;--ink-3:#9a968a;--line:#d8d3c7;--accent:#c4901e;--accent-soft:#e9d8a8;--down:#2f6f7e;
    --serif:"Iowan Old Style","Palatino Linotype","Book Antiqua",Georgia,serif;--sans:"Helvetica Neue",Helvetica,Arial,system-ui,sans-serif;--mono:"SF Mono",Menlo,Consolas,monospace}
  *{box-sizing:border-box} body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
  .hero{padding:80px clamp(20px,6vw,90px) 40px;display:grid;grid-template-columns:minmax(300px,640px) minmax(0,1fr);gap:40px clamp(30px,5vw,90px);align-items:end}
  .hero h1{font:400 clamp(48px,7.5vw,104px)/1 var(--serif);letter-spacing:-.02em;margin:0 0 26px} .hero h1 em{font-style:italic;color:var(--accent)}
  .hero .kick{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:0 0 20px}
  .hero p{font:21px/1.5 var(--serif);color:var(--ink);margin:0} .hero .sub{font:12px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin-top:22px}
  .hero canvas{width:100%;height:auto;display:block}
  .essay{padding:50px clamp(20px,6vw,90px) 40px;border-top:1px solid var(--line);display:grid;grid-template-columns:minmax(0,660px);gap:26px}
  .blk{display:grid;grid-template-columns:150px 1fr;gap:20px;align-items:start}
  .blk h5{font:12px/1.6 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:4px 0 0}
  .blk p{font:17px/1.6 var(--serif);margin:0 0 12px} .blk p:last-child{margin:0}
  .genes{display:flex;flex-wrap:wrap;gap:6px 8px;margin:8px 0 0}
  .genes span{font:11px var(--mono);letter-spacing:.04em;padding:5px 9px;border:1px solid var(--line);border-radius:2px;color:var(--ink-2)} .genes span b{font-weight:600;color:var(--ink);margin-right:6px}
  .stories{padding:40px clamp(20px,6vw,90px) 70px;border-top:1px solid var(--line)}
  .stories h2{font:400 clamp(30px,3.8vw,48px)/1.05 var(--serif);letter-spacing:-.02em;margin:0 0 30px}
  .card{display:grid;grid-template-columns:minmax(0,360px) minmax(0,1fr);gap:20px clamp(30px,5vw,80px);align-items:start;border-top:1px solid var(--ink);padding:22px 0 34px;text-decoration:none;color:inherit}
  .card:hover h3{color:var(--accent)}
  .card .n{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
  .card h3{font:400 clamp(28px,3vw,40px)/1.05 var(--serif);letter-spacing:-.02em;margin:6px 0 12px;transition:color .2s}
  .card .k{font:11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
  .card p{font:16px/1.6 var(--serif);color:var(--ink);margin:0 0 10px} .card p:last-of-type{margin:0}
  .card p b{font-weight:400;font-style:italic;color:var(--accent)}
  .card svg{width:100%;height:auto;display:block;margin:14px 0 0}
  .card .go{font:12px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink);margin-top:14px;display:inline-block;border-bottom:1px solid var(--accent)}
  .how{padding:50px clamp(20px,6vw,90px) 90px;border-top:1px solid var(--line);display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:40px;font-size:14.5px;color:var(--ink-2);max-width:1300px}
  .how h5{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink);margin:0 0 10px} .how p{margin:0 0 10px;font-family:var(--serif);font-size:15px;line-height:1.55}
  .sw{display:inline-block;width:11px;height:11px;border-radius:2px;vertical-align:-1px;margin-right:6px}
  @media (max-width:900px){.hero,.card{grid-template-columns:1fr}.blk{grid-template-columns:1fr;gap:6px}}
</style></head>
<body>
<section class="hero">
  <div>
    <div class="kick">AlphaGenome Atlas — популярным языком</div>
    <h1>Карта <em>невозможного</em></h1>
    <p>Четыре истории о том, как нейросеть прочитала девять миллиардов возможных ошибок в ДНК человека, что из этого может понять тот, кто не биолог, — и какую часть этого вообще можно проверить.</p>
    <div class="sub">Данные: AlphaGenome Atlas, Google DeepMind · ClinVar · Ensembl · 2026</div>
  </div>
  <canvas id="field" width="1200" height="520"></canvas>
</section>

<section class="essay">
  <div class="blk"><h5>С чего всё началось</h5>
    <p>Внутри каждой вашей клетки лежит текст длиной в три миллиарда букв, и в нём, как в любом тексте, бывают опечатки. У любых двух людей их миллионы. Почти все — ничего не значат. Но некоторые решают, перевариваете ли вы молоко, краснеете ли от вина и заболеете ли раком к сорока. Беда в том, что заранее отличить пустую опечатку от важной было почти невозможно: буква посреди гена может оказаться безобидной, а буква в тысячах позиций от него — ключевой.</p>
    <p>В 2026 году DeepMind сделала то, чего нельзя сделать руками: взяла каждую из трёх миллиардов позиций генома, подставила в неё каждую из трёх «не тех» букв — девять миллиардов опечаток — и прогнала через модель AlphaGenome, которая предсказывает, что каждая из них меняет в работе клетки. Результат, петабайт предсказаний, выложили в открытый доступ под именем AlphaGenome Atlas. Мы прочитали его так, как читают большой архив: не целиком, а с вопросами.</p></div>
  <div class="blk"><h5>Почему эти гены</h5>
    <p>Мы не учёные — мы аналитики, и нам хотелось начать с генов, о которых говорят не в лаборатории, а за столом. «Ген кофе», «ген молока», «ген, из-за которого краснеют от вина», «ген спринтера», «ген кинзы». Про каждый из них есть популярная легенда и есть настоящий вариант с номером в базе. Мы взяли десять таких — и спросили у модели, что она думает о каждом. Половина легенд подтвердилась, а две модель попросту не заметила. Это стало первой историей и заодно проверкой на честность: мы обещали не подгонять картинку под легенду.</p>
    <div class="genes"><span><b>LCT</b>молоко</span><span><b>CYP1A2</b>кофе</span><span><b>ALDH2</b>алкоголь</span><span><b>ACTN3</b>спринт</span><span><b>HERC2</b>голубые глаза</span><span><b>TAS2R38</b>брокколи</span><span><b>MC1R</b>рыжие</span><span><b>ABCC11</b>дезодорант</span><span><b>OR6A2</b>кинза</span><span><b>FUT2</b>норовирус</span></div></div>
  <div class="blk"><h5>Куда это привело</h5>
    <p>Первая история оставила два вопроса. Если модель говорит, что опечатка важна, — важна для чего именно, для какого органа? Так появилась вторая история, про ткани. И если модель так уверенно отличает громкие поломки от тихих — согласится ли с ней врач там, где от вердикта зависит жизнь? Так появилась третья, про ген BRCA1 и одиннадцать тысяч клинических приговоров. А когда модель прошла и эту проверку, остался последний, самый неудобный вопрос: а что вообще можно проверить, если большинство из девяти миллиардов замен никто никогда не видел? Четвёртая история — отрезвляющий финал. Четыре истории — это одна дорога: от застольной легенды к органу, от органа к клинике, от клиники к границам знания.</p></div>
</section>

<section class="stories">
  <h2>Четыре истории</h2>
  <a class="card" href="genes.html"><div><span class="n">История 01 · десять генов</span><h3>Гены, о которых вы слышали</h3><span class="k">10 глав · 300 000 замен · интерактивный мутатор</span><svg viewBox="0 0 360 60">%%THUMB1%%</svg></div>
    <div><p>Для каждого из десяти «застольных» генов мы запросили у Атласа все 30 000 возможных опечаток вокруг знаменитого варианта и посмотрели, где участок хрупкий, а где ему всё равно. Оказалось, что знаменитые варианты делятся на крик и шёпот: поломки белка — FUT2, ACTN3, ALDH2 — модель видит без труда, регуляторные — LCT, голубые глаза — слышит вполголоса, а «ген кофе» и «ген кинзы» не слышит вовсе. <b>Самая честная глава — про кофе:</b> связь варианта с признаком реальна и воспроизведена, но механизм явно не в этой букве.</p><p>По дороге читатель может сам сделать опечатку в игрушечном гене и увидеть, что при этом ломается.</p><span class="go">Читать →</span></div></a>
  <a class="card" href="tissues.html"><div><span class="n">История 02 · те же гены, 711 тканей</span><h3>Одна мутация, сорок тканей</h3><span class="k">скроллителлинг · кольцо из 12 систем · 6 слоёв регуляции</span><svg viewBox="0 0 360 60">%%THUMB2%%</svg></div>
    <div><p>Геном у печени и у нейрона один и тот же — разница в том, какие страницы открыты. Мы разложили 711 образцов тканей и клеток по двенадцати системам организма и нарисовали кольцом: каждый штрих — один образец, наружу — усиление, внутрь — ослабление. Потом прошли с «геном молока» всю лестницу регуляции — от открытой двери в ДНК до готовой РНК — и на каждой ступени модель указала на одно и то же место: кишечник. <b>Ей никто не говорил, что это ген лактазы.</b></p><p>Регуляторная опечатка звучит как прожектор, поломка белка — как ровный гул, а у некоторых вариантов кольцо не дрогнет: у модели просто нет микрофона в нужной ткани.</p><span class="go">Читать →</span></div></a>
  <a class="card" href="brca1.html"><div><span class="n">История 03 · модель против консилиума</span><h3>Одиннадцать тысяч приговоров</h3><span class="k">BRCA1 · ClinVar · 389 859 замен · 9 592 вердикта</span><svg viewBox="0 0 360 60">%%THUMB3%%</svg></div>
    <div><p>По каждой опечатке в гене BRCA1 — том самом, из-за которого Анджелина Джоли удалила грудь, — врачи выносят вердикт: патогенная, доброкачественная или «неопределённого значения». Мы взяли все 389 859 возможных замен в гене, наложили 11 650 записей ClinVar и сравнили мнение модели, которая не видела ни одного вердикта, с мнением клиники. <b>По вердиктам экспертной комиссии согласие почти идеальное — площадь под кривой 0,999</b>, и ни одну опасную по мнению экспертов замену модель не назвала безобидной.</p><p>Интереснее расхождения: замена, которая ломает сплайсинг, но спасена запасной изоформой; две тысячи «неопределённых», для двух из пяти которых у модели есть внятное мнение; и черта между «опасно» и «нет», которую читатель проводит сам.</p><span class="go">Читать →</span></div></a>
  <a class="card" href="finale.html"><div><span class="n">История 04 · финал</span><h3>Чего никто не видел</h3><span class="k">gnomAD · Findlay 2018 · лестница проверки · циркулярность</span><svg viewBox="0 0 360 60">%%THUMB4%%</svg></div>
    <div><p>Отрезвляющий финал. Из 389 859 возможных замен в BRCA1 хотя бы у одного человека из 807 тысяч видели 13 %, вердикт есть у 3 %, в лаборатории проверили 1 %, экспертная комиссия высказалась по 0,4 %. Остальное существует только внутри модели. <b>Единственный судья, который не читал её конспектов, — пробирка,</b> и она ставит модели 0,95, а не 0,999.</p><p>Про то, почему модель согласна с людьми лучше, чем с клетками, кто у кого списывал, и что остаётся от Атласа, когда это произнесено вслух.</p><span class="go">Читать →</span></div></a>
</section>

<section class="how">
  <div><h5>Как читать наши графики</h5><p>Главная шкала везде одна — квантиль AVI: доля из девяти миллиардов замен генома, которые модель считает менее разрушительными, чем данную. 0,99 — «сильнее 99 % генома». Это не «вредно для здоровья», это «сильно меняет молекулярную работу участка».</p><p><span class="sw" style="background:var(--ink)"></span>чернила — данные и патогенное, <span class="sw" style="background:var(--accent)"></span>золото — знаменитый вариант, усиление, неопределённость, <span class="sw" style="background:var(--down)"></span>бирюза — ослабление и доброкачественное.</p></div>
  <div><h5>Что это и что это не</h5><p>Это портфолио-проект аналитика, а не научная публикация и не медицинская информация. Все числа — предсказания модели, полученные через AlphaGenome Atlas API, а не результаты экспериментов. Все тексты прошли фактчек по первоисточникам; ссылки — в конце каждой истории. Там же, честно, — где модель ошибается и чего она не знает.</p></div>
  <div><h5>Как сделано</h5><p>Python-скрипты забирают данные из Atlas API, Ensembl и ClinVar, собирают JSON и вшивают его в самодостаточные HTML-страницы без внешних зависимостей. Визуализации — рукописный SVG и canvas: точечные матрицы, кольцо, штрих-код. Исходники и данные приложены к каждой истории, ключ API — нет.</p></div>
</section>
<script>
(function(){const c=document.getElementById('field'),ctx=c.getContext('2d');const W=c.width,H=c.height;let t0=performance.now();
  const r=(s=>()=>{s=(s*9301+49297)%233280;return s/233280})(11);const dots=[];const gap=13;
  for(let y=gap;y<H;y+=gap)for(let x=gap;x<W;x+=gap){const v=r();dots.push({x,y,a:v<.85?.05+v*.06:v<.97?.2:.55,ph:r()*6.28,acc:v>.995})}
  function draw(t){ctx.clearRect(0,0,W,H);for(const d of dots){const p=.6+.4*Math.sin(t/900+d.ph);ctx.beginPath();ctx.arc(d.x,d.y,d.acc?2.6:1.7,0,6.28);ctx.fillStyle=d.acc?`rgba(196,144,30,${.5+.4*p})`:`rgba(23,22,15,${d.a*p})`;ctx.fill()}requestAnimationFrame(draw)}requestAnimationFrame(draw)})();
</script>
</body></html>
'''
def thumb1():
    import random; r = random.Random(3); out = ''
    for i in range(0, 360, 4):
        v = r.random(); hot = 60 < i < 120 or 200 < i < 230
        h = (v ** 6) * 40 + (18 if hot else 0)
        out += f'<rect x="{i}" y="{58-h:.1f}" width="2.4" height="{h:.1f}" fill="#17160f" opacity="{0.15+min(1,h/50)*0.8:.2f}"/>'
    return out + '<rect x="180" y="0" width="2" height="60" fill="#c4901e"/>'
def thumb2():
    import math, random; r = random.Random(5); out = ''
    cx, cy, R = 180, 30, 20
    for k in range(180):
        a = k / 180 * 2 * math.pi; hot = 0.05 < a < 0.7
        L = (r.random() ** 3) * 14 + (10 if hot else 0); sgn = 1 if (hot or r.random() > .5) else -1
        x1, y1 = cx + math.cos(a) * R, cy + math.sin(a) * R; x2, y2 = cx + math.cos(a) * (R + sgn * L), cy + math.sin(a) * (R + sgn * L)
        out += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{"#c4901e" if sgn>0 else "#2f6f7e"}" stroke-width="1" opacity="{0.35+min(1,L/20)*0.6:.2f}"/>'
    return out

def thumb3():
    import random; r=random.Random(9); out=''
    rows=[('#17160f',lambda: 1-10**(-(2.5+r.random()*2.5)) if r.random()<.85 else r.random()),('#2f6f7e',lambda: r.random()**0.4 if r.random()<.7 else 1-10**(-(1+r.random()*2))),('#c4901e',lambda: 1-10**(-(0.3+r.random()*2.7)))]
    for k,(col,f) in enumerate(rows):
        for i in range(160):
            q=f(); import math; x=min(5.3,-math.log10(max(1e-6,1-q)))/5.3*356+2
            out+=f'<line x1="{x:.1f}" y1="{4+k*19}" x2="{x:.1f}" y2="{16+k*19}" stroke="{col}" stroke-width="1" opacity=".55"/>'
    return out
def thumb4():
    import random; r=random.Random(4); out=''
    cells=[(x,y) for y in range(5) for x in range(40)]; r.shuffle(cells)
    cls={}
    for i,(x,y) in enumerate(cells): cls[(x,y)]='#c4901e' if i<1 else '#2f6f7e' if i<2 else '#5a574d' if i<6 else '#9a968a' if i<26 else '#d8d3c7'
    for (x,y),c in cls.items(): out+=f'<rect x="{x*9}" y="{y*12}" width="7" height="10" rx="1" fill="{c}"/>'
    return out
open('index.html', 'w', encoding='utf-8').write(INDEX.replace('%%THUMB1%%', thumb1()).replace('%%THUMB2%%', thumb2()).replace('%%THUMB3%%', thumb3()).replace('%%THUMB4%%', thumb4()))
for f, key, _ in PAGES:
    inject(f, key)
print('nav injected')
