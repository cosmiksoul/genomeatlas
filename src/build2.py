# -*- coding: utf-8 -*-
import re, json, html
from story2 import INTRO2, STEPS, OTHERS, GLOSSARY2, SOURCES2
from story import GLOSSARY

DATA = open('tissues_data.json', encoding='utf-8').read()
GL = GLOSSARY2 + [g for g in GLOSSARY if g[1] not in {t for _, t, _ in GLOSSARY2}]

def wrap(paragraphs, seen):
    out = []
    for p in paragraphs:
        toks = {}
        def sub(m, title, d):
            if title in seen: return m.group(0)
            seen.add(title); k = f"\x00{len(toks)}\x00"
            toks[k] = f'<span class="term" tabindex="0" data-t="{html.escape(title)}" data-d="{html.escape(d)}">{m.group(0)}</span>'
            return k
        t = p
        for rx, title, d in GL:
            t = re.sub(rx, lambda m: sub(m, title, d), t, count=1, flags=re.I)
        for k, v in toks.items(): t = t.replace(k, v)
        out.append(t)
    return out

seen = set()
intro = [(h, wrap([t], seen)[0]) for h, t in INTRO2]
steps = [(m, h, wrap([t], seen)[0]) for m, h, t in STEPS]
others = {k: wrap([v], set())[0] for k, v in OTHERS.items()}

GENE_META = {
 'LCT': ('LCT / MCM6', 'молоко', 'rs4988235'), 'CYP1A2': ('CYP1A2', 'кофе', 'rs762551'), 'ALDH2': ('ALDH2', 'алкоголь', 'rs671'), 'ACTN3': ('ACTN3', 'спринт', 'rs1815739'),
 'HERC2': ('HERC2 / OCA2', 'глаза', 'rs12913832'), 'TAS2R38': ('TAS2R38', 'брокколи', 'rs713598'), 'MC1R': ('MC1R', 'рыжие', 'rs1805007'), 'ABCC11': ('ABCC11', 'дезодорант', 'rs17822931'),
 'OR6A2': ('OR6A2', 'кинза', 'rs72921001'), 'FUT2': ('FUT2', 'норовирус', 'rs601338'),
}

