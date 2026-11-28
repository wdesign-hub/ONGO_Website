(function(){
  var wrap=document.getElementById('mapwrap'); if(!wrap) return;
  var card=document.getElementById('areacard'), title=document.getElementById('areacard-title'), desc=document.getElementById('areacard-desc');
  var D={"west-bay": "Office towers, hotels and residential car parks along the Corniche.", "the-pearl": "Residential towers and marina car parks across the islands.", "lusail": "Marina District, Lusail Boulevard and the new residential quarters.", "msheireb": "Downtown Doha, from Msheireb Downtown to Souq Waqif.", "al-sadd": "Apartments, offices and malls around Al Sadd Street.", "al-waab": "Villas and compounds near Aspire Zone."}, open=null;
  function place(btn){
    if(window.matchMedia('(max-width:600px)').matches){card.style.left='';card.style.top='';return;}
    var w=wrap.clientWidth,h=wrap.clientHeight,x=btn.offsetLeft,y=btn.offsetTop,cw=card.offsetWidth,ch=card.offsetHeight;
    var left=x+24; if(left+cw>w-12) left=x-cw-24; left=Math.max(12,Math.min(left,w-cw-12));
    var top=y-ch/2; top=Math.max(12,Math.min(top,h-ch-12));
    card.style.left=left+'px'; card.style.top=top+'px';
  }
  function close(focus){ if(!open) return; open.setAttribute('aria-expanded','false'); card.hidden=true; if(focus) open.focus(); open=null; }
  function show(btn){
    if(open===btn){close(true);return;}
    if(open) open.setAttribute('aria-expanded','false');
    var k=btn.getAttribute('data-area'); title.textContent=btn.querySelector('.tag').textContent; desc.textContent=D[k];
    card.hidden=false; btn.setAttribute('aria-expanded','true'); open=btn; place(btn);
    title.setAttribute('tabindex','-1'); title.focus({preventScroll:true});
  }
  wrap.querySelectorAll('.pin').forEach(function(b){ b.addEventListener('click',function(e){e.stopPropagation();show(b);}); });
  document.getElementById('areacard-close').addEventListener('click',function(){close(true);});
  card.addEventListener('click',function(e){e.stopPropagation();});
  document.addEventListener('click',function(){close(false);});
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') close(true); });
  window.addEventListener('resize',function(){ if(open) place(open); });
})();
