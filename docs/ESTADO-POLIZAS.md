# Estado del módulo de pólizas — al 17-ago-2026

Traspaso para la sesión siguiente. **Todo está en `main` y desplegado**, rama de
trabajo `servicios-parciales` al día. Lo único sin confirmar es el último deploy
(`a1cff59`, el descuento): el build de Pages falló por un problema de GitHub —no
del código— y se relanzó sin alcanzar a verificarlo. Ver el punto 1 de Pendientes
en `CLAUDE.md`.

## Lo que se hizo desde el 14-ago

| Bloque | Estado |
|---|---|
| **Fase 3B** | cerrada: las cuatro pólizas en Firestore, verificadas contra el servidor |
| **Fase 5 · puente de datos** | `armarPayloadPoliza()`, fallback «Sin datos», paginación de las tres hojas |
| **Fase 5 · portada** | réplica medida del PDF real, a ±0.5 pt |
| **Fase 5 · botón Imprimir** | en el detalle, todos los estatus y roles, con barra de «Guardar como PDF» |
| **Impresión sin ajustes** | `print-color-adjust:exact` — el navy y el calendario salen aunque «Gráficos de fondo» esté apagado |
| **Servicios por unidad** | «4 de 5» con porqué obligatorio |
| **Segurista** | fuera del seguimiento, nota «Incluye segurista» |
| **Descuento** | porcentaje, Owner/Admin, siempre impreso, congelado por regla |
| **Corrector de traslape** | mide lo dibujado y empuja lo que invada el pie; corre tras `fonts.ready` y en `beforeprint` |

**Lo que queda de la Fase 5** es solo la geometría fina de la tabla. El documento
ya imprime completo y correcto; la geometría lo dejaría *idéntico* al formato
medido.

> **Ojo con la lista de pendientes que traías.** Cuatro de los cinco puntos que
> pediste anotar como abiertos **ya están cerrados en esta sesión** (bug de
> frecuencia 5, descuadre de los 11 cobros, y las dos funciones que se quitaron a
> propósito), y la consolidación de las cuatro pólizas **se hizo**. Lo dejo abajo
> con lo que realmente pasó, no con la lista de memoria, para que nadie los
> vuelva a "arreglar".

## ⛔ Dos cosas que NO son bugs y ya se re-verificaron dos veces

Han vuelto a aparecer como "bloqueadores" en dos listas de pendientes distintas.
**No lo son, y no hay que tocarlas.** Verificado ejecutando el código el
14-ago-2026, no leyéndolo:

| «Bug» | Qué pasa de verdad |
|---|---|
| **Frecuencia 5** — *«`intervalo = 12/frecuencia` solo sirve para divisores»* | Ya está arreglado. El código dice literalmente `(a + Math.round(i * MESES_POLIZA / f)) % MESES_POLIZA`, que es exactamente el arreglo que la lista pide. Probadas las **144 combinaciones** de frecuencia × arranque: **0 rotas**. Frecuencia 5 desde el arranque 0 da `[0,2,5,7,10]` |
| **Descuadre de cobros** — *«el resumen dice 11 de $30,326.15»* | Ya está arreglado. Con el caso exacto de la queja —anual $363,913.80, facturación mensual— el resumen dice **«12 de $30,326.15»**. El `11` estaba escrito a mano y se cambió por un conteo de los cobros iguales |

Si vuelven a aparecer en una lista, es que la lista viene de notas viejas. **Correr
la verificación antes de "arreglar" algo que ya funciona**, porque el arreglo
correcto ya está puesto y volver a tocarlo solo puede romperlo.

## El bug que sí era: el importador corría el calendario un mes

De la misma familia que los dos de arriba —**el cero que se comporta como
ausencia**— y encontrado el 14-ago-2026 comparando la primera columna que pinta la
app contra los encabezados **medidos** de los cuatro PDF.