page = r'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Одна мутация, сорок тканей</title>
<style>
  :root{--paper:#f5f2ec;--paper-2:#ece8df;--ink:#17160f;--ink-2:#5a574d;--ink-3:#9a968a;--line:#d8d3c7;--accent:#c4901e;--accent-soft:#e9d8a8;--down:#2f6f7e;--down-soft:#bfd6db;
    --serif:"Iowan Old Style","Palatino Linotype","Book Antiqua",Georgia,serif;--sans:"Helvetica Neue",Helvetica,Arial,system-ui,sans-serif;--mono:"SF Mono",Menlo,Consolas,monospace}
  *{box-sizing:border-box} html{scroll-behavior:smooth}
  body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
  a{color:inherit}
  .masthead{display:flex;justify-content:space-between;align-items:baseline;font:12px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2);padding:28px clamp(20px,6vw,90px) 0}
  .masthead a{text-decoration:none;border-bottom:1px solid var(--line)}
  .hero{min-height:88vh;display:grid;grid-template-columns:minmax(300px,460px) minmax(0,1fr);gap:40px clamp(30px,5vw,90px);align-items:center;padding:20px clamp(20px,6vw,90px) 40px}
  .hero h1{font:400 clamp(44px,6.5vw,92px)/1 var(--serif);letter-spacing:-.02em;margin:0 0 22px}
  .hero h1 em{font-style:italic;color:var(--accent)}
  .hero p{font:19px/1.5 var(--serif);color:var(--ink-2);margin:0;max-width:560px}
  .hero .kicker{font:12px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2);margin:26px 0 0}
  .hero .kicker b{font-weight:400;color:var(--ink)}
  .ring-wrap{position:relative;width:100%;max-width:900px;margin:0 auto}
  .ring-wrap svg{width:100%;height:auto;display:block;overflow:visible}
  .ring-title{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);text-align:center;pointer-events:none}
  .ring-title .g{font:400 26px var(--serif);letter-spacing:-.01em}
  .ring-title .m{font:11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2);margin-top:4px}
  .ring-title .n{font:11px var(--mono);color:var(--ink-3);margin-top:6px}
  .syslab{font:10.5px var(--mono);fill:var(--ink-2);letter-spacing:.04em}
  .syslab.hot{fill:var(--ink);font-weight:600}
  .sysarc{fill:none;stroke:var(--ink);stroke-width:1;opacity:.35}
  .base{fill:none;stroke:var(--line);stroke-width:1}
  .tick{fill:none;stroke:var(--line);stroke-width:1;stroke-dasharray:2 4}
  .bar{stroke-width:1.1;stroke-linecap:butt}
  .bar.up{stroke:var(--accent)} .bar.down{stroke:var(--down)}
  .bar.cl{stroke-dasharray:1.5 1.5}
  .hitline{stroke:var(--ink);stroke-width:2;opacity:.9}
  .ring-fade{animation:fadein .5s ease}
  @keyframes fadein{from{opacity:0}to{opacity:1}}

  .intro{padding:70px clamp(20px,6vw,90px) 60px;border-top:1px solid var(--line);display:grid;grid-template-columns:minmax(0,600px) minmax(0,1fr);gap:40px clamp(40px,6vw,110px);align-items:start}
  .intro-text{display:grid;gap:28px}
  .intro-block{display:grid;grid-template-columns:140px 1fr;gap:20px;align-items:start}
  .intro-block h5{font:12px/1.6 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:4px 0 0}
  .intro-block p{font:17px/1.6 var(--serif);color:var(--ink);margin:0}
  .intro-block:first-child p{font-size:21px;line-height:1.45}
  .legend-card{position:sticky;top:20px;border:1px solid var(--line);padding:22px 24px 18px;border-radius:3px;background:rgba(255,255,255,.35)}
  .legend-card h4{font:400 22px var(--serif);margin:0 0 6px}
  .legend-card p{font:13.5px/1.5 var(--sans);color:var(--ink-2);margin:0 0 10px}
  .legend-card svg{width:100%;height:auto;display:block}
  .lg-row{display:flex;flex-wrap:wrap;gap:8px 18px;font:11px var(--mono);color:var(--ink-2);letter-spacing:.04em;margin-top:10px}
  .lg-row i{display:inline-block;width:14px;height:2px;vertical-align:middle;margin-right:6px}
  .term{border-bottom:1px dotted var(--accent);cursor:help}
  .term:hover,.term:focus{background:var(--accent-soft);outline:none}
  .tip{position:fixed;pointer-events:none;z-index:60;background:var(--ink);color:var(--paper);font:12px/1.4 var(--mono);padding:8px 10px;border-radius:2px;opacity:0;transform:translate(-50%,-125%);transition:opacity .12s;white-space:nowrap}
  .tip b{color:var(--accent-soft);font-weight:400}
  .tip.def{white-space:normal;max-width:300px;font-family:var(--sans);font-size:13px;line-height:1.45;transform:translate(-50%,-115%);text-align:left}
  .tip.def b{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px}

  /* scrolly */
  .scrolly{display:grid;grid-template-columns:minmax(280px,480px) minmax(0,1fr);gap:0 clamp(30px,5vw,90px);padding:40px clamp(20px,6vw,90px) 80px;border-top:1px solid var(--line)}
  .scrolly .steps{padding-top:20vh}
  .step{min-height:70vh;display:flex;flex-direction:column;justify-content:center;opacity:.25;transition:opacity .4s}
  .step.on{opacity:1}
  .step .eyebrow{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
  .step h3{font:400 34px/1.05 var(--serif);letter-spacing:-.02em;margin:0 0 14px}
  .step p{font:16.5px/1.6 var(--serif);color:var(--ink);margin:0}
  .sticky{position:sticky;top:6vh;height:88vh;display:grid;grid-template-rows:auto 1fr auto;gap:8px}
  .sticky .ring-wrap{max-height:70vh;aspect-ratio:1;margin:0 auto;width:min(70vh,100%)}
  .sticky .toplist{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:4px 18px;font:11.5px var(--sans);color:var(--ink-2)}
  .sticky .toplist div{display:flex;justify-content:space-between;gap:8px;border-bottom:1px dotted var(--line);padding:2px 0}
  .sticky .toplist b{font:11px var(--mono);font-weight:400;color:var(--ink)}
  .modbar{display:flex;gap:6px;flex-wrap:wrap}
  .modbar span{font:11px var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:6px 10px;border:1px solid var(--line);border-radius:2px;color:var(--ink-3)}
  .modbar span.on{border-color:var(--ink);color:var(--ink);background:var(--paper-2)}

  /* explorer */
  .explorer{padding:70px clamp(20px,6vw,90px);border-top:1px solid var(--line)}
  .explorer h2,.ladder h2,.others h2{font:400 clamp(32px,4vw,52px)/1.05 var(--serif);letter-spacing:-.02em;margin:0 0 10px}
  .lead{font:17px/1.55 var(--serif);color:var(--ink-2);max-width:640px;margin:0 0 26px}
  .chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
  .chips button{font:11px var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:7px 11px;border:1px solid var(--line);border-radius:2px;background:none;color:var(--ink-2);cursor:pointer}
  .chips button:hover{border-color:var(--ink);color:var(--ink)}
  .chips button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
  .chips button small{display:block;font:10px var(--sans);text-transform:none;letter-spacing:0;opacity:.8}
  .ex-grid{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(260px,.8fr);gap:30px;align-items:start;margin-top:14px}
  .ex-side h4{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-2);margin:18px 0 8px}
  .sysbars .row{display:grid;grid-template-columns:150px 1fr 48px;gap:8px;align-items:center;font:12px var(--sans);color:var(--ink-2);margin-bottom:5px}
  .sysbars .bar{height:8px;position:relative;background:var(--paper-2)}
  .sysbars .bar i{position:absolute;top:0;bottom:0;background:var(--accent)}
  .sysbars .bar i.down{background:var(--down)}
  .sysbars .v{font:11px var(--mono);color:var(--ink-3);text-align:right}
  .toptracks div{display:flex;justify-content:space-between;gap:10px;font:12.5px var(--sans);color:var(--ink-2);border-bottom:1px dotted var(--line);padding:3px 0}
  .toptracks b{font:11px var(--mono);font-weight:400;color:var(--ink);white-space:nowrap}
  .toptracks small{color:var(--ink-3);font-size:11px}

  /* ladder */
  .ladder{padding:70px clamp(20px,6vw,90px);border-top:1px solid var(--line)}
  .ladder table{border-collapse:collapse;width:100%;max-width:1100px;font:12px var(--sans)}
  .ladder th{font:11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);text-align:left;padding:8px 10px;border-bottom:1px solid var(--ink);font-weight:400}
  .ladder td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
  .ladder td.g{font:600 12px var(--mono)} .ladder td.g small{display:block;font:11px var(--sans);font-weight:400;color:var(--ink-2)}
  .ladder .cell{display:flex;align-items:center;gap:8px}
  .ladder .sw{width:14px;height:14px;border-radius:2px;flex:none}
  .ladder .cell span{color:var(--ink-2)} .ladder .cell b{font:11px var(--mono);font-weight:400;color:var(--ink);margin-left:auto}
  .ladder .note{font:13.5px/1.5 var(--serif);color:var(--ink-2);max-width:640px;margin-top:14px}

  /* others */
  .others{padding:70px clamp(20px,6vw,90px);border-top:1px solid var(--line)}
  .ogrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:30px 28px}
  .ocard{border-top:1px solid var(--ink);padding-top:12px;display:grid;grid-template-columns:120px 1fr;gap:14px;align-items:start;cursor:pointer}
  .ocard:hover .oh{color:var(--accent)}
  .ocard .oh{font:600 13px var(--mono)} .ocard .oh small{display:block;font:11px var(--sans);font-weight:400;color:var(--ink-2)}
  .ocard p{font:14px/1.5 var(--serif);color:var(--ink);margin:6px 0 0}
  .ocard svg{width:120px;height:120px;display:block}

  .method{padding:60px clamp(20px,6vw,90px) 80px;border-top:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr;gap:40px;font-size:14px;color:var(--ink-2)}
  .method h5{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink);margin:0 0 10px}
  .method p{margin:0 0 10px}
  .srcs{font:13px var(--sans);color:var(--ink-2)} .srcs ol{margin:8px 0 0;padding-left:18px;display:grid;gap:4px} .srcs a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid var(--line)}
  .tag{position:fixed;right:14px;bottom:14px;z-index:50;font:11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;background:var(--ink);color:var(--paper);padding:8px 10px;border-radius:2px;opacity:.85}
  @media (max-width:1000px){.hero,.intro,.scrolly,.ex-grid,.method{grid-template-columns:1fr}.legend-card{position:static}.sticky{position:static;height:auto}.step{min-height:auto;opacity:1;margin-bottom:40px}}
  @media (max-width:700px){.intro-block{grid-template-columns:1fr;gap:6px}}
