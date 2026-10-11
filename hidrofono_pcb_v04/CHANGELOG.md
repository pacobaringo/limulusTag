# Hidrófono PIP v0.4 - 11 octubre 2026

Base: versión 1 de hidrofono_v03_proyecto.zip y guia_pcb_hidrofono_v03.pdf. La revisión v0.3 se conserva sin sobrescribir.

## Esquema y BOM
- R1: 10 kΩ → 220 Ω, 1 %, thin film 1206 (YAGEO RT1206FRE07220RL).
- R3: 360 Ω → 750 Ω, 1 %, 1206 (YAGEO RC1206FR-07750RL).
- Sustituido el electrolítico EEE-FK0J470R por C1 MLCC 22 µF X5R, 16 V, 1206 (TDK C3216X5R1C226M160AB, ≥6,3 V), permanentemente SOURCE-GND. Eliminado JP1 y la red CAP_POS.
- Añadido C2 47 pF C0G, 50 V, 0603 (KEMET C0603C470J5GACTU), MIC-GND, junto a Q1.
- Añadido Cpar en paralelo PIEZO_IN-GND, 1206 C0G, DNP. Su referencia KiCad es C3 para evitar la anotación inválida de una referencia sin número; campo Alias=Cpar y serigrafía Cpar. Valor y MPN por definir tras ensayo.
- P+ / P- pasan a PIEZO_IN / PIEZO_GND. J1.1=interior→R1; J1.2=exterior→GND. PIEZO_GND es un nombre de conexión de la misma red GND, no una masa separada.
- Añadido J3.1, PTH GND_AGUA a GND. J2.1 MIC, J2.2 GND; TP1 SOURCE.
- Q1 verificado visualmente con el dibujo Toshiba SC-59: 1=S, 2=D, 3=G. D1 verificado con el esquema interno Diodes BAV199: 1=A1, 2=K2, 3=K1/A2. Con 1 y 2 a GND y 3 a GATE, los diodos limitan en antiparalelo. Sin permuta de pines ni corrección del símbolo/huella por patillaje.

## PCB y fabricación
- Conservados Ø20 mm, FR4 1 mm, dos caras, los cuatro pads PTH J1/J2 de borde y los dos NPTH H1/H2 Ø1,2 mm de anclaje en sus posiciones v0.3.
- Retiro mínimo de cobre al contorno: 0,75 mm en ambas caras, incluidos pads, pistas, vías y relleno. Límite del plano B.Cu a radio 9,20 mm.
- 14 vías Ø0,3 mm sin tenting, con apertura de máscara en ambas caras; 5 pads PTH Ø0,9 mm. Taladros de fabricación separados PTH/NPTH.
- Anillo cerrado GND de 0,30 mm alrededor de la puerta. MIC y SOURCE cruzan su perímetro por B.Cu; GATE permanece corto en F.Cu. R2 se desplaza a (100;102,8) mm y TP1 a (103,2;101,5) mm.
- Eliminadas las huellas antiguas C1/JP1. Añadidos símbolos y huellas locales, marcado DNP nativo de C3, netlist, BOM y mapa de pads.
- Serigrafía redistribuida para dejar libres las vías abiertas. Mantenidas las marcas de pin 1 de Q1/D1. Las vistas de PCB no representan componentes montados.
- Archivos finales guardados en formato KiCad 9 para representar explícitamente tenting por vía y DNP y ejecutar ERC/DRC con comprobación esquema-PCB. Abrir con KiCad 9 o posterior.
- ERC/DRC KiCad 9.0.9: cero errores, cero avisos, cero conexiones pendientes y cero problemas de paridad; sin exclusiones. Gerber y Excellon revisados con Gerbonara.

## Guía y encapsulado
- Conservada la estructura de cuatro páginas: cápsula/PCB, componentes y montaje, pedido/pruebas, conexiones.
- Banco DC 3 V / 2,7 kΩ: S≈0,30 V, MIC≈1,92 V, ID≈0,40 mA; referencias nominales, no límites. Ganancia≈-4,4 con carga AC 1,1 kΩ y C1 efectivo. Una carga AC de 2,7 kΩ produciría otra ganancia (modelo ideal≈-10,8).
- Electrodos definidos por ubicación: interior PIEZO_IN; exterior GND. Soldadura Sn62Pb36Ag2, contacto breve; hilos del piezo cortos.
- Hilo de masa al agua MACIZO, no trenzado, con paso sellado. Cable de cubierta PU y longitud según aplicación.
- Cápsula única completamente maciza en PU, sin aire/cavidades intencionadas y sin electrolíticos. Rellenar y desgasificar bajo los componentes, el interior del cilindro y los taladros; validar el proceso de curado y la respuesta final.
- 1000 m se documentan como objetivo pendiente de selección/validación del PU, cable, cerámica, MLCC y conjunto. No se acredita aptitud a presión solo con diseño eléctrico o relleno macizo; requiere ensayo hidrostático y acústico. No se han realizado ensayos físicos.

## Verificación independiente (añadida al subir al repositorio)
- Recomprobados sin KiCad, a partir de los archivos: retiro de cobre (F.Cu 0,91 mm, B.Cu 0,80 mm), 14/14 vías sin tapar en ambas máscaras, separaciones ≥0,20 mm, conectividad de las 5 redes, anillo de guarda cerrado alrededor de GATE, y esquema = netlist = PCB (24 pines). Detalle y scripts en `documentacion/verificacion_independiente/`.
- Pendiente: reproducir ERC/DRC con KiCad 9 (no disponible en el entorno de verificación) y contrastar los patillajes con los PDF de Toshiba y Diodes.
