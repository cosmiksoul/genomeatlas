import re, json, html, os
from story import INTRO, STORY, SOURCES, GLOSSARY, MODEL

src = open('template_genes.html', encoding='utf-8').read()

# ---------- glossary wrapping ----------
def wrap_terms(paragraphs, seen):
    """paragraphs: list of str. seen: set of glossary titles already wrapped in this scope."""
    out = []
    for p in paragraphs:
        tokens = {}
        def sub(m, title, d):
            if title in seen:
                return m.group(0)
            seen.add(title)
            key = f"\x00{len(tokens)}\x00"
            tokens[key] = f'<span class="term" tabindex="0" data-t="{html.escape(title)}" data-d="{html.escape(d)}">{m.group(0)}</span>'
            return key
        text = p
        for rx, title, d in GLOSSARY:
            text = re.sub(rx, lambda m: sub(m, title, d), text, count=1, flags=re.I)
        for k, v in tokens.items():
            text = text.replace(k, v)
        out.append(text)
    return out

intro_seen = set()
intro_blocks = [(h, wrap_terms([t], intro_seen)[0]) for h, t in INTRO]
story_wrapped = {}
for g, paras in STORY.items():
    seen = set()
    story_wrapped[g] = wrap_terms(paras, seen)

# ---------- intro section ----------
src_list = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for t, u in SOURCES['INTRO'])
intro_html = '<section class="intro" id="intro">\n <div class="intro-text">\n' + ''.join(
    f'  <div class="intro-block"><h5>{h}</h5><p>{t}</p></div>\n' for h, t in intro_blocks
) + f'  <details class="srcs"><summary>Источники к введению</summary><ol>{src_list}</ol></details>\n </div>\n' + '''
 <div class="intro-lab">
  <div class="lab-h"><span class="lab-eyebrow">Попробуйте сами</span><h4>Сделайте опечатку в гене</h4>
   <p>Игрушечный ген из 66 букв. Кликните на любую букву — она сменится на следующую (A → C → G → T). Справа — что «увидит» модель: громкость гена в трёх типах клеток и механизм поломки.</p></div>
  <div id="mutator"></div>
  <div class="lab-foot">Это схема, а не AlphaGenome: правила упрощены до четырёх — промотор, мотив белка-регулятора, граница экзона, код аминокислот. Настоящая модель смотрит на миллион букв контекста.</div>
 </div>
</section>
'''
src = re.sub(r'<section class="intro"[^>]*>.*?</section>\n', intro_html, src, count=1, flags=re.S)