</style>
</head>
<body>
<div class="tag">данные: AlphaGenome Atlas · черновик</div>
<div class="tip" id="tip"></div>
<div class="masthead"><span>Датажурналистика · AlphaGenome Atlas · история вторая</span><span><a href="genes.html">← история первая: «Гены, о которых вы слышали»</a></span></div>

<section class="hero">
  <div>
    <h1>Одна мутация,<br><em>сорок</em> тканей</h1>
    <p>Точнее — 711 образцов тканей и клеток и около 4 500 предсказаний на одну букву. Как одна и та же опечатка в ДНК звучит в кишечнике, крови и мозге — и почему чаще всего её слышит только один орган.</p>
    <div class="kicker">На кольце: <b>LCT · rs4988235</b> · «ген молока» · уровень РНК по 371 треку</div>
  </div>
  <div class="ring-wrap" id="heroRing"></div>
</section>

<section class="intro">
  <div class="intro-text">
    %%INTRO%%
  </div>
  <div class="legend-card">
    <h4>Анатомия кольца</h4>
    <p>Двенадцать систем организма — двенадцать секторов. Ширина сектора — сколько в нём образцов. Каждый штрих — один трек: наружу — модель предсказывает усиление, внутрь — ослабление. Насыщенность — квантиль по геному; пунктир — клеточная линия, а не ткань.</p>
    <div id="legendRing"></div>
    <div class="lg-row"><span><i style="background:var(--accent)"></i>усиление</span><span><i style="background:var(--down)"></i>ослабление</span><span><i style="background:var(--ink);opacity:.3"></i>слабый эффект</span><span><i style="background:repeating-linear-gradient(90deg,var(--ink) 0 2px,transparent 2px 4px)"></i>клеточная линия</span></div>
  </div>
