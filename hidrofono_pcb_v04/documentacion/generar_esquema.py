#!/usr/bin/env python3
"""Regenera KiCad/hidrofono_v04.kicad_sch y KiCad/hidrofono.kicad_sym con el
esquema dibujado con cables (v0.4, redibujo).

Conserva referencias, UUID de símbolos y de hoja, huellas, campos y nombres de
red (/PIEZO_IN, /GATE, /SOURCE, /MIC, /GND), de modo que la PCB no cambia.
Uso: python3 generar_esquema.py   (desde documentacion/)
"""
import json, os, re, sys, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD = os.path.join(HERE, '..', 'KiCad')
sys.path.insert(0, os.path.join(HERE, 'verificacion_independiente'))
from sx import parse, find, one  # noqa: E402

U = 2.54                      # rejilla
OX, OY = 8, 6               # desplazamiento de la hoja, en unidades de rejilla
NS = uuid.UUID('6b0c5a52-3f3e-4f0e-9d0e-0d4a8e5b7c11')


def uid(tag):
    return str(uuid.uuid5(NS, tag))


def mm(v):
    return f'{v:.4f}'.rstrip('0').rstrip('.')


def P(x, y):
    """Punto de rejilla -> mm en la hoja."""
    return ((x + OX) * U, (y + OY) * U)


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


FONT = '(effects (font (size 1.27 1.27)))'
FONT_H = '(effects (font (size 1.27 1.27)) hide)'
STROKE = '(stroke (width 0.254) (type default)) (fill (type none))'


def pl(*pts, fill='none'):
    s = ' '.join(f'(xy {mm(x)} {mm(y)})' for x, y in pts)
    return f'(polyline (pts {s}) (stroke (width 0.254) (type default)) (fill (type {fill})))'


def pin(num, name, x, y, ang, length=2.54, kind='passive'):
    return (f'(pin {kind} line (at {mm(x)} {mm(y)} {ang}) (length {mm(length)}) '
            f'(name {q(name)} {FONT}) (number {q(num)} {FONT}))')


def libsym(name, ref, graphics, pins, hide_names=True):
    base = name.split(':')[-1]
    pn = '(pin_names (offset 0.254) hide)' if hide_names else '(pin_names (offset 0.254))'
    if base in ('R', 'C', 'TP', 'GND_WATER'):
        pn = '(pin_numbers hide) ' + pn
    return (f'(symbol {q(name)} {pn} (in_bom yes) (on_board yes) '
            f'(property "Reference" {q(ref)} (id 0) (at 2.54 0 0) {FONT}) '
            f'(property "Value" {q(base)} (id 1) (at 2.54 -2.54 0) {FONT}) '
            f'(property "Footprint" "" (id 2) (at 0 0 0) {FONT_H}) '
            f'(property "Datasheet" "" (id 3) (at 0 0 0) {FONT_H}) '
            f'(symbol {q(base + "_0_1")} {" ".join(graphics)}) '
            f'(symbol {q(base + "_1_1")} {" ".join(pins)}))')


