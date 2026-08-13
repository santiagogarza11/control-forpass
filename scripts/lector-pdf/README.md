# Lector de las cotizaciones de póliza en PDF

Herramienta de un solo uso, **no es parte de la app**. `index.html` sigue sin
dependencias; esto es Python que corre a mano cuando hay que sacar datos de una
cotización hecha en Canva.

De aquí salieron los cuatro `docs/poliza-*.json`.

## Cómo se usa

Los PDF **no están en el repo** (traen precios de clientes). Por omisión se buscan
en `~/Downloads`; para otra carpeta:

```bash
POLIZAS_PDF=~/algun/lado python3 scripts/lector-pdf/generar.py
```

```bash
python3 scripts/lector-pdf/generar.py
```

Escribe `docs/poliza-<SITIO>.json` y al final imprime la verificación: renglones
originales, consolidados, equipos, anual limpio, total impreso y la diferencia.

Los nombres de archivo esperados están en el diccionario `ARCH` de
`consolidar.py`, junto con el total impreso de cada cotización, que es contra lo
que se verifica.

## Los tres archivos

| | |
|---|---|
| `leer.py` | lee el PDF: texto con posición, trazados rellenos, tabla de precios y calendario |
| `consolidar.py` | agrupa renglones, deduce cantidades escondidas y verifica sumas |
| `generar.py` | escribe los JSON con la forma del objeto `POLIZA` |

Cada uno corre solo para depurar:

```bash
python3 scripts/lector-pdf/leer.py "/ruta/Cotización Póliza Forguard_INOAC_FInal.pdf"
```

```bash
python3 scripts/lector-pdf/consolidar.py
```

## Lo que costó encontrar

Cinco cosas que no son obvias y que valen más que el código:

1. **Los meses del calendario no son texto.** Son trazados `m`/`l`/`h f` con color
   de relleno `(0.576, 0.702, 0.835)`. Ninguna extracción de texto los ve.
2. **La posición viene del CTM (`cm`) con su pila `q`/`Q`, no de `Tm`.** `Tm` solo
   trae la escala de la fuente y suele ser `16 0 0 16 0 0`. Si se lee de `Tm`, todo
   sale en (0,0).
3. **Los encabezados de columna se eligen por el renglón donde coinciden más.**
   "Concepto Cotizado:" del título también empieza con "Concepto", y tomando el
   primero que aparece la tabla no se encuentra nunca.
4. **El calendario abarca varias páginas** cuando hay muchos renglones. Se llavea
   por el número de renglón, no por el nombre: el nombre viene partido en dos
   líneas cuando es largo.
5. **`[` y `]` de los arreglos `TJ` no son operadores.** Tratarlos como tales borra
   la pila y se pierde casi todo el texto.

## Lo que encontró

- **MXGT01 trae un 5% de descuento escondido** en cada *Total Mtto*. Por eso su
  anual limpio sale $94,222.52 arriba del impreso.
- **MXNL02 tenía cantidades escondidas** en los totales, sin columna que las
  mostrara: refrigerador doble ×2, barra caliente eléctrica ×4, barra fría ×2,
  trampa de grasa ×2.
- **MXNL02 sale 80 centavos arriba** porque el PDF truncó los centavos de la
  báscula de recibo ($982.80 × 3 = $2,948.40, impreso como $2,948) y hay dos.
- **Huecos de numeración reales**: MXGT01 numera hasta 79 con 72 renglones (faltan
  44, 51, 69–73) y NGK hasta 19 con 17 (faltan 14, 18). Son filas borradas en Canva
  sin renumerar — la suma cuadra sin ellas.
- **Ningún equipo repetido tiene calendario distinto** en ninguna de las cuatro: el
  escalonado se hace por tipo de equipo, no por unidad.

## Cómo se validó

La extracción del calendario de INOAC salió idéntica a lo que Santiago describió de
memoria —barra fría, estufón, plancha y calentón en may; campana, extracción,
licuadora y lavaloza en jun; horno Rational en ago— sin haber usado esa
descripción para nada.