</section>

<section class="scrolly" id="scrolly">
  <div class="steps">
    %%STEPS%%
  </div>
  <div class="sticky">
    <div class="modbar" id="modbar"></div>
    <div class="ring-wrap" id="scrollyRing"></div>
    <div class="toplist" id="scrollyTop"></div>
  </div>
</section>

<section class="explorer" id="explorer">
  <h2>Покрутите сами</h2>
  <p class="lead">Любой из десяти вариантов, любой из шести слоёв. Наведите на штрих — увидите ткань и число. Справа — итог по системам и десять самых громких треков.</p>
  <div class="chips" id="geneChips"></div>
  <div class="chips" id="modChips"></div>
  <div class="ex-grid">
    <div class="ring-wrap" id="exRing"></div>
    <div class="ex-side">
      <h4>Максимум по системам</h4><div class="sysbars" id="sysbars"></div>
      <h4>Самые громкие треки</h4><div class="toptracks" id="toptracks"></div>
    </div>
  </div>
</section>

<section class="ladder" id="ladder">
  <h2>Лестница: где слышно каждую букву</h2>
  <p class="lead">Для каждого варианта и каждого слоя — система организма с самым сильным предсказанным сдвигом. Тон ячейки — сила сдвига относительно самого громкого варианта на этом слое.</p>
  <div id="ladderTable"></div>
  <p class="note">Читается по строкам. У LCT на каждой ступени один и тот же адрес — кишечник. У «белковых» вариантов (FUT2, ACTN3, ALDH2, ABCC11) первые четыре ступени почти пусты, а на последней — тихое падение РНК. У CYP1A2, OR6A2, HERC2 и MC1R адреса случайные и слабые: модель не находит ткань, в которой эта буква что-то значит.</p>
