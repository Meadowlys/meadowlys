from pathlib import Path
import base64, json, os, urllib.request, html, datetime
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'
USER='meadowlys'
def esc(s): return html.escape(str(s),quote=True)
def trim(s,n): return s if len(s)<=n else s[:n-1]+'…'
def tx(x,y,s,size=22,color='#b8b8b8',bold=False,anchor='start'):
 return f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{esc(s)}</text>'
def rect(x,y,w,h,fill,extra=''): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'
def line(x,y,X,Y,c='#414141'): return f'<path d="M{x} {y}H{X}" stroke="{c}"/>' if y==Y else f'<path d="M{x} {y}L{X} {Y}" stroke="{c}"/>'
def image(x,y,w,h,name='banner.jpg'):
 b=base64.b64encode((A/name).read_bytes()).decode(); return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{b}" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="data:image/jpeg;base64,{b}"/>'
def save(name,w,h,parts):
 (A/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'+''.join(parts)+'</svg>')
def projects(repos=None):
 W,H=1000,540; p=[rect(0,0,W,H,'#141414'),image(0,0,W,H),rect(0,0,W,H,'#101010','opacity=".89"'),tx(39,47,'REPOSITORIES',23,'#eeeeee',True),line(39,68,960,68),line(502,98,502,445,'#555555')]
 repos=repos or []; active=repos[0] if repos else None
 for i in range(4):
  y=101+i*84; r=repos[i] if i<len(repos) else None
  if i==0: p += [rect(38,y,444,76,'#c5c5c5','opacity=".13"'),rect(38,y,3,76,'#e5e5e5')]
  if r:
   p += [rect(50,y+10,94,55,'#303030'),tx(97,y+43,'</>',23,'#bcbcbc',True,'middle'),tx(159,y+26,trim(r['name'],28),21,'#ededed' if i==0 else '#aaa',True),tx(159,y+51,trim((r.get('primaryLanguage') or {}).get('name','Repository')+'  ·  '+r['updatedAt'][:10],34),15,'#aaa' if i==0 else '#777')]
  elif i==0:
   p += [rect(50,y+10,94,55,'#303030'),tx(97,y+43,'</>',23,'#bcbcbc',True,'middle'),tx(159,y+26,'Public repositories',21,'#eeeeee',True),tx(159,y+51,'View on GitHub',16,'#b7b7b7')]
  else: p += [line(50,y+37,143,y+37,'#383838'),tx(159,y+43,'—',19,'#555555')]
  p += [line(38,y+80,482,y+80,'#333333')]
 p += [tx(530,117,trim(active['name'],34) if active else 'Public repositories',22,'#eee',True),image(530,137,431,185),rect(530,137,431,185,'#000','opacity=".18"')]
 if active:
  lang=(active.get('primaryLanguage') or {}).get('name','Not specified'); desc=active.get('description') or 'No description provided.'
  import textwrap
  for j,t in enumerate(textwrap.wrap(desc,width=44)[:2]): p += [tx(960,354+j*23,t,17,'#d2d2d2',False,'end')]
  p += [tx(960,413,f'{lang}  /  {active["stargazerCount"]} stars  /  {active["forkCount"]} forks',17,'#b9b9b9',False,'end'),tx(960,440,'Updated '+active['updatedAt'][:10],17,'#b9b9b9',False,'end')]
 else: p += [tx(960,354,'Browse my projects on GitHub.',19,'#dedede',False,'end'),tx(960,383,'Repository data updates via GitHub Actions.',16,'#a9a9a9',False,'end')]
 p += [line(39,475,960,475),'<circle cx="763" cy="503" r="7" fill="none" stroke="#eee" stroke-width="1.5"/><path d="M760 500l6 6m0 -6l-6 6" stroke="#eee" stroke-width="1.5"/>',tx(960,509,'OPEN REPOSITORIES',17,'#eeeeee',True,'end')]; save('projects.svg',W,H,p)
def activity(data=None):
 W,H=1000,280; p=[rect(0,0,W,H,'#101010'),tx(35,42,'GITHUB ACTIVITY',22,'#eee',True),line(35,58,965,58)]
 if data is None:
  p += [tx(35,112,'Contribution data',25,'#eee',True),tx(35,145,'Run the optional GitHub Actions workflow to populate this panel.',18),tx(35,193,'Open my GitHub profile to view live contributions.',18,'#aaa')]
 else:
  cal=data['contributionsCollection']['contributionCalendar']; weeks=cal['weeks'][-52:]; colors=['#292929','#505050','#777777','#b2b2b2','#eeeeee']; levels={'NONE':0,'FIRST_QUARTILE':1,'SECOND_QUARTILE':2,'THIRD_QUARTILE':3,'FOURTH_QUARTILE':4}
  p += [tx(35,110,str(cal['totalContributions']),36,'#eee',True),tx(35,136,'contributions / past year',16),tx(290,110,str(data['repositories']['totalCount']),36,'#eee',True),tx(290,136,'public repositories',16),tx(540,110,str(data['followers']['totalCount']),36,'#eee',True),tx(540,136,'followers',16),tx(960,110,datetime.date.today().isoformat(),17,'#aaa',False,'end')]
  for i,w in enumerate(weeks):
   for d in w['contributionDays']:
    p += [rect(35+i*18,160+d['weekday']*14,13,11,colors[levels.get(d['contributionLevel'],0)],'rx="1"')]
  p += [tx(35,270,'LESS',12,'#999')]+[rect(83+i*18,259,13,11,c) for i,c in enumerate(colors)]+[tx(178,270,'MORE',12,'#999')]
 save('activity.svg',W,H,p)
def fetch():
 query='''query($login:String!) { user(login:$login) { followers { totalCount } repositories(first:8,privacy:PUBLIC,ownerAffiliations:OWNER,orderBy:{field:UPDATED_AT,direction:DESC}) { totalCount nodes { name description isFork stargazerCount forkCount updatedAt primaryLanguage { name } } } contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { weekday contributionLevel } } } } } }'''
 req=urllib.request.Request('https://api.github.com/graphql',data=json.dumps({'query':query,'variables':{'login':USER}}).encode(),headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Content-Type':'application/json','User-Agent':'meadow-profile'},method='POST')
 with urllib.request.urlopen(req,timeout=30) as response: out=json.load(response)
 if out.get('errors') or not out.get('data',{}).get('user'): raise RuntimeError(str(out.get('errors','User not found')))
 return out['data']['user']
if __name__=='__main__':
 if os.environ.get('GH_TOKEN'):
  d=fetch(); repos=[r for r in d['repositories']['nodes'] if not r['isFork'] and r['name'].lower()!=USER.lower()]; projects(repos[:4]); activity(d)
 else: projects(); activity()
