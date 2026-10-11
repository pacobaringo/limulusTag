#!/usr/bin/env python3
"""Genera la ilustración de conexiones de la cápsula v0.4.

Salida: conexiones_v04.svg (autocontenido). Para PDF/PNG, abrir el SVG con
Chromium en modo headless (ver LEEME de verificacion_independiente).
La PCB se dibuja a partir de gerber_top.png (campo 21 mm centrado en el
contorno) y los pads en sus coordenadas reales de la PCB.
"""
import base64, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = base64.b64encode(open(os.path.join(HERE, 'gerber_top.png'), 'rb').read()).decode()

CX, CY, S = 100.0, 110.0, 3.4          # centro de la PCB en el papel (mm) y escala
R_IN = 11.0 * S                        # interior del piezo: Ø22 mm
R_OUT = R_IN + 6.5                     # espesor del cerámico: NO a escala

COL = {'in': '#c62828', 'gnd': '#263238', 'mic': '#1565c0', 'agua': '#2e7d32',
       'ink': '#1b2a33', 'muted': '#55636d', 'warn': '#b26a00'}


def P(x, y):
    return CX + (x - 100) * S, CY + (y - 100) * S


def polar(r, deg):
    a = math.radians(deg)
    return CX + r * math.cos(a), CY + r * math.sin(a)


def path(pts, color, w=0.8, dash=None):
    d = 'M ' + ' L '.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"{da}/>')


def dot(x, y, color, r=1.1):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="#fff" stroke="{color}" stroke-width="0.6"/>'


def text(x, y, s, size=3.0, color=None, weight=400, anchor='start'):
    color = color or COL['ink']
    out = []
    for i, line in enumerate(s.split('\n')):
        out.append(f'<text x="{x:.2f}" y="{y + i * size * 1.3:.2f}" font-size="{size}" fill="{color}" '
                   f'font-weight="{weight}" text-anchor="{anchor}">{line}</text>')
    return '\n'.join(out)


def leader(pts, color=COL['muted']):
    return path(pts, color, 0.3) + f'<circle cx="{pts[0][0]:.2f}" cy="{pts[0][1]:.2f}" r="0.6" fill="{color}"/>'


