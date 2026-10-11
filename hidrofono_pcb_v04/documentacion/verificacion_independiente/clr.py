import sys, math; sys.path.insert(0, sys.argv[2])
from sx import parse, find, one
from shapely.geometry import Point, LineString, Polygon, box
from shapely import affinity
b=parse(open(sys.argv[1]).read())
items=[]  # (layer, net, geom, desc)
for fp in find(b,'footprint'):
    at=one(fp,'at'); x,y=float(at[1]),float(at[2]); rot=float(at[3]) if len(at)>3 else 0
    ref=[p[2] for p in find(fp,'property') if p[1]=='Reference'][0]
    for p in find(fp,'pad'):
        pa=one(p,'at'); px,py=float(pa[1]),float(pa[2]); sz=one(p,'size'); w,h=float(sz[1]),float(sz[2])
        prot=float(pa[3]) if len(pa)>3 else 0
        if p[3] in('circle',) : g=Point(px,py).buffer(w/2,64)
        else: g=box(px-w/2,py-h/2,px+w/2,py+h/2)
        if prot-rot: g=affinity.rotate(g,-(prot-rot),origin=(px,py))
        g=affinity.rotate(g,-rot,origin=(0,0)); g=affinity.translate(g,x,y)
        n=one(p,'net'); net=n[1] if n else None
        layers=one(p,'layers')[1:]
        dr=one(p,'drill')
        for L in ('F.Cu','B.Cu'):
            if any(l in(L,'*.Cu') for l in layers):
                if p[2]=='np_thru_hole': continue
                items.append((L,net,g,f"{ref}.{p[1]}"))
        if dr:  # hole, any layer
            hc=affinity.rotate(Point(px,py),-rot,origin=(0,0)); hc=affinity.translate(hc,x,y)
            items.append(('HOLE',net if p[2]!='np_thru_hole' else 'NPTH',hc.buffer(float(dr[1])/2,64),f"{ref}.{p[1]} hole"))
for s in b:
    if not(isinstance(s,list) and s): continue
    if s[0]=='segment':
        g=LineString([tuple(map(float,one(s,'start')[1:])),tuple(map(float,one(s,'end')[1:]))]).buffer(float(one(s,'width')[1])/2,64)
        items.append((one(s,'layer')[1],one(s,'net')[1],g,'seg'))
    if s[0]=='via':
        c=Point(*map(float,one(s,'at')[1:]));
        for L in ('F.Cu','B.Cu'): items.append((L,one(s,'net')[1],c.buffer(float(one(s,'size')[1])/2,64),'via@%s'%one(s,'at')[1:]))
        items.append(('HOLE',one(s,'net')[1],c.buffer(float(one(s,'drill')[1])/2,64),'via hole'))
    if s[0]=='zone':
        for fpz in find(s,'filled_polygon'):
            pts=[(float(q[1]),float(q[2])) for q in one(fpz,'pts')[1:]]
            items.append((one(fpz,'layer')[1],one(s,'net')[1],Polygon(pts),'zone'))
edge=Point(100,100).buffer(10,720).exterior
worst={}
for L in('F.Cu','B.Cu'):
    its=[i for i in items if i[0]==L]
    m=(9,None)
    for i in range(len(its)):
        for j in range(i+1,len(its)):
            if its[i][1]!=its[j][1]:
                d=its[i][2].distance(its[j][2])
                if d<m[0]: m=(d,its[i][3],its[j][3],its[i][1],its[j][1])
    e=min((it[2].distance(edge),it[3]) for it in its)
    print(L,"min clearance different nets: %.3f"%m[0], m[1:], " | min to edge %.3f %s"%e)
holes=[i for i in items if i[0]=='HOLE']
print("min hole-hole: %.3f"%min(holes[i][2].distance(holes[j][2]) for i in range(len(holes)) for j in range(i+1,len(holes))))
# copper (other net) to NPTH
np_=[h for h in holes if h[1]=='NPTH']
print("min copper to NPTH: %.3f"%min(h[2].distance(i[2]) for h in np_ for i in items if i[0] in('F.Cu','B.Cu')))
# isolated zone islands?
zs=[i for i in items if i[3]=='zone']; print("zone polygons:",len(zs), [round(z[2].area,2) for z in zs])
# connectivity: graph over items of same net, edges if same layer & touching, or HOLE (plated) links F/B
import itertools
cu=[i for i in items if i[0] in('F.Cu','B.Cu')]
for net in sorted(set(i[1] for i in cu if i[1])):
    its=[i for i in cu if i[1]==net]
    par=list(range(len(its)))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for a,c in itertools.combinations(range(len(its)),2):
        A,C=its[a],its[c]
        same= A[0]==C[0] and A[2].distance(C[2])<1e-6
        thru= A[0]!=C[0] and A[3]==C[3] and (A[3].startswith('via') or A[3][0] in 'JT' and A[3]!='TP1.1')
        if same or thru: par[f(a)]=f(c)
    roots=set(f(k) for k in range(len(its)))
    pads=[i[3] for i in its if '.' in i[3]]
    groups={}
    for k,i in enumerate(its):
        if '.' in i[3] and not i[3].startswith('via'): groups.setdefault(f(k),set()).add(i[3])
    print("net",net,"islands with pads:",len(groups), [sorted(g) for g in groups.values()] if len(groups)>1 else "")