`generar.py` escribe `inicioCalendario.mes` **0-indexado** (`MESN` se arma con
`enumerate` sobre `['ene',…]`, así que `'ago'` es 7) y la plantilla lo documenta
igual. El importador lo validaba con `mes >= 1 && mes <= 12` y lo usaba tal cual:
las cuatro pólizas entraron con la vigencia **un mes antes**.

Y como `mesesServicio` son **desfases** desde `fechaInicio`, no se movía un dato:
**se movían todos los servicios de todos los renglones a la vez**, sin error y sin
aviso. El Segurista de MXNL02 caía en oct/feb/jun y el papel lo marca en
nov/mar/jul.

Traía un segundo fallo callado en la misma línea: una póliza que arrancara en
**enero** trae `mes: 0`, reprobaba la validación, y se iba sin vigencia a la fecha
de la cotización con un aviso genérico.

> **La firma de este bug vale más que el bug**: el gran total no se movió
> ($3,283,973.20) mientras el calendario entero sí. Un error que no toca el dinero
> no lo cacha ninguna prueba de totales. Solo se vio midiendo contra el documento.

Arreglado en `6275058`. Con eso, **es la primera vez que el calendario de la app
cuadra contra el documento medido**: las cuatro arrancan en el mes que sus PDF
imprimen.

---

## Terminado y verificado

Todo se probó ejecutando el código en el navegador, no leyendo el diff. Las cifras
son de las corridas reales de esta sesión.

| Bloque | Cómo se verificó |
|---|---|
| **Esquema** `normalizarPoliza` / `normalizarPartida` | 18 pruebas: idempotencia al normalizar 2 y 3 veces, viaje por `aCampos`/`deCampos`, llaves reordenadas como las manda Firestore |
| **Anidamiento en Firestore** (`partidas[] → mapa → mesesServicio[]`) | escritura real contra el servidor de producción, releída y comparada; documento de prueba borrado |
| **Idempotencia contra el servidor** | escribir → releer → normalizar no altera un byte de `partidas`. Es lo que sostiene el congelado de precios |
| **Dinero al centavo** | con 683,134: 11 casillas de $56,927.83 + una de $56,927.87; las 12 suman el anual exacto. 144 combinaciones de frecuencia × arranque |
| **Reparto de meses** (`mesesRegulares`) | frecuencias 1–12 × arranques 0–11: siempre `frecuencia` meses distintos, y los divisores de 12 dan lo mismo que la fórmula vieja |
| **Selector de módulo** | cambiar de módulo = 1 render medido; clic en la pestaña encendida = 0 renders; Forpass sin cambios (5 KPIs, `calcular()` da 17,000) |
| **Captura en tabla** | 26 equipos capturados desde el catálogo con 33 acciones y 0 clics en casillas de mes |
| **Cobranza** | 42 pruebas: OC obligatoria, casilla a verde, reabrir, corregir, deshacer, residuo en la última, permisos por rol |
| **Lista de precios** | 17 pruebas: Owner/Admin editan, Analyst y Viewer solo leen, un 403 de escritura sale de la cola con mensaje específico |
| **Calendario** | 14 pruebas contra el escalonado real de INOAC (may / jun / ago) |
| **Logos** | el recortador de Forpass reutilizado tal cual; avatar clicable en la tarjeta de póliza; Viewer no lo ve |
| **Un cliente, dos módulos** | 16 pruebas: el que solo tiene póliza no aparece en Forpass; el selector de póliza ofrece todos |

### Qué se quitó, y no vuelve

- **Balancear calendario** — repartía arranques para aplanar la carga. Se quitó
  porque **los mantenimientos los manda el equipo, no la carga de trabajo**:
  moverlos cambia el compromiso con el cliente. La barra de "servicios por mes" se
  fue con él (además tapaba botones).
- **Copiar de otra póliza** — clonaba renglones entre sitios. Se quitó porque
  **cada cocina es distinta**: dejaba más trabajo de corrección que de captura.

