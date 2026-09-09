# -*- coding: utf-8 -*-
import re, json, html
from story3 import INTRO3, SECTIONS, DISAGREE_CARDS, GLOSSARY3, SOURCES3
DATA = json.load(open('brca1_data.json', encoding='utf-8'))
S = DATA['stats']

def wrap(text, seen):
    toks = {}
    def sub(m, title, d):
        if title in seen: return m.group(0)
        seen.add(title); k = f"\x00{len(toks)}\x00"
        toks[k] = f'<span class="term" tabindex="0" data-t="{html.escape(title)}" data-d="{html.escape(d)}">{m.group(0)}</span>'
        return k
    t = text
    for rx, title, d in GLOSSARY3:
        t = re.sub(rx, lambda m: sub(m, title, d), t, count=1, flags=re.I)
    for k, v in toks.items(): t = t.replace(k, v)
    return t

seen = set()
intro = [(h, wrap(t, seen)) for h, t in INTRO3]
sec = {k: wrap(v.format(**S['vus']), seen) for k, v in SECTIONS.items()}
cards = ''.join(f'<div class="dcard"><div class="dn">{html.escape(n)}</div><div class="dv">{html.escape(v)}</div><p>{wrap(t, seen)}</p></div>' for n, v, t in DISAGREE_CARDS)

