# Pólizas de mantenimiento preventivo

> Detalle del segundo módulo. El resumen y las reglas generales del proyecto están
> en [CLAUDE.md](../CLAUDE.md); esto es lo que hay que leer **antes de tocar
> pólizas**. Vive aparte porque `CLAUDE.md` se carga en cada sesión y esta parte
> ya pesaba más que todo lo demás junto.

Segundo producto de Forguard: mantenimiento preventivo a cafeterías industriales.
Se cotiza listando equipos y, cuando el cliente acepta, **esa misma cotización se
vuelve póliza activa** — es el mismo documento en otro momento, distinguido por
`estatus`, igual que un sitio usa `estado`.

El dolor que resuelve: no se sabía cuántas pólizas están activas, qué
mantenimientos toca hacer este mes, ni qué equipos se cubren.

**Selector de módulo en el encabezado** (`estado.modulo`, `irAModulo`), donde antes
estaba el `<h1>`: con dos productos ese título era mentira en la mitad de la app.
Se recuerda el último módulo en `localStorage` (`LLAVE_MODULO`) y se carga **antes
del primer render** para que no parpadee. `render()` despacha por módulo y luego
por vista; el panel de admin va **antes de los dos** porque es de la app entera.
Cambiar de módulo es **UN** render.

### La regla de oro

    totalMtto     = precioUnitario × cantidad × frecuencia
    precioAnual   = suma de los renglones
    precioMensual = precioAnual / 12

### El descuento, y por qué este sí es seguro

Hay **una** casilla de descuento, en **porcentaje**, a nivel de la póliza y solo
para Owner/Admin. Reabre una decisión que estaba cerrada, y la reabre a propósito
con la diferencia que importa: **lo que rompió MXGT01 no fue que hubiera un
descuento, fue que estaba escondido dentro del Total Mtto de cada renglón.** El
papel cuadraba consigo mismo y solo apareció al recalcular desde los precios.

Las cuatro reglas que lo mantienen a salvo:

- **Nunca toca los renglones.** `totalRenglon()` sigue siendo precio × cantidad ×
  frecuencia. El descuento se aplica UNA vez, sobre el total.
- **Se imprime como renglón propio**: Subtotal · Descuento X% · Precio Anual. Si
  hay descuento, el cliente lo ve.
- **Solo se guarda el porcentaje.** El monto y el total se derivan, como todo lo
  demás. Guardar el monto sería otra vez el error de MXGT01.
- **Está congelado por regla de servidor**, igual que los precios. Vive FUERA de
  `partidas`, así que sin agregarlo a la cláusula 3 un Analyst podía bajarle 30% a
  una póliza cerrada sin tocar un renglón: congelar los precios sin congelar el
  descuento es no congelar nada.

La cobranza reparte el anual **ya con descuento** en centavos enteros, así que las
doce casillas siguen sumando exacto. Se acota a [0, 100] y a dos decimales: un
5.125% no existe en una negociación y sí produce centavos que nadie reproduce a
mano.

**El total de un renglón nunca se captura ni se guarda.** Vive solo en
`totalRenglon()`. Esto corrige un problema real: en cotizaciones pasadas los
totales se teclearon y dejaron de cuadrar —una traía cantidades escondidas sin
columna, otra un factor que nadie documentó—. **No hay campo de descuento en
ninguna parte**: un ajuste se refleja en el `precioUnitario` del renglón.

`frecuencia` dice CUÁNTOS servicios al año; `mesesServicio: [0..11]` dice EN QUÉ
meses, como corrimientos desde `fechaInicio`. Son datos aparte porque el segundo
alimenta el calendario y el seguimiento. Si no cuadran **se avisa, no se bloquea**
(`cuadraFrecuencia`): se puede guardar una cotización a medias, pero no cerrarla
como activa.

### Dinero al centavo

`683,134 ÷ 12 = 56,927.83`, y por doce da `683,133.96`. **Un solo número mensual
nunca puede cuadrar contra el anual; doce casillas sí.** Por eso la cobranza se
reparte en **centavos enteros** con `repartirCentavos()` y el residuo va a la
**última** casilla —la primera es la que se negocia y se cita—. Las sumas
acumuladas (`adeudo`, `cobrado`) también van en enteros: doce sumas de flotantes
dan `683,133.9999999999`, que en pantalla se ve como un peso faltante.

`precioMensual` es **nominal**, el que se imprime. El calendario real de cobro
está en `montos[]`, y ese sí cuadra al centavo. `dineroCent()` muestra centavos;
`dinero()` se queda como está, es el de Forpass.