Están en el historial de git si algún día hacen falta, pero el motivo fue de
negocio, no técnico.

### Bugs cerrados en esta sesión

| Bug | Estado |
|---|---|
| Frecuencia 5 (y 7, 8, 9, 10, 11) marcaba el renglón en rojo | **cerrado.** `intervalo = 12/frecuencia` solo servía con divisores; ahora `round(i × 12 / frecuencia)`. 144 combinaciones probadas |
| El resumen decía "11 de $30,326.15" con 12 cobros iguales | **cerrado.** Estaba el `11` escrito a mano; ahora se cuentan los iguales |
| Un 403 de lectura del catálogo impedía entrar a la app | **cerrado.** `leerCatalogo()` se traga cualquier error |
| Un 403 de escritura se atoraba en la cola para siempre | **cerrado.** Sale de la cola y el aviso dice qué colección falló |
| La siembra del catálogo escribía sola al arrancar | **cerrado.** Ahora es un botón |
| `limpiarSesionYDatos` no incluía `polizas` | **cerrado** |
| Picar meses a mano no ajustaba los servicios/año | **cerrado** |
| Cuatro listeners del modal borrados por accidente | **cerrado** (ver la trampa en `CLAUDE.md`) |

---

## A medias

### Las cuatro pólizas reales: **cargador hecho, decisiones tomadas** (14-ago-2026)

Hay botón **Pólizas → Importar JSON**: se escogen archivos, sale una vista previa
con lo que va a entrar y sus avisos, y **nada se guarda hasta confirmar**. Entra
como `enviada` con la fecha del documento y **facturación mensual** (doce casillas)
— decidido por Santiago.

No lee de la red a propósito: un `fetch` a `docs/` dependería de que Pages sirva esa
carpeta —nunca comprobado— y no funcionaría en modo local.

| | Renglones | Consolidado | Equipos | **Anual que entra** | Impreso | Dif |
|---|---|---|---|---|---|---|
| MXNL02 | 34 | 30 | 40 | **$737,134.80** | $683,134.00 | +$54,000.80 |
| MXGT01 | 72 | 36 | 72 | **$1,884,480.40** | $1,790,257.88 | +$94,222.52 |
| INOAC | 12 | 12 | 15 | **$288,840.00** | $288,840.00 | $0.00 ✓ |
| NGK | 17 | 17 | 22 | **$373,518.00** | $373,518.00 | $0.00 ✓ |
| | | | | **$3,283,973.20** | | |

**Las diferencias están explicadas y NO se deben "ajustar":**

- **MXNL02, +$0.80** — la báscula de recibo cuesta $982.80 y × 3 = $2,948.40, pero
  el PDF imprime $2,948: truncó los centavos. Dos básculas × $0.40.
- **MXNL02, +$54,000** — el Segurista, corregido a mano (abajo).
- **MXGT01, +$94,222.52** — el **5% de descuento escondido** en cada Total Mtto.
  Con la decisión B ya tomada —precios limpios, sin descuento— **tiene que subir**.

**Los dos renglones donde la cotización se contradecía a sí misma** están en
`CORRECCIONES` de `consolidar.py`, llaveados por *(sitio, renglón del papel)* para
poder ir a checarlos contra la cotización impresa. Con eso, **las cuatro entran con
cero renglones sin cuadrar y las cuatro ya son cerrables**:

- **MXGT01 #18, Cámara de congelación** — decía 3 servicios con 2 meses marcados.
  Único así en 72 renglones; su gemela (Cámara de refrigeración ARTIC, mismo precio
  y frecuencia) y los 9 renglones de su bloque están en mar/jul/nov. Falta la marca
  de nov. **El dinero no se mueve.**
