from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
import os, json, urllib.request, subprocess, tempfile, textwrap, shutil, html
from activity import activity, fetch as fetch_activity
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; U='meadowlys'
BASE='https://interfaceingame.com/wp-content/uploads/the-last-of-us-part-ii/the-last-of-us-part-ii-'
SOURCES={'load.jpg':BASE+'game-load-menu.jpg','start.jpg':BASE+'start-screen.jpg','pause.jpg':BASE+'pause-menu.jpg','ellie-source.gif':'https://media.tenor.com/9ZmRmZL_h1EAAAAM/ellie-tlou2.gif','boat.mp4':'https://motionbgs.com/dl/hd/710'}
W,H=1000,563
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
if not Path(FONT).exists(): FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)
def text(d,x,y,s,n=17,c=210,b=False,anchor=None): d.text((x,y),str(s),font=font(n,b),fill=(c,c,c),anchor=anchor)
def fit(s,n,w,b=False):
 s=str(s or ''); f=font(n,b)
 while s and f.getlength(s)>w: s=s[:-1]
 return s if s==str(s or '') and f.getlength(s)<=w else s
# Width-aware clipping, including ellipsis.
def cut(s,n,w,b=False):
 s=str(s or ''); f=font(n,b)
 if f.getlength(s)<=w:return s
 while s and f.getlength(s+'…')>w:s=s[:-1]
 return s+'…'
def download(url,p):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'*/*'})
 with urllib.request.urlopen(req,timeout=45) as r, open(p,'wb') as f:
  data=r.read(65*1024*1024+1)
  if len(data)>65*1024*1024:raise ValueError('asset too large')
  f.write(data)
def fetch_repos():
 req=urllib.request.Request(f'https://api.github.com/users/{U}/repos?per_page=100&sort=updated&type=owner',headers={'User-Agent':'meadow-profile','Accept':'application/vnd.github+json',**({'Authorization':'Bearer '+os.environ['GH_TOKEN']} if os.environ.get('GH_TOKEN') else {})})
 with urllib.request.urlopen(req,timeout=25) as r: out=json.load(r)
 return [x for x in out if not x['fork'] and x['name'].lower()!=U and not x['private']][:4]
def gray(im):return ImageOps.grayscale(im).convert('RGB')
def base(im):return ImageEnhance.Brightness(gray(ImageOps.fit(im,(W,H))).filter(ImageFilter.GaussianBlur(5))).enhance(.36)
def overlay(im,box,alpha=80):
 layer=Image.new('RGBA',im.size); ImageDraw.Draw(layer).rectangle(box,fill=(0,0,0,alpha)); return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
def thumbs(load):
 if load is None:return []
 im=ImageOps.fit(load,(1000,563)); return [gray(im.crop(b)) for b in [(546,132,947,305),(37,237,152,319),(37,334,152,416),(37,430,152,478)]]
def render(im,repos,ts,active=0):
 im=overlay(im,(0,0,W,H),65); d=ImageDraw.Draw(im)
 text(d,38,35,'REPOSITORIES',23,238,True); d.line((38,71,963,71),fill=(57,57,57))
 d.line((513,94,513,470),fill=(78,78,78)); d.rectangle((512,94+active*70,515,161+active*70),fill=(225,225,225))
 items=repos or [{'name':'public repositories','description':'browse my projects on github','language':None,'updated_at':'','stargazers_count':0,'forks_count':0}]
 for i,r in enumerate(items):
  y=94+i*96; selected=i==active
  if selected:
   strip=Image.new('RGBA',im.size); ImageDraw.Draw(strip).rectangle((37,y,481,y+83),fill=(200,200,200,26)); im=Image.alpha_composite(im.convert('RGBA'),strip).convert('RGB'); d=ImageDraw.Draw(im)
  if ts:
   t=ImageOps.fit(ts[i%len(ts)],(115,83)); im.paste(ImageEnhance.Brightness(t).enhance(1 if selected else .52),(37,y))
  else:
   d.rectangle((37,y,152,y+83),outline=(70,70,70)); text(d,94,y+42,'</>',20,155,False,'mm')
  c=226 if selected else 139
  text(d,168,y+10,cut(r['name'],18,307),18,c)
  meta=(r.get('language') or 'Repository')+'    '+r.get('updated_at','')[:10] if repos else 'GitHub'
  text(d,168,y+36,cut(meta,15,308),15,c-10)
  text(d,168,y+58,cut(r.get('description') or '',14,308),14,c-24)
  d.line((37,y+90,481,y+90),fill=(48,48,48))
 r=items[active]; text(d,546,92,cut(r['name'],22,410),22,235,True)
 if ts: im.paste(ImageOps.fit(ts[active%len(ts)],(401,173)),(546,132))
 else:
  d.rectangle((546,132,947,305),outline=(65,65,65)); text(d,746,217,'github / meadowlys',22,160,False,'mm')
 d=ImageDraw.Draw(im)
 if repos:
  for j,s in enumerate([r.get('language') or 'No language listed',f"{r['stargazers_count']} stars     {r['forks_count']} forks",'Updated '+r['updated_at'][:10]]):text(d,948,329+j*25,s,18,190,False,'ra')
  desc=textwrap.wrap(r.get('description') or 'No description provided.',width=45)[:2]
  for j,s in enumerate(desc):text(d,948,410+j*22,cut(s,15,405),15,173,False,'ra')
 else:text(d,948,335,'view all public projects',18,190,False,'ra')
 d.line((37,503,963,503),fill=(69,69,69));text(d,961,522,'× OPEN REPOSITORIES',16,230,False,'ra')
 return im