### Esquema (`normalizarPoliza` / `normalizarPartida`)

Una sola colección nueva, `polizas`, sin subcolecciones. **No hay campo `meses`**:
`MESES_POLIZA = 12` es la única fuente, porque la cláusula impresa dice "doce (12)
meses" y el calendario del documento tiene 12 columnas clavadas.

`estatus`: `cotizacion → enviada → activa`, más `perdida` y `cancelada`. Solo cinco
guardados; "Terminada" y "Por vencer" **se derivan** de las fechas, igual que un
sitio no guarda "Contrato cubierto".

`clienteId` referencia la colección `clientes` que ya existía. `sitioId` es
**opcional** —hay pólizas en cafeterías sin kiosco— y `sitioNombre` **siempre** se
guarda como texto, porque es lo que sale impreso y debe sobrevivir a que el sitio
se borre. El `vendedor {uid, nombre, correo, telefono}` se guarda **copiado**: el
documento tiene que decir lo mismo dentro de un año aunque esa persona ya no esté.
Por eso se agregó `telefono` a `usuarios/{uid}`, y cada quien puede editar el
suyo (la regla lo permite junto a `ultimoAcceso`).

**Lo ejecutado vive en `hechos`, al nivel de la póliza** —no dentro de cada
partida— y llaveado por **id de partida → mes**:
`{"<idPartida>": {"0": {cuando, quien, nota}}}`. La presencia de la llave ya dice
que se hizo.

Que viva arriba **no es cosmético, es lo que lo hace funcionar**. La regla de
Firestore congela `partidas` en cuanto la póliza deja de ser cotización: exige que
salga idéntica a como entró. Guardado adentro de la partida, marcar un
mantenimiento cambiaba `partidas`, así que un Analyst **no podría marcar un
servicio en una póliza activa** — justo el único momento en que se marcan. Un 403
sin explicación, en manos de quien más lo necesita. Es exactamente por lo que
`cobrosDetalle` vive arriba: la simetría era la pista, y se descubrió midiendo
antes de escribir la pantalla.

Cada partida trae por eso un **`id` estable**. Llavear por la posición en el
arreglo se rompería en cuanto alguien duplica o borra un renglón — que es la misma
lección que ya costó una vez: esto empezó como arreglos en paralelo a
`mesesServicio`, y si el cliente metía un equipo y el calendario pasaba de
`[0,4,8]` a `[0,2,4,8]`, el registro del mes 4 se recorría al mes 2, sin error y
sin aviso. **Llavear por el dato, nunca por la posición**, en los dos niveles.

Un servicio real en un mes que ya salió del calendario **no se borra** — ver
`serviciosFueraDeCalendario()`. Uno cuyo renglón se borró sí: `normalizarPoliza`
tira las llaves huérfanas, y quitar un renglón con servicios avisa antes.

### La lista de precios

El catálogo **sí es colección**, contra lo que se decidió en Fase 2: los precios
los edita el equipo, así que tienen que persistir. Vive en **un solo documento**,
`catalogo/lista`, con el arreglo de 48 equipos adentro — uno y no 48 porque se lee
en cada carga y se edita casi nunca: **48 equipos por 1 lectura**. Todos la leen,
solo Owner/Admin la escribe, y ese candado sí lo exige el servidor.

`CATALOGO_SEMILLA` es solo semilla y se sube **con un botón, nunca sola**. Salió de
las cuatro cotizaciones reales: 48 equipos distintos de 106 renglones. **Sin
marca** —cambia de sitio en sitio y la pone el vendedor— y 22 sin descripción,
porque MXGT01 y MXNL02 no traen esa página y no se inventa el texto de un
mantenimiento.

El precio del catálogo es **sugerencia, no dato**: el mismo equipo se cotizó a
16,000 y a 8,000 en distintos clientes. El renglón siempre manda. Un equipo que
ya no se vende se **apaga**, no se borra: las pólizas viejas apuntan a su id y
necesitan resolver su texto.

La `descripcion` va al revés que el precio: se resuelve del catálogo por
`catalogoId` y solo se copia al renglón si alguien la editó. Describe el trabajo,
no el contrato, y así 79 renglones no cargan ~20 KB de texto repetido.

### Los meses se calculan, no se pican

En las cotizaciones reales la frecuencia manda el intervalo: **`intervalo = 12 /
frecuencia`**. Con la frecuencia y el mes de arranque los meses salen solos, así
que la captura es **un control por renglón** en vez de picar 3 de 12 casillas.
Capturar MXNL02 eran 102 clics; ahora son 0.