- **MXNL02 #32, Segurista** — decía 1 servicio con 3 meses marcados. **$27,000 no
  puede ser tarifa anual: el mismo concepto cuesta $25,000 AL MES en MXGT01 y en
  Nexxus**, dos sitios hermanos del mismo cliente. Es precio por servicio, o sea que
  la línea venía cotizada de menos. En las otras dos la frecuencia y el calendario
  coinciden, así que el "1" es el tecleado. Se tomó el calendario: **3**.

**Lo que NO se corrigió, y por qué.** La regla es estrecha: se toca un renglón
**solo cuando el documento se contradice a sí mismo**. Que el mismo equipo cueste
distinto en dos clientes no es un error, es un precio. Por eso sigue igual —aunque
huela raro— la **licuadora industrial de INOAC a $7,280** contra ~$919 en MXNL02 y
NGK: ocho veces, pero INOAC cuadra exacto con su total impreso. Vale la pena que
alguien la revise; no vale la pena cambiarla sola.

**Precios dobles de MXNL02, resueltos:** Campana de Extracción a $16,000 y $8,000,
Extracción a $22,000 y $11,000 son **dos equipos distintos**, no un error —
confirmado por Santiago. Los dos pares tienen **calendarios distintos** ([2,6,10] y
[3,7,11]), o sea dos sistemas escalonados, y ese equipo va de $4,800 a $22,000 entre
los otros clientes.

**Cantidades escondidas detectadas** (solo MXNL02, sin columna de cantidad):
renglón 7 Refrigerador Doble ×2, renglón 24 Barra Caliente Eléctrica ×4, renglón 25
Barra Fría ×2, renglón 34 Trampa de Grasa ×2.

### El lector de PDF ya está en el repo y corre con cualquier PDF

`scripts/lector-pdf/` — ver su README. Un comando:

```bash
python3 scripts/lector-pdf/generar.py ~/Downloads/"la cotización.pdf"
```

Lee cliente, sitio y fecha **de la portada** y los imprime para revisarlos; se
corrigen con `--cliente`, `--sitio`, `--fecha`, `--total`. Sin argumentos rehace las
cuatro conocidas. **Verificado: regenera los cuatro JSON idénticos.**

**No machaca un `docs/poliza-*.json` existente.** Ese candado no es teórico: la
portada de la cotización de Nexxus dice «MXGT01» porque la copiaron de la anterior,
y sin él se habría llevado por delante la de MXGT01 en silencio.

Lo que importa saber del formato:

- Los meses **no son texto**: son trazados `m`/`l`/`h f` con color de relleno
  `(0.576, 0.702, 0.835)`.
- La posición viene del **CTM** (`cm`) con su pila `q`/`Q`, **no de `Tm`** — `Tm`
  solo trae la escala de la fuente.
- Los encabezados de columna se eligen por **el renglón donde coinciden más**:
  "Concepto Cotizado:" del título también empieza con "Concepto".
- El calendario abarca **varias páginas** cuando hay muchos renglones.
- MXGT01 numera hasta 79 con solo 72 renglones (faltan 44, 51, 69–73) y NGK hasta
  19 con 17 (faltan 14, 18): son huecos reales de Canva, no filas perdidas — la
  suma cuadra sin ellos.
- `leer.py` es **librería, no se corre solo** (el README decía que sí; era falso).

### Hay una quinta cotización sin cargar: **Mercado Libre Nexxus**

26-jun-2026, 79 renglones, **$1,952,850.40** limpio contra **$1,855,207.88**
impresos — el **mismo 5% escondido** de MXGT01. El lector la saca sin tocarle nada
(probado). Santiago dijo **todavía no**: primero las cuatro verificadas. Ojo con su
portada, que dice «MXGT01».

---

## Huecos conocidos

