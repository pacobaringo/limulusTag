import sys, math
from gerbonara import GerberFile
from gerbonara.graphic_primitives import Circle, Line, Arc, ArcPoly, Rectangle
from gerbonara.utils import MM
cx, cy = 100.0, -100.0
def rmax_prim(p):
    if isinstance(p, Circle): return math.hypot(p.x-cx,p.y-cy)+p.r
    if isinstance(p, Line): return max(math.hypot(p.x1-cx,p.y1-cy),math.hypot(p.x2-cx,p.y2-cy))+p.width/2
    if isinstance(p, Rectangle):
        (x0,y0),(x1,y1)=p.bounding_box()
        return max(math.hypot(x-cx,y-cy) for x in (x0,x1) for y in (y0,y1))
    if isinstance(p, ArcPoly):
        pts=list(p.outline)
        # sample arcs approximately by vertices plus bbox check
        r=max(math.hypot(x-cx,y-cy) for x,y in pts)
        return r
    if isinstance(p, Arc):
        return max(math.hypot(p.x1-cx,p.y1-cy),math.hypot(p.x2-cx,p.y2-cy))+p.width/2
    (x0,y0),(x1,y1)=p.bounding_box(); return max(math.hypot(x-cx,y-cy) for x in (x0,x1) for y in (y0,y1))
for f in sys.argv[1:]:
    g=GerberFile.open(f)
    worst=(0,None)
    for o in g.objects:
        if getattr(o,'polarity_dark',True) is False: continue
        for p in o.to_primitives(MM):
            r=rmax_prim(p)
            if r>worst[0]: worst=(r,p)
    print(f, "max copper radius %.4f mm -> edge clearance %.4f mm"%(worst[0],10-worst[0]))
    print("   worst:", type(worst[1]).__name__, str(worst[1])[:150])