> ## ⚠ `arranque` y `mesesServicio` son DESFASES, nunca meses calendario
>
> Los dos cuentan **meses dentro del plazo**, contados desde `fechaInicio`. El `0`
> es el primer mes de la vigencia, no enero. Con `fechaInicio` en agosto de 2026,
> `mesesServicio: [3,7,11]` significa **nov-26 · mar-27 · jul-27**.
>
> **Esto ya hizo tropezar a dos personas.** La palabra «arranque» se lee como «el
> mes en que arranca la póliza» y no es eso: es el desfase del primer servicio de
> **un renglón** dentro del plazo — lo que hace falta para escalonar equipos entre
> sí. Que existan **12 desfases posibles** por frecuencia es la prueba: si fueran
> meses calendario no habría doce ciclos distintos que probar.
>
> Dos consecuencias prácticas:
>
> - **La columna del calendario impreso ES el valor guardado.** No se rota. Aplicar
>   un `(mes - mesArranque + 12) % 12` rotaría lo ya rotado y movería todos los
>   servicios: el Segurista de MXNL02 pasaría de nov/mar/jul a abr/ago/dic.
> - **`fechaInicio`, con año, es la única fuente de los encabezados** (`ago 26` …
>   `jul 27`). Nunca `Math.min(...mesesServicio)`: si ningún equipo se atiende el
>   primer mes —normal, en INOAC están escalonados a propósito— el mínimo ancla el
>   calendario en el mes equivocado y **todos** los renglones se recorren juntos.

El arranque **se deduce** de los meses (`mesArranqueDe`), no se guarda: un campo
más sería un dato que se desincroniza de los meses reales, que son los que
alimentan el calendario y el seguimiento. El selector ofrece solo los ciclos
distintos que existen —con frecuencia 3 hay 4, no 12, porque arrancar en el mes 0
y en el 4 dan el mismo `[0,4,8]`—. Las frecuencias que no parten el año en partes
iguales (5, 7, 8…) no tienen patrón: esas van a mano.

`mesesRegulares` reparte con **`round(i × 12 / frecuencia)`**, no con un intervalo
entero. La primera versión hacía `intervalo = 12 / frecuencia` y **solo servía para
los divisores de 12**: con frecuencia 5 daba 2.4, al redondear salían meses
repetidos, el `Set` los colapsaba, y el renglón quedaba con 4 meses en rojo por no
cuadrar con su propia frecuencia. Los divisores dan exactamente lo mismo que antes
—verificado— y ahora 1..12 siempre generan `frecuencia` meses distintos.

`arranquesDe()` calcula los ciclos distintos en vez de dividir: con frecuencia 3
son 4, con 5 son los 12 porque el patrón no se repite antes.

Las 12 casillas siguen ahí como **modo avanzado** (el botón *Calendario* de la
fila), cerradas por omisión, para el renglón con meses irregulares. Al picarlas el
arranque pasa a «a mano», la fila se marca, y **los servicios al año se ajustan
solos** a los meses que quedaron marcados: si escoges cuatro meses son cuatro
servicios. Antes había que corregir el número aparte y el renglón se quedaba en
rojo por no cuadrar consigo mismo. Vaciarlos todos no lo baja a cero — cero
servicios al año no significa nada.

Los tres iconos de la fila (*Calendario*, *Duplicar*, *Borrar*) llevan su etiqueta
en un globito de CSS, no en `title`: el nativo tarda casi un segundo y con tres
iconos seguidos nadie adivina cuál es cuál mientras espera.

### El segurista no es un equipo

Un renglón cuyo concepto dice «segurista» es una PERSONA supervisando, no un
equipo que reciba mantenimiento. Su dinero es un renglón cotizado normal, pero
**no entra al seguimiento**: no cuenta en programados/hechos/atrasados —sin esto
sus meses vivirían en rojo para siempre—, en el calendario aparece como nota
(«Incluye segurista») en los meses cubiertos, sus chips no son botones y el modal
de servicio lo rechaza.

Se detecta **por el concepto** (`esSegurista`), no con una bandera en la partida,
a propósito: `partidas` está congelada por la regla del servidor en las pólizas
vivas, y agregarle un campo dejaría a un Analyst sin poder guardar nada en una
activa.

En el calendario, el **porqué de un mes parcial va en el globito** (y en el
registro al picar), no inline: el texto largo rompía las tarjetas angostas. La
fracción «4 de 5» sí queda visible — es la señal operativa.

### Cobranza

