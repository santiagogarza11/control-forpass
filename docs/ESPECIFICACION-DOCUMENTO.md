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

### Qué peso usa cada elemento — y hasta dónde llega Poppins

Extraído de INOAC, el único que la conserva. **Poppins aparece únicamente en las
etiquetas de portada y en el bloque de contacto del pie.** El título de 72 pt y
todo el cuerpo de la tabla salieron en Helvetica, así que de esos **no se puede
saber** qué eran.

| Peso | pt | Dónde, exactamente | Apariciones |
|---|---|---|---|
| **Poppins-Italic** | 6.7 | etiquetas de portada: «Cliente», «Fecha», «Proyecto:» | 3 |
| **Poppins-Regular** | 6.7 | los valores de esas etiquetas: «: INOAC», «: 15 de abril 2026» | 4 |
| **Poppins-Bold** | 5.8 | etiquetas del pie: «Teléfono», «Correo:» | 15 |
| **Poppins-Regular** | 5.8 | valores del pie: teléfono, dirección | 14 |
| **Poppins-Medium** | 5.8 | **una sola vez**, en `pablo.quiroga@forguard.com` | **1** |

> **Medium no está justificado por la evidencia.** Se usa exactamente una vez, en
> un correo que en la otra hoja va en Bold. Es inconsistencia de un documento hecho
> a mano, no una decisión de diseño. Embeber **Regular, Bold e Italic** cubre todo
> lo demostrable; Medium agregaría ~30 KB para reproducir un descuido.

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

## Inventario hoja por hoja

**Solo existen cinco tipos de hoja** en las cuatro cotizaciones, ni uno más:

| Tipo | Título de 31.7 pt | Aparece en |
|---|---|---|
| Portada | *(el de 72 pt)* | las 4 |
| Tabla de renglones | «Póliza de Mantenimiento» | las 4 |
| **Descripción de Trabajos** | «Descripción de Trabajos» | **solo INOAC y NGK** |
| Calendario | «Calendario de Mantenimientos» | las 4 |
| Consideraciones | «Consideraciones Relevantes» | las 4 |

**Orden adoptado:** Portada → Tabla → Descripción → Calendario → Consideraciones.

Confirmado: **el calendario siempre va en hojas aparte, siempre después de la
tabla.** Nunca dentro de la tabla de renglones.

### Tres de las cinco hojas se desbordan y hay que partirlas

| Hoja | Tope | De dónde sale |
|---|---|---|
| Tabla de renglones | **23 filas** | paso 21.53 pt · 1ª en y=183.5 · última en y=657.1 |
| Calendario | **21 renglones** | máximo observado (MXGT01), paso 22.4 pt |
| Descripción | **por altura, no por conteo** | sus filas miden de 19.8 a 28.0 pt: el texto es largo y envuelve |

El bloque de cierre —Precio Anual, Precio Mensual y las notas— va **solo en la
última hoja de la tabla**: en una intermedia sobraría y en la primera diría un
total que todavía no se termina de listar.

### La hoja de Descripción sale corta en dos de las cuatro

Lista **un renglón por concepto distinto**, y solo los que tienen texto:

| | Conceptos únicos | Con descripción | Sin |
|---|---|---|---|
| INOAC | 12 | **12** | 0 |
| NGK | 17 | 15 | 2 |
| MXNL02 | 26 | 16 | **10** |
| MXGT01 | 35 | 15 | **20** |

MXNL02 y MXGT01 **no traían esa hoja**, así que sus descripciones se cruzaron por
concepto desde INOAC y NGK. Los que quedaron sin texto **se omiten**: imprimir un
renglón con la celda en blanco no informa de nada, y no se inventa el texto de un
mantenimiento.

| | Orden de las hojas |
|---|---|
| MXNL02 | portada · **consideraciones** · tabla · tabla · calendario · calendario |
| MXGT01 | portada · tabla ×4 · **consideraciones** · calendario ×4 |
| INOAC | portada · tabla · **consideraciones** · calendario · descripción |
| NGK | portada · tabla · calendario · descripción · **consideraciones** |

La hoja de «consideraciones» es la misma en las cuatro: *Cotización de Servicios
Extras · Consideraciones Relevantes* (visitas fuera de cronograma, etc.).

**Cuatro documentos, cuatro órdenes distintos.** Como con las columnas, no hay un
orden canónico que copiar: hay que elegirlo.

---

## Tabla de renglones

| | Valor |
|---|---|
| **Paso entre filas** | **21.53 pt** · *21.15 en INOAC* |
| Reglas horizontales | 24 por hoja al mismo paso — **23 de fila + 1 bajo el encabezado** |
| **Reglas verticales** | **ninguna** |
| Encabezado | y = 161.0 (MXGT01) · 167.3 (NGK) |
| Regla del encabezado | y = 175.5 — entre el encabezado y la primera fila |
| Primera fila | y ≈ **183.5** · *189.7 en MXNL02 y NGK* |
| Última fila observada | y ≈ **657.1** |
| **Máximo de filas por hoja** | **23** (medido en MXGT01 hoja 3) |
| Pie: «Precio más Iva.» | y = 762.6 |
| Pie: tagline | y = 774.5 |

**Ancho de columna: no extraíble.** No hay una sola regla vertical dibujada, así que
el archivo no dice dónde empieza ni termina una celda.

### Alineación — medido, y no es lo que se esperaba

No son ni izquierda ni derecha. **Cada columna tiene una línea de centro, y el
encabezado y los datos la comparten**: el desfase entre el centro del encabezado y
el centro de los datos es de **0.0 pt** en todas menos una.

