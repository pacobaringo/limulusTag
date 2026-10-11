# Fuentes y trazabilidad - PIP v0.4

Consultadas el 11 de octubre de 2026. Los enlaces son referencias; las fichas completas no se redistribuyen.

## Base del diseño
- `hidrofono_v03_proyecto.zip`, versión 1: proyecto KiCad, símbolos, huellas y guía de partida. Se conservan identidades y pines de los componentes existentes cuando corresponde.
- `guia_pcb_hidrofono_v03.pdf`, versión 1: estructura de cuatro páginas, dimensiones y montaje de partida.
- La revisión sigue los valores y conexiones indicados en la solicitud v0.4. C3 es la referencia válida KiCad de la huella solicitada Cpar, con alias y serigrafía Cpar.

## Encapsulados y patillajes (dibujos inspeccionados)
- [Toshiba, 2SK209, datasheet y dibujo SC-59](https://toshiba.semicon-storage.com/info/2SK209_datasheet_en_20140301.pdf?did=19662&prodName=2SK209). Página 1: 1 Source, 2 Drain, 3 Gate. La huella mantiene 1=S, 2=D, 3=G; Q1 está rotado 180° en esta PCB.
- [Diodes Incorporated, BAV199, circuito interno y SOT-23](https://www.diodes.com/datasheet/download/BAV199.pdf), [ruta alternativa de la ficha](https://www.diodes.com/assets/Datasheets/ds30232.pdf). Página 1, par en serie: 1 ánodo inicial, 2 cátodo final, 3 unión entre diodos (K1/A2). En esta aplicación, 1 y 2 a GND, 3 a puerta: protección antiparalela. La huella y el símbolo v0.3 coinciden; no se permutan pines. El BAV199 no equivale a unir los pines 1 y 2 a sus dos ánodos.

## Componentes seleccionados
- [TDK C3216X5R1C226M160AB, ficha de producto](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3216X5R1C226M160AB): C1, 22 µF ±20 %, X5R, 16 V, 1206; altura nominal 1,6 mm. [Hoja de características](https://product.tdk.com/en/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c3216x5r1c226m160ab.pdf).
- [KEMET C0603C470J5GACTU, ficha](https://search.kemet.com/component-documentation/download/specsheet/C0603C470J5GACTU): C2, 47 pF ±5 %, 50 V, C0G, 0603.
- [YAGEO RC1206FR-07750RL, ficha](https://yageogroup.com/component-documentation/download/specsheet/RC1206FR-07750RL): R3, 750 Ω, 1 %, 0,25 W, 1206.
- [YAGEO serie RT, ejemplo RT1206FRE0730KL](https://www.yageogroup.com/component-documentation/download/specsheet/RT1206FRE0730KL): confirma tecnología thin film y dimensiones de la serie 1206. Es una ficha de otro valor y NO el componente que se monta. R1 de la BOM es RT1206FRE07220RL (220 Ω, 1 %, thin film, 1206); la ficha individual del fabricante no estuvo accesible en esta consulta. Confirmar el MPN y su hoja de especificaciones al comprar; no sustituir por el ejemplo de 30 kΩ.
- C3/Cpar: huella 1206 C0G, DNP, sin valor ni MPN elegido. No se ha añadido a la compra de componentes a montar.

## Instrumentación y fabricación
- [KiCad 9, CLI oficial](https://docs.kicad.org/9.0/en/cli/cli.html): ERC, DRC con paridad esquema-PCB, netlist, Gerber, taladros y SVG.
- [Open Acoustic Devices, nota de piezos e hidrófonos](https://github.com/OpenAcousticDevices/Application-Notes/blob/master/Using_AudioMoth_with_Piezoelectric_Hydrophones_and_Contact_Microphones/Using_AudioMoth_with_Piezoelectric_Hydrophones_and_Contact_Microphones.pdf): arquitectura de hidrófono PIP de referencia. La carga AC de 1,1 kΩ y los nominales de la guía corresponden al modelo indicado en la solicitud; comprobar el receptor real.

## Alcance
Las fichas citadas no califican esta cápsula completa para 1000 m. El PU macizo y el cable requieren selección, proceso validado y ensayo hidrostático. La revisión no incluye un molde, una formulación de PU ni una calibración acústica; son trabajos posteriores a la validación eléctrica.
