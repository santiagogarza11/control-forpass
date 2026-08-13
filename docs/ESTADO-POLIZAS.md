# Estado del módulo de pólizas — cierre de sesión 13-ago-2026

Traspaso para la sesión siguiente. Rama **`modulo-polizas`**, sin desplegar.

> **Ojo con la lista de pendientes que traías.** Cuatro de los cinco puntos que
> pediste anotar como abiertos **ya están cerrados en esta sesión** (bug de
> frecuencia 5, descuadre de los 11 cobros, y las dos funciones que se quitaron a
> propósito), y la consolidación de las cuatro pólizas **se hizo**. Lo dejo abajo
> con lo que realmente pasó, no con la lista de memoria, para que nadie los
> vuelva a "arreglar".

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

### Las cuatro pólizas reales están extraídas pero **no cargadas**

`docs/poliza-MXNL02.json`, `poliza-MXGT01.json`, `poliza-INOAC.json`,
`poliza-NGK.json` — con la forma del objeto `POLIZA`, `mesesServicio` como
corrimientos 0–11 desde `inicioCalendario`, cantidades consolidadas y las 23
descripciones reales cruzadas por concepto.

**No hay cargador.** Son datos listos, nadie los importa. Falta un botón
"Importar póliza desde JSON" en el módulo, o meterlos por consola.

| | Renglones | Consolidado | Equipos | Anual limpio | Impreso | Dif |
|---|---|---|---|---|---|---|
| MXNL02 | 34 | 30 | 40 | $683,134.80 | $683,134.00 | **+$0.80** |
| MXGT01 | 72 | 36 | 72 | $1,884,480.40 | $1,790,257.88 | **+$94,222.52** |
| INOAC | 12 | 12 | 15 | $288,840.00 | $288,840.00 | $0.00 ✓ |
| NGK | 17 | 17 | 22 | $373,518.00 | $373,518.00 | $0.00 ✓ |

**Las dos diferencias están explicadas y NO se deben "ajustar":**

- **MXNL02, +$0.80** — la báscula de recibo cuesta $982.80 y × 3 = $2,948.40, pero
  el PDF imprime $2,948: truncó los centavos. Dos básculas × $0.40. El total
  impreso está 80 centavos abajo del precio que de verdad se cotizó.
- **MXGT01, +$94,222.52** — el **5% de descuento escondido** en cada Total Mtto
  (`1,884,480.40 × 0.95 = 1,790,256.38`; el $1.50 restante es el mismo
  truncamiento). Con la decisión B ya tomada —precios limpios, sin descuento— este
  número **tiene que subir**.

**Cantidades escondidas detectadas** (solo MXNL02, sin columna de cantidad):
renglón 7 Refrigerador Doble ×2, renglón 24 Barra Caliente Eléctrica ×4, renglón 25
Barra Fría ×2, renglón 34 Trampa de Grasa ×2.

**Dato del criterio de agrupación:** se aplicó concepto + marca + precio +
frecuencia + **meses**, y **ningún grupo se partió por meses** en ninguna de las
cuatro. Las unidades del mismo equipo siempre comparten calendario; el escalonado
se hace por tipo de equipo. Lo que sí impidió agrupar fueron **precios distintos
para el mismo concepto** en MXNL02: Campana de Extracción a $16,000 y a $8,000,
Extracción a $22,000 y a $11,000 — exactamente la mitad. Puede ser equipo chico y
grande, o un error de la cotización original. **Falta que Santiago lo confirme.**

### El lector de PDF no está en el repo

Vive en el scratchpad de la sesión (`leer.py`, `consolidar.py`, `generar.py`) y se
pierde al cerrar. Si hay que volver a extraer, lo que importa saber:

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

---

## Huecos conocidos

- **La regla de congelado de precios nunca se ejerció de verdad.** Un Owner pasa
  por la primera cláusula sin llegar a comparar `partidas`, así que el 403 no se
  ha visto. **Hace falta una cuenta Analyst.** La señal indirecta sí está
  verificada: lo que se reenvía es idéntico a lo guardado, y esa comparación es más
  estricta que la de Firestore.
- **`http://localhost:8000/*` sigue autorizado** en las restricciones del `apiKey`
  en Google Cloud. Se puso para probar en local. Quitarlo cuando ya no se use — no
  es una barrera de seguridad real (se pasa forjando el `Referer`), pero sobra.
- **Las reglas de `catalogo` pueden no estar publicadas.** Si el botón "Guardar la
  lista en el servidor" rebota, es eso: el bloque está en `config/firestore.rules`.
- **Nada está desplegado.** ~2,300 líneas nuevas en `index.html`, solo en la rama.

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

1. Un botón **"Importar póliza desde JSON"** que lea los archivos de `docs/`.
2. Confirmar con Santiago los precios dobles de MXNL02 (campana y extracción).
3. Decidir si MXGT01 entra con el anual limpio de $1,884,480.40.
4. **Registrar servicios ejecutados** — el esquema lo aguanta (`hechosDetalle`) y
   el calendario ya los pinta, pero no hay dónde marcar "este ya se hizo". Es el
   gemelo exacto de la cobranza y va en el mismo molde.

### Fase 4 — tablero

Indicadores de pólizas en la portada de su módulo ya están (activas, en la calle,
servicios del mes, atrasados). Falta el cruce con Forpass si se quiere una portada
única, y la vista de "qué toca este mes" a nivel de todas las pólizas, no de una.

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