def main():
    o = []
    o.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             'width="297mm" height="210mm" viewBox="0 0 297 210" '
             'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
    o.append('<defs><clipPath id="pcb"><circle cx="%.2f" cy="%.2f" r="%.2f"/></clipPath>'
             '<pattern id="pu" width="3" height="3" patternUnits="userSpaceOnUse">'
             '<rect width="3" height="3" fill="#e3f2ef"/><circle cx="1.5" cy="1.5" r="0.25" fill="#9cc9c0"/></pattern>'
             '</defs>' % (CX, CY, 10 * S))
    o.append('<rect width="297" height="210" fill="#ffffff"/>')
    o.append(text(12, 16, 'Hidrófono PIP v0.4 · conexiones de la cápsula maciza', 6.0, weight=700))
    o.append(text(12, 23, 'Ilustración de montaje. La PCB es la vista real de los Gerber (cara superior) a escala ×3,4; '
                  'el resto no está a escala.', 3.0, COL['muted']))

    # ---------------- Panel A: vista axial -----------------------------------
    o.append(text(12, 34, 'A · Vista desde el extremo del cilindro (PCB dentro del piezo)', 3.6, weight=700))
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{(R_IN + R_OUT) / 2:.2f}" fill="none" stroke="#d8c09a" '
             f'stroke-width="{R_OUT - R_IN:.2f}"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R_IN:.2f}" fill="url(#pu)"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R_IN:.2f}" fill="none" stroke="#8d99a6" stroke-width="0.9"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R_OUT:.2f}" fill="none" stroke="#8d99a6" stroke-width="0.9"/>')
    img = 21 * S
    o.append(f'<image x="{CX - img / 2:.2f}" y="{CY - img / 2:.2f}" width="{img:.2f}" height="{img:.2f}" '
             f'clip-path="url(#pcb)" xlink:href="data:image/png;base64,{PNG}" href="data:image/png;base64,{PNG}"/>')

    j11, j12 = P(92.5, 98.0), P(92.5, 102.0)
    j21, j22 = P(107.5, 98.5), P(107.5, 101.5)
    j3, tp1 = P(98.5, 92.0), P(103.2, 101.5)
    h1, h2 = P(103.0, 106.0), P(106.0, 105.0)

    # Electrodo interior -> J1.1 (corto, por dentro)
    ein = polar(R_IN, 196)
    o.append(path([j11, (j11[0] - 4, j11[1] - 1.5), ein], COL['in'], 1.0))
    o.append(dot(*ein, COL['in']))
    # Electrodo exterior -> J1.2 (pasa por encima del borde del cilindro)
    eout = polar(R_OUT, 160)
    mid_in = polar(R_IN - 0.5, 166)
    o.append(path([j12, (j12[0] - 4, j12[1] + 1), mid_in], COL['gnd'], 1.0))
    o.append(path([mid_in, eout], COL['gnd'], 1.0, '1.4 0.9'))
    o.append(dot(*eout, COL['gnd']))
    # Cable: J2.1 MIC (vivo) y J2.2 GND (malla), sale por el extremo hacia la superficie
    cab = polar(R_IN - 2, 2)
    o.append(path([j21, (j21[0] + 3, j21[1]), (cab[0], cab[1] - 1.2)], COL['mic'], 1.0))
    o.append(path([j22, (j22[0] + 3, j22[1]), (cab[0], cab[1] + 1.2)], COL['gnd'], 1.0))
    o.append(f'<circle cx="{cab[0]:.2f}" cy="{cab[1]:.2f}" r="3.2" fill="#6d7b86" stroke="#37474f" stroke-width="0.5"/>')
    o.append(f'<circle cx="{cab[0]:.2f}" cy="{cab[1]:.2f}" r="1.6" fill="#cfd8dc"/>')
    # Hilo GND_AGUA macizo desde J3: sale por el extremo, sellado
    wout = polar(R_IN - 3, 262)
    o.append(path([j3, (j3[0], j3[1] - 3), wout], COL['agua'], 1.3))
    o.append(f'<circle cx="{wout[0]:.2f}" cy="{wout[1]:.2f}" r="2.0" fill="#a5d6a7" stroke="{COL["agua"]}" stroke-width="0.5"/>')
    for p, c in ((j11, COL['in']), (j12, COL['gnd']), (j21, COL['mic']), (j22, COL['gnd']), (j3, COL['agua'])):
        o.append(f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="2.3" fill="none" stroke="{c}" stroke-width="0.7"/>')

    # Rótulos panel A (izquierda)
    o.append(leader([ein, (52, 84), (47, 84)]))
    o.append(text(12, 85, 'J1.1 PIEZO_IN', 3.3, COL['in'], 700))
    o.append(text(12, 89.5, 'Electrodo INTERIOR (cara de\ndentro del cilindro) → R1.\nHilo corto, por el interior.', 2.7))
    o.append(leader([eout, (52, 120), (47, 120)]))
    o.append(text(12, 121, 'J1.2 PIEZO_GND', 3.3, COL['gnd'], 700))
    o.append(text(12, 125.5, 'Electrodo EXTERIOR → GND.\nPasa por encima del borde\ndel cilindro (trazo a rayas).', 2.7))
    o.append(text(12, 143, 'Soldar con Sn62Pb36Ag2,\ncontacto breve, sin calentar\nla cerámica. Hilos cortos.', 2.7, COL['muted']))
    # Rótulos panel A (derecha)
    RX = 152
    o.append(leader([(wout[0] + 2, wout[1]), (RX - 4, 60), (RX - 1, 60)]))
    o.append(text(RX, 61, 'J3 GND_AGUA', 3.2, COL['agua'], 700))
    o.append(text(RX, 65.5, 'Hilo MACIZO, no trenzado. Paso\nsellado en el PU; solo el extremo\nen contacto con el agua.', 2.6))
    guard = P(97.0, 97.0)
    o.append(leader([guard, (RX - 4, 84), (RX - 1, 84)]))
    o.append(text(RX, 85, 'Anillo de guarda GND (F.Cu)', 3.0, weight=700))
    o.append(text(RX, 89.3, 'Rodea el nodo GATE (R1.2, Q1.3,\nD1.3, R2.1). Limpiar y secar esa\nzona antes de encapsular.', 2.6))
    o.append(leader([(cab[0] + 3.2, cab[1]), (RX - 4, 108), (RX - 1, 108)]))
    o.append(text(RX, 109, 'Cable con cubierta de PU', 3.0, weight=700))
    o.append(text(RX, 113.3, 'J2.1 MIC = vivo (alim. + audio)\nJ2.2 GND = malla\nLongitud según aplicación;\nalivio de tracción aparte.', 2.6))
    o.append(leader([tp1, (RX - 4, 136), (RX - 1, 136)]))
    o.append(text(RX, 137, 'TP1 / S: fuente del JFET', 3.0, weight=700))
    o.append(text(RX, 141.3, 'Banco 3 V vía 2,7 kΩ: S ≈ 0,30 V,\nMIC ≈ 1,92 V (nominales).', 2.6))
    o.append(leader([h2, (RX - 4, 154), (RX - 1, 154)]))
    o.append(leader([h1, (RX - 4, 154)]))
    o.append(text(RX, 155, 'H1 / H2: anclajes NPTH', 3.0, weight=700))
    o.append(text(RX, 159.3, 'Sin conexión eléctrica; el PU los\natraviesa. No son alivio de tracción.', 2.6))

    # Aviso de serigrafía
    silk = P(95.8, 105.6)
    o.append(leader([silk, (96, 166), (96, 168)], COL['warn']))
    o.append(f'<rect x="11" y="168" width="132" height="22" rx="1.5" fill="#fff6e5" stroke="{COL["warn"]}" stroke-width="0.4"/>')
    o.append(text(14, 173.5, '⚠ Serigrafía de la PCB: los textos «PIEZO_GND / PIEZO_IN» están debajo de J1,', 2.8, COL['warn'], 700))
    o.append(text(14, 177.5, 'apilados en orden INVERSO al de los pads. Guiarse por la posición del pad:\n'
                  'pad SUPERIOR (junto a R1) = J1.1 PIEZO_IN → electrodo interior;\n'
                  'pad INFERIOR (junto a D1) = J1.2 PIEZO_GND → electrodo exterior. Comprobar con polímetro.', 2.7))

    # ---------------- Panel B: corte lateral ---------------------------------
    bx = 207
    o.append(text(bx, 34, 'B · Corte lateral de la cápsula (sin escala)', 3.6, weight=700))
    o.append(f'<rect x="{bx}" y="50" width="83" height="76" rx="9" fill="url(#pu)" stroke="#7fb7ad" stroke-width="0.5"/>')
    for x in (bx + 16, bx + 64):
        o.append(f'<rect x="{x}" y="62" width="6" height="52" fill="#d8c09a" stroke="#8d99a6" stroke-width="0.4"/>')
    o.append(f'<line x1="{bx + 22}" y1="62" x2="{bx + 22}" y2="114" stroke="#8d99a6" stroke-width="0.9"/>')
    o.append(f'<line x1="{bx + 64}" y1="62" x2="{bx + 64}" y2="114" stroke="#8d99a6" stroke-width="0.9"/>')
    o.append(f'<line x1="{bx + 16}" y1="62" x2="{bx + 16}" y2="114" stroke="#8d99a6" stroke-width="0.9"/>')
    o.append(f'<line x1="{bx + 70}" y1="62" x2="{bx + 70}" y2="114" stroke="#8d99a6" stroke-width="0.9"/>')
    o.append(f'<rect x="{bx + 24}" y="102" width="38" height="2.4" fill="#2e6b45"/>')
    for x, w in ((bx + 30, 4), (bx + 38, 3), (bx + 46, 4), (bx + 54, 3)):
        o.append(f'<rect x="{x}" y="99.6" width="{w}" height="2.4" fill="#37474f"/>')
    # piezo interior -> J1.1 (corto)
    o.append(path([(bx + 22, 94), (bx + 26, 94), (bx + 26, 102)], COL['in'], 0.9))
    # piezo exterior -> J1.2 (por encima del borde)
    o.append(path([(bx + 16, 76), (bx + 12, 76), (bx + 12, 57), (bx + 28, 57), (bx + 28, 102)], COL['gnd'], 0.9))
    # cable
    o.append(path([(bx + 58, 102), (bx + 58, 76), (bx + 52, 66), (bx + 52, 40)], '#6d7b86', 2.8))
    o.append(path([(bx + 58, 102), (bx + 58, 76), (bx + 52, 66), (bx + 52, 40)], COL['mic'], 0.6))
    # hilo de agua
    o.append(path([(bx + 40, 102), (bx + 40, 46)], COL['agua'], 1.1))
    o.append(f'<circle cx="{bx + 40}" cy="46" r="1.1" fill="{COL["agua"]}"/>')
    for i in range(3):
        y = 40 + i * 2.2
        o.append(f'<path d="M {bx + 34} {y} q 1.5 -1.2 3 0 t 3 0 t 3 0 t 3 0" fill="none" stroke="#4fa3d1" stroke-width="0.4"/>')
    o.append(text(bx + 2, 42, 'GND_AGUA: extremo\nexpuesto, paso sellado', 2.5, COL['agua']))
    o.append(text(bx + 55, 41, 'cable PU → superficie', 2.5))
    o.append(text(bx + 3, 120, 'PU macizo: dentro del cilindro, bajo componentes,\nen vías y taladros. Sin aire ni electrolíticos.', 2.5, '#2b6b61'))
    o.append(text(bx + 43, 109, 'PCB Ø20 mm en Ø22 mm', 2.3, '#2e6b45', anchor='middle'))
    o.append(text(bx + 1, 132, 'Interior del piezo → J1.1 · exterior → J1.2.', 2.5))

    # Leyenda
    ly = 145
    o.append(text(bx, ly, 'Leyenda de hilos', 3.2, weight=700))
    for i, (c, lab) in enumerate(((COL['in'], 'PIEZO_IN · electrodo interior → J1.1'),
                                   (COL['gnd'], 'GND / PIEZO_GND · exterior → J1.2; malla → J2.2'),
                                   (COL['mic'], 'MIC · vivo del cable → J2.1'),
                                   (COL['agua'], 'GND_AGUA · hilo macizo → J3.1'))):
        y = ly + 6 + i * 5
        o.append(path([(bx, y - 1), (bx + 10, y - 1)], c, 1.2))
        o.append(text(bx + 13, y, lab, 2.7))
    o.append(text(bx, ly + 30, 'Redes y pads según la netlist v0.4\n(/PIEZO_IN, /GATE, /SOURCE, /MIC, /GND).', 2.5, COL['muted']))
    o.append(text(12, 200, 'Medusa IoT · Hidrófono PIP v0.4 · 1000 m es objetivo de diseño pendiente de ensayo hidrostático, '
                  'no una capacidad certificada.', 2.6, COL['muted']))
    o.append('</svg>')
    open(os.path.join(HERE, 'conexiones_v04.svg'), 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    print('ok')


if __name__ == '__main__':
    main()