La desviación del centro a lo largo de la columna es **exactamente 0.00**, con
valores de 3 a 6 anchos distintos. Eso no es «aproximadamente centrado».

| Columna (NGK) | Línea de centro | Alineación |
|---|---|---|
| `#` | 133.5 | centrada |
| **Concepto** | encabezado en 208.1, **datos a la IZQUIERDA en x = 144.8** | la única excepción |
| Cantidad | **297.0** | centrada |
| Precio Unitario | **354.2** | centrada |
| Total | **415.3** | centrada |
| Frecuencia | **474.4** | centrada |
| Total Mtto | **531.4** | centrada |

En MXGT01 pasa lo mismo con sus columnas: Marca centrada en 319.9, Precio en 410.8,
Frecuencia en 485.0, Total Mtto en 542.0; Concepto a la izquierda.

> **Para el CSS**: `text-align:center` en todas menos Concepto, y posicionar por
> **centro de columna**, no por borde izquierdo. Las `x` de la sección anterior son
> dónde arranca el *texto del encabezado*, que en Concepto está 63 pt a la derecha
> de sus propios datos. Cuadrar el CSS a esas `x` deja la columna corrida.

### ¿Cabe el concepto más ancho? Sí, por 1.2 pt

Medido con las **métricas reales de Poppins**, no de Helvetica: Poppins es
**9.6 – 12.2 % más ancha**, así que la duda estaba bien puesta.

Los **70 conceptos distintos** de las cuatro cotizaciones, a 7.2 pt Regular contra
los 126.6 pt de la columna:

| | |
|---|---|
| Se pasan | **0 de 70** |
| El más ancho | `Barra Caliente De Servicio Eléctrica` = **125.4 pt** |
| Holgura | **1.2 pt · la columna queda al 99 %** |
| Tope práctico | **~36 caracteres**. Con 38 ya se pasa |
| Marcas (5.8 pt) | la más ancha `HELVEX/FAB. ESPEC` = 53.1 pt, sin problema |

> **Cabe solo con padding horizontal CERO.** Con 1 pt por lado se pasa uno, con
> 3 pt se pasan tres. Si el CSS le pone aire a la celda, se rompe de inmediato.

| Padding por lado | Ancho útil | Conceptos que se pasan |
|---|---|---|
| 0 pt | 126.6 | **0** |
| 1 pt | 124.6 | 1 |
| 2 pt | 122.6 | 2 |
| 3 pt | 120.6 | 3 |

Salida si se quiere aire: **a 7.0 pt caben todos con 2 pt de padding por lado**.
Son 2.8 % más chico, invisible al ojo, y compra el margen que a 7.2 no existe.

**El aviso de captura es más necesario, no menos**: el umbral es **36 caracteres**.

### La cadena aritmética de NGK — confirmada

Los 17 renglones, sin una sola excepción:

```
Total      = precioUnitario × cantidad      17/17
Total Mtto = Total × frecuencia             17/17
```

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
| **Paso horizontal, entre centros** | **23.53 pt** · *23.85 en INOAC* |
| **Ancho de la rejilla** (12 × paso) | **282.4 pt** · *286.2 en INOAC* |
| Span del primer al último centro (11 pasos) | 258.8 pt · *262.3 en INOAC* |
| Celda marcada | **23.5 × 22.3 pt** · *23.8 × 18.0 en INOAC* |
| Paso vertical | 22.3 pt · *18.0 en INOAC* |
| Color de la celda marcada | **`#8BB4D8`** |

**Los dos números que no cuadraban eran el mismo dato mal medido.** El «24.3» salió
de las `x` donde *arranca* cada etiqueta, y las etiquetas tienen anchos distintos.
Medido entre **centros**, el paso es **23.53 pt** y es idéntico en las doce columnas
(mín 23.53, máx 23.53). El «257–264» era el span de **once** pasos, no de doce.

Como la celda mide 23.5 y el paso es 23.53, **las celdas van pegadas**: no hay
canal entre columnas.

### Los encabezados ya están anclados a la vigencia

No dicen Ene–Dic. Dicen los doce meses de la vigencia, empezando por el de inicio:

| | Encabezados reales |
|---|---|
| MXNL02 | ago-26 · sep-26 · oct-26 · nov-26 · dic-26 · ene-27 · feb-27 · mar-27 · abr-27 · may-27 · jun-27 · **jul-27** |
| MXGT01 | jun-26 · jul-26 · ago-26 · … · abr-27 · **may-27** |
| INOAC | may-26 · jun-26 · jul-26 · … · mar-27 · **abr-27** |
| NGK | ago-26 · sep-26 · … · may-27 · jun-27 · **jun-27** ⚠ |

**El punto queda decidido por el dato, sin opinar: `columna = (mes - mesArranque + 12) % 12`
es lo que los documentos ya hacen.** Los clientes ya recibieron calendarios
anclados a su vigencia.

> ⚠ **NGK trae un error humano en su calendario**: sus dos últimas columnas dicen
> las dos `jun-27`. La segunda debería ser `jul-27`. Es la misma clase de error que
> ya documentamos en los renglones — el papel no es la autoridad.

---

## Colores, del vector

Estos **no** están muestreados de un JPEG: salen del relleno declarado en el
contenido, así que no traen desplazamiento de color.

| Color | Cobertura | Dónde |
|---|---|---|
| **`#002369`** | la dominante en las 4 | fondo de portada y bloques navy |
| `#031649` | una capa completa | **rectángulo de 612 × 792 en la hoja 1** — la capa base de la portada, debajo del `#002369` |
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