- ~~**La regla de congelado de precios nunca se ejerció de verdad.**~~ **Ejercida
  el 18-ago-2026** con la cuenta Analyst `test1` sobre Prolec en `activa`: los
  cuatro intentos de romperla rebotaron y los dos legítimos pasaron. Encontró un
  bug que solo se podía ver así —la comparación del descuento reventaba en las
  pólizas que no traían el campo, y el servidor rechazaba todo, incluso lo
  legítimo—, arreglado en `d1313a9` y publicado en la consola. Detalle en
  `docs/POLIZAS.md` §Congelado de precios. **Falta el rol Viewer.**
- **`http://localhost:8000/*` sigue autorizado** en las restricciones del `apiKey`
  en Google Cloud. Se puso para probar en local. Quitarlo cuando ya no se use — no
  es una barrera de seguridad real (se pasa forjando el `Referer`), pero sobra.
- **Las reglas de `catalogo` pueden no estar publicadas.** Si el botón "Guardar la
  lista en el servidor" rebota, es eso: el bloque está en `config/firestore.rules`.
- ~~**Nada está desplegado.**~~ Renglón viejo: todo está en `main` y desplegado
  desde el 14-ago. La rama `servicios-parciales` ya no existe.

---

## Qué NO hay que tocar

Verificado intacto en cada bloque de esta sesión:

- **`descargarExcel`** y todo el generador XLSX. Si algún día se agrega una hoja de
  pólizas: las letras de columna se calculan con `letraCol()`, nunca a mano, y el
  total del renglón va como fórmula, no tecleado.
- **`pagos[]`** y **`pagosDetalle`** de sitios. La cobranza de pólizas usa
  `cobros`/`cobrosDetalle` a propósito: con el mismo nombre, `calcular(poliza)` no
  tronaría — devolvería basura plausible.
- **`normalizarSitio`** — `sitios` no ganó ni un campo.
- **`calcular()`** — `calcularPoliza()` es función nueva y aparte.

---

## Fases que faltan

### Fase 3B — cargar las cuatro pólizas reales

1. ~~Botón "Importar póliza desde JSON"~~ **hecho**, con vista previa.
2. ~~Precios dobles de MXNL02~~ **dos equipos distintos**, confirmado.
3. ~~¿MXGT01 con el anual limpio?~~ **sí**, $1,884,480.40.
4. ~~Registrar servicios ejecutados~~ **hecho** — y obligó a mover el esquema, ver
   abajo.
5. Cargar **Nexxus** cuando Santiago diga.

### ✅ Fase 3B cerrada — 14-ago-2026, verificada contra Firestore

Desplegado (`bf6cf56` en `main`), reglas de `polizas` y `catalogo` pegadas en la
consola, y **las cuatro pólizas importadas contra el servidor real** desde el sitio
en vivo, con el selector de archivos.

Verificado releyendo de Firestore con `listarNube('polizas')`, no en pantalla:

| | |
|---|---|
| MXGT01 | $1,884,480.40 |
| MXNL02 | $737,134.80 |
| INOAC | $288,840.00 |
| NGK | $373,518.00 |
| **Total de las cuatro** | **$3,283,973.20** ✓ |
| Vigencia de MXNL02 | **ago-26** |
| Segurista | **nov-26 · mar-27 · jul-27** — igual al documento medido |
| **Idempotencia tras el viaje** | **`true`** |

La última es la que sostiene el congelado de precios: `partidas` sale de Firestore
**byte por byte igual** a como entró, así que un Analyst sí va a poder capturar
cobranza y servicios sobre una póliza activa.

**Queda una sola verificación pendiente**, y no se puede hacer antes: que `polizas`
aparezca **dentro de `backups/ultimo.json`** del repo privado. El robot corre a las
03:00, 09:00 y 15:00 de Monterrey, así que hay que esperar la primera corrida
posterior a la importación y **abrir el archivo**, no leer el log — el log puede
decir «ok» sin incluir la colección. `CLAUDE.md` advierte que ese script escribía
las colecciones a mano y es el lugar que se olvida.

