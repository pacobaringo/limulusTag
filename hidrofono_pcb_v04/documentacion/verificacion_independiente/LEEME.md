# Verificación independiente de la v0.4 (sin KiCad)

Fecha: 2026-10-11. Comprobación del paquete `hidrofono_v04_proyecto.zip` hecha con scripts propios (Python, Shapely, Gerbonara 1.6.3). **No se ha podido ejecutar KiCad 9** en este entorno: la red bloquea el PPA de KiCad y Ubuntu 24.04 solo ofrece KiCad 7, que no abre archivos de KiCad 9. Los informes ERC/DRC de `../ERC_KiCad.txt` y `../DRC_KiCad.txt` son los del paquete original y no se han reproducido aquí.

| Script | Comprueba | Resultado |
|---|---|---|
| `edge.py` (Gerber) | Distancia del cobre al contorno Ø20 mm | F.Cu 0,911 mm (pad J3); B.Cu 0,800 mm (plano). Ambas ≥ 0,75 mm |
| `mask2.py` (Gerber) | Las 14 vías quedan sin tapar en las dos máscaras (anillo r = 0,33 mm) | 14/14 abiertas en F.Mask y 14/14 en B.Mask |
| `pcb.py` (`.kicad_pcb`) | Huellas, valores, atributos y pad→red | R1 220 Ω, R3 750 Ω, C1 22 µF X5R SOURCE–GND, C2 47 pF C0G MIC–GND, C3 (Cpar) DNP PIEZO_IN–GND, J3 GND_AGUA PTH, sin JP1. Q1 y D1 con la huella SOT‑23 estándar, rotada pero no reflejada |
| `clr.py` (`.kicad_pcb`) | Separación mínima entre cobre de redes distintas, distancia al borde, conectividad de cada red | 0,200 mm en F.Cu y 0,250 mm en B.Cu (regla: 0,20 mm). Las 5 redes son una sola isla cada una, sin conexiones pendientes. Separación mínima entre taladros: 0,81 mm |
| `schnet.py` (`.kicad_sch`) | Conectividad reconstruida desde los cables y etiquetas del esquema | 24 pines; coinciden exactamente con `netlist.xml` y con los pads de la PCB |

Además:
- **Anillo de guarda:** lazo cerrado de 0,30 mm en F.Cu, unido a GND a través de los pads D1.1 y D1.2, de sus vías al plano y de la vía en (95,5; 104,2). Dentro del lazo quedan R1.2, Q1.3, D1.3 y R2.1 (todo el nodo GATE). Fuera quedan R1.1 (PIEZO_IN) y R2.2 (GND). SOURCE y MIC salen del lazo por B.Cu. El nodo GATE mide unos 7 mm de pista en total.
- **Gerber:** el zip coincide byte a byte con `fabricacion/` y con `SHA256_Gerber.txt`. Los taladros son 14 × 0,30 mm PTH, 5 × 0,90 mm PTH y 2 × 1,20 mm NPTH.
- **Guía:** con el modelo IDSS = 2,5 mA y |VGS(off)| = 0,5 V, R3 = 750 Ω da ID = 0,40 mA, VS = 0,30 V, VD = 3 − 0,40 × 2,7 = 1,92 V y gm = 4 mS. La ganancia −4,4 corresponde a gm × 1,1 kΩ, siendo 1,1 kΩ la carga AC **total**; con una carga AC de 2,7 kΩ saldría −10,8. Los números son coherentes.

Discrepancias menores, sin efecto eléctrico:
- `hidrofono_v04.kicad_sch` está en formato `20230121` (KiCad 7), mientras el CHANGELOG dice que todos los archivos se guardaron en formato KiCad 9. KiCad 9 lo abre sin problema; al guardarlo una vez desde KiCad 9 queda homogéneo.
- Los patillajes de 2SK209 (1 = S, 2 = D, 3 = G) y de BAV199 (1 = A1, 2 = K2, 3 = K1/A2) no se han podido contrastar aquí con los PDF de Toshiba y Diodes, porque la red los bloquea. Coinciden con lo que declara el paquete y con fuentes secundarias. Antes de fabricar conviene mirar el dibujo SC‑59 de Toshiba.
- No se pueden comprobar las posiciones heredadas de la v0.3 (J1, J2, H1, H2) ni la estructura de la guía v0.3: los archivos v0.3 no vienen en el zip, solo sus SHA‑256.

Uso: `python3 clr.py ../../KiCad/hidrofono_v04.kicad_pcb .` (análogo para `pcb.py` y `schnet.py`); `python3 edge.py <gerber_cobre>`; `python3 mask2.py <gerber_mascara>`.
