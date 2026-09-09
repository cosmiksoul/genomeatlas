import re, json
from story import MODEL
s = open('template_genes.html', encoding='utf-8').read()
site = open('site_data.json', encoding='utf-8').read()

# 1. embed data
s = s.replace('<script>\n/* ---------- данные глав', '<script>\nconst SITE=' + site + ';\n/* ---------- данные глав', 1)
assert 'const SITE=' in s

# 2. replace builders
new_builders = r'''
/* ---------- real-data builders ---------- */
const FEAT_ORDER=['Белок (аминокислота)','Белок (обрыв/старт/стоп)','Сплайсинг','Консервативность','Открытость хроматина','Белки-регуляторы','Старт транскрипции','Уровень РНК','3D-контакты ДНК'];
function fmtPos(p){return p.toLocaleString('ru-RU').replace(/,/g,' ')}
function buildStrip(g,host){
  const D=SITE.genes[g.id],W=SITE.win,N=2*W,q=D.strip_q;
  const wrap=document.createElement('div');wrap.className='strip-wrap';host.appendChild(wrap);
  const cv=document.createElement('canvas');cv.className='strip';wrap.appendChild(cv);
  const svg=el('svg',{viewBox:`0 0 1000 56`,class:'structs'},wrap);
  function draw(){const w=wrap.clientWidth||900,h=64;cv.width=w*devicePixelRatio;cv.height=h*devicePixelRatio;cv.style.width=w+'px';cv.style.height=h+'px';const ctx=cv.getContext('2d');ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);ctx.clearRect(0,0,w,h);
    ctx.fillStyle='rgba(23,22,15,.06)';ctx.fillRect(0,h-1,w,1);
    const bw=w/N;for(let i=0;i<N;i++){const v=q[i]/99;if(v<.5)continue;const bh=Math.max(1,(v-.5)*2*(h-8));ctx.fillStyle=v>=.99?'rgba(23,22,15,.95)':v>=.95?'rgba(23,22,15,.55)':'rgba(23,22,15,.18)';ctx.fillRect(i*bw,h-1-bh,Math.max(bw,.6),bh)}
    ctx.fillStyle='#c4901e';ctx.fillRect(W*(w/N)-1,0,2,h)}
  draw();addEventListener('resize',draw);
  /* gene structures */
  const x=p=>(p-(D.pos-W))/N*1000;
  D.structs.forEach((st,k)=>{const y=14+k*16;const a=Math.max(0,x(st.start)),b=Math.min(1000,x(st.end));
    el('line',{x1:a,x2:b,y1:y,y2:y,stroke:'var(--ink)','stroke-width':1,opacity:.5},svg);
    st.exons.forEach(([s0,e0])=>{const ea=Math.max(0,x(s0)),eb=Math.min(1000,x(e0));if(eb>0&&ea<1000)el('rect',{x:ea,y:y-4,width:Math.max(1.2,eb-ea),height:8,fill:'var(--ink)',opacity:.85},svg)});
    const arrow=st.strand>0?'→':'←';const lx=Math.min(Math.max(a,4),940);el('text',{x:lx,y:y-7,class:'regionlab'},svg).textContent=`${st.name} ${arrow}`});
  if(!D.structs.length)el('text',{x:4,y:12,class:'regionlab'},svg).textContent='в окне нет генов, кодирующих белок';
  el('text',{x:0,y:54,class:'axlab'},svg).textContent=`${D.chrom}:${fmtPos(D.pos-W)}`;el('text',{x:1000,y:54,class:'axlab','text-anchor':'end'},svg).textContent=fmtPos(D.pos+W);
  el('text',{x:500,y:54,class:'axlab','text-anchor':'middle'},svg).textContent='▲ '+g.rs;
  cv.addEventListener('mousemove',e=>{const r=cv.getBoundingClientRect();const i=Math.floor((e.clientX-r.left)/r.width*N);if(i<0||i>=N)return;const p=D.pos-W+i;showTip(`${D.chrom}:${fmtPos(p)} (${i-W>=0?'+':''}${i-W} от варианта)<br><b>квантиль ${(q[i]/99).toFixed(2)}</b> — лучшая из 3 замен`,e.clientX,e.clientY)});
  cv.addEventListener('mouseleave',hideTip);
}
function buildZoom(g,host){
  const D=SITE.genes[g.id],Z=60,N=2*Z+1,rows=['A','C','G','T'];const cw=9,rh=14,left=30,top=10;
  const svg=el('svg',{viewBox:`0 0 ${left+N*cw} ${top+4*rh+22}`,class:'matrix'},host);
  rows.forEach((b,k)=>el('text',{x:0,y:top+k*rh+4,class:'rowlab'},svg).textContent='→ '+b);
  const circles=[];
  D.zoom.filter(z=>Math.abs(z[0])<=Z).forEach(([off,alt,avi,q])=>{const k=rows.indexOf(alt);const cx=left+(off+Z)*cw,cy=top+k*rh;const fam=off===0&&alt===D.alt;
    const c=el('circle',{cx,cy,r:q>.99?3.6:q>.9?2.8:1.9,fill:fam?'var(--accent)':'var(--ink)','fill-opacity':fam?1:.05+Math.pow(q,4)*.9,class:'cell'},svg);c.__d={q,avi,fam};circles.push(c);
    if(fam)el('circle',{cx,cy,r:6.5,fill:'none',stroke:'var(--accent)','stroke-width':1.4},svg);
    c.addEventListener('mousemove',e=>showTip(`${D.chrom}:${fmtPos(D.pos+off)} · ${D.zoom_ref[off]} → ${alt}<br><b>AVI ${avi.toFixed(2)} · квантиль ${q.toFixed(3)}</b>${fam?'<br>★ '+g.rs:''}`,e.clientX,e.clientY));c.addEventListener('mouseleave',hideTip)});
  rows.forEach((b,k)=>{});
  el('text',{x:left,y:top+4*rh+14,class:'axlab'},svg).textContent=`−${Z} букв`;el('text',{x:left+N*cw,y:top+4*rh+14,class:'axlab','text-anchor':'end'},svg).textContent=`+${Z} букв`;
  el('text',{x:left+Z*cw,y:top+4*rh+14,class:'axlab','text-anchor':'middle'},svg).textContent='▲ '+g.rs;
  return circles;
}
function buildTissues(g,host){
  const D=SITE.genes[g.id],rows=D.tissues;const rh=22,w=560,svg=el('svg',{viewBox:`0 0 ${w} ${rows.length*rh}`,class:'tissue'},host);
  const mx=Math.max(.01,...rows.map(r=>Math.abs(r.e)));const x0=190,x1=w-60,xm=(x0+x1)/2;
  el('line',{x1:xm,x2:xm,y1:0,y2:rows.length*rh,stroke:'var(--line)','stroke-width':1},svg);
  rows.forEach((d,k)=>{const y=k*rh+rh/2;const top=k===0;
    el('line',{x1:x0,x2:x1,y1:y,y2:y,stroke:'var(--line)','stroke-width':1,'stroke-dasharray':'1 3'},svg);
    el('text',{x:x0-10,y:y+4,class:'name'+(top?' top':''),'text-anchor':'end'},svg).textContent=d.t;
    const cx=xm+(d.e/mx)*(x1-xm);
    const c=el('circle',{cx,cy:y,r:3+Math.abs(d.e)/mx*8,fill:top?'var(--accent)':'var(--ink)','fill-opacity':top?1:.25+Math.abs(d.e)/mx*.6,stroke:'var(--paper)','stroke-width':2},svg);
    el('text',{x:w-4,y:y+4,class:'val','text-anchor':'end'},svg).textContent=(d.e>0?'+':'')+d.e.toFixed(3);
    c.addEventListener('mousemove',e=>showTip(`${d.raw}<br><b>Δ экспрессии ${D.targets[0]}: ${d.e>0?'+':''}${d.e.toFixed(4)}</b>${d.q!=null?' · квантиль '+d.q.toFixed(2):''}`,e.clientX,e.clientY));c.addEventListener('mouseleave',hideTip)});
  el('text',{x:x0,y:rows.length*rh+2,class:'axlab'},svg).textContent='↓ меньше';el('text',{x:x1,y:rows.length*rh+2,class:'axlab','text-anchor':'end'},svg).textContent='больше ↑';
}
function buildAttr(g,host){
  const D=SITE.genes[g.id],gr=Object.fromEntries(Object.entries(D.famous.groups).map(([k,v])=>[k,Math.min(1,v)]));const keys=[...FEAT_ORDER].sort((a,b)=>(gr[b]||0)-(gr[a]||0)).slice(0,6);
  const rh=30,w=570,units=20,svg=el('svg',{viewBox:`0 0 ${w} ${keys.length*rh}`,class:'attr'},host);
  keys.forEach((k,i)=>{const v=gr[k]||0,y=i*rh+rh/2,n=Math.round(v*units);
    el('text',{x:0,y:y+4,class:'lab',style:v<0.005?'fill:var(--ink-3)':''},svg).textContent=k;
    for(let u=0;u<units;u++)el('rect',{x:190+u*15,y:y-5,width:10,height:10,rx:1,class:'u'+(u<n?'':' off'),'fill-opacity':u<n?(i===0?1:.55):1},svg);
    el('text',{x:w-10,y:y+4,class:'pct','text-anchor':'end'},svg).textContent=v<0.005?'—':Math.round(v*100)+' %'});
}
'''
s = re.sub(r'function matrixData\(g\)\{.*?(?=\n/\* ---------- )', new_builders.strip('\n'), s, count=1, flags=re.S)
assert 'buildStrip' in s