# --- Símbolos (coordenadas de librería: y hacia arriba) ----------------------
SYMS = {
    # Resistencia vertical: 1 arriba, 2 abajo
    'R': ('R', [f'(rectangle (start -1.016 -2.54) (end 1.016 2.54) {STROKE})'],
          [pin('1', '1', 0, 5.08, 270), pin('2', '2', 0, -5.08, 90)]),
    # Condensador vertical: 1 arriba, 2 abajo
    'C': ('C', [pl((-2.032, 0.762), (2.032, 0.762)), pl((-2.032, -0.762), (2.032, -0.762)),
                pl((0, 2.54), (0, 0.762)), pl((0, -0.762), (0, -2.54))],
          [pin('1', '1', 0, 5.08, 270), pin('2', '2', 0, -5.08, 90)]),
    # JFET canal N: G izquierda, D arriba, S abajo (pines 1=S, 2=D, 3=G)
    'JFET': ('Q', [pl((0, -2.54), (0, 2.54)),
                   pl((-5.08, 0), (0, 0)),
                   pl((-1.524, 0.635), (0, 0), (-1.524, -0.635), fill='outline'),
                   pl((0, 1.905), (2.54, 1.905), (2.54, 5.08)),
                   pl((0, -1.905), (2.54, -1.905), (2.54, -5.08)),
                   f'(circle (center 0.635 0) (radius 3.81) {STROKE})'],
             [pin('1', 'S', 2.54, -7.62, 90), pin('2', 'D', 2.54, 7.62, 270),
              pin('3', 'G', -7.62, 0, 0)]),
    # BAV199: par en serie 1=A1 -> 3=K1/A2 -> 2=K2; dibujado como antiparalelo
    'DIODE': ('D', [pl((0, 5.08), (0, 3.81)), pl((-2.54, 3.81), (2.54, 3.81)),
                    pl((-2.54, 3.81), (-2.54, -5.08)), pl((2.54, 3.81), (2.54, -5.08)),
                    pl((-3.81, -1.27), (-1.27, -1.27), (-2.54, 1.27), (-3.81, -1.27), fill='outline'),
                    pl((-3.81, 1.27), (-1.27, 1.27)),
                    pl((1.27, 1.27), (3.81, 1.27), (2.54, -1.27), (1.27, 1.27), fill='outline'),
                    pl((1.27, -1.27), (3.81, -1.27)),
                    '(circle (center 0 3.81) (radius 0.381) (stroke (width 0) (type default)) (fill (type outline)))'],
              [pin('1', 'A1', -2.54, -7.62, 90), pin('2', 'K2', 2.54, -7.62, 90),
               pin('3', 'K1/A2', 0, 7.62, 270)]),
    # Conector de 2 pads PTH, pines a la derecha: 1 arriba, 2 abajo
    'CONN': ('J', [f'(rectangle (start -2.54 -5.08) (end 1.27 5.08) {STROKE})',
                   '(circle (center 0.381 2.54) (radius 0.508) (stroke (width 0.254) (type default)) (fill (type none)))',
                   '(circle (center 0.381 -2.54) (radius 0.508) (stroke (width 0.254) (type default)) (fill (type none)))'],
             [pin('1', '1', 3.81, 2.54, 180, 2.54), pin('2', '2', 3.81, -2.54, 180, 2.54)]),
    # Punto de prueba: pin abajo
    'TP': ('TP', [f'(circle (center 0 0) (radius 1.016) {STROKE})'],
           [pin('1', 'S', 0, -3.81, 90, 2.794)]),
    # Masa al agua: pin arriba, símbolo de tierra con ondas
    'GND_WATER': ('J', [pl((0, 2.54), (0, 1.27)), pl((-2.54, 1.27), (2.54, 1.27)),
                        pl((-1.778, 0.254), (1.778, 0.254)), pl((-1.016, -0.762), (1.016, -0.762)),
                        '(arc (start -2.54 -2.032) (mid -1.905 -1.524) (end -1.27 -2.032) (stroke (width 0.254) (type default)) (fill (type none)))',
                        '(arc (start -1.27 -2.032) (mid -0.635 -2.54) (end 0 -2.032) (stroke (width 0.254) (type default)) (fill (type none)))',
                        '(arc (start 0 -2.032) (mid 0.635 -1.524) (end 1.27 -2.032) (stroke (width 0.254) (type default)) (fill (type none)))',
                        '(arc (start 1.27 -2.032) (mid 1.905 -2.54) (end 2.54 -2.032) (stroke (width 0.254) (type default)) (fill (type none)))'],
                  [pin('1', 'GND_AGUA', 0, 5.08, 270)]),
}

# Pines en coordenadas de rejilla relativas al símbolo (y hacia abajo, en pantalla)
PINS = {
    'R': {'1': (0, -2), '2': (0, 2)}, 'C': {'1': (0, -2), '2': (0, 2)},
    'JFET': {'1': (1, 3), '2': (1, -3), '3': (-3, 0)},
    'DIODE': {'1': (-1, 3), '2': (1, 3), '3': (0, -3)},
    'CONN': {'1': (1.5, -1), '2': (1.5, 1)}, 'TP': {'1': (0, 1.5)},
    'GND_WATER': {'1': (0, -2)},
}

