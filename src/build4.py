# -*- coding: utf-8 -*-
import re, json, html
from story4 import INTRO4, SECTIONS4, GLOSSARY4, SOURCES4
D = json.load(open('finale_data.json', encoding='utf-8')); F = D['funnel']; SG = D['sge']

def wrap(text, seen):
    toks = {}
    def sub(m, title, d):
        if title in seen: return m.group(0)
        seen.add(title); k = f"\x00{len(toks)}\x00"
        toks[k] = f'<span class="term" tabindex="0" data-t="{html.escape(title)}" data-d="{html.escape(d)}">{m.group(0)}</span>'
        return k
    t = text
    for rx, title, d in GLOSSARY4:
        t = re.sub(rx, lambda m: sub(m, title, d), t, count=1, flags=re.I)
    for k, v in toks.items(): t = t.replace(k, v)
    return t
seen = set()
intro = [(h, wrap(t, seen)) for h, t in INTRO4]
sec = {k: wrap(v, seen) for k, v in SECTIONS4.items()}
fmt = lambda n: f'{n:,}'.replace(',', ' ')

page = r'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Чего никто не видел</title>
<style>
  :root{--paper:#f5f2ec;--paper-2:#ece8df;--ink:#17160f;--ink-2:#5a574d;--ink-3:#9a968a;--line:#d8d3c7;--accent:#c4901e;--accent-soft:#e9d8a8;--down:#2f6f7e;
    --serif:"Iowan Old Style","Palatino Linotype","Book Antiqua",Georgia,serif;--sans:"Helvetica Neue",Helvetica,Arial,system-ui,sans-serif;--mono:"SF Mono",Menlo,Consolas,monospace}
  *{box-sizing:border-box} html{scroll-behavior:smooth}
  body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
  .hero{padding:80px clamp(20px,6vw,90px) 50px;display:grid;grid-template-columns:minmax(300px,520px) minmax(0,1fr);gap:40px clamp(30px,5vw,90px);align-items:center}
  .hero h1{font:400 clamp(44px,6.5vw,92px)/1 var(--serif);letter-spacing:-.02em;margin:0 0 22px} .hero h1 em{font-style:italic;color:var(--accent)}
  .hero p{font:19px/1.5 var(--serif);color:var(--ink-2);margin:0;max-width:560px}
  .hero .kick{font:12px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin-top:24px}
  .mednote{font:12px/1.5 var(--mono);color:var(--ink-3);margin-top:14px;max-width:520px}
  .ladder{display:grid;gap:10px}
  .ladder .row{display:grid;grid-template-columns:170px 1fr 90px;gap:14px;align-items:center;font:12px var(--sans);color:var(--ink-2)}
  .ladder .row b{font:400 15px var(--serif);color:var(--ink)} .ladder .bar{height:22px;position:relative} .ladder .bar i{position:absolute;left:0;top:0;bottom:0;background:var(--ink)}
  .ladder .bar i.o{background:var(--ink);opacity:.35} .ladder .bar i.c{background:var(--ink);opacity:.6} .ladder .bar i.l{background:var(--down)} .ladder .bar i.e{background:var(--accent)}
  .ladder .v{font:12px var(--mono);color:var(--ink);text-align:right;font-variant-numeric:tabular-nums} .ladder .v small{display:block;color:var(--ink-3);font-size:10px}
  .intro{padding:60px clamp(20px,6vw,90px) 50px;border-top:1px solid var(--line);display:grid;grid-template-columns:minmax(0,640px);gap:28px}
  .intro-block{display:grid;grid-template-columns:140px 1fr;gap:20px;align-items:start}
  .intro-block h5{font:12px/1.6 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:4px 0 0}
  .intro-block p{font:17px/1.6 var(--serif);color:var(--ink);margin:0} .intro-block:first-child p{font-size:21px;line-height:1.45}
  section.blk{padding:70px clamp(20px,6vw,90px);border-top:1px solid var(--line)}
  section.blk h2{font:400 clamp(30px,3.8vw,48px)/1.05 var(--serif);letter-spacing:-.02em;margin:0 0 10px}
  .lead{font:17px/1.6 var(--serif);color:var(--ink);max-width:680px;margin:0 0 26px}
  .two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:40px;align-items:start}
  .term{border-bottom:1px dotted var(--accent);cursor:help} .term:hover,.term:focus{background:var(--accent-soft);outline:none}
  .tip{position:fixed;pointer-events:none;z-index:60;background:var(--ink);color:var(--paper);font:12px/1.4 var(--mono);padding:8px 10px;border-radius:2px;opacity:0;transform:translate(-50%,-125%);transition:opacity .12s;white-space:nowrap}
  .tip b{color:var(--accent-soft);font-weight:400}
  .tip.def{white-space:normal;max-width:300px;font-family:var(--sans);font-size:13px;line-height:1.45;transform:translate(-50%,-115%);text-align:left}
  .tip.def b{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px}
  svg{display:block;width:100%;height:auto;overflow:visible}
  .axlab{font:10.5px var(--mono);fill:var(--ink-3);letter-spacing:.04em}
  /* waffle */
  .waffle{display:grid;grid-template-columns:repeat(40,1fr);gap:3px;max-width:900px}
  .waffle i{aspect-ratio:1;display:block;background:var(--line);border-radius:1px;transition:transform .2s}
  .waffle i.o{background:var(--ink);opacity:.35} .waffle i.c{background:var(--ink);opacity:.6} .waffle i.l{background:var(--down)} .waffle i.e{background:var(--accent)}
  .wl{display:flex;flex-wrap:wrap;gap:8px 20px;font:11px var(--mono);color:var(--ink-2);letter-spacing:.04em;margin:14px 0 0} .wl i{display:inline-block;width:11px;height:11px;border-radius:1px;vertical-align:-1px;margin-right:6px;background:var(--line)}
  .wl i.o{background:var(--ink);opacity:.35} .wl i.c{background:var(--ink);opacity:.6} .wl i.l{background:var(--down)} .wl i.e{background:var(--accent)}
  .bignum{font:400 clamp(60px,9vw,120px)/1 var(--serif);letter-spacing:-.03em;margin:0} .bignum small{display:block;font:12px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin-top:8px}
  /* genes bars */
  .gbars .row{display:grid;grid-template-columns:90px 1fr 60px 1fr 60px;gap:10px;align-items:center;font:12px var(--sans);color:var(--ink-2);margin-bottom:7px}
  .gbars .row b{font:600 12px var(--mono);color:var(--ink)} .gbars .bar{height:10px;background:var(--paper-2);position:relative} .gbars .bar i{position:absolute;left:0;top:0;bottom:0;background:var(--ink);opacity:.5} .gbars .bar i.t{background:var(--accent);opacity:1}
  .gbars .v{font:11px var(--mono);color:var(--ink-3);text-align:right} .gbars .h{font:11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)}
  /* coverage table */
  .cov{border-collapse:collapse;font:13px var(--sans);max-width:560px;width:100%} .cov th{font:11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);text-align:left;padding:8px 10px;border-bottom:1px solid var(--ink);font-weight:400} .cov td{padding:8px 10px;border-bottom:1px solid var(--line)} .cov td.n{font-family:var(--mono);text-align:right}
  /* scatter */
  .sc .pt{opacity:.55} .sc .pt.func{fill:var(--down)} .sc .pt.nonfunc{fill:var(--ink)} .sc .pt.inter{fill:var(--accent)}
  .kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0}
  .kpi{border-top:1px solid var(--ink);padding-top:8px} .kpi b{display:block;font:400 40px/1 var(--serif);letter-spacing:-.02em} .kpi span{font:11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)} .kpi small{display:block;font:12px var(--sans);color:var(--ink-2);margin-top:4px}
  .exl h4{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-2);margin:16px 0 8px} .exl div{display:flex;justify-content:space-between;gap:10px;font:12.5px var(--mono);border-bottom:1px dotted var(--line);padding:4px 0} .exl div b{font-weight:400;color:var(--ink-3)}
  /* circular diagram */
  .circ text{font:12px var(--sans);fill:var(--ink)} .circ .node{fill:var(--paper);stroke:var(--ink);stroke-width:1} .circ .node.model{stroke:var(--accent);stroke-width:2} .circ .arr{fill:none;stroke:var(--ink);stroke-width:1.2;marker-end:url(#ah)} .circ .arr.hot{stroke:var(--accent);stroke-width:1.6} .circ .lab{font:10.5px var(--mono);fill:var(--ink-2)}
  .close{padding:90px clamp(20px,6vw,90px);border-top:1px solid var(--ink);background:var(--paper-2)}
  .close h2{font:400 clamp(36px,5vw,72px)/1 var(--serif);letter-spacing:-.02em;margin:0 0 26px;max-width:900px} .close h2 em{font-style:italic;color:var(--accent)}
  .close p{font:19px/1.6 var(--serif);max-width:720px;margin:0}
  .method{padding:60px clamp(20px,6vw,90px) 80px;border-top:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr;gap:40px;font-size:14px;color:var(--ink-2)}
  .method h5{font:12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink);margin:0 0 10px} .method p{margin:0 0 10px}
  .srcs{font:13px var(--sans);color:var(--ink-2)} .srcs ol{margin:8px 0 0;padding-left:18px;display:grid;gap:4px} .srcs a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid var(--line)}
  .tag{position:fixed;right:14px;bottom:14px;z-index:50;font:11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;background:var(--ink);color:var(--paper);padding:8px 10px;border-radius:2px;opacity:.85}
  @media (max-width:1000px){.hero,.two,.method{grid-template-columns:1fr}.kpis{grid-template-columns:1fr}.waffle{grid-template-columns:repeat(25,1fr)}}
  @media (max-width:700px){.intro-block{grid-template-columns:1fr;gap:6px}.gbars .row{grid-template-columns:70px 1fr 50px}.gbars .row .t2{display:none}}