</section>

<section class="others" id="others">
  <h2>Остальные девять</h2>
  <p class="lead">Уровень РНК целевого гена. Нажмите на карточку — вариант откроется в кольце выше.</p>
  <div class="ogrid" id="ogrid"></div>
</section>

<section class="method">
  <div>
    <h5>Откуда данные</h5>
    <p>AlphaGenome Atlas API, запрос <code>query_variant</code> по каждому из десяти вариантов со скорерами DNASE, ATAC, CHIP_HISTONE, CHIP_TF, CAGE и RNA_SEQ (для целевого гена). Треки — из ENCODE, GTEx, FANTOM5; для каждого трека Атлас отдаёт предсказанный сдвиг и квантиль относительно всех замен генома. Разбиение 711 образцов на 12 систем — по названиям биообразцов, вручную проверенными правилами; спорные случаи (клеточные линии опухолей) отнесены к органу происхождения.</p>
    <details class="srcs"><summary>Источники</summary><ol>%%SOURCES%%</ol></details>
  </div>
  <div>
    <h5>Что здесь не так, как в жизни</h5>
    <p>Кольцо показывает, что модель <em>предсказывает</em>, а не что измерено в эксперименте. Набор тканей неравномерный: крови и клеточных линий много, меланоцитов радужки, обонятельного эпителия и вкусовых сосочков нет вовсе — поэтому для части вариантов у модели просто нет нужного «микрофона». Величины сдвигов на разных слоях несопоставимы между собой, каждый слой нормирован отдельно.</p>
    <p>Скрипты и данные: pull_tissues.py, prep_tissues.py, tissues_data.json.</p>
  </div>
</section>

<script>
const DATA=%%DATA%%;
const META=%%META%%;
const OTHERS=%%OTHERS%%;
const SYS=DATA.systems, MODS=Object.keys(DATA.modalities), MODN=DATA.modalities;
const MODSHORT={DNASE:'DNase',ATAC:'ATAC',CHIP_HISTONE:'Гистоны',CHIP_TF:'Белки',CAGE:'Старт',RNA_SEQ:'РНК'};
const NS='http://www.w3.org/2000/svg';
const el=(n,a={},p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);p&&p.appendChild(e);return e};
const tip=document.getElementById('tip');
function showTip(h,x,y,cls){tip.className='tip'+(cls?' '+cls:'');tip.innerHTML=h;tip.style.left=Math.min(Math.max(150,x),innerWidth-150)+'px';tip.style.top=y+'px';tip.style.opacity=1}
function hideTip(){tip.style.opacity=0}
/* global scale per modality: 98th percentile of |effect| across all genes */
const SCALE={};MODS.forEach(m=>{const v=[];for(const g in DATA.genes)DATA.genes[g].tracks[m].forEach(t=>v.push(Math.abs(t[2])));v.sort((a,b)=>a-b);SCALE[m]=Math.max(1e-3,v[Math.floor(v.length*.995)])});