Las casillas del detalle son **botones**, y abren `modalCobroPoliza()` con el mismo
molde que la captura de mensualidades de Forpass: la OC es obligatoria, queda quién
capturó y cuándo, y un cobro ya capturado **se puede reabrir para corregirlo o
deshacerlo**. Lo único distinto es que el monto sale de `montos[]`, y cuando es la
última casilla el modal avisa que lleva el residuo del reparto.

Debajo aparece una tabla con lo ya capturado —monto, OC, quién, cuándo, si está
facturada—, que es lo que se cuadra contra el cliente.

Capturar cobranza en una póliza activa **pasa el congelado de precios** porque no
toca `partidas`. Eso depende de que `normalizarPoliza` sea idempotente; si dejara
de serlo, un analyst no podría capturar ni una OC.

### Servicios ejecutados

El gemelo de la cobranza: registrar que un mantenimiento **ya se hizo**. Se llega
por dos lados, y los dos importan:

- **Los chips de meses del detalle** son botones: uno por renglón y por mes. Sirve
  cuando ya sabes qué equipo vas a marcar.
- **El calendario** (`modalCalendario`), donde cada equipo del mes es un botón. Es
  el que se usa de verdad —el técnico va un mes y atiende varios equipos— así que
  al guardar **se vuelve a abrir el calendario** para seguir marcando sin salir y
  entrar. Cancelar desde ahí también regresa: abrir un equipo y arrepentirse no te
  puede sacar de la lista que venías recorriendo.

Dos diferencias con el cobro:

- **La fecha se captura**, no es la del momento. Un cobro se registra cuando llega
  la OC, pero un mantenimiento se marca el lunes y se hizo el viernes: poner la del
  sistema sería mentir en el papel que se le enseña al cliente. Se propone una
  fecha **dentro del mes de la vigencia** (hoy si estamos en ese mes, si no el
  día 1), y no se acepta una futura: un servicio no se marca por adelantado.
- **Un renglón con cantidad > 1 se marca POR UNIDADES.** El modal pinta un botón
  por unidad, todos prendidos; se apagan los que no se atendieron y el porqué se
  vuelve obligatorio. Se guarda `hechas` (cuántas) y `motivo` (por qué faltaron)
  en el registro del mes — las unidades de un renglón consolidado son idénticas,
  así que se guarda el CUÁNTAS, nunca cuáles. Cero prendidos no se puede guardar:
  eso no es un servicio, es no marcar el mes. Un registro viejo sin `hechas`
  significa «todas» y `normalizarPoliza` lo materializa así (idempotente, y
  `hechas` se acota a `[1, cantidad]`; `motivo` se tira si quedó completo). El
  parcial se ve en el chip del detalle (ámbar, «4/5», porqué en el globito) y en
  el calendario («4 de 5» con el porqué al lado).

Deshacer usa `confirmar()` y **reabre el calendario con un tick de retraso**:
`confirmar()` corre su callback y *después* cierra el modal, así que abrirlo ahí
mismo lo abriría para cerrarlo en la misma línea.

El listener de los botones del calendario se cuelga **dentro** de
`modalCalendario`, no fuera: `cerrarModal()` reemplaza `#modalCuerpo` por un clon,
así que el listener se va con él y no se acumula. Colgarlo una vez al arrancar
apuntaría al nodo viejo.

### Lo que se quitó, y por qué no vuelve

- **Balancear calendario.** Repartía los arranques para aplanar la carga. Se quitó
  porque **los mantenimientos de cada equipo están programados por el equipo, no
  por la carga de trabajo**: moverlos para que el año quede parejo cambia el
  compromiso con el cliente. La barra de "servicios por mes" se fue con él (además
  tapaba los botones cuando había pocos renglones).
- **Copiar de otra póliza.** La idea era clonar los 13 sitios de Mercado Libre.
  **Cada cocina es distinta**: no hay dos iguales, así que copiar dejaba más
  trabajo de corrección que de captura.

Si alguien las quiere de vuelta, están en el historial de git — pero el motivo por
el que se fueron es de negocio, no técnico.

### Un cliente, dos módulos

La colección `clientes` es **una sola** —así una empresa con kioscos y pólizas es un
solo registro, con un solo logo— pero **cada módulo lista solo los que le tocan**
(`clientesDeForpass()`): un cliente que existe nada más porque se le cotizó una
póliza no ensucia la lista de Forpass con "0 sitios". Forpass avisa cuántos hay
escondidos ("2 más solo con póliza") para que no parezca que se perdieron.

El que **no tiene nada** sí aparece en Forpass: ahí es donde se crean, y esconderlo
mientras le capturas el primer sitio sería peor. El selector del modal de póliza
ofrece **todos**, sin filtrar: para cotizar necesitas poder elegir a cualquiera.