</style></head>
<body>
<div class="tag">данные: Atlas + gnomAD + ClinVar + MaveDB · черновик</div>
<div class="tip" id="tip"></div>
<section class="hero">
  <div>
    <h1>Чего никто <em>не видел</em></h1>
    <p>Финал. Три истории мы проверяли модель — врачами, тканями, консилиумом. Теперь про то, какая часть Атласа вообще проверяема. Спойлер: очень небольшая.</p>
    <div class="kick">Ген BRCA1 · 389 859 возможных замен · лестница проверки</div>
    <div class="mednote">Всё на этой странице — предсказания модели и открытые данные, не медицинская информация.</div>
  </div>
  <div class="ladder" id="ladder"></div>
</section>

<section class="intro">%%INTRO%%</section>

<section class="blk" id="waffle">
  <h2>Тысяча квадратов</h2>
  <p class="lead">%%S_WAFFLE%%</p>
  <div class="waffle" id="waffleGrid"></div>
  <div class="wl"><span><i></i>только в модели · 872</span><span><i class="o"></i>видели у людей · 128</span><span><i class="c"></i>есть вердикт ClinVar · 30</span><span><i class="l"></i>проверили в лаборатории · 10</span><span><i class="e"></i>экспертная комиссия · 4</span></div>
</section>