fmt = lambda n: f'{n:,}'.replace(',', ' ')
page = r'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Одиннадцать тысяч приговоров</title>
<style>
  :root{--paper:#f5f2ec;--paper-2:#ece8df;--ink:#17160f;--ink-2:#5a574d;--ink-3:#9a968a;--line:#d8d3c7;--accent:#c4901e;--accent-soft:#e9d8a8;--down:#2f6f7e;
    --serif:"Iowan Old Style","Palatino Linotype","Book Antiqua",Georgia,serif;--sans:"Helvetica Neue",Helvetica,Arial,system-ui,sans-serif;--mono:"SF Mono",Menlo,Consolas,monospace}
  *{box-sizing:border-box} html{scroll-behavior:smooth}
  body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
  a{color:inherit}
  .hero{padding:70px clamp(20px,6vw,90px) 40px;display:grid;grid-template-columns:minmax(300px,480px) minmax(0,1fr);gap:40px clamp(30px,5vw,90px);align-items:end}
  #heroViz{align-self:center}
  .hero h1{font:400 clamp(44px,6.5vw,92px)/1 var(--serif);letter-spacing:-.02em;margin:0 0 22px} .hero h1 em{font-style:italic;color:var(--accent)}
  .hero p{font:19px/1.5 var(--serif);color:var(--ink-2);margin:0;max-width:560px}
  .hero .nums{display:grid;grid-template-columns:repeat(4,auto);gap:10px 28px;justify-content:start;margin-top:26px}
  .hero .nums b{display:block;font:400 34px/1 var(--serif);letter-spacing:-.02em;white-space:nowrap;font-variant-numeric:tabular-nums} .hero .nums span{font:11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);white-space:nowrap}
  .mednote{font:12px/1.5 var(--mono);color:var(--ink-3);margin-top:20px;max-width:520px}
  .hero .nums i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
  .c-P{background:var(--ink)} .c-B{background:var(--down)} .c-VUS{background:var(--accent)} .c-conflict{background:var(--ink-3)}
  .intro{padding:60px clamp(20px,6vw,90px) 50px;border-top:1px solid var(--line);display:grid;grid-template-columns:minmax(0,640px) minmax(280px,380px);justify-content:space-between;gap:28px clamp(40px,6vw,120px)}
  .intro-text{display:grid;gap:28px}
  .intro-block{display:grid;grid-template-columns:140px 1fr;gap:20px;align-items:start}
  .scard{align-self:start;position:sticky;top:90px;border:1px solid var(--line);border-radius:3px;background:rgba(255,255,255,.35);padding:22px 24px 20px}
  .scard h4{font:400 22px var(--serif);margin:0 0 4px}
  .scard .sd{font:13px/1.5 var(--sans);color:var(--ink-2);margin:0 0 14px}
  .scard .srow{display:flex;align-items:baseline;gap:10px;font:13px var(--sans);color:var(--ink-2);border-bottom:1px dotted var(--line);padding:7px 0}
  .scard .srow:last-child{border-bottom:0}
  .scard .srow i{width:11px;height:11px;border-radius:2px;flex:none;align-self:center}
  .scard .srow b{font:12px var(--mono);font-weight:400;color:var(--ink);margin-left:auto;font-variant-numeric:tabular-nums}
  .scard h5{font:11px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:18px 0 4px}
  .scard .stars{color:var(--accent);letter-spacing:-1px;font-size:12px;flex:none}
  @media (max-width:1200px){.intro{grid-template-columns:minmax(0,640px)}.scard{position:static}}
  .intro-block h5{font:12px/1.6 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:4px 0 0}
  .intro-block p{font:17px/1.6 var(--serif);color:var(--ink);margin:0} .intro-block:first-child p{font-size:21px;line-height:1.45}
  section.blk{padding:70px clamp(20px,6vw,90px);border-top:1px solid var(--line)}
  section.blk h2{font:400 clamp(30px,3.8vw,48px)/1.05 var(--serif);letter-spacing:-.02em;margin:0 0 10px}
  .lead{font:17px/1.6 var(--serif);color:var(--ink);max-width:680px;margin:0 0 26px}
  .lead.dim{color:var(--ink-2)}
  .term{border-bottom:1px dotted var(--accent);cursor:help} .term:hover,.term:focus{background:var(--accent-soft);outline:none}
  .tip{position:fixed;pointer-events:none;z-index:60;background:var(--ink);color:var(--paper);font:12px/1.4 var(--mono);padding:8px 10px;border-radius:2px;opacity:0;transform:translate(-50%,-125%);transition:opacity .12s;white-space:nowrap}
  .tip b{color:var(--accent-soft);font-weight:400}
  .tip.def{white-space:normal;max-width:300px;font-family:var(--sans);font-size:13px;line-height:1.45;transform:translate(-50%,-115%);text-align:left}
  .tip.def b{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px}
  svg{display:block;width:100%;height:auto;overflow:visible}
  .axlab{font:10.5px var(--mono);fill:var(--ink-3);letter-spacing:.04em} .rowlab{font:12px var(--sans);fill:var(--ink)} .rowlab tspan{fill:var(--ink-3);font-family:var(--mono);font-size:10.5px}
  .grid{stroke:var(--line);stroke-width:1;stroke-dasharray:2 4}
  .bc{stroke-width:1;opacity:.55} .bc.P{stroke:var(--ink)} .bc.B{stroke:var(--down)} .bc.VUS{stroke:var(--accent)} .bc.conflict{stroke:var(--ink-3)}
  .bc.dimmed{opacity:.06}
  .thr{stroke:var(--accent);stroke-width:1.5}
  .toggle{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}
  .toggle button{font:11px var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:7px 11px;border:1px solid var(--line);border-radius:2px;background:none;color:var(--ink-2);cursor:pointer}
  .toggle button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
  /* threshold */
  .thr-grid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(280px,.7fr);gap:30px;align-items:start}
  .thr-ctl{display:flex;align-items:center;gap:14px;font:12px var(--mono);color:var(--ink-2);margin:10px 0 18px}
  .thr-ctl input{width:320px;accent-color:var(--ink)}
  .kpis{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .kpi{border-top:1px solid var(--ink);padding-top:8px} .kpi b{display:block;font:400 40px/1 var(--serif);letter-spacing:-.02em;font-variant-numeric:tabular-nums} .kpi span{font:11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)} .kpi small{display:block;font:12px var(--sans);color:var(--ink-2);margin-top:4px}
  .thr-note{font:14px/1.5 var(--serif);color:var(--ink-2);margin-top:16px}
  /* map */
  .exlab{font:9.5px var(--mono);fill:var(--ink-2);text-anchor:middle}
  .exon{fill:var(--ink);opacity:.85} .exon.utr{opacity:.3}
  .mk{stroke-width:1;opacity:.6} .mk.P{stroke:var(--ink)} .mk.B{stroke:var(--down)} .mk.VUS{stroke:var(--accent);opacity:.3}
  /* cards */
  .dgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:26px}
  .dcard{border-top:1px solid var(--ink);padding-top:12px} .dcard .dn{font:600 14px var(--mono)} .dcard .dv{font:11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:4px 0 10px} .dcard p{font:14.5px/1.55 var(--serif);margin:0}
  /* vus */
  .vgrid{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:20px}
  .vlist h4{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-2);margin:0 0 8px}
  .vlist div{display:flex;justify-content:space-between;gap:10px;font:13px var(--mono);border-bottom:1px dotted var(--line);padding:4px 0} .vlist div b{font-weight:400;color:var(--ink-3)}
  .stars{color:var(--accent);letter-spacing:-1px}
  .warn{border:1px solid var(--accent);padding:14px 18px;font:14px/1.5 var(--serif);color:var(--ink);max-width:680px;margin-top:26px;border-radius:2px}
  .method{padding:60px clamp(20px,6vw,90px) 80px;border-top:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr;gap:40px;font-size:14px;color:var(--ink-2)}
  .method h5{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink);margin:0 0 10px} .method p{margin:0 0 10px}
  .srcs{font:13px var(--sans);color:var(--ink-2)} .srcs ol{margin:8px 0 0;padding-left:18px;display:grid;gap:4px} .srcs a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid var(--line)}
  .tag{position:fixed;right:14px;bottom:14px;z-index:50;font:11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;background:var(--ink);color:var(--paper);padding:8px 10px;border-radius:2px;opacity:.85}
  @media (max-width:1000px){.hero,.thr-grid,.vgrid,.method{grid-template-columns:1fr}.hero .nums{grid-template-columns:1fr 1fr}.hero .nums b{font-size:28px}}
  @media (max-width:700px){.intro-block{grid-template-columns:1fr;gap:6px}}