# 3. chapter panels html + wiring
old_panels = s[s.index('    <div class="panels">'):s.index('    </div>`;\n  main.appendChild(s);')]
new_panels = '''    <div class="panels">
      <div class="panel"><div class="panel-h"><h3>30 000 замен вокруг варианта</h3><span class="sub">окно ±5 000 букв · для каждой позиции — самая сильная из 3 замен</span></div>
        <div class="legend"><span><i class="l1"></i>верхние 50 %</span><span><i class="l2"></i>верхние 5 %</span><span><i class="l3"></i>верхний 1 % генома</span><span><i class="acc" style="border-radius:0;width:3px;height:12px;border:0;background:var(--accent)"></i>знаменитый вариант</span></div>
        <div class="strip-host"></div>
        <p class="panel-note">${SITE.genes[g.id].share99>0.1?'Каждая шестая':SITE.genes[g.id].share99>0.05?'Каждая двадцатая':'Лишь одна из '+Math.round(1/SITE.genes[g.id].share99)} замен в этом окне попадает в верхний 1 % по всему геному (${(SITE.genes[g.id].share99*100).toFixed(1)} %). Знаменитый вариант ${SITE.genes[g.id].famous.share_above<0.01?'сильнее почти всех':SITE.genes[g.id].famous.share_above<0.1?'сильнее '+Math.round((1-SITE.genes[g.id].famous.share_above)*100)+' %':SITE.genes[g.id].famous.share_above>0.9?'слабее '+Math.round(SITE.genes[g.id].famous.share_above*100)+' %':'сильнее '+Math.round((1-SITE.genes[g.id].famous.share_above)*100)+' %'} соседних замен.</p></div>
      <div class="panel"><div class="panel-h"><h3>Крупный план: ±60 букв, все 3 замены</h3><span class="sub">строка — на какую букву заменили; тон и размер — квантиль AVI</span></div>
        <div class="legend"><span><i class="l1"></i>обычная</span><span><i class="l2"></i>верхние 10 %</span><span><i class="l3"></i>верхний 1 %</span><span><i class="acc"></i>знаменитый вариант</span></div>
        <div class="mx"></div>
        <div class="controls"><label>порог квантиля</label><input type="range" min="0" max="99" value="0"><span class="thr">показать все</span></div></div>
      <div class="panel"><div class="panel-h"><h3>Где организм это почувствует</h3><span class="sub">предсказанный сдвиг экспрессии ${SITE.genes[g.id].targets[0]} по тканям и клеткам, топ-14 по модулю</span></div><div class="ts"></div>
        <p class="panel-note">Шкала — предсказанное изменение уровня РНК гена в логарифмической шкале; значения около нуля означают «ген читается как обычно». Ткани и клеточные линии — из наборов ENCODE и GTEx.</p></div>
      <div class="panel"><div class="panel-h"><h3>Что именно ломается</h3><span class="sub">из чего сложена оценка AVI знаменитого варианта · AVI ${SITE.genes[g.id].famous.avi.toFixed(2)}, квантиль ${SITE.genes[g.id].famous.q.toFixed(3)}</span></div><div class="at"></div></div>
      <div class="panel model"><div class="panel-h"><h3>Что видит модель</h3><span class="sub">итог главы по данным Атласа</span></div><p class="model-text">${MODEL[g.id]}</p></div>
'''
s = s.replace(old_panels, new_panels)
assert 'Что видит модель' in s
s = s.replace("const TISSUES=", "const MODEL=" + json.dumps(MODEL, ensure_ascii=False) + ";\nconst TISSUES=", 1)
s = s.replace("  const circles=buildMatrix(g,s.querySelector('.mx'));buildTissues(g,s.querySelector('.ts'));buildAttr(g,s.querySelector('.at'));",
              "  buildStrip(g,s.querySelector('.strip-host'));const circles=buildZoom(g,s.querySelector('.mx'));buildTissues(g,s.querySelector('.ts'));buildAttr(g,s.querySelector('.at'));")