```bash
gh api repos/santiagogarza11/control-forpass-backups/contents/backups/ultimo.json --jq '.content' | base64 -d | python3 -c "import json,sys; d=json.load(sys.stdin); print({k: (len(v) if isinstance(v,list) else type(v).__name__) for k,v in d.items()})"
```

### Hay una quinta póliza en el servidor: «Prolec» — **es una prueba**

$106,461, cliente NGK, con 2 de 15 servicios marcados. **No salió del importador**
—no existe ningún `poliza-Prolec.json`— y la aritmética lo confirma: el indicador
de portada da $3,390,434, y `3,390,434 − 3,283,973 = 106,461`, exactamente Prolec.
Las cuatro importadas están intactas.

Santiago confirmó el 14-ago-2026 que **es una prueba suya**. Se deja en el servidor;
no estorba. Si algún día se limpia, se borra desde su tarjeta.

**Al verificar totales hay que filtrar por sitio**, no sumar todo: el indicador de
la portada cuenta las cinco.

### El registro de servicios movió el esquema (y por poco sale roto)

`hechosDetalle` vivía **dentro de cada partida**, y la regla de Firestore congela
`partidas` en cuanto la póliza deja de ser cotización. O sea que marcar un servicio
cambiaba `partidas` y **un Analyst habría recibido un 403 al marcar un
mantenimiento en una póliza activa** — el único momento en que se marcan. Se midió
antes de escribir la pantalla, comparando el `partidas` que se reenvía.

Lo ejecutado vive ahora en **`hechos`, al nivel de la póliza**, llaveado por **id
de partida → mes**, igual que `cobrosDetalle` vive arriba. Cada partida ganó un
**`id` estable**: llavear por posición se rompería al duplicar o borrar un renglón.
No hubo migración que hacer —no hay ni una póliza en el servidor— pero
`normalizarPoliza` **sí sube el formato viejo solo** por si aparece en un respaldo.

`docs/POLIZAS.md` afirmaba *"capturar cobranza y servicios pasa"*. La mitad de
servicios era falsa desde que se escribió; ya está corregido, con la nota de por
qué nadie lo cachó.

**Probado ejecutando: 29 pruebas.** Que marcar servicios no toca `partidas`,
idempotencia (2×, 3× y viaje por Firestore), orden de llaves estable, que
normalizar no muta su entrada, migración del formato viejo incluso con renglones
basura de por medio, que se tiran los servicios sin fecha y los de renglones
borrados, los dos caminos de la interfaz (chips y calendario), validaciones,
corregir, deshacer, que duplicar no hereda servicios, que borrar un renglón avisa y
se lleva los suyos, que **editar la póliza no borra el historial**, permisos en tres
niveles y Forpass intacto.

### Fase 4 — tablero

Indicadores de pólizas en la portada de su módulo ya están (activas, en la calle,
servicios del mes, atrasados). Falta el cruce con Forpass si se quiere una portada
única, y la vista de "qué toca este mes" a nivel de todas las pólizas, no de una.

### Servicios por unidad: hecho (14-ago-2026, 30 verificaciones)

Pedido por Santiago: con «3 Rational» en un renglón, marcar el mes daba por
atendidos los tres. Ahora el modal pinta **un botón por unidad** (prendidos por
omisión), se apagan los no atendidos, y **el porqué es obligatorio** cuando falta
alguno. Detalle en `docs/POLIZAS.md` §Servicios ejecutados. Esquema: `hechas` y
`motivo` dentro del registro del mes en `hechos` — fuera de `partidas`, así que
el congelado ni se entera (verificado: `partidas` sale idéntica).

### Segurista fuera del seguimiento + el porqué al globito (14-ago-2026, 21 pruebas)