### El logo del cliente

El recortador con zoom y la compresión a 256 px / 120 KB son **los de Forpass, sin
duplicar nada**: `modalCliente()` tal cual. Se llega desde el **detalle** de la
póliza, en el renglón del cliente, y solo desde ahí — es el único lugar del módulo
donde abrir otro modal no destruye una captura en curso.

El ＋ Nuevo del modal de captura solo pide el nombre (por lo mismo: `prompt` en vez
de modal), y el aviso dice dónde subir el logo después.

En la **tarjeta** de la lista el avatar es un botón que lleva al mismo modal — es
donde el ojo busca la foto. Se ve idéntico al avatar normal; la única pista es el
cursor y el globito. Para Viewer no es botón, pero el logo se ve igual.

### El calendario, y por qué hay diálogos del navegador

`modalCalendario()` pinta doce tarjetas con qué equipos toca atender cada mes, cuál
ya se hizo y cuál cayó fuera de calendario. Contesta la pregunta operativa del
módulo —"qué hay que hacer este mes"—, que en la tabla de captura no se ve porque
ahí la vista es por renglón.

**Dentro del modal de la póliza se usa `window.confirm` y `window.prompt`, no
`confirmar()`.** No es descuido: `confirmar()` llama a `abrirModal`, que reemplaza
`#modalCuerpo`, así que **borraría toda la captura en curso**. El sistema de
modales es de uno a la vez. Feo pero seguro.

### La captura es una tabla, no tarjetas

Una fila por equipo con los campos editables en la celda. Empezó como una tarjeta
por renglón y **no escalaba**: MXGT01 tiene 79 renglones. Y consolidar es correcto
porque **todas las unidades del mismo tipo comparten calendario** — verificado en
el calendario de INOAC, que tiene 12 renglones para 12 tipos y el `ESTUFÓN` de
cantidad 2 aparece una sola vez. Queda "duplicar renglón" para el caso raro.

El pie de totales va **fuera** del contenedor que se recorre a lo ancho: los
totales son lo que más se mira y no pueden quedar escondidos a la derecha.

Los equipos que más se cotizan salen como **chips** debajo del buscador, a un
clic: se ordenan por cuántas veces aparecen en las pólizas que ya existen, y si no
hay ninguna, por el catálogo. Teclear el nombre completo de los de siempre era el
trabajo tonto de la captura.

Los renglones se agregan **de a muchos**: junto a "Agregar otro" hay una casilla
para el número, porque picar el botón cuarenta veces es absurdo. El tope es
`MAX_RENGLONES = 150` —MXGT01, la más grande de verdad, trae 79 sin consolidar—.
Ese número se midió, no se adivinó: a 150 renglones (1,043 campos) pintar la tabla
tarda 34 ms, quitar un renglón 14 ms y **una tecla 0.2 ms**. Lo último solo se logra
porque `refrescar(idx)` actualiza UN renglón cuando se teclea; recorrer los 150 en
cada tecla sí se sentía.

### Congelado de precios

No es convención, es mecanismo. La regla de Firestore exige que en una póliza que
no está en `cotizacion` ni `enviada`, `partidas` salga **idéntica** a como entró.
Capturar cobranza y servicios pasa; tocar un precio no. Cerrar y reabrir es de
Owner/Admin, y `fechaCierre` es la marca visible (se limpia al reabrir, y eso
descongela).

> Que **los servicios** pasen no salió gratis: costó sacar `hechos` de dentro de
> `partidas` y subirlo al nivel de la póliza. Mientras vivió adentro, esta línea
> era mentira —marcar un mantenimiento cambiaba `partidas`— y nadie lo notó porque
> la pantalla para marcarlos no existía todavía. **Cualquier cosa que se capture
> sobre una póliza viva tiene que ir FUERA de `partidas`.**

**La bitácora es la evidencia**: ya era inmutable por regla (`allow update,
delete: if false`), así que el `precioAnual` del momento de cierre queda ahí y
nadie —ni un Owner— lo puede editar. Sin agregar un campo ni una regla.

Eso obliga a que `normalizarPoliza` sea **idempotente**: si al releer reordenara
algo o cambiara un tipo, la comparación fallaría y un analyst no podría ni capturar
una OC — 403 sin explicación. Probado contra el servidor: escribir, releer y
volver a normalizar no altera un byte. Por eso `mesesServicio` se ordena, las
llaves de `hechosDetalle` se recorren **por número** (no alfabéticamente, donde
`"10" < "2"`), y `precioUnitario` se limita al centavo.
