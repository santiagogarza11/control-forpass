# Especificación medida del documento de póliza

Medidas **sacadas de las cuatro cotizaciones reales**, no estimadas. Lo que no se
puede sacar del archivo está marcado **«no extraíble»** en vez de rellenarse con
un número plausible.

Herramienta: MuPDF (el mismo motor de `pdffonts`/`pdfinfo`/`pdftotext`), porque
esta Mac no tiene Homebrew ni poppler. Entorno aislado en el scratchpad, nada se
instaló en el proyecto.

---

## Lo primero, porque cambia todas las demás cifras

Las cuatro declaran la página de **1275 × 1650**. Eso no es un tamaño raro: es
**Carta a 150 DPI exactos** (1275/150 = 8.5″, 1650/150 = 11″). El documento se
diseñó en píxeles y se exportó 1:1 a unidades de PDF.

> **Todo el archivo está a escala 2.0833×.** Para tener puntos reales sobre Carta
> hay que dividir entre 150/72. Todas las medidas de abajo ya vienen divididas.

Sin esa corrección, el cuerpo de la tabla parece de 15 pt cuando en realidad es de
**7.2 pt**.

---

## Página

| | Valor | |
|---|---|---|
| MediaBox declarado | 1275 × 1650 | idéntico en las 4 y en todas sus hojas |
| Tamaño real | **Carta, 612 × 792 pt** (8.5 × 11 in) | a 150 DPI |
| Rotación | 0 | |
| Hojas | MXNL02 6 · MXGT01 10 · INOAC 5 · NGK 5 | |
| Productor | `macOS Version 15.2 / 15.6.1` | **no es exportación directa de Canva** |

Ese último renglón importa: **los PDF se reimprimieron por macOS**, así que son un
registro con pérdida del diseño original. Se nota sobre todo en las fuentes.

---

## Fuentes — el dato menos confiable del archivo

| Cotización | Fuentes incrustadas |
|---|---|
| MXNL02 | Helvetica, Helvetica-Bold, Helvetica-Oblique |
| MXGT01 | Helvetica, Helvetica-Bold, Helvetica-Oblique |
| NGK | Helvetica, Helvetica-Bold, Helvetica-Oblique |
| **INOAC** | **Poppins-Regular, Poppins-Bold, Poppins-Medium, Poppins-Italic** + Helvetica |

**Tres de las cuatro perdieron la tipografía al reimprimirse** y quedaron en
Helvetica. Solo INOAC conserva Poppins. Además, cada archivo trae **una Helvetica
sin incrustar**, que el lector sustituye por su cuenta.

Conclusión: **la tipografía de diseño es no extraíble de tres de los cuatro
archivos.** Lo único que sí se puede afirmar es que **Poppins está en el diseño
original**, porque INOAC lo demuestra. De **Inter no hay rastro en ninguno** — es
elección del autor de la plantilla, no del documento original.

### Tamaños en pt reales

| Elemento | pt | Aparece en |
|---|---|---|
| Título de portada («Cotización» / «Póliza de» / «Mtto Prev.») | **72.0** | las 4 |
| Cifra grande | **31.7** | las 4 |
| Tagline «Sostenemos a los que sostienen todo.» | **8.2** | las 4 |
| Cuerpo de tabla — concepto y marca | **7.2** | las 4 |
| Cuerpo de tabla — cifras (precio, frecuencia, total) | **6.2** | las 4 |
| Etiquetas de portada («Cliente», «Fecha») | **6.7** | las 4 |
| Texto fino | **5.8** | las 4 |
| Intermedio | **7.7** | las 4 |

Interlineado declarado: **no extraíble.** El PDF guarda posiciones absolutas de
línea, no `line-height`. Lo que sí se midió es el paso entre filas (abajo).

---

## Márgenes

**Un PDF no guarda márgenes.** Lo de abajo es dónde *empieza y termina lo dibujado*,
medido — que es lo más cercano que existe.

| Hoja | Izquierda | Derecha | Superior | Inferior |
|---|---|---|---|---|
| Portada | **145.6** | 50.6 | 280.6 · *338.8 en MXNL02* | 36.8 |
| Contenido (texto) | **119.6 – 120.1** | 47.0 – 50.6 | **59.4** · *84.0 en MXNL02* | 18.5 |

Dos avisos:

- Esos números son de **texto**. La **tinta** empieza antes: hay un elemento navy
  en la esquina superior izquierda que arranca en **x = 38.0 pt**. Si el CSS se
  cuadra a 120 pt, la decoración de la esquina se sale.