Pedidos por Santiago sobre la marcha: el segurista es una persona supervisando,
no un equipo — ahora es nota «Incluye segurista» en los meses cubiertos (MXGT01
los 12, MXNL02 sus 3), sin palomita, sin contar en los KPIs de servicios (MXGT01
131→119 programados) y con su dinero intacto. Y el motivo de un parcial salió de
la tarjeta del calendario: fracción visible, porqué en el globito. Detalle y
porqués en `docs/POLIZAS.md` §El segurista no es un equipo.

### ⏸ Diferido por Santiago: vigencia variable (1–24 meses)

Lo pidió el 14-ago-2026 —cotizar lo que resta del año— y lo difirió él mismo en
el mismo mensaje por riesgo. Correcto: `MESES_POLIZA = 12` es decisión cerrada
con raíces en la cláusula impresa («doce (12) meses»), las 12 columnas del
calendario del documento, `repartirCentavos`, `mesesRegulares` y `arranquesDe`.
**Si se reabre, es proyecto con fase propia, no un ajuste** — y ya existe el
motivo de negocio real que la tabla de decisiones pedía.

### Fase 5 — botón Imprimir: hecho (13-ago-2026, 44 verificaciones)

Botón **Imprimir** en el detalle de la póliza, junto a Calendario y Editar:

- **Todos los estatus y todos los roles**, Viewer incluido: imprimir es lectura y
  el Viewer ya ve las cifras — el control de acceso es la cuenta, no el botón.
- Abre `docs/plantilla_poliza_forguard.html` con `window.open(..., '_blank')`
  **sin `noopener`** (con `noopener` no hereda el `sessionStorage`).
- El título de portada lo resuelve el payload por estatus: `activa` → «Póliza de /
  Mtto Prev.», todo lo demás → «Cotización / Póliza de / Mtto Prev.».
- **Barra de guardar con UN botón** («Guardar como PDF» → `window.print()`). Los
  tres ajustes que la primera versión pedía a mano **ya no existen para el
  usuario**: `print-color-adjust:exact` en todo imprime el navy y las celdas del
  calendario aunque «Gráficos de fondo» esté apagado (su estado por omisión), y
  con `@page{margin:0}` el navegador no tiene margen donde pintar sus encabezados.
  **Verificado imprimiendo con Chrome headless sin tocar un ajuste**: 5 hojas de
  612×792 exactos, navy de borde a borde, cinta verde en su esquina, 1,532
  muestras del azul de celdas, cero texto del navegador. Lo único que el diálogo
  no nos deja decidir es el destino — la barra lo dice. `position:fixed` (no
  recorre la paginación), oculta en `@media print`, fuera del DOM en «Sin datos».
- **El documento ya no repite el nombre del cliente**: si el sitio ya lo trae
  adentro —«INOAC»/«INOAC», «Prolec»/«Prolec Planta 1»— se imprime solo el sitio;
  si es código aparte («Mercado Libre»/«MXGT01») van los dos. Ignora mayúsculas y
  acentos. Cinco casos probados.
- La **portada es réplica medida** de la real: fondo `#031649`, escudo gigante con
  los trazos del vector del PDF tal cual, título Helvetica 72 pt (la única
  excepción a Poppins, a propósito), todo a ±0.5 pt contra el render de referencia.

### Fase 5 — documento imprimible y PDF

`docs/plantilla_poliza_forguard.html` se abre en pestaña nueva y recibe los datos
por `sessionStorage`. **Cuatro cosas antes:**

1. **Embeber Poppins en base64.** Hoy la baja por CDN y eso rompe la regla de "sin
   internet, todo embebido".
2. **Cambiar su navy `#08194B` por el de marca `#002369`.**
3. **Abrir la pestaña SIN `noopener`** o no hereda el `sessionStorage` y llega
   vacía.
4. **Verificar que GitHub Pages sirva el archivo en `docs/`** — nunca se comprobó.

Y una decisión comercial pendiente: **qué mensual imprime el documento.**
$56,927.83 × 12 = $683,133.96, cuatro centavos menos que el anual. O lleva nota al
pie, o imprime la última mensualidad aparte.
