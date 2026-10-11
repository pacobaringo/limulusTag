import sys, math
from gerbonara import GerberFile
from gerbonara.utils import MM
vias=[(93.9,100.25),(93.9,102.15),(95.5,104.2),(97.85,95.5),(98.2,97.0),(100.55,96.1),(100.9375,94.6),(101.7,98.05),(101.7,99.95),(102.7,96.65),(103.0,100.4),(103.0,102.8),(103.2,101.5),(105.4,94.0)]
def inside(pt,poly):
    x,y=pt;c=False
    for i in range(len(poly)):
        x1,y1=poly[i];x2,y2=poly[i-1]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
for f in sys.argv[1:]:
    g=GerberFile.open(f)
    polys=[]
    for o in g.objects:
        for p in o.to_primitives(MM):
            if hasattr(p,'outline'): polys.append([tuple(q) for q in p.outline])
    out=[]
    for vx,vy in vias:
        # sample ring at r=0.3 (via copper edge) : all 16 points must be inside some opening
        ok=all(any(inside((vx+0.33*math.cos(a), -vy+0.33*math.sin(a)),P) for P in polys) for a in [k*math.pi/8 for k in range(16)])
        out.append(ok)
    print(f, sum(out), "/", len(vias), "vias fully open (r=0.33 mm)")