- **MXNL02 va corrida**: su portada arranca 58 pt más abajo y su contenido 25 pt
  más abajo que las otras tres. No es error de medición, es otra plantilla.

Anclaje fijo, **idéntico en las cuatro**: el tagline en `x = 420.4, y = 747.0` y el
título de portada en `x = 145.6`.

---

## Tabla de renglones

| | Valor |
|---|---|
| **Paso entre filas** | **21.53 pt** · *21.15 en INOAC* |
| Reglas horizontales | 24 por hoja, al mismo paso — la retícula es real |
| **Reglas verticales** | **ninguna** |
| Primera fila | y ≈ **183.5** · *189.7 en MXNL02 y NGK* |
| Última fila observada | y ≈ **657.1** |
| **Máximo de filas por hoja** | **23** (medido en MXGT01 hoja 3) |
| Pie: «Precio más Iva.» | y = 762.6 |
| Pie: tagline | y = 774.5 |

**Ancho de columna: no extraíble.** No hay una sola regla vertical dibujada, así que
el archivo no dice dónde empieza ni termina una celda. Lo único medible es **dónde
arranca el texto de cada columna**, que es lo que va abajo.

### Y aquí está el hallazgo grande: las cuatro NO comparten columnas

| Cotización | Columnas, con la x donde arranca cada una |
|---|---|
| **MXNL02** | `#`@132 · Concepto@194 · **Marca**@311 · Precio Unitario@389 · Frecuencia@468 · Total Mtto@527 |
| **MXGT01** | `#`@132 · Concepto@194 · **Marca**@311 · Precio Unitario@389 · Frecuencia@468 · Total Mtto@527 |
| **INOAC** | `#`@132 · Concepto@206 · **Cantidad**@314 · Precio Unitario@375 · Frecuencia@450 · Total Mtto@509 |
| **NGK** | `#`@132 · Concepto@194 · **Cantidad**@284 · Precio Unitario@332 · **Total**@408 · Frecuencia@458 · Total Mtto@517 |

Tres formatos distintos en cuatro documentos:

- MXNL02 y MXGT01 traen **Marca y no Cantidad** — por eso hubo que deducir las
  cantidades escondidas de los totales.
- INOAC trae **Cantidad y no Marca**.
- NGK trae **siete columnas**, con un *Total* extra entre Precio y Frecuencia.

**No existe «el formato actual».** Hay que elegir uno, y la elección es de negocio.
Lo único común a las cuatro es `#`@132 y que *Total Mtto* cierra a la derecha.

---

## Calendario

| | Valor |
|---|---|
| Columnas | 12 |
| Paso horizontal | **24.3 pt** · *24.6 en INOAC* |
| Ancho total de la rejilla | 257 – 264 pt |
| Celda marcada | **23.5 × 22.3 pt** · *23.8 × 18.0 en INOAC* |
| Paso vertical | 22.3 pt · *18.0 en INOAC* |
| Color de la celda marcada | **`#8BB4D8`** |
| x de la primera columna | 231–269, cambia con el ancho de la columna de concepto |

---

## Colores, del vector

Estos **no** están muestreados de un JPEG: salen del relleno declarado en el
contenido, así que no traen desplazamiento de color.

| Color | Cobertura | Dónde |
|---|---|---|
| **`#002369`** | la dominante en las 4 | fondo de portada y bloques navy |
| `#031649` | una capa completa | navy más profundo |
| `#8BB4D8` | 0.5% | celda marcada del calendario |

> **El navy real es `#002369`, exactamente el de marca.** Queda confirmado que
> `#08194B` de la plantilla estaba mal, y ya no por lo que diga `CLAUDE.md` sino
> medido en los cuatro documentos.

---

## Resumen de lo no extraíble

| Dato | Por qué |
|---|---|
| Márgenes de diseño | el PDF no guarda el concepto; solo se puede medir dónde cae la tinta |
| Anchos de columna | no hay reglas verticales dibujadas |
| Interlineado (`line-height`) | solo hay posiciones absolutas de línea |
| Tipografía original de MXNL02, MXGT01 y NGK | se perdió al reimprimir por macOS; quedó Helvetica |
| Tracking / espaciado entre letras | no se declara |
| Jerarquía semántica (qué es encabezado, qué es celda) | los PDF de Canva no vienen etiquetados; todo es texto posicionado |