s = s.replace("rng_.addEventListener('input',()=>{const t=rng_.value/100;thr.textContent=t?`только AVI ≥ ${t.toFixed(2)} · ${circles.filter(c=>c.__d.v>=t).length} замен`:'показать все';circles.forEach(c=>c.style.opacity=c.__d.v>=t||c.__d.famous?1:.06)});",
              "rng_.addEventListener('input',()=>{const t=rng_.value/100;thr.textContent=t?`квантиль ≥ ${t.toFixed(2)} · ${circles.filter(c=>c.__d.q>=t).length} из ${circles.length}`:'показать все';circles.forEach(c=>c.style.opacity=c.__d.q>=t||c.__d.fam?1:.05)});")

# 4. fact row
s = s.replace('<div class="fact"><div class="k">Разрушительных замен в гене</div><div class="v">${g.danger} %</div></div>',
              '<div class="fact"><div class="k">AVI варианта · квантиль</div><div class="v mono">${SITE.genes[g.id].famous.avi.toFixed(2)} · ${SITE.genes[g.id].famous.q.toFixed(3)}</div></div>')

# 5. finale
old_fin = s[s.index('<section class="finale">'):s.index('<section class="method">')]
new_fin = '''<section class="finale">
  <h2>Крик или шёпот</h2>
  <p class="lead">Десять знаменитых вариантов на одной шкале AVI. Половина из них — громкие поломки белка, которые модель видит без труда. Другая половина — тихие регуляторные сдвиги, а «ген кофе» модель и вовсе считает одной из самых безобидных замен в геноме.</p>
  <div id="shout"></div>
  <h2 style="margin-top:80px">Насколько хрупок каждый участок</h2>
  <p class="lead">Доля замен в окне ±5 000 букв, попадающих в верхний 1 % по всему геному. У ACTN3 окно почти целиком лежит на экзонах — отсюда рекорд; у ABCC11 и ALDH2 вокруг варианта в основном интроны.</p>
  <div class="compare" id="compare"></div>
</section>

'''
s = s.replace(old_fin, new_fin)
old_fin_js = s[s.index('/* finale */'):s.index('</script>\n</body>')]
new_fin_js = r'''/* finale: shout-or-whisper */
(function(){
  const host=document.getElementById('shout');const W=1000,H=308,x0=60,x1=W-40;const lo=-0.5,hi=2.3;const X=v=>x0+(v-lo)/(hi-lo)*(x1-x0);
  const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'shout'},host);
  const items=GENES.map(g=>({g,avi:SITE.genes[g.id].famous.avi,q:SITE.genes[g.id].famous.q,prot:(SITE.genes[g.id].famous.groups['Белок (аминокислота)']+SITE.genes[g.id].famous.groups['Белок (обрыв/старт/стоп)'])>0.4})).sort((a,b)=>a.avi-b.avi);
  const yA=232;
  /* bands under axis */
  [[0.2,0.7,'регуляция и консервативность','var(--accent)'],[0.9,2.3,'поломка белка','var(--ink)']].forEach(([a,b,t,c])=>{el('rect',{x:X(a),y:yA-192,width:X(b)-X(a),height:202,fill:c,opacity:c==='var(--ink)'?.045:.08},svg);el('text',{x:X(a)+8,y:yA+22,class:'regionlab'},svg).textContent=t});
  el('line',{x1:x0,x2:x1,y1:yA,y2:yA,stroke:'var(--ink)','stroke-width':1,opacity:.6},svg);
  [-0.5,0,0.5,1,1.5,2].forEach(v=>{el('line',{x1:X(v),x2:X(v),y1:yA-4,y2:yA+4,stroke:'var(--ink)',opacity:.6},svg);el('text',{x:X(v),y:yA+40,class:'axlab','text-anchor':'middle'},svg).textContent=v});
  el('text',{x:x0,y:yA+58,class:'axlab'},svg).textContent='← безобиднее';el('text',{x:x1,y:yA+58,class:'axlab','text-anchor':'end'},svg).textContent='разрушительнее → AVI';
  const rowsEnd=[];const LW=168;
  items.forEach((it,i)=>{const x=X(it.avi);let row=0;while(rowsEnd[row]!==undefined&&x-rowsEnd[row]<LW)row++;rowsEnd[row]=x;const ly=yA-26-row*32;
    el('line',{x1:x,x2:x,y1:yA-8,y2:ly+6,stroke:'var(--accent)',opacity:.55},svg);
    el('circle',{cx:x,cy:yA,r:7,fill:it.prot?'var(--ink)':'var(--accent)',stroke:'var(--paper)','stroke-width':2},svg);
    const anchor=x<x0+60?'start':x>x1-60?'end':'middle';
    const t=el('text',{x:x,y:ly,class:'glab','text-anchor':anchor},svg);t.innerHTML=`${it.g.id} <tspan class="t">${it.g.trait.toLowerCase()}</tspan>`;
    el('text',{x:x,y:ly+14,'text-anchor':anchor,style:'font:10px var(--mono);fill:var(--ink-3)'},svg).textContent=`AVI ${it.avi.toFixed(2)} · q ${it.q.toFixed(3)}`});
  el('text',{x:x0,y:H-6,class:'axlab'},svg).textContent='● чёрный — в оценке доминирует белок (AlphaMissense / обрыв)   ● золотой — регуляция и консервативность   ·   q — квантиль среди всех 9 млрд замен';
})();
const cmp=document.getElementById('compare');
[...GENES].sort((a,b)=>SITE.genes[b.id].share99-SITE.genes[a.id].share99).forEach(g=>{const D=SITE.genes[g.id];const d=document.createElement('div');d.className='card';d.innerHTML=`<h4>${g.id}</h4><div class="t">${g.title}</div><div class="big">${(D.share99*100).toFixed(1)}<span style="font-size:20px"> %</span><small>из ${D.n.toLocaleString('ru-RU')} замен — в топ-1 % генома</small></div>`;
  const svg=el('svg',{viewBox:'0 0 100 40'},d);const n=Math.round(D.share99*200);
  for(let i=0;i<200;i++){el('circle',{cx:2.5+(i%40)*2.5,cy:2.5+Math.floor(i/40)*7,r:i<n?1.6:1,fill:i<n?'var(--accent)':'var(--ink)','fill-opacity':i<n?1:.15},svg)}
  cmp.appendChild(d)});
'''
s = s.replace(old_fin_js, new_fin_js)

