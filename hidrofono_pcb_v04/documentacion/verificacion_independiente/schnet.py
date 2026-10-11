import sys, math; sys.path.insert(0, sys.argv[2])
from sx import parse, find, one
s=parse(open(sys.argv[1]).read())
libs={ls[1]:ls for ls in find(one(s,'lib_symbols'),'symbol')}
def pins_of(lib):
    out=[]
    def walk(n):
        for c in n:
            if isinstance(c,list):
                if c and c[0]=='pin': out.append((one(c,'number')[1],float(one(c,'at')[1]),float(one(c,'at')[2])))
                else: walk(c)
    walk(lib); return out
R=lambda v: (round(v[0],2),round(v[1],2))
pts={}  # point -> list of (kind,name)
nodes=[]
for sym in find(s,'symbol'):
    lid=one(sym,'lib_id')[1]; at=one(sym,'at'); x,y,rot=float(at[1]),float(at[2]),float(at[3])
    mir=one(sym,'mirror')
    ref=[p[2] for p in find(sym,'property') if p[1]=='Reference'][0]
    for num,px,py in pins_of(libs[lid]):
        py=-py  # lib y up
        if mir and mir[1]=='x': py=-py
        if mir and mir[1]=='y': px=-px
        a=math.radians(-rot)  # schematic rotation is CCW visually; y down
        gx=x+px*math.cos(a)-py*math.sin(a); gy=y+px*math.sin(a)+py*math.cos(a)
        nodes.append((f"{ref}.{num}",R((gx,gy))))
segs=[]
for w in find(s,'wire'):
    p=one(w,'pts'); a=R(tuple(map(float,p[1][1:]))); b=R(tuple(map(float,p[2][1:]))); segs.append((a,b))
labels=[(l[1],R(tuple(map(float,one(l,'at')[1:3])))) for l in find(s,'label')+find(s,'global_label')]
juncs=[R(tuple(map(float,one(j,'at')[1:3]))) for j in find(s,'junction')]
# power symbols: symbols whose lib is power -> treat their value as net name
allpts=set([p for _,p in nodes]+[p for _,p in labels]+juncs+[q for sg in segs for q in sg])
par={p:p for p in allpts}
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
def onseg(p,a,b):
    (x,y),(x1,y1),(x2,y2)=p,a,b
    if abs((x2-x1)*(y-y1)-(y2-y1)*(x-x1))>1e-6: return False
    return min(x1,x2)-1e-6<=x<=max(x1,x2)+1e-6 and min(y1,y2)-1e-6<=y<=max(y1,y2)+1e-6
for a,b in segs:
    for p in allpts:
        if onseg(p,a,b):
            # wire-to-wire mid T without junction: only endpoints or junction/pin/label connect
            par[f(p)]=f(a)
groups={}
for name,p in labels: groups.setdefault(name,set()).add(f(p))
net_of={}
for name,rs in groups.items():
    for r in rs: net_of[r]=name
pw={}
for sym in find(s,'symbol'):
    lid=one(sym,'lib_id')[1]
    if lid.startswith('power:') or 'GND' in lid and lid!='Hydro:GND_WATER':
        pass
res={}
for ref,p in nodes:
    res[ref]=net_of.get(f(p),'?'+str(p))
for k in sorted(res): print(k,res[k])
