// Injected into the page under test. After __DELAY__ ms it measures every visible text run (HTML and SVG):
// WCAG contrast against what is actually painted behind it, SVG text/text and text/dot overlaps, SVG text running
// outside its <svg>, rendered text under 9 px, and anything wider than the viewport. Results go to a hidden pre#__out
// element and, inside an iframe, to the parent page by postMessage.
// Jump every finite CSS/Web animation (bars growing in, fades) to its end before measuring: mid-animation, labels sit on
// the wrong background, and headless Chrome sometimes never starts an animation clock at all, so waiting can hang.
setTimeout(()=>{(document.getAnimations?document.getAnimations():[]).forEach(a=>{try{if(isFinite(a.effect.getComputedTiming().endTime))a.finish();}catch(e){}});
  setTimeout(measure,30);},__DELAY__);
function measure(){
  // A figure inside a closed <details> is laid out but never painted, so its labels measure against a box that
  // is not the one a reader sees and report collisions and clipping that do not exist. A fold is content, and
  // its figures have to be legible too, so every fold opens before anything is measured.
  document.querySelectorAll('details').forEach(d=>d.open=true);
  const out={contrast:[],overlap:[],tiny:[],wide:[],hscroll:document.documentElement.scrollWidth>window.innerWidth+1,width:window.innerWidth,texts:0};
  // Every computed colour becomes {r,g,b,a} in 0..255 sRGB. rgb()/rgba() is read directly. Any other form - oklch()
  // and oklab() (what Chrome serialises for color-mix(in oklch) and oklch tokens), color(srgb ...) from color-mix(in
  // srgb) (its channels can run past 0..1 when a mixed colour is outside sRGB), lab(), lch(), color(display-p3 ...) -
  // is painted opaque on a 1x1 canvas and read back, so the browser does the conversion and gamut clipping it does
  // when it draws. Alpha comes from the string. (A peptide explainer, 2026-11-20: every peptide name was oklch, listed
  // under `unknown` and never tested, while the run said PASS; a DJ-set tool, 2026-11-03: color(srgb) threw on the
  // first text.)
  const cx=Object.assign(document.createElement('canvas'),{width:1,height:1}).getContext('2d',{willReadFrequently:true}),memo=new Map();
  const parse=c=>{c=(c||'').trim();if(!c||c==='none'||/^url\(/.test(c))return null;if(memo.has(c))return memo.get(c);let v=null;
    const m=c.match(/^rgba?\(([^)]+)\)$/);
    if(m){const p=m[1].split(/[\s,\/]+/).filter(Boolean).map(s=>/%$/.test(s)?parseFloat(s)/100:Number(s));v={r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1};}
    else if(/^(color|oklch|oklab|lab|lch|hsla?|hwb)\(/.test(c)){
      const am=c.match(/\/\s*([\d.eE+-]+%?|none)\s*\)$/),a=!am||am[1]==='none'?1:/%$/.test(am[1])?parseFloat(am[1])/100:Number(am[1]);
      const opaque=am?c.slice(0,am.index).trimEnd()+')':c;
      cx.clearRect(0,0,1,1);cx.fillStyle='#010203';cx.fillStyle=opaque;
      if(cx.fillStyle!=='#010203'||/^rgba?\(1, 2, 3/.test(opaque)){cx.fillRect(0,0,1,1);const d=cx.getImageData(0,0,1,1).data;v={r:d[0],g:d[1],b:d[2],a};}}
    memo.set(c,v);return v;};
  const over=(f,b)=>f.a>=.999?f:{r:f.r*f.a+b.r*(1-f.a),g:f.g*f.a+b.g*(1-f.a),b:f.b*f.a+b.b*(1-f.a),a:1};   // source-over, as the browser composites
  const lum=({r,g,b})=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return .2126*f(r)+.7152*f(g)+.0722*f(b);};
  const ratio=(a,b)=>{const x=lum(a),y=lum(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
  const unmeasured=(el,c)=>{out.unknownCount=(out.unknownCount||0)+1;const s=name(el)+' '+c;out.unknown=out.unknown||[];if(!out.unknown.includes(s)&&out.unknown.length<8)out.unknown.push(s);};
  // painted background: walk up through translucent layers to the first opaque one (or the first solid stop of a
  // gradient: highlighter marks are gradients), then composite the translucent layers over it
  const COLOR=/\b(?:rgba?|oklch|oklab|lab|lch|color|hsla?|hwb)\([^)]*\)/g,WHITE={r:255,g:255,b:255,a:1};
  const bgOf=el=>{const layers=[];let base=null;
    for(let e=el;e&&e.nodeType===1&&!base;e=e.parentElement){if(e instanceof SVGElement&&!(e instanceof SVGSVGElement))continue;const cs=getComputedStyle(e),c=parse(cs.backgroundColor);
      if(c&&c.a>.001){if(c.a>=.999)base=c;else layers.push(c);}
      if(!base&&/gradient/.test(cs.backgroundImage)){const g=(cs.backgroundImage.match(COLOR)||[]).map(parse).find(x=>x&&x.a>.5);if(g)base={...g,a:1};}}
    return layers.reduceRight((b,f)=>over(f,b),base||WHITE);};
  const big=cs=>{const s=parseFloat(cs.fontSize),w=parseInt(cs.fontWeight)||400;return s>=24||(s>=18.66&&w>=700);};
  const name=el=>(el.id?'#'+el.id:el.tagName.toLowerCase()+(typeof el.className==='string'&&el.className?'.'+el.className.split(' ')[0]:''));
  // ?probe=<css selector> lists the measured colours and ratio of every matching text run, passing or not, so one
  // element's contrast is read off the run instead of converted by hand (and the fixture test checks the numbers)
  const probeSel=new URLSearchParams(location.search).get('probe'),hex=c=>'#'+[c.r,c.g,c.b].map(v=>Math.round(v).toString(16).padStart(2,'0')).join('');
  const probe=(el,txt,fg,bg,k)=>{if(!probeSel)return;try{if(!el.closest(probeSel))return;}catch(e){return;}(out.probe=out.probe||[]).push({el:name(el),text:txt.trim().slice(0,40),fg:hex(fg),bg:hex(bg),ratio:+k.toFixed(3)});};
  const tiny=(el,px,txt)=>{if(px<9&&out.tiny.length<12)out.tiny.push({el:name(el),text:txt.slice(0,30),px:+px.toFixed(1)});};
  // HTML text: background = nearest opaque ancestor background
  const tw=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
  while((n=tw.nextNode())){const el=n.parentElement;if(!n.textContent.trim()||!el||el.closest('svg')||el.closest('script,style,title,#__out'))continue;
    const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;const cs=getComputedStyle(el);if(cs.visibility==='hidden'||parseFloat(cs.opacity)===0)continue;
    const fg=parse(cs.color);if(!fg){unmeasured(el,cs.color);continue;}   // a colour the parser does not read is listed and counted, never a crash
    out.texts++;const bg=bgOf(el),k=ratio(over(fg,bg),bg),need=big(cs)?3:4.5;
    if(k<need)out.contrast.push({el:name(el),text:n.textContent.trim().slice(0,40),ratio:+k.toFixed(2),need});
    probe(el,n.textContent,over(fg,bg),bg,k);
    if(el.offsetWidth)tiny(el,parseFloat(cs.fontSize)*r.width/el.offsetWidth,n.textContent.trim());}
  // SVG text: background = topmost painted shape under the text's centre
  document.querySelectorAll('svg').forEach(svg=>{
    const texts=[...svg.querySelectorAll('text')].filter(t=>t.textContent.trim()),dots=[...svg.querySelectorAll('circle')].filter(d=>!d.closest('[data-bg]')&&getComputedStyle(d).fill!=='none'),sr=svg.getBoundingClientRect();
    texts.forEach(t=>{const r=t.getBoundingClientRect();if(!r.width)return;out.texts++;
      if(r.left<sr.left-.5||r.right>sr.right+.5||r.top<sr.top-.5||r.bottom>sr.bottom+.5)out.overlap.push({svg:svg.id,a:t.textContent,b:'outside svg'});
      let bg=null;for(const e of document.elementsFromPoint(r.left+r.width/2,r.top+r.height/2)){if(e===t||e.tagName==='text'||e.tagName==='tspan')continue;
        if(e instanceof SVGElement&&!(e instanceof SVGSVGElement)){if(/^(line|polyline)$/.test(e.tagName)){continue;}const eb=e.getBoundingClientRect();if(eb.width<3||eb.height<3)continue;   // lines are not backgrounds
          const cs=getComputedStyle(e),f=parse(cs.fill),fa=f?f.a*parseFloat(cs.fillOpacity)*parseFloat(cs.opacity):0;if(fa>=.5){bg=over({...f,a:fa},bgOf(svg));break;}continue;}
        bg=bgOf(e);break;}
      bg=bg||bgOf(svg);const tcs=getComputedStyle(t),tf=parse(tcs.fill);if(!tf){out.texts--;unmeasured(t,tcs.fill);return;}   // a gradient or pattern fill is listed, never a crash
      const fg=over({...tf,a:tf.a*parseFloat(tcs.fillOpacity)},bg),k=ratio(fg,bg);if(k<4.5)out.contrast.push({el:(svg.id||'svg')+' text',text:t.textContent.slice(0,40),ratio:+k.toFixed(2),need:4.5});
      probe(t,t.textContent,fg,bg,k);
      try{const bb=t.getBBox();if(bb.height)tiny(t,parseFloat(getComputedStyle(t).fontSize)*r.height/bb.height,t.textContent);}catch(e){}});
    // A rotated label's screen box is an axis-aligned hull far bigger than its glyphs, so parallel 45-degree labels
    // on an axis "overlap" with clear space between them. Rotated text is judged on its own oriented box instead
    // (its getBBox corners through its screen matrix), tested for overlap by separating axes.
    const rot=t=>{const m=t.getScreenCTM();return !!m&&Math.abs(m.b)>1e-3;};
    const quad=t=>{const bb=t.getBBox(),m=t.getScreenCTM();return [[bb.x,bb.y],[bb.x+bb.width,bb.y],[bb.x+bb.width,bb.y+bb.height],[bb.x,bb.y+bb.height]].map(([x,y])=>[m.a*x+m.c*y+m.e,m.b*x+m.d*y+m.f]);};
    const hit=(P,Q)=>{for(const S of [P,Q])for(let k=0;k<4;k++){const [x1,y1]=S[k],[x2,y2]=S[(k+1)%4],nx=y2-y1,ny=x1-x2,L=Math.hypot(nx,ny)||1;
      const pr=R=>R.map(([x,y])=>(nx*x+ny*y)/L),p=pr(P),q=pr(Q);if(Math.max(...p)<=Math.min(...q)+.5||Math.max(...q)<=Math.min(...p)+.5)return false;}return true;};
    for(let i=0;i<texts.length;i++){const a=texts[i].getBoundingClientRect();
      for(let j=i+1;j<texts.length;j++){if(texts[i].contains(texts[j])||texts[j].contains(texts[i]))continue;const b=texts[j].getBoundingClientRect();
        if(rot(texts[i])||rot(texts[j])){try{if(hit(quad(texts[i]),quad(texts[j])))out.overlap.push({svg:svg.id,a:texts[i].textContent.slice(0,30),b:texts[j].textContent.slice(0,30)});}catch(e){}continue;}
        // An svg text box runs ascent to descent, so two STACKED lines on a tight line step overlap by a pixel
        // or two with clear white between the glyphs. That is leading, not a collision, and counting it fails a
        // page for having ordinary line spacing. So a stacked pair counts only when it bites deeper than a
        // quarter of the smaller box; labels sharing a line are judged on their horizontal overlap as before.
        const oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top),mh=Math.min(a.height,b.height);
        const sameLine=Math.abs((a.top+a.bottom)/2-(b.top+b.bottom)/2)<mh*.5;
        if(a.left<b.right-.5&&b.left<a.right-.5&&oy>.5&&(sameLine||oy>mh*.25))out.overlap.push({svg:svg.id,a:texts[i].textContent.slice(0,30),b:texts[j].textContent.slice(0,30)});}
      dots.forEach(d=>{if(d.parentNode===texts[i].parentNode&&d.parentNode.hasAttribute('data-cluster'))return;const b=d.getBoundingClientRect(),s=b.width*.15;
        const rr=b.width/2;if(Math.hypot((a.left+a.right)/2-(b.left+b.right)/2,(a.top+a.bottom)/2-(b.top+b.bottom)/2)<rr*.5&&a.width/2<=rr*1.1)return;   // a label centred in its own badge
        if(a.left<b.right-s&&b.left+s<a.right&&a.top<b.bottom-s&&b.top+s<a.bottom)out.overlap.push({svg:svg.id,a:texts[i].textContent.slice(0,30),b:'circle '+(d.getAttribute('aria-label')||'').slice(0,40)});});}
  });
  // shapes cut off at their svg's edge (the svg clips unless overflow is visible)
  out.clipped=[];document.querySelectorAll('svg').forEach(svg=>{if(svg.closest('defs,symbol,marker,clipPath,mask')||getComputedStyle(svg).overflow==='visible')return;
    const sr=svg.getBoundingClientRect();if(!sr.width)return;
    svg.querySelectorAll('rect,circle,ellipse,path,polygon,polyline,line,use').forEach(sh=>{if(sh.closest('defs,symbol,marker,clipPath,mask,[clip-path]'))return;   // background shapes clip too
      const r=sh.getBoundingClientRect();if(!r.width&&!r.height)return;
      if(r.left<sr.left-1.5||r.right>sr.right+1.5||r.top<sr.top-1.5||r.bottom>sr.bottom+1.5)
        out.clipped.push({svg:svg.id||'svg',el:sh.tagName,past:{left:Math.round(sr.left-r.left),right:Math.round(r.right-sr.right),top:Math.round(sr.top-r.top),bottom:Math.round(r.bottom-sr.bottom)}});});});
  // HTML text drawn over an svg box or ellipse (a legend sitting on a figure's shape)
  // rendered() skips content Chrome lays out but never paints, such as the inside of a closed <details>
  const rendered=e=>!e.checkVisibility||e.checkVisibility({contentVisibilityAuto:true,visibilityProperty:true});
  const shapes=[...document.querySelectorAll('svg rect,svg ellipse')].filter(sh=>!sh.closest('defs,symbol,marker,clipPath,mask')&&getComputedStyle(sh).visibility!=='hidden'&&rendered(sh))
    .map(sh=>({sh,r:sh.getBoundingClientRect(),s:sh.ownerSVGElement&&sh.ownerSVGElement.getBoundingClientRect()}))
    .filter(o=>o.r.width>2&&o.r.height>2&&!(o.s&&o.r.width*o.r.height>.6*o.s.width*o.s.height));   // skip panel-sized backgrounds
  const tw2=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let m2;
  while((m2=tw2.nextNode())){const el=m2.parentElement;if(!m2.textContent.trim()||!el||el.closest('svg,script,style,title,#__out')||!rendered(el))continue;
    const rg=document.createRange();rg.selectNodeContents(m2);
    for(const tr of rg.getClientRects())for(const o of shapes){const r=o.r;
      if(tr.left<r.right-1&&r.left<tr.right-1&&tr.top<r.bottom-1&&r.top<tr.bottom-1){out.overlap.push({a:m2.textContent.trim().slice(0,30),b:'svg '+o.sh.tagName+' in '+(o.sh.ownerSVGElement&&o.sh.ownerSVGElement.id||'svg')});break;}}}
  out.wide=[...document.querySelectorAll('body *')].filter(e=>!e.closest('svg')&&e.id!=='__out'&&e.getBoundingClientRect().right>window.innerWidth+1)
    .map(e=>name(e)+' right='+Math.round(e.getBoundingClientRect().right)).slice(-8);
  if(window.parent!==window)parent.postMessage(out,'*');
  const pre=document.createElement('pre');pre.id='__out';pre.style.display='none';pre.textContent=JSON.stringify(out);document.body.appendChild(pre);
}