</style></head>
<body>
<div class="tag">данные: AlphaGenome Atlas + ClinVar · черновик</div>
<div class="tip" id="tip"></div>
<section class="hero">
  <div>
    <h1>Одиннадцать тысяч <em>приговоров</em></h1>
    <p>Ген BRCA1 — самый изученный ген рака. По каждой найденной в нём опечатке врачи выносят вердикт: опасна или нет. Мы дали те же опечатки модели, которая не видела ни одного вердикта, — и сравнили.</p>
    <div class="nums">
      <div><b>%%N_P%%</b><span><i class="c-P"></i>патогенных</span></div>
      <div><b>%%N_B%%</b><span><i class="c-B"></i>доброкачественных</span></div>
      <div><b>%%N_V%%</b><span><i class="c-VUS"></i>неопределённых</span></div>
      <div><b>%%N_C%%</b><span><i class="c-conflict"></i>противоречивых</span></div>
    </div>
    <div class="mednote">Всё на этой странице — предсказания модели и открытые данные, не медицинская информация. Вердикт по конкретному варианту выносит врач-генетик.</div>
  </div>
  <div id="heroViz"></div>
</section>

<section class="intro">
  <div class="intro-text">%%INTRO%%</div>
  <aside class="scard">
    <h4>Шкала ClinVar</h4>
    <p class="sd">Пять вердиктов, которые лаборатории выносят каждой найденной замене. В проекте они сгруппированы в четыре класса — цвета те же на всех графиках.</p>
    <div class="srow"><i class="c-P"></i><span>патогенные и вероятно патогенные</span><b>%%N_P%%</b></div>
    <div class="srow"><i class="c-B"></i><span>доброкачественные и вероятно</span><b>%%N_B%%</b></div>
    <div class="srow"><i class="c-VUS"></i><span>неопределённого значения</span><b>%%N_V%%</b></div>
    <div class="srow"><i class="c-conflict"></i><span>противоречивые</span><b>%%N_C%%</b></div>
    <h5>Вес вердикта</h5>
    <div class="srow"><span class="stars">★☆☆</span><span>одна лаборатория, без критериев</span></div>
    <div class="srow"><span class="stars">★★☆</span><span>несколько лабораторий сошлись</span></div>
    <div class="srow"><span class="stars">★★★</span><span>экспертная комиссия ENIGMA</span></div>
  </aside>