<section class="blk" id="top">
  <div class="two">
    <div><h2>А если только опасные?</h2><p class="lead">%%S_TOP%%</p></div>
    <div><div class="bignum">%%TOP1%%<small>замен BRCA1 в верхнем проценте генома по модели</small></div><div class="ladder" id="ladderTop" style="margin-top:26px"></div></div>
  </div>
</section>

<section class="blk" id="genes">
  <h2>Десять генов, та же история</h2>
  <p class="lead">%%S_GENES%%</p>
  <div class="gbars" id="gbars"></div>
</section>

<section class="blk" id="coverage">
  <div class="two">
    <div><h2>Микроскоп, а не территория</h2><p class="lead">%%S_COVERAGE%%</p></div>
    <table class="cov"><thead><tr><th>Квантиль по модели</th><th>Замен в BRCA1</th><th>Видели у людей</th></tr></thead><tbody>%%COV%%</tbody></table>
  </div>
</section>

<section class="blk" id="lab">
  <h2>Против пробирки</h2>
  <p class="lead">%%S_LAB%%</p>
  <div class="kpis"><div class="kpi"><b>%%AUC%%</b><span>согласие с экспериментом</span><small>AUC, %%NSGE%% замен, «нефункциональные» против «функциональных»</small></div><div class="kpi"><b>%%AUCM%%</b><span>по миссенс-заменам</span><small>%%NMIS%% замен аминокислот — самый трудный класс</small></div><div class="kpi"><b>0,999</b><span>согласие с комиссией</span><small>для сравнения — из третьей истории</small></div></div>
  <div class="two">
    <div id="scatter"></div>
    <div class="exl"><h4>Клетки говорят «сломано», модель — «почти ничего»</h4>%%EX1%%<h4>Клетки говорят «работает», модель — «верхняя тысячная»</h4>%%EX2%%</div>
  </div>
</section>

<section class="blk" id="circular">
  <div class="two">
    <div><h2>Кто у кого списывал</h2><p class="lead">%%S_CIRCULAR%%</p></div>
    <div id="circ"></div>
  </div>
</section>