# ---------- css ----------
css = '''
  /* INTRO v2 */
  .intro{padding:80px clamp(20px,6vw,90px) 70px;border-top:1px solid var(--line);display:grid;grid-template-columns:minmax(0,600px) minmax(0,1fr);gap:40px clamp(40px,6vw,110px);align-items:start}
  .intro-text{display:grid;gap:28px}
  .intro-block{display:grid;grid-template-columns:140px 1fr;gap:20px;align-items:start}
  .intro-block h5{font:12px/1.6 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:4px 0 0}
  .intro-block p{font:17px/1.6 var(--serif);color:var(--ink);margin:0}
  .intro-block:first-child p{font-size:21px;line-height:1.45}
  .intro-lab{position:sticky;top:20px;border:1px solid var(--line);background:rgba(255,255,255,.35);padding:22px 24px 18px;border-radius:3px}
  .lab-eyebrow{font:11px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
  .lab-h h4{font:400 24px var(--serif);margin:4px 0 8px}
  .lab-h p{font:13.5px/1.5 var(--sans);color:var(--ink-2);margin:0 0 16px}
  .lab-foot{font:11.5px/1.5 var(--mono);color:var(--ink-3);margin-top:14px;border-top:1px dashed var(--line);padding-top:10px}
  .srcs{font:13px var(--sans);color:var(--ink-2);margin-top:6px}
  .srcs summary{cursor:pointer;font:11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}
  .srcs summary:hover{color:var(--ink)}
  .srcs ol{margin:8px 0 0;padding-left:18px;display:grid;gap:4px}
  .srcs a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid var(--line)}
  .srcs a:hover{color:var(--ink);border-color:var(--ink)}
  .chapter .srcs{margin-top:18px;margin-bottom:24px}
  @media (max-width:1000px){.intro{grid-template-columns:1fr}.intro-lab{position:static}}
  @media (max-width:700px){.intro-block{grid-template-columns:1fr;gap:6px}}

  /* glossary terms */
  .term{border-bottom:1px dotted var(--accent);cursor:help;text-decoration:none}
  .term:hover,.term:focus{background:var(--accent-soft);outline:none}
  .tip.def{white-space:normal;max-width:300px;font-family:var(--sans);font-size:13px;line-height:1.45;transform:translate(-50%,-115%);text-align:left}
  .tip.def b{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px}

  /* mutator */
  .mut-strip{display:flex;flex-wrap:wrap;gap:3px 0;margin:6px 0 4px;user-select:none}
  .mut-b{width:22px;height:30px;display:flex;align-items:center;justify-content:center;font:600 13px var(--mono);cursor:pointer;border-bottom:3px solid transparent;border-radius:2px;transition:background .12s;position:relative}
  .mut-b:hover{background:var(--paper-2)}
  .mut-b.changed{background:var(--accent);color:var(--paper)}
  .mut-b.changed::after{content:attr(data-ref);position:absolute;top:-11px;font:9px var(--mono);color:var(--accent);text-decoration:line-through}
  .mut-b.r-enh{border-color:#8a7a4a}.mut-b.r-prom{border-color:#3d3a30}.mut-b.r-exon{border-color:var(--ink)}.mut-b.r-splice{border-color:var(--accent)}.mut-b.r-intron{border-color:var(--line)}
  .mut-legend{display:flex;flex-wrap:wrap;gap:6px 14px;font:10.5px var(--mono);color:var(--ink-2);letter-spacing:.03em;margin:0 0 14px}
  .mut-legend i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:5px}
  .mut-out{display:grid;grid-template-columns:1fr 1fr;gap:16px 24px;align-items:start}
  .mut-bars .row{display:grid;grid-template-columns:110px 1fr 44px;gap:10px;align-items:center;font:12px var(--sans);color:var(--ink-2);margin-bottom:8px}
  .mut-bars .bar{height:10px;background:var(--line);border-radius:2px;overflow:hidden}
  .mut-bars .bar i{display:block;height:100%;background:var(--ink);transition:width .35s cubic-bezier(.2,.8,.2,1)}
  .mut-bars .v{font:11px var(--mono);color:var(--ink-3);text-align:right}
  .mut-prot{font:13px var(--mono);letter-spacing:.02em;line-height:1.9;color:var(--ink)}
  .mut-prot span{display:inline-block;padding:0 5px;border:1px solid var(--line);border-radius:2px;margin:0 2px 2px 0}
  .mut-prot span.diff{border-color:var(--accent);background:var(--accent-soft)}
  .mut-prot span.stop{border-color:var(--ink);background:var(--ink);color:var(--paper)}
  .mut-prot span.lost{opacity:.25;text-decoration:line-through}
  .mut-mech{font:14px/1.45 var(--serif);color:var(--ink);margin:0 0 8px;min-height:44px}
  .mut-mech b{color:var(--accent);font-weight:400;font-style:italic}
  .mut-avi{font:11px var(--mono);color:var(--ink-3);letter-spacing:.06em;text-transform:uppercase}
  .mut-avi b{font:400 22px var(--serif);color:var(--ink);letter-spacing:0;text-transform:none;margin-right:6px}
  .mut-reset{font:11px var(--mono);letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--line);color:var(--ink-2);padding:6px 10px;border-radius:2px;cursor:pointer;margin-top:10px}
  .mut-reset:hover{border-color:var(--ink);color:var(--ink)}
  @media (max-width:600px){.mut-out{grid-template-columns:1fr}}
'''
src = src.replace('  /* NAV */', css + '\n  /* NAV */', 1) if '/* INTRO v2 */' not in src else src
src = src.replace('.chapter .story{align-self:start}', '.chapter .story{align-self:start}')

# ---------- story + sources json ----------
src = re.sub(r'const STORY=.*?;\nconst TISSUES=', 'const STORY=' + json.dumps(story_wrapped, ensure_ascii=False) + ';\nconst SOURCES=' + json.dumps({k: v for k, v in SOURCES.items() if k != 'INTRO'}, ensure_ascii=False) + ';\nconst TISSUES=', src, count=1, flags=re.S)

# per-chapter sources after body paragraphs (idempotent)
if 'Источники главы' not in src:
    src = src.replace('${(STORY[g.id]||[]).map(t=>`<p class="body">${t}</p>`).join("")}',
        '${(STORY[g.id]||[]).map(t=>`<p class="body">${t}</p>`).join("")}<details class="srcs"><summary>Источники главы</summary><ol>${(SOURCES[g.id]||[]).map(([t,u])=>`<li><a href="${u}" target="_blank" rel="noopener">${t}</a></li>`).join("")}</ol></details>')