</section>

<section class="blk" id="barcode">
  <h2>Штрих-код гена</h2>
  <p class="lead">%%S_BARCODE%%</p>
  <div class="toggle" id="starToggle"><button data-s="0" class="on">Все вердикты</button><button data-s="2">Две звезды и выше</button><button data-s="3">Только экспертная комиссия</button></div>
  <div id="barcodeViz"></div>
  <p class="lead dim" style="margin-top:22px">%%S_EXPERT%%</p>
</section>

<section class="blk" id="threshold">
  <h2>Где провести черту</h2>
  <p class="lead">%%S_THRESHOLD%%</p>
  <div class="thr-grid">
    <div><div class="thr-ctl"><label>порог квантиля</label><input type="range" id="thrRange" min="0" max="119" value="48"><b id="thrVal"></b></div><div id="thrViz"></div></div>
    <div><div class="kpis" id="kpis"></div><p class="thr-note" id="thrNote"></p></div>
  </div>
</section>

<section class="blk" id="map">
  <h2>Карта гена</h2>
  <p class="lead">%%S_MAP%%</p>
  <div id="mapViz"></div>
</section>

<section class="blk" id="disagree">
  <h2>Где модель и консилиум расходятся</h2>
  <p class="lead">%%S_DISAGREE%%</p>
  <div class="dgrid">%%CARDS%%</div>
</section>

<section class="blk" id="vus">
  <h2>Две тысячи неопределённых</h2>
  <p class="lead">%%S_VUS%%</p>
  <div id="vusViz"></div>
  <div class="vgrid">
    <div class="vlist"><h4>Неопределённые, которые модель считает разрушительными</h4>%%VUS_TOP%%</div>
    <div class="vlist"><h4>Неопределённые, которые модель считает безобидными</h4>%%VUS_BOTTOM%%</div>
  </div>
  <div class="warn">Это не медицинская информация и не основание для решений. Предсказание модели — один из многих признаков, которые клиника учитывает при классификации; вердикт по вашему варианту выносит генетик, а не алгоритм. Если у вас есть результат теста с «неопределённым» вариантом — обсудите его с врачом-генетиком.</div>
</section>

<section class="method">
  <div><h5>Откуда данные</h5>
    <p>AlphaGenome Atlas API: <code>query_interval</code> по всему гену BRCA1 (chr17:43 042 292–43 172 245, GRCh38) — 389 859 однобуквенных замен с оценкой AVI, квантилем и разложением на признаки. ClinVar через NCBI E-utilities: 11 655 записей типа «single nucleotide variant» для BRCA1, координаты и аллели из canonical SPDI, классификация — поле germline classification, статус проверки — review status. Структура гена — Ensembl, канонический транскрипт ENST00000357654.</p>
    <p>Классы: «патогенные» = Pathogenic + Likely pathogenic; «доброкачественные» = Benign + Likely benign; «неопределённые» = Uncertain significance; «противоречивые» = Conflicting classifications. Записи без классификации (2 023) исключены. Тип замены выведен из HGVS-названия.</p>
    <details class="srcs"><summary>Источники</summary><ol>%%SOURCES%%</ol></details>
  </div>
  <div><h5>Что здесь не так, как в жизни</h5>
    <p>ClinVar — не истина, а сумма мнений: одна звезда может быть ошибкой одной лаборатории, а классификации меняются со временем. Сравнение по экспертной комиссии честнее, но и она опирается на данные, которых у модели нет: семьи, функциональные тесты, частоты в популяциях. Часть согласия объясняется тем, что консервативность и AlphaMissense, входящие в AVI, сами обучались на похожих данных — это не «слепой» тест в строгом смысле.</p>
    <p>Скрипты и данные: pull_brca1.py, prep_brca1.py, brca1_data.json.</p>
  </div>