<section class="close">
  <h2>Карта — не территория. <em>Хорошая карта</em> — всё равно не территория.</h2>
  <p>%%S_CLOSE%%</p>
</section>

<section class="method">
  <div><h5>Откуда данные</h5>
    <p>Атлас: те же 389 859 замен BRCA1 и окна ±5 000 букв десяти генов, что в историях 01 и 03. gnomAD v4.1 через GraphQL API: все однобуквенные варианты в тех же координатах, «видели» = allele count ≥ 1 в экзомах или геномах. Оценка «меньше десятой части» для генома целиком: в gnomAD v4 каталогизировано 786,5 млн SNV — около 9 % из ~9 млрд возможных. ClinVar: 11 650 записей из истории 03. Эксперимент: Findlay et al. 2018, нормализованные оценки из MaveDB (urn:mavedb:00000097-0-2), координаты c.-номенклатуры NM_007294.3 пересчитаны в GRCh38 по каноническому транскрипту; референсная буква совпала с Атласом для 100 % из 3 828 замен. Классы по порогам авторов: нефункциональные &lt; −1,328, функциональные &gt; −0,748.</p>
    <details class="srcs"><summary>Источники</summary><ol>%%SOURCES%%</ol></details>
  </div>
  <div><h5>Что здесь не так, как в жизни</h5>
    <p>«Не видели у людей» означает «нет в gnomAD» — в других базах и в клинических выборках часть этих замен есть: 7 607 замен BRCA1 из ClinVar в gnomAD отсутствуют. Эксперимент Findlay измеряет выживаемость одной клеточной линии, а не риск болезни; его порогов достаточно для сравнения, но не для диагноза. Обе стороны сравнения — и Атлас, и пробирка — могут ошибаться одновременно.</p>
    <p>Скрипты и данные: prep_finale.py, finale_data.json, data/gnomad_*.parquet, data/brca1_sge_joined.parquet.</p>
  </div>
</section>

<script>
const D=%%DATA%%;const F=D.funnel;
const NS='http://www.w3.org/2000/svg';const el=(n,a={},p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);p&&p.appendChild(e);return e};
const tip=document.getElementById('tip');function showTip(h,x,y,cls){tip.className='tip'+(cls?' '+cls:'');tip.innerHTML=h;tip.style.left=Math.min(Math.max(150,x),innerWidth-150)+'px';tip.style.top=y+'px';tip.style.opacity=1}function hideTip(){tip.style.opacity=0}
const fmt=n=>n.toLocaleString('ru-RU').replace(/,/g,' ');
function ladder(host,rows,total){host.innerHTML=rows.map(([l,v,c])=>`<div class="row"><b>${l}</b><div class="bar"><i class="${c}" style="width:${Math.max(.4,v/total*100)}%"></i></div><div class="v">${fmt(v)}<small>${(v/total*100).toFixed(1)} %</small></div></div>`).join('')}
ladder(document.getElementById('ladder'),[['возможных замен',F.possible,''],['видели у людей',F.observed,'o'],['есть в ClinVar',F.clinvar,'c'],['проверили в клетках',F.sge,'l'],['экспертная комиссия',F.expert,'e']],F.possible);
ladder(document.getElementById('ladderTop'),[['в верхнем 1 %',F.top1,''],['видели у людей',F.top1_observed,'o'],['есть в ClinVar',F.top1_clinvar,'c'],['проверили в клетках',F.top1_sge,'l'],['экспертная комиссия',F.top1_expert,'e']],F.top1);
/* waffle */
(function(){const g=document.getElementById('waffleGrid');const n=1000;const per=F.possible/n;const cnt={o:Math.round(F.observed/per),c:Math.round(F.clinvar/per),l:Math.round(F.sge/per),e:Math.round(F.expert/per)};
  /* seeded shuffle of positions so layers look scattered but nested */
  let s=7;const r=()=>{s=(s*9301+49297)%233280;return s/233280};const idx=[...Array(n).keys()];for(let i=n-1;i>0;i--){const j=Math.floor(r()*(i+1));[idx[i],idx[j]]=[idx[j],idx[i]]}
  const cls=new Array(n).fill('');idx.slice(0,cnt.o).forEach(i=>cls[i]='o');idx.slice(0,cnt.c).forEach(i=>cls[i]='c');idx.slice(0,cnt.l).forEach(i=>cls[i]='l');idx.slice(0,cnt.e).forEach(i=>cls[i]='e');
  const names={'':'существует только в модели',o:'видели хотя бы у одного человека',c:'есть вердикт в ClinVar',l:'проверили в лаборатории (Findlay 2018)',e:'высказалась экспертная комиссия'};
  cls.forEach((c,i)=>{const d=document.createElement('i');if(c)d.className=c;d.addEventListener('mousemove',e=>showTip(`≈ ${fmt(Math.round(per))} замен · <b>${names[c]}</b>`,e.clientX,e.clientY));d.addEventListener('mouseleave',hideTip);g.appendChild(d)});})();
