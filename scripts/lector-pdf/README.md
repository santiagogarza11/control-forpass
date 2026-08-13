# Lector de las cotizaciones de póliza en PDF

**No es parte de la app.** `index.html` sigue sin dependencias; esto es Python que
corre a mano cuando hay que sacar los datos de una cotización hecha en Canva. Lo
que produce se mete al tablero con **Pólizas → Importar JSON**.

Es para el **rezago de cotizaciones viejas**. Las nuevas se capturan en la app: ahí
el tablero es la fuente y el PDF sale de él, no al revés.

## Cómo se usa

Con la ruta de un PDF, el que sea:

```bash
python3 scripts/lector-pdf/generar.py ~/Downloads/"Cotización Póliza Forguard_INOAC_FInal.pdf"
```

Escribe `docs/poliza-<SITIO>.json`. El cliente, el sitio y la fecha se leen de la
portada del PDF y **se imprimen para que los revises** — estas portadas se copian
de una cotización a otra y a veces traen el sitio de la anterior. Para corregir:

```bash
python3 scripts/lector-pdf/generar.py ruta.pdf --sitio MXNL03 --cliente "Mercado Libre" \
        --fecha "26 de junio 2026" --total 1855207.88
```

**No machaca un `docs/poliza-*.json` que ya exista**: se planta y te dice qué pasó.
Ese candado no es teórico — la portada de la cotización de Nexxus dice «MXGT01»
porque la copiaron, y sin él se habría llevado por delante la de MXGT01 en silencio.

Sin argumentos rehace las cuatro cotizaciones conocidas, las del diccionario `ARCH`
de `consolidar.py`, que traen su total impreso para verificarse contra él:

```bash
python3 scripts/lector-pdf/generar.py
```

Los PDF **no están en el repo** (traen precios de clientes). Las conocidas se
buscan en `~/Downloads`; para otra carpeta, `POLIZAS_PDF=~/algun/lado`.

`--help` lo resume todo.

## Lo que imprime al final

Dos cosas, separadas a propósito:

1. **La verificación de la extracción** — renglones, equipos, lo extraído contra el
   total impreso y la diferencia. Mide si el lector leyó bien el PDF.
2. **Las correcciones a mano** — con su motivo y cuánto mueven el anual. Se aplican
   *después* de la verificación, para que ésta siga midiendo la extracción y no se
   confunda "leí mal" con "el PDF estaba mal".

Cuando no se pasa `--total`, lo busca en el PDF (la cifra más cercana a la suma de
la columna *Total Mtto*, y solo si queda a menos del 1%). Si no lo encuentra, lo
dice: no se inventa un número contra el cual verificar.

## Los tres archivos

| | |
|---|---|
| `leer.py` | lee el PDF: texto con posición, trazados rellenos, tabla de precios y calendario. Es librería, no se corre solo |
| `consolidar.py` | agrupa renglones, deduce cantidades escondidas, verifica sumas y guarda las correcciones a mano |
| `generar.py` | la línea de comandos: lee la portada y escribe los JSON con la forma del objeto `POLIZA` |

```bash
python3 scripts/lector-pdf/consolidar.py     # detalle renglón por renglón de las cuatro
```

## Correcciones a mano

`CORRECCIONES` en `consolidar.py`, llaveada por **(sitio, número de renglón en el
papel)** para que se pueda ir a checar contra la cotización impresa.

La regla para tocar un renglón es estrecha a propósito: **solo cuando el documento
se contradice a sí mismo** —la columna de servicios al año dice una cosa y el
calendario dibujado dice otra—. Que el mismo equipo cueste distinto en dos clientes
**no** es un error: es un precio, y el renglón siempre manda. Por eso la licuadora
industrial de INOAC ($7,280 contra ~$919 en MXNL02 y NGK) sigue como está: huele
raro, pero el documento cuadra consigo mismo y con su total impreso.

Van en la tabla y no editando el JSON para que **sobrevivan a volver a leer el PDF**.

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
- **Dos renglones donde la cotización se contradice a sí misma** — están en
  `CORRECCIONES` con su motivo:
  - *MXGT01 #18, Cámara de congelación*: dice 3 servicios y trae 2 meses marcados.
    Único así en 72 renglones; su gemela y los 9 renglones de su bloque están en
    mar/jul/nov. Falta la marca de nov. El dinero no se mueve.
  - *MXNL02 #32, Segurista*: dice 1 servicio y trae 3 meses marcados. $27,000 no
    puede ser tarifa anual — el mismo concepto cuesta **$25,000 al mes** en MXGT01
    y en Nexxus, dos sitios hermanos. Se toma el calendario: 3. Sube el anual
    $54,000 y deja de cuadrar con el papel a propósito.
- **Existe una quinta cotización**, Mercado Libre **Nexxus** (26-jun-2026): 79
  renglones, $1,952,850.40 limpio contra $1,855,207.88 impresos — el **mismo 5%
  escondido** de MXGT01. Todavía **no** se carga; su portada además dice «MXGT01».

## Cómo se validó

La extracción del calendario de INOAC salió idéntica a lo que Santiago describió de
memoria —barra fría, estufón, plancha y calentón en may; campana, extracción,
licuadora y lavaloza en jun; horno Rational en ago— sin haber usado esa
descripción para nada.