function ring(host,gid,mod,opts={}){
  const size=opts.size||760,cx=size/2,cy=size/2,R0=opts.R0||size*.30,L=opts.L||size*.16,labels=opts.labels!==false;
  host.innerHTML='';const pad=labels?size*(opts.pad||.19):0;const svg=el('svg',{viewBox:`${-pad} ${-pad} ${size+2*pad} ${size+2*pad}`,class:'ring-fade'},host);
  const tr=DATA.genes[gid].tracks[mod];
  /* group by system */
  const groups=SYS.map((s,i)=>({i,s,items:tr.filter(t=>t[0]===i)})).filter(g=>g.items.length);
  const N=tr.length,gap=Math.PI/90;const avail=2*Math.PI-gap*groups.length;let a=-Math.PI/2;
  el('circle',{cx,cy,r:R0,class:'base'},svg);
  if(labels){[0.5,1].forEach(f=>{el('circle',{cx,cy,r:R0+L*f,class:'tick'},svg);el('circle',{cx,cy,r:Math.max(4,R0-L*f),class:'tick'},svg)})}
  const angles=[];let hot=null,hotv=0;
  groups.forEach(g=>{const w=avail*g.items.length/N;const a0=a;
    g.items.sort((p,q)=>p[1]-q[1]);
    g.items.forEach((t,k)=>{const ang=a0+w*(k+.5)/g.items.length;const e=t[2],q=t[3];const len=Math.min(1.35,Math.pow(Math.abs(e)/SCALE[mod],0.7))*L;
      const r1=e>=0?R0+len:Math.max(4,R0-len);const x1=cx+Math.cos(ang)*R0,y1=cy+Math.sin(ang)*R0,x2=cx+Math.cos(ang)*r1,y2=cy+Math.sin(ang)*r1;
      const op=q<0?.5:.25+.75*Math.pow(q,3);
      if(len>1.2)el('line',{x1,y1,x2,y2,class:'bar '+(e>=0?'up':'down')+(t[5]?' cl':''),opacity:op.toFixed(2)},svg);
      angles.push({ang,t,x1,y1,x2,y2});if(Math.abs(e)>hotv){hotv=Math.abs(e);hot=g.s}});
    /* sector arc + label */
    const ra=R0-L*.02;el('path',{d:arc(cx,cy,R0+L*1.42,a0,a0+w),class:'sysarc'},svg);
    if(labels){const am=a0+w/2,rl=R0+L*1.5;const x=cx+Math.cos(am)*rl,y=cy+Math.sin(am)*rl;const t=el('text',{x,y:y+4,class:'syslab'+(g.s===hot?' hot':''),'text-anchor':Math.cos(am)>.06?'start':Math.cos(am)<-.06?'end':'middle'},svg);t.textContent=g.s.replace(' и ',' и ')+(opts.counts?' · '+g.items.length:'');}
    a+=w+gap});
  if(labels){const c=document.createElement('div');c.className='ring-title';c.innerHTML=`<div class="g">${META[gid][0]}</div><div class="m">${MODN[mod]}</div><div class="n">${N} треков · ${META[gid][2]}</div>`;host.appendChild(c)}
  /* hover: nearest by angle */
  if(opts.interactive!==false){let hl=null;
    svg.addEventListener('mousemove',e=>{const r=svg.getBoundingClientRect();const full=size+2*pad;const px=(e.clientX-r.left)/r.width*full-pad-cx,py=(e.clientY-r.top)/r.height*full-pad-cy;const d=Math.hypot(px,py);if(d<R0-L*1.3||d>R0+L*1.5){hideTip();hl&&hl.remove();hl=null;return}
      let ang=Math.atan2(py,px);let best=null,bd=1e9;for(const o of angles){let dd=Math.abs(((o.ang-ang+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI);if(dd<bd){bd=dd;best=o}}
      if(!best||bd>0.02){hideTip();hl&&hl.remove();hl=null;return}
      hl&&hl.remove();hl=el('line',{x1:best.x1,y1:best.y1,x2:best.x2,y2:best.y2,class:'hitline'},svg);
      const t=best.t;showTip(`${DATA.labels[t[1]]}${t[4]&&DATA.extras[t[4]]?' · '+DATA.extras[t[4]]:''}${t[5]?' · клеточная линия':''}<br><b>${t[2]>0?'+':''}${t[2].toFixed(3)}</b>${t[3]>=0?' · квантиль '+t[3].toFixed(2):''} · ${SYS[t[0]]}`,e.clientX,e.clientY)});
    svg.addEventListener('mouseleave',()=>{hideTip();hl&&hl.remove();hl=null})}
  return {hot};
}
function arc(cx,cy,r,a0,a1){return `M${cx+Math.cos(a0)*r},${cy+Math.sin(a0)*r} A${r},${r} 0 ${a1-a0>Math.PI?1:0} 1 ${cx+Math.cos(a1)*r},${cy+Math.sin(a1)*r}`}
function topTracks(gid,mod,n){return [...DATA.genes[gid].tracks[mod]].sort((a,b)=>Math.abs(b[2])-Math.abs(a[2])).slice(0,n)}

/* hero */
ring(document.getElementById('heroRing'),'LCT','RNA_SEQ',{size:760,counts:true});

/* legend mini ring */
(function(){const host=document.getElementById('legendRing');ring(host,'LCT','DNASE',{size:420,R0:118,L:68,labels:true,interactive:false,pad:.44});})();

/* scrolly */
const modbar=document.getElementById('modbar');MODS.forEach(m=>{const s=document.createElement('span');s.textContent=MODSHORT[m];s.dataset.m=m;modbar.appendChild(s)});
function setScrolly(mod){ring(document.getElementById('scrollyRing'),'LCT',mod,{size:720});modbar.querySelectorAll('span').forEach(s=>s.classList.toggle('on',s.dataset.m===mod));
  document.getElementById('scrollyTop').innerHTML=topTracks('LCT',mod,6).map(t=>`<div><span>${DATA.labels[t[1]]}${t[4]&&DATA.extras[t[4]]?' · '+DATA.extras[t[4]]:''}</span><b>${t[2]>0?'+':''}${t[2].toFixed(2)}</b></div>`).join('')}
setScrolly('DNASE');
const stepEls=[...document.querySelectorAll('.step')];
new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){stepEls.forEach(s=>s.classList.toggle('on',s===e.target));setScrolly(e.target.dataset.m)}}),{rootMargin:'-45% 0px -45% 0px'}).observe&&stepEls.forEach(s=>new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){stepEls.forEach(x=>x.classList.toggle('on',x===e.target));setScrolly(e.target.dataset.m)}}),{rootMargin:'-45% 0px -45% 0px'}).observe(s));