/* genes bars */
(function(){const h=document.getElementById('gbars');h.innerHTML='<div class="row"><span></span><span class="h">видели у людей, из 30 000</span><span></span><span class="h t2">видели среди верхнего 1 %</span><span class="t2"></span></div>'+D.genes.sort((a,b)=>b.observed-a.observed).map(g=>`<div class="row"><b>${g.gene}</b><div class="bar"><i style="width:${g.observed*100/0.35}%"></i></div><span class="v">${(g.observed*100).toFixed(0)} %</span><div class="bar t2"><i class="t" style="width:${g.top1_observed*100/0.45}%"></i></div><span class="v t2">${(g.top1_observed*100).toFixed(0)} %</span></div>`).join('')})();
/* scatter */
(function(){const host=document.getElementById('scatter');const W=600,H=420,L=50,B=40,T=16,R=16;const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'sc'},host);
  const X=s=>L+(s+3.2)/(3.2+1.0)*(W-L-R);const Y=q=>T+(1-Math.min(5.3,-Math.log10(Math.max(1e-6,1-q)))/5.3)*(H-T-B);
  [[-3,'−3'],[-2,'−2'],[-1,'−1'],[0,'0']].forEach(([v,l])=>{el('line',{x1:X(v),x2:X(v),y1:T,y2:H-B,stroke:'var(--line)','stroke-dasharray':'2 4'},svg);el('text',{x:X(v),y:H-B+16,class:'axlab','text-anchor':'middle'},svg).textContent=l});
  [[0,'0'],[.9,'0,9'],[.99,'0,99'],[.999,'0,999'],[.9999,'0,9999']].forEach(([v,l])=>{el('line',{x1:L,x2:W-R,y1:Y(v),y2:Y(v),stroke:'var(--line)','stroke-dasharray':'2 4'},svg);el('text',{x:L-6,y:Y(v)+4,class:'axlab','text-anchor':'end'},svg).textContent=l});
  el('line',{x1:X(-1.328),x2:X(-1.328),y1:T,y2:H-B,stroke:'var(--ink)',opacity:.5},svg);el('line',{x1:X(-0.748),x2:X(-0.748),y1:T,y2:H-B,stroke:'var(--ink)',opacity:.5},svg);
  el('text',{x:X(-2.2),y:T+12,class:'axlab','text-anchor':'middle'},svg).textContent='клетки: ген сломан';el('text',{x:X(0.1),y:T+12,class:'axlab','text-anchor':'middle'},svg).textContent='клетки: ген работает';
  el('text',{x:W-R,y:H-4,class:'axlab','text-anchor':'end'},svg).textContent='оценка эксперимента (выживаемость клеток) →';el('text',{x:L,y:H-4,class:'axlab'},svg).textContent='↑ квантиль модели';
  let s=3;const r=()=>{s=(s*9301+49297)%233280;return s/233280};
  D.sge_points.forEach(p=>{const c=el('circle',{cx:X(Math.max(-3.2,Math.min(1,p[0])))+(r()-.5)*2,cy:Y(p[1]),r:2.2,class:'pt '+p[4]},svg);c.addEventListener('mousemove',e=>showTip(`${p[3]} · ${p[2]}<br><b>эксперимент ${p[0].toFixed(2)} · квантиль ${p[1].toFixed(4)}</b>`,e.clientX,e.clientY));c.addEventListener('mouseleave',hideTip)});
})();
/* circular diagram */
(function(){const host=document.getElementById('circ');const W=560,H=380;const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'circ'},host);
  const defs=el('defs',{},svg);const m=el('marker',{id:'ah',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:7,markerHeight:7,orient:'auto-start-reverse'},defs);el('path',{d:'M0,0 L10,5 L0,10 z',fill:'var(--ink)'},m);
  const nodes={enc:[110,60,'ENCODE / GTEx'],model:[280,190,'AlphaGenome · AVI'],am:[110,190,'AlphaMissense'],cv:[450,190,'ClinVar'],exp:[450,60,'Комиссия ENIGMA'],sge:[450,320,'Пробирка (Findlay)'],cons:[110,320,'Консервативность']};
  const box=(k)=>{const [x,y,t]=nodes[k];el('rect',{x:x-80,y:y-18,width:160,height:36,rx:3,class:'node'+(k==='model'?' model':'')},svg);el('text',{x,y:y+4,'text-anchor':'middle'},svg).textContent=t};
  const arrow=(a,b,lab,hot,dx=0,dy=0)=>{const [x1,y1]=nodes[a],[x2,y2]=nodes[b];const ang=Math.atan2(y2-y1,x2-x1);const sx=x1+Math.cos(ang)*84,sy=y1+Math.sin(ang)*20,ex=x2-Math.cos(ang)*84,ey=y2-Math.sin(ang)*20;el('line',{x1:sx,y1:sy,x2:ex,y2:ey,class:'arr'+(hot?' hot':'')},svg);if(lab)el('text',{x:(sx+ex)/2+dx,y:(sy+ey)/2+dy,class:'lab','text-anchor':'middle'},svg).textContent=lab};
  Object.keys(nodes).forEach(box);
  arrow('enc','model','обучение',true,-30,-6);arrow('am','model','признак',true,0,-6);arrow('cons','model','признак',true,-30,10);
  arrow('sge','cv','3 828 результатов отправлены',false,60,14);arrow('cv','exp','вердикты',false,40,0);arrow('exp','cv','',false);
  el('text',{x:280,y:H-8,class:'lab','text-anchor':'middle'},svg).textContent='золотые стрелки — что модель видела при обучении; сравнение с ClinVar не является независимым';
})();
/* glossary */
(function(){let pinned=null;function show(t){tip.className='tip def';tip.innerHTML=`<b>${t.dataset.t}</b>${t.dataset.d}`;const r=t.getBoundingClientRect();tip.style.left=Math.min(Math.max(160,r.left+r.width/2),innerWidth-160)+'px';tip.style.top=r.top+'px';tip.style.opacity=1}
  function hide(){if(pinned)return;tip.style.opacity=0}
  document.addEventListener('mouseover',e=>{const t=e.target.closest('.term');if(t)show(t)});document.addEventListener('mouseout',e=>{if(e.target.closest('.term'))hide()});
  document.addEventListener('click',e=>{const t=e.target.closest('.term');if(t){pinned=pinned===t?null:t;if(pinned)show(t);else hide()}else if(pinned){pinned=null;hide()}});addEventListener('scroll',()=>{if(pinned){pinned=null;hide()}},{passive:true})})();