</section>

<script>
const D=%%DATA%%;const S=D.stats;
const NS='http://www.w3.org/2000/svg';const el=(n,a={},p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);p&&p.appendChild(e);return e};
const tip=document.getElementById('tip');function showTip(h,x,y,cls){tip.className='tip'+(cls?' '+cls:'');tip.innerHTML=h;tip.style.left=Math.min(Math.max(150,x),innerWidth-150)+'px';tip.style.top=y+'px';tip.style.opacity=1}function hideTip(){tip.style.opacity=0}
const CLS={P:'Патогенные',B:'Доброкачественные',VUS:'Неопределённые',conflict:'Противоречивые'};
const CONS={missense:'миссенс',nonsense:'стоп-кодон',synonymous:'синонимичная',intron:'интрон',splice_site:'сайт сплайсинга',UTR:'UTR',other:'другое'};
const X=q=>Math.min(XMAX,-Math.log10(Math.max(1e-6,1-q)));
const XMAX=5.3;const TICKS=[[0,'0'],[1,'0,9'],[2,'0,99'],[3,'0,999'],[4,'0,9999'],[5,'0,99999']];
function stars(n){return '★'.repeat(n)+'☆'.repeat(3-n)}
function seeded(i){let x=Math.sin(i*9301+49297)*233280;return x-Math.floor(x)}