# ---------- glossary tooltip + mutator JS ----------
js = r'''
/* ---------- glossary tooltips ---------- */
(function(){
  let pinned=null;
  function show(t,e){tip.className='tip def';tip.innerHTML=`<b>${t.dataset.t}</b>${t.dataset.d}`;const r=t.getBoundingClientRect();tip.style.left=Math.min(Math.max(160,r.left+r.width/2),innerWidth-160)+'px';tip.style.top=r.top+'px';tip.style.opacity=1}
  function hide(){if(pinned)return;tip.style.opacity=0;setTimeout(()=>{if(tip.style.opacity=='0')tip.className='tip'},150)}
  document.addEventListener('mouseover',e=>{const t=e.target.closest('.term');if(t)show(t,e)});
  document.addEventListener('mouseout',e=>{if(e.target.closest('.term'))hide()});
  document.addEventListener('focusin',e=>{const t=e.target.closest('.term');if(t)show(t)});
  document.addEventListener('focusout',e=>{if(e.target.closest('.term')){pinned=null;hide()}});
  document.addEventListener('click',e=>{const t=e.target.closest('.term');if(t){pinned=pinned===t?null:t;if(pinned)show(t);else hide()}else if(pinned){pinned=null;hide()}});
  window.addEventListener('scroll',()=>{if(pinned){pinned=null;hide()}},{passive:true});
})();

/* ---------- mutator (toy gene) ---------- */
(function(){
  const REG=[['enh','TGTTTAC','мотив белка-регулятора печени'],['intron','CAGAT',''],['prom','TATAAA','промотор (ТАТА-бокс)'],['intron','GC',''],
             ['exon','ATGGCTGAATGGAAACGT','экзон 1'],['splice','GT','граница экзона'],['intron','AAGCTCTTTCAC',''],['splice','AG','граница экзона'],['exon','GGCTACTTCTAA','экзон 2']];
  const CODON={TTT:'Phe',TTC:'Phe',TTA:'Leu',TTG:'Leu',CTT:'Leu',CTC:'Leu',CTA:'Leu',CTG:'Leu',ATT:'Ile',ATC:'Ile',ATA:'Ile',ATG:'Met',GTT:'Val',GTC:'Val',GTA:'Val',GTG:'Val',TCT:'Ser',TCC:'Ser',TCA:'Ser',TCG:'Ser',CCT:'Pro',CCC:'Pro',CCA:'Pro',CCG:'Pro',ACT:'Thr',ACC:'Thr',ACA:'Thr',ACG:'Thr',GCT:'Ala',GCC:'Ala',GCA:'Ala',GCG:'Ala',TAT:'Tyr',TAC:'Tyr',TAA:'STOP',TAG:'STOP',CAT:'His',CAC:'His',CAA:'Gln',CAG:'Gln',AAT:'Asn',AAC:'Asn',AAA:'Lys',AAG:'Lys',GAT:'Asp',GAC:'Asp',GAA:'Glu',GAG:'Glu',TGT:'Cys',TGC:'Cys',TGA:'STOP',TGG:'Trp',CGT:'Arg',CGC:'Arg',CGA:'Arg',CGG:'Arg',AGT:'Ser',AGC:'Ser',AGA:'Arg',AGG:'Arg',GGT:'Gly',GGC:'Gly',GGA:'Gly',GGG:'Gly'};
  const BASES='ACGT';
  const ref=[],region=[];REG.forEach(([r,seq])=>{for(const b of seq){ref.push(b);region.push(r)}});
  let cur=ref.slice();
  const host=document.getElementById('mutator');
  host.innerHTML=`<div class="mut-strip"></div>
   <div class="mut-legend"><span><i style="background:#8a7a4a"></i>мотив регулятора</span><span><i style="background:#3d3a30"></i>промотор</span><span><i style="background:var(--ink)"></i>экзон</span><span><i style="background:var(--accent)"></i>граница экзона</span><span><i style="background:var(--line)"></i>интрон</span></div>
   <div class="mut-out"><div class="mut-bars"></div><div><p class="mut-mech"></p><div class="mut-avi"><b>0.00</b>AVI игрушечный</div><div class="mut-prot"></div></div></div>
   <button class="mut-reset">↺ вернуть как было</button>`;
  const strip=host.querySelector('.mut-strip'),bars=host.querySelector('.mut-bars'),mech=host.querySelector('.mut-mech'),avi=host.querySelector('.mut-avi b'),prot=host.querySelector('.mut-prot');
  const CELLS=[['Печень',1],['Кишечник',.6],['Нейрон',.3]];
  bars.innerHTML=CELLS.map(([n])=>`<div class="row"><span>${n}</span><div class="bar"><i></i></div><span class="v"></span></div>`).join('');
  ref.forEach((b,i)=>{const d=document.createElement('div');d.className='mut-b r-'+region[i];d.textContent=b;d.dataset.ref=b;d.title=REG.find(r=>r[0]===region[i])[2]||'интрон';d.addEventListener('click',()=>{cur[i]=BASES[(BASES.indexOf(cur[i])+1)%4];d.textContent=cur[i];d.classList.toggle('changed',cur[i]!==ref[i]);update()});strip.appendChild(d)});
  host.querySelector('.mut-reset').addEventListener('click',()=>{cur=ref.slice();strip.querySelectorAll('.mut-b').forEach((d,i)=>{d.textContent=ref[i];d.classList.remove('changed')});update()});
  function translate(seq){const aa=[];for(let i=0;i+2<seq.length;i+=3){const c=CODON[seq.slice(i,i+3)]||'?';aa.push(c);if(c==='STOP')break}return aa}
  function exonSeq(s){return s.filter((_,i)=>region[i]==='exon').join('')}
  function update(){
    const mult={Печень:1,Кишечник:1,Нейрон:1};const notes=[];let score=0;
    const changed=cur.map((b,i)=>b!==ref[i]?i:-1).filter(i=>i>=0);
    const hit=r=>changed.some(i=>region[i]===r);
    if(hit('prom')){for(const k in mult)mult[k]*=.25;notes.push('<b>промотор</b>: полимеразе не за что зацепиться — ген глохнет во всех клетках');score+=.7}
    if(hit('enh')){mult['Печень']*=.2;notes.push('<b>мотив регулятора</b>: белок печени больше не садится — ген глохнет только в печени');score+=.5}
    if(hit('splice')){for(const k in mult)mult[k]*=.15;notes.push('<b>сплайсинг</b>: РНК нарезается не там, экзон теряется');score+=.8}
    const refAA=translate(exonSeq(ref)),curAA=translate(exonSeq(cur));
    let protHtml='';const stopIdx=curAA.indexOf('STOP');const truncated=stopIdx>=0&&stopIdx<refAA.length-1;
    refAA.forEach((a,i)=>{const c=curAA[i];if(a==='STOP')return;if(c===undefined||c==='STOP'&&i<refAA.length-1){protHtml+=`<span class="${c==='STOP'?'stop':'lost'}">${c==='STOP'?'STOP':a}</span>`}else protHtml+=`<span class="${c!==a?'diff':''}">${c}</span>`});
    prot.innerHTML=protHtml;
    if(truncated){notes.push('<b>нонсенс</b>: стоп-сигнал посреди инструкции — белок обрывается');score+=.85}
    else{const diffs=refAA.filter((a,i)=>a!=='STOP'&&curAA[i]!==a).length;if(diffs){notes.push(`<b>миссенс</b>: ${diffs===1?'другая аминокислота':diffs+' другие аминокислоты'} — вопрос к AlphaMissense, сломает ли это белок`);score+=.35*diffs}
      else if(hit('exon'))notes.push('<b>синонимичная замена</b>: буква другая, аминокислота та же')}
    if(hit('intron')&&!notes.length)notes.push('<b>нейтрально</b>: опечатка в интроне, модель почти ничего не видит');
    if(!changed.length)notes.push('Пока всё как в референсе. Кликните на букву.');
    if(hit('intron'))score+=.02*changed.filter(i=>region[i]==='intron').length;
    mech.innerHTML=notes.join('<br>');
    avi.textContent=Math.min(1,score).toFixed(2);
    bars.querySelectorAll('.row').forEach((row,k)=>{const [n,base]=CELLS[k];const v=base*mult[n];row.querySelector('i').style.width=(v*100)+'%';row.querySelector('.v').textContent=Math.round(v*100)+'%'});
  }
  update();
})();
'''
src = src.replace('/* ---------- assemble ---------- */', js + '\n/* ---------- assemble ---------- */', 1) if 'glossary tooltips' not in src else src

open('template_genes.html', 'w', encoding='utf-8').write(src)

# markdown draft w/ sources
md = "# Гены, о которых вы слышали — текст (v2, после фактчека)\n\n## Лид\n\n" + "".join(f"**{h}**\n\n{t}\n\n" for h, t in INTRO)
md += "Источники:\n\n" + "".join(f"- [{t}]({u})\n" for t, u in SOURCES['INTRO']) + "\n"
order = ['LCT','CYP1A2','ALDH2','ACTN3','HERC2','TAS2R38','MC1R','ABCC11','OR6A2','FUT2']
for i, g in enumerate(order, 1):
    md += f"## Глава {i} · {g}\n\n" + "".join(t + "\n\n" for t in STORY[g]) + "**Что видит модель.** " + MODEL[g] + "\n\n"
    md += "Источники:\n\n" + "".join(f"- [{t}]({u})\n" for t, u in SOURCES[g]) + "\n"
md += "## Глоссарий\n\n" + "".join(f"- **{t}** — {d}\n" for _, t, d in GLOSSARY)
os.makedirs('../drafts', exist_ok=True)
open('../drafts/genes-story.md', 'w', encoding='utf-8').write(md)
print('built')