</script>
</body></html>
'''
cov = ''.join(f'<tr><td>{k}</td><td class="n">{fmt(F["n_by_q"][k])}</td><td class="n">{F["obs_by_q"][k]*100:.1f} %</td></tr>' for k in F['n_by_q'])
exl = lambda L: ''.join(f'<div><span>{html.escape(h)} · {k}</span><b>эксп. {s:.2f} · q {str(round(q,3)).replace(".",",")}</b></div>' for h, k, s, q in L)
page = (page.replace('%%INTRO%%', ''.join(f'<div class="intro-block"><h5>{h}</h5><p>{t}</p></div>' for h, t in intro))
  .replace('%%S_WAFFLE%%', sec['waffle']).replace('%%S_TOP%%', sec['top']).replace('%%S_GENES%%', sec['genes']).replace('%%S_COVERAGE%%', sec['coverage']).replace('%%S_LAB%%', sec['lab']).replace('%%S_CIRCULAR%%', sec['circular']).replace('%%S_CLOSE%%', sec['close'])
  .replace('%%TOP1%%', fmt(F['top1'])).replace('%%COV%%', cov)
  .replace('%%AUC%%', f"{SG['auc']:.3f}".replace('.', ',')).replace('%%AUCM%%', f"{SG['auc_missense']:.3f}".replace('.', ',')).replace('%%NSGE%%', fmt(SG['n'])).replace('%%NMIS%%', fmt(SG['n_missense']))
  .replace('%%EX1%%', exl(D['ex_nf_low'])).replace('%%EX2%%', exl(D['ex_f_high']))
  .replace('%%SOURCES%%', ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for t, u in SOURCES4))
  .replace('%%DATA%%', json.dumps(D, ensure_ascii=False, separators=(',', ':'))))
open('finale.html', 'w', encoding='utf-8').write(page)
print('ok', len(page) // 1024, 'KB')