/* explorer */
let exG='LCT',exM='RNA_SEQ';
const gc=document.getElementById('geneChips'),mc=document.getElementById('modChips');
Object.keys(DATA.genes).forEach(g=>{const b=document.createElement('button');b.innerHTML=`${g}<small>${META[g][1]}</small>`;b.onclick=()=>{exG=g;renderEx()};b.dataset.g=g;gc.appendChild(b)});
MODS.forEach(m=>{const b=document.createElement('button');b.textContent=MODN[m];b.onclick=()=>{exM=m;renderEx()};b.dataset.m=m;mc.appendChild(b)});
function renderEx(){gc.querySelectorAll('button').forEach(b=>b.classList.toggle('on',b.dataset.g===exG));mc.querySelectorAll('button').forEach(b=>b.classList.toggle('on',b.dataset.m===exM));
  ring(document.getElementById('exRing'),exG,exM,{size:720});
  const sm=DATA.genes[exG].summary[exM];const mx=Math.max(.001,...Object.values(sm).map(Math.abs));
  document.getElementById('sysbars').innerHTML=SYS.filter(s=>sm[s]!==undefined).map(s=>{const v=sm[s];const w=Math.abs(v)/mx*50;return `<div class="row"><span>${s}</span><div class="bar"><i class="${v<0?'down':''}" style="left:${v<0?50-w:50}%;width:${w}%"></i></div><span class="v">${v>0?'+':''}${v.toFixed(2)}</span></div>`}).join('');
  document.getElementById('toptracks').innerHTML=topTracks(exG,exM,10).map(t=>`<div><span>${DATA.labels[t[1]]}${t[4]&&DATA.extras[t[4]]?' <small>'+DATA.extras[t[4]]+'</small>':''}${t[5]?' <small>линия</small>':''}</span><b>${t[2]>0?'+':''}${t[2].toFixed(3)}</b></div>`).join('')}