/* barcode */
function barcode(host,opts={}){
  const W=1000,rowH=opts.rowH||64,left=150,right=30,rows=opts.rows||['P','B','VUS','conflict'];const H=rows.length*rowH+30;
  host.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`},host);const x=v=>left+X(v)/XMAX*(W-left-right);
  TICKS.forEach(([v,l])=>{const xx=left+v/XMAX*(W-left-right);el('line',{x1:xx,x2:xx,y1:0,y2:H-24,class:'grid'},svg);el('text',{x:xx,y:H-8,class:'axlab','text-anchor':'middle'},svg).textContent=l});
  el('text',{x:W-right,y:10,class:'axlab','text-anchor':'end'},svg).textContent='квантиль AVI →';
  const minStar=opts.minStar||0;const lines=[];
  rows.forEach((c,ri)=>{const pts=D.points.filter(p=>p[1]===c);const y0=ri*rowH;
    const t=el('text',{x:0,y:y0+rowH/2-4,class:'rowlab'},svg);t.innerHTML=`${CLS[c]} <tspan>${pts.filter(p=>p[6]>=minStar).length}</tspan>`;
    el('line',{x1:left,x2:W-right,y1:y0+rowH-8,y2:y0+rowH-8,stroke:'var(--line)'},svg);
    pts.forEach((p,i)=>{const dim=p[6]<minStar;const yy=y0+10+seeded(i+ri*7)*(rowH-30);const l=el('line',{x1:x(p[3]),x2:x(p[3]),y1:yy,y2:yy+12,class:'bc '+c+(dim?' dimmed':'')},svg);l.__p=p;lines.push(l)})});
  if(opts.interactive!==false){svg.addEventListener('mousemove',e=>{const r=svg.getBoundingClientRect();const px=(e.clientX-r.left)/r.width*W,py=(e.clientY-r.top)/r.height*H;let best=null,bd=1e9;for(const l of lines){if(l.classList.contains('dimmed'))continue;const dx=+l.getAttribute('x1')-px,dy=+l.getAttribute('y1')+6-py;const d=dx*dx+dy*dy*0.3;if(d<bd){bd=d;best=l}}
    if(best&&bd<60){const p=best.__p;showTip(`${p[5]}<br><b>квантиль ${p[3].toFixed(4)} · AVI ${p[4].toFixed(2)}</b><br>${CLS[p[1]]} · ${CONS[p[2]]||p[2]} · ${stars(p[6])} · экзон ${p[7]||'—'}`,e.clientX,e.clientY)}else hideTip()});svg.addEventListener('mouseleave',hideTip)}
  return svg;
}
barcode(document.getElementById('heroViz'),{rowH:84,interactive:false});
let minStar=0;function drawBarcode(){barcode(document.getElementById('barcodeViz'),{minStar})}
drawBarcode();
document.querySelectorAll('#starToggle button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#starToggle button').forEach(x=>x.classList.toggle('on',x===b));minStar=+b.dataset.s;drawBarcode()});

/* threshold */
(function(){const host=document.getElementById('thrViz'),rng=document.getElementById('thrRange'),val=document.getElementById('thrVal'),kp=document.getElementById('kpis'),note=document.getElementById('thrNote');
  const W=1000,H=200,left=40;const svg=el('svg',{viewBox:`0 0 ${W} ${H}`},host);const x=i=>left+i/(D.curve.length-1)*(W-left-20);
  /* sens & spec curves */
  const path=(idx,cls)=>{let d='';D.curve.forEach((c,i)=>{d+=(i?'L':'M')+x(i)+','+(H-30-c[idx]*(H-50))});return el('path',{d,fill:'none',stroke:cls,'stroke-width':1.8},svg)};
  path(1,'var(--ink)');path(2,'var(--down)');
  [0,.5,1].forEach(v=>{el('line',{x1:left,x2:W-20,y1:H-30-v*(H-50),y2:H-30-v*(H-50),class:'grid'},svg);el('text',{x:left-6,y:H-30-v*(H-50)+4,class:'axlab','text-anchor':'end'},svg).textContent=v});
  [[1,'0,9'],[2,'0,99'],[3,'0,999'],[4,'0,9999']].forEach(([e,l])=>{const i=(e-1)/3.3*(D.curve.length-1);el('line',{x1:x(i),x2:x(i),y1:20,y2:H-30,class:'grid'},svg);el('text',{x:x(i),y:H-10,class:'axlab','text-anchor':'middle'},svg).textContent=l});
  el('text',{x:left+8,y:16,class:'axlab',style:'fill:var(--ink)'},svg).textContent='— чувствительность (патогенные пойманы)';el('text',{x:left+8,y:30,class:'axlab',style:'fill:var(--down)'},svg).textContent='— специфичность (доброкачественные не оклеветаны)';
  const cur=el('line',{x1:0,x2:0,y1:0,y2:H-30,class:'thr'},svg);
  function upd(){const i=+rng.value;const c=D.curve[i];cur.setAttribute('x1',x(i));cur.setAttribute('x2',x(i));val.textContent=c[0].toFixed(4).replace('.',',');
    kp.innerHTML=`<div class="kpi"><b>${Math.round(c[1]*100)} %</b><span>чувствительность</span><small>из ${S.n.P} патогенных поймано ${Math.round(c[1]*S.n.P)}</small></div><div class="kpi"><b>${Math.round(c[2]*100)} %</b><span>специфичность</span><small>из ${S.n.B} доброкачественных ложно обвинено ${Math.round((1-c[2])*S.n.B)}</small></div><div class="kpi"><b>${c[3]}</b><span>неопределённых → «опасно»</span><small>из ${S.n.VUS} при этой черте</small></div><div class="kpi"><b>${c[0]>=0.999?'верхняя тысячная':c[0]>=0.99?'верхний процент':'верхние 10 %'}</b><span>где черта</span><small>относительно всех 9 млрд замен генома</small></div>`;
    note.textContent=c[0]<0.97?'Слишком низко: ловим почти всех, но обвиняем половину невиновных — BRCA1 слишком консервативен для такой черты.':c[0]<0.996?'Рабочая зона: и чувствительность, и специфичность выше 95 %. Примерно здесь модель и клиника согласны лучше всего.':'Строгая черта: почти без ложных обвинений, но каждая четвёртая-пятая опасная замена остаётся за бортом.'}
  rng.addEventListener('input',upd);upd();
  svg.addEventListener('click',e=>{const r=svg.getBoundingClientRect();const px=(e.clientX-r.left)/r.width*W;rng.value=Math.round((px-left)/(W-left-20)*(D.curve.length-1));upd()});
})();

/* gene map (transcript orientation: minus strand -> flip) */
(function(){const host=document.getElementById('mapViz');const G=D.gene;const W=1000,H=320,left=20,right=20,yA=150;
  const svg=el('svg',{viewBox:`0 0 ${W} ${H}`},host);
  /* squashed layout: exons get min width, introns compressed */
  const ex=[...G.exons].sort((a,b)=>b.start-a.start); /* transcript order for minus strand */
  const total=G.end-G.start;const segs=[];let acc=0;
  /* allocate: exon width = max(6, len*k), intron width = sqrt-compressed */
  const exLen=ex.reduce((s,e)=>s+(e.end-e.start),0);
  const intr=[];for(let i=0;i<ex.length-1;i++)intr.push(ex[i].start-ex[i+1].end);
  const exScale=0.55*(W-left-right)/exLen;const intrUnit=0.45*(W-left-right)/intr.reduce((s,v)=>s+Math.sqrt(v),0);
  let xcur=left;const exonX=[];
  ex.forEach((e,i)=>{const w=Math.max(6,(e.end-e.start)*exScale);exonX.push({e,x:xcur,w});xcur+=w;if(i<ex.length-1)xcur+=Math.sqrt(intr[i])*intrUnit});
  const posX=p=>{for(let i=0;i<exonX.length;i++){const {e,x,w}=exonX[i];if(p>=e.start&&p<=e.end)return x+w*(1-(p-e.start)/(e.end-e.start||1));
      if(i<exonX.length-1&&p<e.start&&p>exonX[i+1].e.end){const a=x+w,b=exonX[i+1].x;return a+(b-a)*(1-(p-exonX[i+1].e.end)/(e.start-exonX[i+1].e.end))}}
    return p>G.end?left:xcur};
  el('line',{x1:left,x2:xcur,y1:yA,y2:yA,stroke:'var(--ink)',opacity:.4},svg);
  exonX.forEach(({e,x,w},i)=>{const utr=e.end<G.cds[0]||e.start>G.cds[1];el('rect',{x,y:yA-9,width:w,height:18,class:'exon'+(utr?' utr':'')},svg);el('text',{x:x+w/2,y:yA+24,class:'exlab'},svg).textContent=e.i;
    const t=el('title',{},svg);});
  D.points.filter(p=>['P','B','VUS'].includes(p[1])).forEach((p,i)=>{const xx=posX(p[0]);const j=seeded(i)*40;const y1=p[1]==='P'?yA-16-j:p[1]==='B'?yA+34+j:yA-8;const y2=p[1]==='VUS'?yA+8:(p[1]==='P'?y1-14:y1+14);
    const l=el('line',{x1:xx,x2:xx,y1,y2,class:'mk '+p[1]},svg);l.__p=p});
  el('text',{x:left,y:yA-92,class:'axlab'},svg).textContent='↑ патогенные';el('text',{x:left,y:yA+100,class:'axlab'},svg).textContent='↓ доброкачественные · золотом на экзонах — неопределённые';
  el('text',{x:left,y:H-4,class:'axlab'},svg).textContent="5′ · начало гена (экзон 1)";el('text',{x:xcur,y:H-4,class:'axlab','text-anchor':'end'},svg).textContent="конец гена (экзон 23) · 3′";
  /* exon summary hover */
  exonX.forEach(({e,x,w})=>{const r=el('rect',{x,y:yA-100,width:w,height:200,fill:'transparent'},svg);r.addEventListener('mousemove',ev=>showTip(`Экзон ${e.i} · ${(e.end-e.start+1)} п.о.<br><b>${e.P} патогенных · ${e.B} доброкачественных · ${e.VUS} неопределённых</b>`,ev.clientX,ev.clientY));r.addEventListener('mouseleave',hideTip)});
})();

/* VUS strip */
(function(){const host=document.getElementById('vusViz');const W=1000,H=120,left=40,right=30;const svg=el('svg',{viewBox:`0 0 ${W} ${H}`},host);const x=v=>left+X(v)/XMAX*(W-left-right);
  TICKS.forEach(([v,l])=>{const xx=left+v/XMAX*(W-left-right);el('line',{x1:xx,x2:xx,y1:0,y2:H-24,class:'grid'},svg);el('text',{x:xx,y:H-8,class:'axlab','text-anchor':'middle'},svg).textContent=l});
  el('rect',{x:x(.99),y:0,width:W-right-x(.99),height:H-24,fill:'var(--ink)',opacity:.05},svg);el('rect',{x:left,y:0,width:x(.9)-left,height:H-24,fill:'var(--down)',opacity:.07},svg);
  el('text',{x:x(.99)+6,y:14,class:'axlab'},svg).textContent=`верхний 1 % · ${S.vus.ge99}`;el('text',{x:left+6,y:14,class:'axlab'},svg).textContent=`ниже 0,9 · ${S.vus.lt90}`;
  const pts=D.points.filter(p=>p[1]==='VUS');pts.forEach((p,i)=>{const yy=22+seeded(i*3)*(H-60);const l=el('line',{x1:x(p[3]),x2:x(p[3]),y1:yy,y2:yy+12,class:'bc VUS'},svg);l.__p=p});
})();

/* glossary tooltips */
(function(){let pinned=null;function show(t){tip.className='tip def';tip.innerHTML=`<b>${t.dataset.t}</b>${t.dataset.d}`;const r=t.getBoundingClientRect();tip.style.left=Math.min(Math.max(160,r.left+r.width/2),innerWidth-160)+'px';tip.style.top=r.top+'px';tip.style.opacity=1}
  function hide(){if(pinned)return;tip.style.opacity=0}
  document.addEventListener('mouseover',e=>{const t=e.target.closest('.term');if(t)show(t)});document.addEventListener('mouseout',e=>{if(e.target.closest('.term'))hide()});
  document.addEventListener('click',e=>{const t=e.target.closest('.term');if(t){pinned=pinned===t?null:t;if(pinned)show(t);else hide()}else if(pinned){pinned=null;hide()}});addEventListener('scroll',()=>{if(pinned){pinned=null;hide()}},{passive:true})})();
</script>
</body></html>
'''
vl = lambda L: ''.join(f'<div><span>{html.escape(n)}</span><b>{str(round(q,4)).replace(".",",")} <span class="stars">{"★"*s}{"☆"*(3-s)}</span></b></div>' for n, q, s in L)
page = (page.replace('%%INTRO%%', ''.join(f'<div class="intro-block"><h5>{h}</h5><p>{t}</p></div>' for h, t in intro))
        .replace('%%N_P%%', fmt(S['n']['P'])).replace('%%N_B%%', fmt(S['n']['B'])).replace('%%N_V%%', fmt(S['n']['VUS'])).replace('%%N_C%%', fmt(S['n']['conflict']))
        .replace('%%S_BARCODE%%', sec['barcode']).replace('%%S_EXPERT%%', sec['expert']).replace('%%S_THRESHOLD%%', sec['threshold']).replace('%%S_MAP%%', sec['map']).replace('%%S_DISAGREE%%', sec['disagree']).replace('%%S_VUS%%', sec['vus'])
        .replace('%%CARDS%%', cards).replace('%%VUS_TOP%%', vl(DATA['examples']['vus_top'])).replace('%%VUS_BOTTOM%%', vl(DATA['examples']['vus_bottom']))
        .replace('%%SOURCES%%', ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for t, u in SOURCES3))
        .replace('%%DATA%%', json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))))
open('brca1.html', 'w', encoding='utf-8').write(page)
print('ok', len(page) // 1024, 'KB')