# 6. css additions + mock tag + method text
s = s.replace('  /* NAV */', '''  .strip-wrap{position:relative;margin:6px 0 4px}
  .strip{display:block;width:100%}
  .structs{margin-top:2px}
  .panel-note{font:13.5px/1.5 var(--serif);color:var(--ink-2);margin:10px 0 0;max-width:640px}
  .shout .glab{font-size:12px}
  .panel.model{border-top:2px solid var(--accent)}
  .model-text{font:15.5px/1.62 var(--serif);color:var(--ink);margin:8px 0 0;max-width:680px}
  /* NAV */''', 1)
s = s.replace('<title>Гены, о которых вы слышали — макет</title>', '<title>Гены, о которых вы слышали</title>')
s = s.replace('<div class="mock-tag">макет · данные иллюстративные</div>', '<div class="mock-tag">данные: AlphaGenome Atlas · черновик</div>')
s = re.sub(r'<h5>Что здесь макет</h5>.*?</div>\n</section>', '''<h5>Как мы это считали</h5>
    <p>Для каждого из десяти вариантов через AlphaGenome Atlas API запрошены все однобуквенные замены в окне ±5 000 букв — по 30 000 на ген, 300 000 всего — с оценкой AVI, её квантилем относительно всех ~9 млрд замен генома и разложением на 18 признаков. Для знаменитого варианта дополнительно — предсказанный сдвиг экспрессии целевого гена по 371 треку тканей и клеточных линий. Структуры генов — Ensembl (канонические транскрипты, GRCh38).</p>
    <p>Модель предсказывает <em>молекулярный</em> эффект, а не «вы будете быстро бегать». Квантиль 0,99 означает «сильнее 99 % всех возможных замен в геноме», а не «вредно для здоровья». Скрипты и данные: pull_atlas.py, prep_site.py.</p>
  </div>
</section>''', s, count=1, flags=re.S)
s = s.replace('данные иллюстративные', 'черновик')
open('genes.html', 'w', encoding='utf-8').write(s)
print('ok', len(s) // 1024, 'KB')