renderEx();

/* ladder */
(function(){const genes=Object.keys(DATA.genes);const mx={};MODS.forEach(m=>mx[m]=Math.max(...genes.map(g=>Math.max(...Object.values(DATA.genes[g].summary[m]).map(Math.abs)))));
  let h='<table><thead><tr><th>Вариант</th>'+MODS.map(m=>`<th>${MODN[m]}</th>`).join('')+'</tr></thead><tbody>';
  genes.forEach(g=>{h+=`<tr><td class="g">${g}<small>${META[g][1]} · ${META[g][2]}</small></td>`;MODS.forEach(m=>{const sm=DATA.genes[g].summary[m];const [s,v]=Object.entries(sm).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1]))[0];const f=Math.abs(v)/mx[m];const col=v>=0?'196,144,30':'47,111,126';h+=`<td><div class="cell"><i class="sw" style="background:rgba(${col},${(0.08+f*.92).toFixed(2)})"></i><span>${s}</span><b>${v>0?'+':''}${v.toFixed(2)}</b></div></td>`});h+='</tr>'});
  document.getElementById('ladderTable').innerHTML=h+'</tbody></table>'})();

/* others */
(function(){const og=document.getElementById('ogrid');Object.keys(DATA.genes).filter(g=>g!=='LCT').forEach(g=>{const d=document.createElement('div');d.className='ocard';d.innerHTML=`<div class="thumb"></div><div><div class="oh">${g}<small>${META[g][1]} · ${META[g][2]}</small></div><p>${OTHERS[g]||''}</p></div>`;og.appendChild(d);
  ring(d.querySelector('.thumb'),g,'RNA_SEQ',{size:240,R0:75,L:40,labels:false,interactive:false});
  d.addEventListener('click',()=>{exG=g;exM='RNA_SEQ';renderEx();document.getElementById('explorer').scrollIntoView({behavior:'smooth'})})})})();

/* glossary tooltips */
(function(){let pinned=null;
  function show(t){tip.className='tip def';tip.innerHTML=`<b>${t.dataset.t}</b>${t.dataset.d}`;const r=t.getBoundingClientRect();tip.style.left=Math.min(Math.max(160,r.left+r.width/2),innerWidth-160)+'px';tip.style.top=r.top+'px';tip.style.opacity=1}
  function hide(){if(pinned)return;tip.style.opacity=0}
  document.addEventListener('mouseover',e=>{const t=e.target.closest('.term');if(t)show(t)});
  document.addEventListener('mouseout',e=>{if(e.target.closest('.term'))hide()});
  document.addEventListener('click',e=>{const t=e.target.closest('.term');if(t){pinned=pinned===t?null:t;if(pinned)show(t);else hide()}else if(pinned){pinned=null;hide()}});
  addEventListener('scroll',()=>{if(pinned){pinned=null;hide()}},{passive:true});
})();
</script>
</body>
</html>
'''
page = page.replace('%%INTRO%%', ''.join(f'<div class="intro-block"><h5>{h}</h5><p>{t}</p></div>\n' for h, t in intro))
page = page.replace('%%STEPS%%', ''.join(f'<div class="step" data-m="{m}"><div class="eyebrow">Ступень {i+1} · {DATA and json.loads(DATA)["modalities"][m]}</div><h3>{h}</h3><p>{t}</p></div>\n' for i, (m, h, t) in enumerate(steps)))
page = page.replace('%%SOURCES%%', ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for t, u in SOURCES2))
page = page.replace('%%DATA%%', DATA).replace('%%META%%', json.dumps(GENE_META, ensure_ascii=False)).replace('%%OTHERS%%', json.dumps(others, ensure_ascii=False))
open('tissues.html', 'w', encoding='utf-8').write(page)
print('ok', len(page) // 1024, 'KB')