# --- Colocación (rejilla). rot en grados KiCad; mirror 'y' refleja en X -----
RAIL = 52
PLACE = {
    'J1': ('CONN', 14, 37, 0, None),
    'C3': ('C', 26, 44, 0, None),
    'R1': ('R', 32, 36, 90, None),
    'D1': ('DIODE', 40, 44, 0, None),
    'R2': ('R', 48.5, 44, 0, None),
    'Q1': ('JFET', 56, 36, 0, None),
    'C2': ('C', 76, 30, 0, None),
    'J2': ('CONN', 84, 26, 0, 'y'),
    'R3': ('R', 59, 46, 0, None),
    'C1': ('C', 66, 46, 0, None),
    'TP1': ('TP', 70, 40.5, 0, None),
    'J3': ('GND_WATER', 88, RAIL + 2, 0, None),
}


def pin_pos(ref, num):
    kind, x, y, rot, mir = PLACE[ref]
    px, py = PINS[kind][num]
    if mir == 'y':
        px = -px
    for _ in range((rot // 90) % 4):      # KiCad: rotación antihoraria en pantalla
        px, py = py, -px
    return (x + px, y + py)


PP = pin_pos
# Polilíneas de cable (rejilla). Las T se resuelven partiendo segmentos.
WIRES = [
    # PIEZO_IN
    [PP('J1', '1'), (26, 36), PP('R1', '1')],
    [(26, 36), PP('C3', '1')],
    # GATE
    [PP('R1', '2'), PP('Q1', '3')],
    [(40, 36), PP('D1', '3')],
    [(48.5, 36), PP('R2', '1')],
    # MIC
    [PP('Q1', '2'), (57, 25), (76, 25), PP('J2', '1')],
    [(76, 25), PP('C2', '1')],
    # SOURCE
    [PP('Q1', '1'), (57, 42), (59, 42), (66, 42), PP('TP1', '1')],
    [(59, 42), PP('R3', '1')],
    [(66, 42), PP('C1', '1')],
    # GND: carril y bajadas
    [PP('J1', '2'), (15.5, RAIL), (88, RAIL)],
    [PP('C3', '2'), (26, RAIL)],
    [PP('D1', '1'), (39, RAIL)], [PP('D1', '2'), (41, RAIL)],
    [PP('R2', '2'), (48.5, RAIL)],
    [PP('R3', '2'), (59, RAIL)], [PP('C1', '2'), (66, RAIL)],
    [PP('C2', '2'), (76, RAIL)],
    [PP('J2', '2'), (80, 27), (80, RAIL)],
    [PP('J3', '1'), (88, RAIL)],
]
LABELS = [('PIEZO_IN', (20, 36), 0), ('GATE', (43.5, 36), 0), ('MIC', (62, 25), 0),
          ('SOURCE', (61, 42), 0), ('GND', (30, RAIL), 0)]


def segments():
    segs = []
    for poly in WIRES:
        segs += [(poly[i], poly[i + 1]) for i in range(len(poly) - 1) if poly[i] != poly[i + 1]]
    pts = {p for s in segs for p in s}
    pts |= {pin_pos(r, n) for r, (k, *_r) in PLACE.items() for n in PINS[k]}
    out = []
    for a, b in segs:
        cuts = [a, b]
        for p in pts:
            if p in (a, b):
                continue
            (x1, y1), (x2, y2), (x, y) = a, b, p
            if (x2 - x1) * (y - y1) == (y2 - y1) * (x - x1) and \
               min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
                cuts.append(p)
        cuts.sort(key=lambda p: (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2)
        out += [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)]
    return out


def junctions(segs):
    from collections import Counter
    c = Counter(p for s in segs for p in s)
    pinpts = {pin_pos(r, n) for r, (k, *_r) in PLACE.items() for n in PINS[k]}
    return sorted(p for p, n in c.items() if n + (p in pinpts) >= 3)


def main():
    src = open(os.path.join(KICAD, 'hidrofono_v04.kicad_sch'), encoding='utf-8').read()
    old = parse(src)
    root = one(old, 'uuid')[1]
    tb = re.search(r'\(title_block .*?\)\)\s*\(lib_symbols', src, re.S)
    title_block = tb.group(0)[:-len('(lib_symbols')].strip() if tb else ''
    props = {}
    for s in find(old, 'symbol'):
        ref = [p[2] for p in find(s, 'property') if p[1] == 'Reference'][0]
        props[ref] = (one(s, 'uuid')[1], one(s, 'lib_id')[1], one(s, 'dnp')[1],
                      [(p[1], p[2], any(isinstance(e, list) and 'hide' in e for e in p)) for p in find(s, 'property')])

    lib = ' '.join(libsym(f'Hydro:{n}', r, g, p) for n, (r, g, p) in SYMS.items())
    out = [f'(kicad_sch (version 20230121) (generator eeschema)', f'  (uuid {q(root)})', '  (paper "A4")',
           '  ' + title_block, f'  (lib_symbols {lib})']

    for ref, (kind, x, y, rot, mir) in PLACE.items():
        suid, lib_id, dnp, plist = props[ref]
        assert lib_id == f'Hydro:{kind}', (ref, lib_id)
        X, Y = P(x, y)
        horiz = rot in (90, 270)
        lab = []
        order = {'Reference': 0, 'Value': 1, 'Footprint': 2, 'Datasheet': 3}
        if not any(n == 'Datasheet' for n, _v, _h in plist):
            plist = plist + [('Datasheet', '', True)]
        plist = sorted(plist, key=lambda t: order.get(t[0], 4))
        for pid, (name, val, hidden) in enumerate(plist):
            if name in ('Reference', 'Value'):
                dy = -1.3 if name == 'Reference' else 1.3
                if horiz:
                    at, just = (X, Y + (-2.2 if name == 'Reference' else 2.4), 90), ''
                elif ref == 'J2':
                    at, just = (X + 3.0, Y + dy, 0), ' (justify right)'
                elif ref in ('J1', 'C2'):
                    at, just = (X - (4 if ref == 'J1' else 2.6), Y + dy, 0), ' (justify right)'
                else:
                    dx = {'JFET': 5.6, 'DIODE': 4.0, 'CONN': 3.0}.get(kind, 2.6)
                    at, just = (X + dx, Y + dy, 0), ' (justify left)'
            else:
                at, just = (X, Y, 0), ''
            hide = ' hide' if hidden or name not in ('Reference', 'Value') else ''
            lab.append(f'(property {q(name)} {q(val)} (id {pid}) (at {mm(at[0])} {mm(at[1])} {at[2]}) '
                       f'(effects (font (size 1.27 1.27)){just}{hide}))')
        mirror = f' (mirror {mir})' if mir else ''
        out.append(f'  (symbol (lib_id {q(lib_id)}) (at {mm(X)} {mm(Y)} {rot}){mirror} (unit 1) '
                   f'(in_bom yes) (on_board yes) (dnp {dnp}) (uuid {q(suid)}) ' + ' '.join(lab) +
                   f' (instances (project "hidrofono_v04" (path {q("/" + root)} (reference {q(ref)}) (unit 1)))))')

    segs = segments()
    for a, b in segs:
        (x1, y1), (x2, y2) = P(*a), P(*b)
        out.append(f'  (wire (pts (xy {mm(x1)} {mm(y1)}) (xy {mm(x2)} {mm(y2)})) '
                   f'(stroke (width 0) (type default)) (uuid {q(uid(f"w{a}{b}"))}))')
    for j in junctions(segs):
        X, Y = P(*j)
        out.append(f'  (junction (at {mm(X)} {mm(Y)}) (diameter 0) (color 0 0 0 0) (uuid {q(uid(f"j{j}"))}))')
    for name, p, ang in LABELS:
        X, Y = P(*p)
        out.append(f'  (label {q(name)} (at {mm(X)} {mm(Y)} {ang}) (effects (font (size 1.27 1.27)) '
                   f'(justify left bottom)) (uuid {q(uid("l" + name))}))')

    # Recuadro del nodo de puerta protegido por el anillo de guarda en la PCB
    gx0, gy0, gx1, gy1 = P(33.3, 34) + P(53.8, 48.8)
    out.append(f'  (polyline (pts (xy {mm(gx0)} {mm(gy0)}) (xy {mm(gx1)} {mm(gy0)}) (xy {mm(gx1)} {mm(gy1)}) '
               f'(xy {mm(gx0)} {mm(gy1)}) (xy {mm(gx0)} {mm(gy0)})) (stroke (width 0.2) (type dash) (color 0 132 0 1)) '
               f'(uuid {q(uid("guard"))}))')
    texts = [
        ((33.5, 33.5), 'Nodo GATE · anillo de guarda GND en la PCB', 1.0),
        ((1.5, 41), 'Piezo JLI-PZ001', 1.27),
        ((1.5, 42.6), 'interior -> J1.1 PIEZO_IN', 1.0),
        ((1.5, 44.2), 'exterior -> J1.2 PIEZO_GND', 1.0),
        ((22.0, 44.4), 'Cpar', 1.27),
        ((88.5, 23.5), 'Cable PU (longitud según aplicación)', 1.27),
        ((88.5, 25.3), '1 MIC = vivo (alimentación + audio)', 1.0),
        ((88.5, 27.6), '2 GND = malla', 1.0),
        ((66, RAIL + 3.5), 'J3 GND_AGUA: hilo MACIZO, no trenzado;', 1.0),
        ((66, RAIL + 5), 'paso sellado, solo el extremo al agua', 1.0),
        ((0, 11), 'HIDRÓFONO PIP v0.4 · cápsula única MACIZA en PU (sin aire, sin electrolíticos)', 1.8),
        ((0, 13.5), 'Amplificador JFET en fuente común con alimentación por la línea MIC (PIP). Banco: 3 V a través de 2,7 kΩ.', 1.27),
        ((0, 15.2), 'Nominales (no límites): S ≈ 0,30 V · MIC ≈ 1,92 V · ID ≈ 0,40 mA · ganancia ≈ -4,4 con carga AC total 1,1 kΩ.', 1.27),
        ((0, 58), 'Q1 2SK209 (SC-59): 1 = S, 2 = D, 3 = G.   D1 BAV199: 1 = A1 y 2 = K2 a GND, 3 = K1/A2 a GATE (diodos en antiparalelo).', 1.27),
        ((0, 59.7), 'C1 MLCC 22 µF X5R siempre conectado SOURCE-GND (sin JP1).   C2 47 pF C0G junto a Q1.   C3 = Cpar, C0G 1206, NO MONTAR por defecto.', 1.27),
        ((0, 61.4), 'Redes: /PIEZO_IN, /GATE, /SOURCE, /MIC, /GND (idénticas a la PCB). PIEZO_GND es el nombre del pad J1.2, unido a GND.', 1.27),
    ]
    for (x, y), t, size in texts:
        X, Y = P(x, y)
        out.append(f'  (text {q(t)} (at {mm(X)} {mm(Y)} 0) (effects (font (size {size} {size})) '
                   f'(justify left bottom)) (uuid {q(uid("t" + t))}))')
    out.append(f'  (sheet_instances (path "/" (page "1")))')
    out.append(')')
    open(os.path.join(KICAD, 'hidrofono_v04.kicad_sch'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')

    symlib = ['(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)']
    symlib += ['  ' + libsym(n, r, g, p) for n, (r, g, p) in SYMS.items()]
    symlib.append(')')
    open(os.path.join(KICAD, 'hidrofono.kicad_sym'), 'w', encoding='utf-8').write('\n'.join(symlib) + '\n')
    print('ok:', len(segs), 'cables,', len(junctions(segs)), 'uniones')


if __name__ == '__main__':
    main()
