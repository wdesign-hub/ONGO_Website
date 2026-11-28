(function(){
  var root=document.documentElement, modeBtn=document.getElementById('modebtn'), meta=document.querySelector('meta[name="theme-color"]');
  var mq=window.matchMedia('(prefers-color-scheme: dark)');
  function isDark(){var m=root.getAttribute('data-mode');if(m) return m==='dark';var t=root.getAttribute('data-theme');if(t) return t==='dark';return mq.matches;}
  function sync(){var d=isDark();root.classList.toggle('is-dark',d);modeBtn.setAttribute('aria-pressed',String(d));modeBtn.setAttribute('aria-label',d?'Switch to light mode':'Switch to dark mode');if(meta) meta.setAttribute('content',d?'#0B110C':'#FBFBF8');}
  modeBtn.addEventListener('click',function(){var next=isDark()?'light':'dark';root.setAttribute('data-mode',next);try{localStorage.setItem('ongo-mode',next);}catch(e){}sync();});
  if(mq.addEventListener) mq.addEventListener('change',sync);
  new MutationObserver(sync).observe(root,{attributes:true,attributeFilter:['data-theme']});
  sync();
  var mb=document.getElementById('menubtn'), mn=document.getElementById('mnav');
  if(mb&&mn){
    mb.addEventListener('click',function(e){e.stopPropagation();var o=mb.getAttribute('aria-expanded')==='true';mb.setAttribute('aria-expanded',String(!o));mb.setAttribute('aria-label',o?'Open menu':'Close menu');mn.hidden=o;});
    mn.addEventListener('click',function(e){ if(e.target.tagName==='A'){mb.setAttribute('aria-expanded','false');mb.setAttribute('aria-label','Open menu');mn.hidden=true;} });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape'&&!mn.hidden){mn.hidden=true;mb.setAttribute('aria-expanded','false');mb.setAttribute('aria-label','Open menu');mb.focus();} });
  }
})();

(function(){
  if(!window.matchMedia||matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window)) return;
  var els=document.querySelectorAll('.s h2,.s .row,.tl,.promises div,.faq details,.voices>*,.final,.mapfig');
  if(!els.length) return;
  document.documentElement.classList.add('js-motion');
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('is-in');io.unobserve(e.target);}});},{rootMargin:'0px 0px -8% 0px',threshold:.08});
  els.forEach(function(el,i){el.classList.add('rv');el.style.setProperty('--d',(i%3)*70+'ms');io.observe(el);});
  setTimeout(function(){els.forEach(function(el){el.classList.add('is-in');});},4000);
})();
