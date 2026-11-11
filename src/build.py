"""Build nivasgallo.com pages from src/.

  python3 src/build.py            -> site/*.html  (artifact previews: body fragments, head tags inline)
  python3 src/build.py --deploy   -> dist/        (full HTML documents for static hosting)
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
DEPLOY = '--deploy' in sys.argv
OUT = os.path.join(ROOT, 'dist' if DEPLOY else 'site')

FONTS = 'https://fonts.googleapis.com/css2?family=Inter+Tight:wght@100..900&display=swap'

MOON = '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>'
SUN = '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg>'
LOCK_SR = '<span class="sr-only"> Password protected.</span>'

HEADER = f'''<a class="skip" href="#main">Skip to content</a>
<header class="g site-head"><div class="in top">
  <a class="logo display" href="index.html"><span class="sr-only">Nivas Gallo, home</span><span class="lg-full" aria-hidden="true">Nivas <span class="lt">Gallo</span></span><span class="lg-mono" aria-hidden="true">N<span class="lt">G</span></span></a>
  <nav aria-label="Main"><ul>
    <li><a href="index.html#work">Work</a></li>
    <li><a href="index.html#about">About</a></li>
    <li><a href="index.html#contact">Contact</a></li>
    <li><button type="button" class="mode" id="mode" aria-label="Switch to dark mode" title="Switch to dark mode">{MOON}{SUN}</button></li>
  </ul></nav>
</div></header>'''

CONTACT_FOOTER = '''<footer class="g contact-band" id="contact" aria-labelledby="contact-h"><div class="in">
  <h2 class="big" id="contact-h">Let's start<br>something.</h2>
  <div class="links">
    <a href="mailto:nivasgallo@gmail.com">nivasgallo@gmail.com</a>
    <span>London, UK</span>
  </div>
  <div class="social meta"><a href="https://www.linkedin.com/in/nivasgallo/" target="_blank" rel="noopener">LinkedIn<span class="sr-only"> (opens in a new tab)</span></a><span>CV <span class="tbc">PDF coming soon</span></span></div>
  <div class="foot"><span>© 2026 Nivas Gallo</span><span>Designed and built by me, with Claude Code</span></div>
</div></footer>'''

def next_footer(href, label, lock=False):
    pill = f'<span class="lock" aria-hidden="true">Password</span>{LOCK_SR}' if lock else ''
    return f'''<footer class="g next"><div class="in">
  <a class="go" href="{href}"><span class="k">Next project</span><strong>{label}{pill}</strong></a>
  <div class="foot"><a href="index.html#work">All work</a><span>© 2026 Nivas Gallo</span></div>
</div></footer>'''

GATE_JS = '''<script>
(function(){
  var P=JSON.parse(document.getElementById('payload').textContent);
  function d(b){return Uint8Array.from(atob(b),function(c){return c.charCodeAt(0)})}
  var form=document.getElementById('unlock'),pw=document.getElementById('pw'),err=document.getElementById('err'),go=document.getElementById('go');
  async function open(pass,announce){
    var base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pass),'PBKDF2',false,['deriveKey']);
    var key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:d(P.salt),iterations:P.iter,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['decrypt']);
    var html=new TextDecoder().decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:d(P.iv)},key,d(P.ct)));
    var c=document.getElementById('content'); c.innerHTML=html; c.hidden=false;
    document.getElementById('gate').hidden=true;
    try{sessionStorage.setItem('ng-yo',pass)}catch(e){}
    if(window.ngMotion){window.ngMotion(c)}
    if(announce){c.focus()}
  }
  form.addEventListener('submit',async function(e){
    e.preventDefault(); err.hidden=true; pw.removeAttribute('aria-invalid');
    if(!pw.value){pw.focus();return}
    go.disabled=true; go.textContent='Unlocking';
    try{await open(pw.value,true)}catch(x){err.hidden=false;pw.setAttribute('aria-invalid','true');pw.focus();pw.select()}
    go.disabled=false; go.textContent='Unlock';
  });
  var saved=null; try{saved=sessionStorage.getItem('ng-yo')}catch(e){}
  if(saved) open(saved,false).catch(function(){try{sessionStorage.removeItem('ng-yo')}catch(e){}});
})();
</script>'''

PAGES = {
    'index.html': dict(title='Nivas Gallo', desc='Nivas Gallo, Lead Product Designer in London. Case studies from Betfair, Sky Bet and the Betfair Exchange.', footer=CONTACT_FOOTER),
    'rebuild.html': dict(title='Betfair Rebuild · Nivas Gallo', desc='Case study: replacing Betfair’s Sportsbook app with one platform, TBD.', footer=next_footer('your-odds.html', 'Your Odds+.', lock=True)),
    'your-odds.html': dict(title='Your Odds+ · Nivas Gallo', desc='Password-protected case study: better prices for loyal customers.', footer=next_footer('odds-boost.html', 'Betfair Odds Boost.'), payload='src/your-odds.payload.json'),
    'odds-boost.html': dict(title='Betfair Odds Boost · Nivas Gallo', desc='Case study: a daily boost that lets customers choose which bet to reward.', footer=next_footer('rebuild.html', 'Betfair Rebuild.')),
}

def head_tags(p):
    return (f'<title>{p["title"]}</title>\n<meta name="description" content="{p["desc"]}">\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTS}">\n<link rel="stylesheet" href="css/site.css">')

def build(name, p):
    body = open(os.path.join(SRC, 'pages', name)).read()
    extra = ''
    if 'payload' in p:
        payload = open(os.path.join(ROOT, p['payload'])).read()
        body += '\n<div id="content" role="region" tabindex="-1" aria-label="Your Odds+ case study" hidden></div>'
        extra = f'<script type="application/json" id="payload">{payload}</script>\n{GATE_JS}\n'
    page = f'''{HEADER}

<main id="main" tabindex="-1">
{body}
</main>

{p["footer"]}

{extra}<script src="js/site.js"></script>'''
    if DEPLOY:
        return (f'<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n'
                f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                f'{head_tags(p)}\n</head>\n<body>\n{page}\n</body>\n</html>\n')
    return f'{head_tags(p)}\n<meta name="claude:viewport-fit-sides" content="cover">\n\n{page}\n'

os.makedirs(os.path.join(OUT, 'css'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'js'), exist_ok=True)
shutil.copy(os.path.join(SRC, 'site.css'), os.path.join(OUT, 'css', 'site.css'))
shutil.copy(os.path.join(SRC, 'site.js'), os.path.join(OUT, 'js', 'site.js'))
shutil.copytree(os.path.join(SRC, 'img'), os.path.join(OUT, 'img'), dirs_exist_ok=True)
if DEPLOY:
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
for name, p in PAGES.items():
    open(os.path.join(OUT, name), 'w').write(build(name, p))
    print('built', os.path.join(OUT, name))