def main(online=False):
 repos=[]; ts=[]; backgrounds=[]; A.mkdir(exist_ok=True)
 if online:
  repos=fetch_repos()
  with tempfile.TemporaryDirectory() as t:
   t=Path(t)
   for name,url in SOURCES.items():
    try:
     download(url,t/name)
     if name.endswith('.jpg'):
      img=Image.open(t/name);img.load()
      if name=='load.jpg':ts=thumbs(img)
      if name=='start.jpg':backgrounds=[base(img)]
      if name=='pause.jpg':gray(img).save(A/'pause.jpg',quality=92)
     elif name=='ellie-source.gif':
      from PIL import ImageSequence
      src=Image.open(t/name); fs=[]; ds=[]
      for frame in ImageSequence.Iterator(src):fs.append(gray(frame.convert('RGB')).resize((360,round(frame.height*360/frame.width))));ds.append(max(40,frame.info.get('duration',80)))
      fs[0].save(A/'ellie.gif',save_all=True,append_images=fs[1:],duration=ds,loop=0,optimize=True)
     else:
      subprocess.run(['ffmpeg','-v','error','-y','-i',str(t/name),'-t','6','-vf','fps=8,scale=1000:563:force_original_aspect_ratio=increase,crop=1000:563',str(t/'boat-%03d.jpg')],check=True,timeout=90)
      bs=[base(Image.open(p)) for p in sorted(t.glob('boat-*.jpg'))]
      if bs:backgrounds=bs
    except Exception as e:print(f'{name}: {e}')
   if not backgrounds:raise RuntimeError('No real boat source available; retaining existing widgets.')
 else:backgrounds=[Image.new('RGB',(W,H),(23,23,23))]
 frames=[render(bg,repos,ts,min(i//12,max(0,len(repos)-1))) for i,bg in enumerate(backgrounds)]
 frames[0].save(A/'projects-preview.png'); frames[0].save(A/'projects.gif',save_all=True,append_images=frames[1:],duration=125,loop=0,optimize=True)
 if online:
  try:activity(fetch_activity())
  except Exception as e:print('Activity:',e)
  # Direct project links are updated from the same public API data.
  md=ROOT/'README.md'; s=md.read_text(); start='<!-- PROJECTS:START -->'; end='<!-- PROJECTS:END -->'; links=' · '.join(f'<a href="{html.escape(r["html_url"],quote=True)}">{html.escape(r["name"])}</a>' for r in repos)
  if links:s=s.split(start)[0]+start+'\n<p align="center">'+links.replace(' · ',' &nbsp; / &nbsp; ')+'</p>\n'+end+s.split(end)[1]
  if (A/'pause.jpg').exists():s=s.replace(SOURCES['pause.jpg'],'assets/pause.jpg')
  if (A/'ellie.gif').exists():s=s.replace(SOURCES['ellie-source.gif'],'assets/ellie.gif')
  if (A/'activity.svg').exists() and 'assets/activity.svg' not in s:s=s.replace('<p align="center"><a href="https://github.com/meadowlys"><img src="https://github-readme-activity-graph', '<p align="center"><img src="assets/activity.svg" width="100%" alt="Contribution history"></p>\n<p align="center"><a href="https://github.com/meadowlys"><img src="https://github-readme-activity-graph')
  md.write_text(s)
if __name__=='__main__':main('--online' in __import__('sys').argv)
