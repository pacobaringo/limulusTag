# Hidrófono PIP v0.4 - cápsula maciza

Abrir `KiCad/hidrofono_v04.kicad_pro` con KiCad 9 o posterior. Símbolos y huellas locales incluidos. Leer `guia_pcb_hidrofono_v04.pdf` antes de montar. Los SVG/PNG son vistas de consulta, no archivos de fabricación.

## Fabricación y montaje
Subir únicamente `hidrofono_v04_Gerber.zip` al fabricante: siete capas Gerber y Excellon PTH/NPTH. Placa Ø20 mm, FR4 1,0 mm, dos caras, 1 oz. Vías SIN tapar, sin relleno de fábrica; máscaras abiertas en ambas caras. Retiro de cobre ≥0,75 mm. Sin ensamblaje automático; montar manualmente según BOM.csv. C1 y C2 se montan; C3/Cpar NO se monta por defecto. JP1 no existe.

## Conexiones
J1.1 PIEZO_IN al electrodo interior; J1.2 PIEZO_GND al exterior (red GND). J2.1 MIC al vivo del cable; J2.2 GND a malla. J3.1 GND_AGUA a hilo MACIZO con paso sellado y extremo en contacto con agua. TP1 mide SOURCE. No hay batería ni ADC en esta placa. Mantener cortos los hilos de la cerámica y elegir longitud/cubierta PU del cable según la aplicación. H1/H2 son anclajes NPTH; no sustituyen un alivio de tracción.

AudioMoth TRS: punta MIC, cuerpo GND, anillo libre. Para iPhone, usar en superficie TRS→TRRS CTIA y adaptador Apple con entrada de micrófono: cuerpo TRRS MIC, segundo anillo GND. Medir alimentación, detección y señal del receptor real antes de encapsular.

## Prueba y encapsulado
Banco DC: 3 V en serie con 2,7 kΩ hacia MIC. Nominales del modelo típico: S≈0,30 V, MIC≈1,92 V, ID≈0,40 mA; no límites. Ganancia nominal≈-4,4 con carga AC 1,1 kΩ y bypass efectivo. En banco con carga AC 2,7 kΩ la ganancia ideal sería≈-10,8.

PU macizo: llenar interior de la cerámica, bajo componentes, ambas caras y taladros, desgasificando y curando según la formulación elegida. No lleva electrolíticos, cámaras de aire ni cavidades intencionadas. Calibrar después del encapsulado. El objetivo de 1000 m requiere ensayo de presión del conjunto (orden de 10 MPa adicionales); no es una profundidad certificada en esta entrega.

## Comprobación
ERC/DRC y paridad esquema-PCB en documentacion. Sin exclusiones. BOM, netlist, mapa de pads, comprobación de Gerber/máscara y registro de cambios incluidos. Las pruebas electrónicas, de protección, de acústica, de compatibilidad Apple y de presión aún no se han realizado. R1=220 Ω reduce la limitación de corriente frente a v0.3; verificar los impulsos antes de usar un receptor definitivo.
