import sys, math; sys.path.insert(0, sys.argv[2])
from sx import parse, find, one
b=parse(open(sys.argv[1]).read())
nets={c[1]:c[2] for c in find(b,'net')}
for fp in find(b,'footprint'):
    at=one(fp,'at'); x,y=float(at[1]),float(at[2]); rot=float(at[3]) if len(at)>3 else 0
    layer=one(fp,'layer')[1]
    props={p[1]:p[2] for p in find(fp,'property')}
    attrs=one(fp,'attr')
    pads=[]
    for p in find(fp,'pad'):
        n=one(p,'net'); pa=one(p,'at')
        px,py=float(pa[1]),float(pa[2]); a=math.radians(-rot)
        gx=x+px*math.cos(a)-py*math.sin(a); gy=y+px*math.sin(a)+py*math.cos(a)
        sz=one(p,'size'); dr=one(p,'drill')
        pads.append(f"{p[1]}:{p[2]}:{n[-1] if n else '-'}@({gx:.2f},{gy:.2f}) sz{sz[1]}x{sz[2]}"+(f" dr{dr[1]}" if dr else ""))
    print(props.get('Reference'),props.get('Value'),layer,f"rot{rot}",attrs[1:] if attrs else '', props.get('MPN',''), props.get('Alias',''))
    for q in pads: print("    ",q)
print("tracks by net/layer:")
from collections import Counter
c=Counter((s[0],one(s,'layer')[1] if one(s,'layer') else 'via', one(s,'net')[1]) for s in b if isinstance(s,list) and s and s[0] in('segment','via','arc'))
for k,v in sorted(c.items()): print("  ",k,v, nets.get(k[2]))
