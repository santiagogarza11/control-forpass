# Control de Forpass · CRM de kioscos

Tablero interno de **Forguard**: kioscos Forpass por cliente, precios,
mensualidades, órdenes de compra y quién lleva cada cuenta. Reemplazó un Excel
manual (`Control_Forpass_2.xlsx`) y sigue exportando a ese formato.

- **En línea:** https://santiagogarza11.github.io/control-forpass/
- **Repo página** (público): `santiagogarza11/control-forpass`
- **Repo respaldos** (privado): `santiagogarza11/control-forpass-backups`

## Arquitectura

| Pieza | Dónde vive |
|---|---|
| La página (HTML + toda la lógica) | GitHub Pages — solo sirve archivos |
| Datos y cuentas | Firebase, proyecto `control-de-forpass` |
| Respaldo 3×/día | GitHub Actions → repo privado |

**Todo es `index.html`** (~7,700 líneas): fuente Manrope, logo, estilos, lógica,
animaciones y generador de Excel embebidos. Sin dependencias, sin build, sin
`npm install`. Firestore y Auth por **REST con `fetch`**, sin SDK. Commit a
`main` = deploy (1–3 min).

```
index.html              ← toda la app
config/firestore.rules  ← se pegan a mano en la consola (no hay Firebase CLI)
scripts/lector-pdf/     ← herramienta suelta, NO es parte de la app
docs/CONECTAR-SERVIDOR.md · docs/POLIZAS.md · docs/ESTADO-POLIZAS.md
docs/plantilla_poliza_forguard.html · docs/poliza-*.json
README.md · CLAUDE.md
```

`scripts/lector-pdf/` es Python que se corre a mano para sacar los datos de una
cotización hecha en Canva. **La app sigue sin dependencias**: eso no se carga en
el navegador ni se despliega.

`ControlForpassBackups/` está anidado aquí pero es el repo privado. Está en
`.gitignore` a propósito: **nunca debe entrar a este repo público.**

## Marca

Tomada de forguard.com. Si allá cambia algo, cámbialo aquí o se desfasan.

| | Valor |
|---|---|
| Navy | `#002369` · oscuro `#00143D` · medio `#103580` |
| Acento (la firma de la marca) | verde `#54C682` |
| Neutros | texto `#5D5D5D` · línea `#E4E7EC` · fondo `#F6F7F9` |
| Tipografía | **Manrope**, variable (un `@font-face` cubre 400–800) |

Manrope **no trae cursivas** y el tablero no usa ninguna: si hace falta una, hay
que traer el archivo italic o el navegador la inclina y se ve mal.

**La obra del logo vive una sola vez**, en un sprite `<svg><defs><g id="fgArte">`
al inicio del `<body>`. El encabezado y la pantalla de carga la usan con `<use
href="#fgArte">`. El logo del login tiene copia propia porque anima sus grupos
por separado. Va oculto con `width/height 0` y **no** con `display:none`: con
eso último algunos navegadores no resuelven las referencias de `<use>`.

## Funcionalidad

**Roles** (`ROLES`, guardados en `usuarios/{uid}` de Firestore, no en Auth):

| Rol | Ve | Edita | Panel cuentas | |
|---|---|---|---|---|
| Owner | ✅ | ✅ | ✅ | intocable; único que nombra Owner |
| Admin | ✅ | ✅ | ✅ | no puede tocar a un Owner |
| Analyst | ✅ | ✅ | ❌ | captura clientes, sitios y pagos |
| Viewer | ✅ | ❌ | ❌ | consulta y baja el Excel |

Un cambio de permisos se aplica **en dos lugares**: la interfaz (`esOwner`,
`esAdmin`, `puedeEditar`, `exigirPermiso`, `exigirAdmin`) **y**
`config/firestore.rules`. Tocar solo la interfaz no es seguridad — el botón se
esconde pero el servidor acepta. Respaldar/restaurar: Owner y Admin. Excel:
cualquiera. Nadie se puede borrar ni degradar a sí mismo.

**Cliente** (logo recortable con zoom, se reduce a 256 px) → **sitios**. Cada
sitio: nombre, zona (texto libre con lista sugerida, 10 colores de etiqueta),
Forpass instalados, estado, tipo de contratación, mensualidad, extras, fechas,
`encargado` (quién de Forguard lo lleva; solo Owner/Admin asignan) y `contactos`
(quién manda la OC del lado del cliente).

**Mensualidades:** de 1 a 24 (`MAX_MESES`), 12 lo normal. Onboarding y viáticos
se cobran **una sola vez, en el pago 1**. Está centralizado en `calcular()`, que
devuelve `montos[]` con el importe de cada mes — sumar de ahí, **nunca**
multiplicar la mensualidad. Cada pago guarda `{oc, quien, cuando, facturado}` en
`pagosDetalle`; la OC es obligatoria y un pago pagado se puede reabrir para
corregirlo. Semáforo por sitio: Atrasado / Por pagar (≤7 días) / Al día /
Contrato cubierto / Pausado-Baja. Los tres puntos abren el plan de pagos.

**Portada:** 5 indicadores. Los tres de cobranza abren su detalle
(`modalCobranza`, `modalPorVencer`) y **solo se ofrecen cuando hay algo que ver**
— un "Ver cuáles" con cero adentro decepciona. Los dos primeros son sumas y no
abren nada a propósito. En la tarjeta del cliente, un sitio pausado y un contrato
ya cubierto llevan insignias distintas: sin eso los dos se veían como "0 Forpass
activos · $0", que son situaciones opuestas. **El logo del encabezado es atajo a
Clientes** (`btnInicio` → `irAClientes`): el instinto es picarle ahí para volver.
Queda deshabilitado en la portada para salir del recorrido del teclado, y
funciona también en el panel de admin.

**Mi cuenta** (`modalPerfil`): nombre, correo, permiso con su descripción y la
lista concreta de lo que ese rol puede hacer (`loQuePuedeHacer`). Desde ahí se
cambia la contraseña: **se pide la actual** — no es trámite, sin eso quien
encuentre una laptop con la sesión abierta podría cambiarla y dejar fuera al
dueño. Ese re-login además entrega el token fresco que Firebase exige, y hay que
**guardar los tokens nuevos** que devuelve o el cambio saca al usuario justo
después de hacer todo bien.

**Excel:** ZIP y OOXML armados a mano, sin librerías. Hoja *Control Forpass*
(una fila por sitio; las columnas de mes crecen según el contrato más largo; las
calculadas van como fórmulas vivas con `TODAY()`, `DATEDIF`, `SUM`) y *Pagos con
OC* (un renglón por mensualidad, para cuadrar contra órdenes de compra). **Las
letras de columna de las fórmulas se calculan, nunca se escriben a mano.**

**Respaldos:** 03:00, 09:00 y 15:00 de Monterrey, con cuenta de servicio, a
`backups/AAAA-MM-DD.json` y `backups/ultimo.json`. Salen con la misma forma que
el botón "Respaldo JSON", así que se restauran desde la página. Si nada cambió
no hay commit. La fecha queda en `sistema/respaldo`; el tablero avisa en la
portada si pasan `DIAS_RESPALDO_VIEJO` (2). No hay limpieza automática (~67 KB
c/u). Restaurar reemplaza el servidor para todo el equipo: bajar un respaldo
antes.

## Pólizas de mantenimiento preventivo

Segundo producto: mantenimiento preventivo a cafeterías industriales. Se cotiza
listando equipos y, cuando el cliente acepta, **esa misma cotización se vuelve
póliza activa** — el mismo documento en otro momento, distinguido por `estatus`,
igual que un sitio usa `estado`.

**El detalle completo está en [docs/POLIZAS.md](docs/POLIZAS.md).** Léelo antes de
tocar cualquier cosa del módulo. Lo mínimo que hay que saber:

- **Un solo lugar calcula el dinero:** `totalRenglon()` = precio × cantidad ×
  frecuencia. **Ningún total se guarda nunca.** No hay campo de descuento.
- **La cobranza se reparte en centavos enteros** (`repartirCentavos`) y el residuo
  va a la última casilla, para que las doce sumen el anual exacto.
- **Colecciones nuevas:** `polizas` y `catalogo` (un solo documento,
  `catalogo/lista`). Las reglas se pegan a mano — ver `config/firestore.rules`.
- **Los precios se congelan por regla de servidor** cuando la póliza sale de
  `cotizacion`/`enviada`. Eso exige que `normalizarPoliza` sea **idempotente**.
- **Selector de módulo en el encabezado** (`estado.modulo`), donde antes estaba el
  `<h1>`. `render()` despacha por módulo y luego por vista; admin va antes de los
  dos. Cambiar de módulo es UN render.
- **Hay UN descuento**, en porcentaje, a nivel de póliza y solo de Owner/Admin.
  Nunca toca `totalRenglon()`, se guarda solo el %, **siempre se imprime como
  renglón** y está congelado por regla igual que los precios. Ver POLIZAS.md.
- **Servicios por unidad**: un renglón de 5 equipos se marca «4 de 5» con el
  porqué obligatorio. Vive en `hechos`, fuera de `partidas`.
- **El segurista no es un equipo**: se detecta por el concepto (`esSegurista`),
  no cuenta en el seguimiento y el calendario lo anuncia como «Incluye segurista».
- **El documento imprimible ya funciona de punta a punta**: botón Imprimir en el
  detalle (todos los estatus, todos los roles), portada réplica medida, y el papel
  sale bien **sin tocar un ajuste del diálogo** de Chrome.

**Decisiones cerradas — no se reabren sin motivo nuevo:**

| Decisión | Por qué |
|---|---|
| Lo ejecutado va en **`hechos`, al nivel de la póliza**, llaveado por id de partida → mes | dentro de `partidas` la regla de congelado impedía que un Analyst marcara un servicio en una póliza activa: 403 justo en el único momento en que se marcan |
| Cada partida trae **`id` estable**, y nada se llavea por posición | mover el calendario recorría los registros de mes en silencio; duplicar o borrar un renglón haría lo mismo un nivel arriba |
| **Plazo fijo en 12** (`MESES_POLIZA`), sin campo `meses` | la cláusula impresa dice "doce (12) meses" y el calendario del documento tiene 12 columnas clavadas |
| **Cinco estatus**: `cotizacion → enviada → activa`, más `perdida` y `cancelada` | "terminada" y "por vencer" se derivan de las fechas, como los sitios no guardan "Contrato cubierto" |
| **Congelado de precios por regla de servidor**, no por convención | la interfaz sola no es seguridad; la regla exige que `partidas` salga idéntica |
| **Descuento solo en porcentaje, a nivel de póliza, de Owner/Admin y SIEMPRE impreso como renglón** *(reabierta 14-ago-2026)* | lo que rompió MXGT01 no fue el descuento sino que viviera escondido en el Total Mtto de cada renglón. Nunca toca `totalRenglon()`, solo se guarda el %, y está congelado por regla igual que los precios |
| **El total siempre derivado**, nunca guardado | ni `precioAnual` ni el total de un renglón. Guardar un total calculado es cómo se llega a que no cuadre |
| **El catálogo es colección** (`catalogo/lista`), un documento con el arreglo | los precios los edita el equipo, así que persisten; uno y no 48 para que sea 1 lectura |
| **Un solo `clientes`**, cada módulo filtra el suyo | una empresa con kioscos y pólizas es un registro con un solo logo |

## Vigilancia de la cuenta

Bloquear a alguien escribe `activo:false` en `usuarios/{uid}`. **Desde el
navegador NO se puede deshabilitar la cuenta de Auth** —eso pide el Admin SDK—
así que esa bandera de Firestore es la única señal que existe. El servidor la
respeta al instante, pero la app del bloqueado ya tiene todo en memoria: sin
vigilancia seguiría viendo un tablero que ya no le toca hasta recargar.

`revisarCuenta()` corre por tres disparadores, del más barato al más frecuente:

| Disparador | Costo | Cuándo actúa |
|---|---|---|
| 403 del servidor | gratis | al instante, en cuanto intenta algo |
| `visibilitychange` al volver a la pestaña | gratis | cuando retoma el trabajo |
| Reloj de `VIGILAR_CUENTA_MS` (2 min) con la pestaña visible | 1 lectura | el respaldo |

Cuesta **~240 lecturas al día por persona**; con un equipo de 10 son ~2,400, un
5% del tope gratuito. Subir el intervalo lo abarata.

Funciona porque **un usuario siempre puede leer su propio documento aunque esté
bloqueado**: la regla lo permite por uid sin exigir `activo`.

También detecta **cambios de rol**, y en ese caso **no desconecta**: actualiza
`sesion.rol`, avisa, y saca del panel de admin si ya no le toca. `arrancarVigilancia()`
al entrar, `detenerVigilancia()` al salir.

## Animaciones

Tres momentos, todos con el logo de la marca y todos respetando
`prefers-reduced-motion`:

| Momento | Qué hace | Duración | Constante |
|---|---|---|---|
| Login | El escudo se ensambla y el nombre se descubre | 3.7 s | los `dur` del SVG `#logoAcceso` |
| Al entrar | El logo se llena de navy y vuela al encabezado | 1.6 s mínimo | `CARGA_MINIMA_MS` |
| Al salir | Persiana que baja, drena el logo y sube | 2 s | `PERSIANA_MS` + `PERSIANA_CUBRE_MS` |

**Lo que gobierna cuánto se ve la pantalla de carga es `CARGA_MINIMA_MS`, no el
`dur` del llenado.** El llenado es un ciclo infinito, así que da igual cuánto
tarde la red; al llegar los datos `completarLlenado()` lo termina en 240 ms y
`volarAlEncabezado()` lo manda al header. El mínimo es un piso, nunca un techo.

**La entrada escalonada de las tarjetas corre solo al cambiar de vista**, nunca
en cada redibujado (`animarTarjetas`, clase `.grid.sin-entrada`). `render()`
rehace `$('vista').innerHTML` completo, y al arrancar corre varias veces: si la
animación se reinicia en cada una, las tarjetas se ven desaparecer y reaparecer.
Se prende en `entrarCliente()` e `irAClientes()`, y se apaga al final de
`render()`. **Excepción:** si la pantalla de carga está encima, ese render pasó
tapado y nadie lo vio, así que sí hay que animar el siguiente.

## Decisiones

- **Un archivo sin dependencias.** Cero mantenimiento, funciona offline, nada
  que actualizar. El costo es un `index.html` grande; se asumió a gusto.
- **Los totales derivados no se guardan.** Ni `precioAnual`, ni el total de un
  renglón. Guardar un total calculado es cómo se llega a que no cuadre.
- **Selector de módulo en el encabezado, no portada con dos botones.** Una portada
  sería un clic extra al entrar, todos los días, para siempre.
- **Para probar en local hay que autorizar `localhost` en la llave.** El `apiKey`
  está restringido por dominio, así que el login rebota desde `file://` y desde
  `http://localhost:8000` con *"Requests from referer … are blocked"*. Se agrega
  `http://localhost:8000/*` en Google Cloud → Credenciales. Firestore no lo
  necesita —va con `Bearer`—, solo el login. Esa restricción no es una barrera de
  seguridad: se pasa forjando el `Referer` con `curl`. Sirve contra que otro sitio
  reuse la llave; lo que protege los datos son las reglas y el login.
- **El `apiKey` va en claro y no es secreto** — es un identificador público de
  Firebase, restringido por dominio en Google Cloud (`santiagogarza11.github.io/*`
  y `control-de-forpass.firebaseapp.com/*`). Lo que protege los datos son las
  reglas más el login. Las alertas de GitHub por esa llave son falsos positivos.
- **La cuenta de servicio del respaldo SÍ es secreta.** Da acceso total y se
  salta todas las reglas. Vive solo en el secreto `CUENTA_SERVICIO` de Actions.
  Nunca en el código, nunca por chat. *(Una se filtró por chat el 5-ago-2026; se
  revocó y se verificó que Google la rechaza.)*
- **Respaldos en repo privado aparte**: este es público y Git guarda la historia
  para siempre, aunque se borre después.
- **Modo local**: con `CONFIG_NUBE` vacío la página guarda solo en el navegador,
  sin cuentas. Es la salida si algún día se abandona Firebase. La primera
  conexión sube lo capturado en local en vez de borrarlo.
- **"Sigue con la contraseña inicial" se deduce, no se guarda.** Se comparan dos
  fechas que Firebase ya tiene (`createdAt` vs `passwordUpdatedAt` de
  `accounts:lookup`). **No agregar una bandera en Firestore:** obligaría a tocar
  las reglas —que se pegan a mano— y sería un dato más que se desincroniza. Ver
  `revisarClaveInicial()` y `claveEsInicial`.

## Trampas conocidas (ya nos mordieron)

- **En una regla de Firestore, un campo ausente NO es vacío: es un ERROR, y un
  error deniega.** La cláusula 3 del congelado comparaba
  `request.resource.data.descuento == resource.data.descuento` con acceso por
  punto. El descuento se agregó el 14-ago y **ninguna de las seis pólizas que ya
  existían lo tenía guardado**, así que la comparación reventaba y el servidor
  rechazaba TODO sobre una póliza cerrada —incluso reescribir el documento sin
  cambiar un solo valor—. Un Analyst no podía capturar una OC ni marcar un
  servicio: justo el único momento en que se marcan. Se arregló con
  `get('descuento', 0)` en las dos puntas. **La regla general:** en la cláusula 3
  un error de evaluación estorba a quien SÍ tiene permiso, así que ahí todo campo
  va con `get()`; en la cláusula 2, en el `create` y en `/usuarios` un error
  deniega a quien no debía pasar y fallar cerrado es lo correcto. Cualquier campo
  nuevo al nivel de la póliza que se compare en la cláusula 3 va con `get()`.
- **Firestore no devuelve las llaves de un mapa en orden estable.** Dos lecturas
  seguidas del MISMO documento sin cambios dan `JSON.stringify` distintos. Por eso
  «`partidas` sale byte por byte igual» no es literal: comparadas canónicamente
  —ordenando llaves— sí son idénticas, y a la regla le da igual porque compara
  valores, no texto. Verificar idempotencia comparando cadenas crudas **produce
  falsas alarmas**: en la sesión del 18-ago dijo dos veces que las partidas habían
  cambiado cuando el `updateTime` ni se había movido.
- **Al agregar una colección hay que tocar SIETE lugares**, y el respaldo es el
  que se olvida. Con `polizas`: las reglas (a mano en la consola), `datos`,
  `cargar()`, `limpiarSesionYDatos()`, `bajarDeLaNube()`, `subirTodo()`, el
  respaldo JSON y el **robot del repo privado**. Faltó `limpiarSesionYDatos` y
  `datos.polizas` quedaba en `undefined` al cerrar sesión. Y el script del robot
  escribía las colecciones **a mano** en el archivo de salida: agregarla a
  `COLECCIONES` no bastaba —la bajaba, la contaba, la imprimía en el log y la
  dejaba fuera del archivo—. Ahora se arma de `datos`, un solo lugar.
- **Un 403 se disfraza de problema de cuenta.** `pedirNube` trata CUALQUIER 403
  como "te quitaron el acceso", y eso solo es cierto si viene de algo que sí
  deberías poder leer. Pasó tres veces en una sesión: la lectura de
  `catalogo/lista` sin su regla pegada respondía 403 —no 404, así que
  `permitirVacio` no ayudaba—, `manejarFalloDeArranque` lo leía como cuenta sin
  acceso y **no se podía entrar**. De pasada disparaba `revisarCuenta()`, que
  anunciaba un cambio de permiso que nadie había hecho. Cada colección nueva
  necesita que su lectura se aísle en su propio try/catch: **un dato de comodidad
  no puede tumbar el login.** Ver `leerCatalogo()`.
- **Un 403 de escritura NO es pasajero y no se debe reintentar.** La cola lo
  reintentaba para siempre: el tablero decía "cambios pendientes" a perpetuidad,
  estorbaba al cerrar sesión, y el aviso genérico culpaba a la cuenta cuando lo
  que faltaba era publicar una regla. Ahora se saca de la cola y el aviso dice
  **cuál** colección falló.
- **Nada debe escribir solo al arrancar.** La siembra del catálogo era automática
  y, sin la regla pegada, envenenaba la cola de quien entrara. Un botón no le
  puede hacer eso a nadie sin que se haya pedido.
- **`confirmar()` desde dentro de un modal borra la captura.** Llama a
  `abrirModal`, que reemplaza `#modalCuerpo`. El sistema de modales es de uno a la
  vez, así que dentro del modal de la póliza se usan `window.confirm` y
  `window.prompt`: feos, pero no tocan el DOM.
- **Borrar código por rangos de texto se lleva lo que no era.** Al quitar
  "balancear calendario" y "copiar de otra póliza" con cortes de índice a índice
  se fueron con ellos CUATRO listeners del modal (`pInicio`, `pFacturacion`,
  `pCliente`, `btnClienteNuevo`). Síntoma: mover la vigencia no movía el
  calendario y el resumen no se actualizaba. Después de borrar por rango,
  **contar los listeners que deben quedar.**
- **Los meses del calendario de un PDF de Canva no son texto**: son trazados
  `m`/`l`/`h f` con color de relleno, y la posición viene del CTM (`cm`) con su
  pila `q`/`Q`, no de `Tm`. Ver el lector de la Fase 3B en el traspaso.
- **El color que un PDF DECLARA no es el que PINTA.** La marca de agua de la
  portada declara relleno `#002369` y lo pinta aplanado a `#021449` — hay una
  transparencia encima que las herramientas de extracción no reportan. Para
  replicar, el color se toma del **píxel renderizado**, no del vector declarado;
  el vector da la geometría, el render da el color. (Es el primo del JPEG que
  desplazó el navy: ninguna fuente única dice toda la verdad.)
- **La portada es réplica medida y va en Helvetica del sistema** — la única
  excepción a Poppins, a propósito: replica el documento descargado tal cual y
  con Helvetica Neue el acento de la ó se dibuja distinto (lo cachó un panel de
  jueces). Sus medidas viven en `docs/ESPECIFICACION-DOCUMENTO.md` §Portada; la
  calibración vertical del título (−5.2) se midió tinta contra tinta y se
  recalibra midiendo, no calculando.
- **Los PDF de referencia son reimpresiones de macOS, no exportaciones de Canva**
  (el productor lo dice). Tres de los cuatro **perdieron la tipografía** y quedaron
  en Helvetica; solo INOAC conserva Poppins. Y la página declara **1275×1650**, que
  es **Carta a 150 DPI**: todo el archivo está a escala 2.0833×, así que el cuerpo
  de la tabla parece de 15 pt y es de **7.2 pt**. Medir sin dividir da un CSS al
  doble de tamaño. Ver `docs/ESPECIFICACION-DOCUMENTO.md`.
- **Las cuatro cotizaciones no comparten columnas.** MXNL02 y MXGT01 traen Marca y
  no Cantidad, INOAC al revés, NGK tiene siete columnas. **"El formato actual" no
  existe**: el documento nuevo imprime las **siete de NGK** —`#` · Concepto ·
  Cantidad · Precio Unitario · Total · Frecuencia · Total Mtto—, con la marca
  pegada al concepto. Es el único que imprime la aritmética completa, y sus 17
  renglones la cumplen. Tampoco comparten el **orden de hojas**; el adoptado es
  Portada → Tabla → Descripción → Calendario → Consideraciones.
- **`overflow:hidden` en una hoja del documento recorta datos en silencio.** Lo
  tenía y MXGT01 imprimía **27 de sus 36 equipos** —más el bloque de Precio Anual
  fuera del papel— con la hoja viéndose llena y bien formada. Ya no está y no
  vuelve. Tres de las cinco hojas se parten: tabla a 23 filas, calendario a 21, y
  la descripción **por altura medida**, porque sus filas no son de alto fijo. Hay
  una aserción permanente —`verificarRenglonesImpresos()`— que cuenta lo impreso
  contra el payload y, si no cuadra, pinta una banda roja que **también sale en el
  papel**. Un documento que se ve roto vale mil veces más que uno que se ve bien y
  le faltan nueve equipos.
- **En la plantilla, `querySelector('tbody')` no devuelve el que crees.** El
  encabezado de cada hoja lleva su propia `<table class="metabar">` y el navegador
  le inserta un `<tbody>` implícito, así que un selector pelón agarra ESE. Por eso
  el molde de la paginación no se vaciaba y la segunda hoja salía con la lista
  entera repetida. Siempre `table.grid.desc tbody`, nunca `tbody` solo.
- **Las cotizaciones en PDF traen errores humanos, y la portada miente.** La de
  Nexxus dice «MXGT01» porque la copiaron de la anterior: un script que le crea al
  PDF habría machacado `docs/poliza-MXGT01.json` en silencio. El lector no
  sobreescribe un JSON existente, y las correcciones a mano viven en
  `CORRECCIONES` de `consolidar.py` —llaveadas por *(sitio, renglón del papel)*—
  para que **sobrevivan a volver a leer el PDF**. La regla para corregir es
  estrecha: **solo donde el documento se contradice a sí mismo** (la columna de
  servicios dice una cosa y el calendario otra). Que el mismo equipo cueste
  distinto en dos clientes **no** es un error, es un precio: el renglón manda.
- **Un arreglo paralelo se desalinea cuando el otro cambia.** El registro de
  servicios empezó como arreglo paralelo a `mesesServicio` y mover el calendario
  recorría los registros de mes sin error y sin aviso. Si lo que indexa puede
  cambiar, **llavea por el dato, no por la posición**. (`pagos[]` de sitios tiene
  la misma limitación: cambiar `meses` trunca por posición. Ahí duele menos porque
  es una casilla, no historial de trabajo.)
- **Lo que se capture sobre una póliza viva tiene que ir FUERA de `partidas`.** La
  regla de congelado exige que `partidas` salga idéntica, así que cualquier cosa
  guardada ahí adentro deja de poder escribirse en cuanto la póliza se activa —y
  solo para quien no es Admin, que es el peor de los modos de fallar—. El registro
  de servicios vivía adentro y habría dado 403 al Analyst justo en el único momento
  en que se marcan servicios. Se subió a `hechos`, al nivel de la póliza, como ya
  estaba `cobrosDetalle`. **`docs/POLIZAS.md` afirmaba lo contrario durante toda
  una fase** y nadie lo cachó porque la pantalla no existía: la única forma de
  saberlo fue medir si el `partidas` que se reenvía cambiaba, antes de escribirla.
- **Al subir un campo fuera de `partidas`, `leerForm()` deja de arrastrarlo.**
  Mientras el historial de servicios vivió dentro de cada partida viajaba solo;
  arriba hay que sumarlo a mano al objeto `conservado` de `modalPoliza`, junto a
  `cobros` y `cobrosDetalle`, o editar una póliza le borra el historial. Es la
  misma trampa que ya documentada para los sitios, un nivel más arriba.
- **Doce sumas de flotantes no dan el total.** Ver la sección de pólizas: el
  dinero que se reparte va en centavos enteros.
- **Un `<h1>` deja de ser cierto cuando la app crece.** Decía "Control de
  Forpass" y con el módulo de pólizas era mentira la mitad del tiempo.
- **`renderConservandoFoco` tenía el id del buscador clavado.** Cualquier segundo
  buscador necesita que se le pase el suyo, o el foco salta al de Forpass.
- **`leerForm()` solo trae los campos del formulario** y `normalizarSitio`
  rellena el resto en blanco. Al guardar una edición hay que **arrastrar
  explícitamente** `pagosDetalle`, `contactos` y `encargado` — y cualquier campo
  nuevo que se administre fuera del formulario. Sin eso, editar un sitio borra
  sus OC.
- **`cerrarModal()` reemplaza `#modalCuerpo` por un clon limpio** para tirar los
  listeners: leer un campo después de cerrar devuelve `null`. Leer antes.
- **Listeners delegados en `#modalCuerpo` van una sola vez**, fuera de la función
  que redibuja. Adentro se acumulan y una acción corre N veces.
- **El manejador de `data-accion` vive en `#vista`**, y el encabezado está fuera:
  un botón de la cabecera necesita su propio listener.
- **Cachés del panel de admin** (`admin.usuarios`, `admin.bitacora`) se llenan
  desde varios lados; `modalEncargado` también carga `usuarios`. Revisar todas
  las que se van a usar antes de saltarse una consulta.
- **Solo se cierra sesión por problemas de la cuenta, nunca por red.** Un fetch
  fallido sin internet trabaja con la copia local y reintenta. Ver
  `esFalloDeRed()` y `manejarFalloDeArranque()`.
- **Fechas como texto `AAAA-MM-DD`**, con `sumarMeses`, `diasEntre`,
  `mesesTranscurridos`. No usar `Date` para aritmética de meses: las zonas
  horarias corren los días.
- **Un dato que significa dos cosas produce parpadeos.** `respaldoInfo === null`
  quería decir "no se ha preguntado" **y** "ya se preguntó y no hay nada": el
  aviso se pintaba en cada refresh y al quitarse movía las tarjetas. Se arregló
  con `respaldoRevisado` aparte. Mismo patrón en `claveRevisada`.
- **Cada `render()` extra se paga en pantalla.** Los avisos de portada se revisan
  juntos con un solo render, y solo si el HTML del aviso cambió de verdad. Antes
  eran dos redibujados completos por dos banderitas.
- **Tapar antes de cambiar.** La persiana de logout tarda 840 ms en bajar; si el
  login se muestra en el milisegundo cero, se ve primero y la persiana lo tapa
  después. Ver `PERSIANA_CUBRE_MS` y `salirConPersiana()`. Por lo mismo
  `limpiarSesionYDatos()` está separado de `salir()`: la sesión se borra en el
  milisegundo cero, el login se destapa 840 ms después.
- **En CSS, una animación con `forwards` le gana a una declaración normal.** Para
  desvanecer algo que entró con `animation`, hay que sacarlo con **otra
  animación**, no con un `opacity:0`.
- **`requestAnimationFrame`, las animaciones SMIL y las transiciones CSS no
  corren en pestañas ocultas.** Cualquier promesa que dependa de ellas necesita un
  `setTimeout` de respaldo, o se queda colgada tapando el tablero para siempre. Y
  no se puede medir una animación en una pestaña de fondo: da valores congelados
  que parecen un bug.
- **SMIL arranca al cargar la página.** Si el elemento se muestra después, hay
  que rebobinarlo con `setCurrentTime(0)` o aparece congelado en su fotograma
  final. Ver `reproducirIntro()` y `mostrarCargando()`.
- **Dos `<mask>` o `<clipPath>` con el mismo id y el navegador usa uno solo para
  los dos.** Sufijos: `fgWordMask` (login), `fgClipCarga`, `fgDrenaje`.
- **Un cambio puede estar committeado y el build de Pages fallado.** Verificar
  con `gh api repos/santiagogarza11/control-forpass/pages/builds/latest`;
  reconstruir con `gh api -X POST repos/santiagogarza11/control-forpass/pages/builds`.
- **Paginar prediciendo no basta: hay que medir lo dibujado y corregir.** Los
  topes de 23 y 21 filas y el reparto de la descripción son PREDICCIONES, y
  fallan por cosas que no controlamos —métricas de fuente de cada máquina, un
  tamaño mínimo de letra configurado en Chrome, un concepto larguísimo—. En la
  máquina de Santiago cabía una fila más que en la mía y el pie le salía escrito
  **encima del texto**, en el papel que ve el cliente; medí tres veces en la mía
  y siempre dio limpio. Ahora `evitarTraslapeConPie()` recorre las hojas ya
  pintadas y empuja a la siguiente lo que invada el pie, creando hoja si hace
  falta. Y corre **después de `document.fonts.ready`** (si asientan tarde, los
  altos cambian y el reparto queda viejo) **y otra vez en `beforeprint`**, que es
  el único momento que de verdad importa. La aserción permanente ahora también
  cuenta filas encimadas, no solo filas faltantes.
- **La plantilla del documento se abre con `?v=` del momento, y no es capricho.**
  Pages le manda `cache-control: max-age=600`, y como se abre en **pestaña nueva**
  el `Cmd+Shift+R` del tablero no la alcanza: se arreglaba un defecto del papel, se
  desplegaba, y el PDF seguía saliendo roto diez minutos. Pasó de verdad —con el
  pie encimado sobre la tabla— y costó media hora de medir la copia buena mientras
  el navegador servía la vieja. **Si algo del documento "no se arregló", lo primero
  es descartar la caché.**
- **Tras el deploy el navegador sirve la versión vieja.** El build puede estar
  bien y el DOM tener lo anterior. Refresco forzado (`Cmd+Shift+R`) o `?v=algo`
  al final del link. Al verificar con `curl` no pasa, porque ignora el caché.

## Cuándo se va a trabar (medido, ago-2026)

Un sitio pesa **1.1 KB** y un cliente sin logo **94 bytes**; un logo pesa hasta
**120 KB**. O sea que los logos mandan, no los datos.

| Límite | Aguanta | Qué pasa |
|---|---|---|
| Copia local del navegador (~5 MB) | ~40 clientes con logo de 120 KB, ~250 con logos de 20 KB | Sale "No se pudo guardar en este navegador". Se arregla con código, no pagando: guardar los logos aparte |
| Lecturas de Firebase (50k/día gratis) | ~60–80 clientes con equipo de 8 | Firebase deja de contestar hasta medianoche. Se arregla pasando a plan Blaze: centavos al mes |

Cada carga de página lee **todos** los clientes y sitios (`listarNube` pagina de
300 en 300, así que no se corta en silencio), más ~240 lecturas al día por
persona de la vigilancia de cuenta. Pintar la portada son 1.5 ms hoy; con 500
clientes serían ~125 ms. Nunca va a ser el cuello de botella.

## Pendientes

### Lo primero al abrir sesión (18-ago-2026)

**Nada urgente.** Lo de la sesión anterior quedó cerrado: el deploy de `a1cff59`
sí salió (build `built` sobre `c2afd65`, y el sitio en vivo trae `pDescuento`), y
la rama `servicios-parciales` **ya no existe** —se mergeó a `main` por
fast-forward, así que `main` es todo lo que tenía, pero nunca llegó a `origin`—.
La próxima función arranca rama nueva.

**Fase 4 cerrada el 18-ago** (rama `agenda-servicios`): la Agenda de servicios —
qué toca AHORA en todas las pólizas, en tres bloques (Atrasados / Toca ahora /
Programados) por mes y por sitio, con cada equipo como botón que abre el registro
de siempre. La garantía verificada ejecutando: la agenda y los indicadores de la
portada cuentan las MISMAS pólizas (`c.activa`) y dan los mismos números — con
una vencida inyectada, 18=18 y desaparece de los dos lados. Los textos de
«Admin u Owner» ahora dicen «un Admin» (pedido de Santiago, 7 lugares).

**Fase 5 cerrada el 18-ago.** La geometría de la tabla ya va a los centros medidos
—desviación **0.00 pt** en los siete—, el paso de fila en 21.53 uniforme, los cuerpos
en 7.2 y 6.2, el calendario en su paso de 22.4 y el aviso de captura calibrado en 36
caracteres midiendo lo dibujado. Los topes de 23 y 21 filas se remidieron y se
quedan. Falta **una sola cosa, anotada a propósito**: la tabla arranca 24.3 pt más
abajo que el documento real (parejo, así que no se ve torcida), y subirla exige
rediseñar el encabezado de las cinco hojas. Ver
`docs/ESPECIFICACION-DOCUMENTO.md` §Lo aplicado.

**Cerrado el 18-ago:** el congelado de precios se ejerció por primera vez con un
Analyst real y con un Viewer real, salieron dos bugs —la regla rechazaba también
lo legítimo, y el formulario ofrecía lo que el servidor iba a negar—, los dos
arreglados, desplegados y verificados. El congelado ahora cubre además la
vigencia, la facturación y la fecha de cierre. Reglas pegadas en la consola.

**No hay nada a medias en el servidor.** La prueba del congelado del 18-ago dejó
Prolec como estaba; lo único que cambió es que ya tiene `descuento: 0`, que es un
cero donde antes no había campo.

### Lo que sigue, en orden de valor

1. **Los 18 hallazgos restantes del escaneo del 18-ago** (el grave del documento
   imprimible ya quedó resuelto y verificado el mismo día): siguen los desfases
   interfaz/servidor —«Cancelada» y el borrado ofrecidos a un Analyst, el guardado
   de activas que exige Admin hasta para reeditar— y los dos de la cola. **Lista
   completa con línea, causa y arreglo propuesto en
   [docs/HALLAZGOS-18AGO.md](docs/HALLAZGOS-18AGO.md).** Salieron de 29 agentes
   con verificación adversaria; ninguno es hueco de seguridad.
2. **Segundo documento: evidencia de servicios ejecutados.** El historial de
   `hechos` ya da para el reporte que el cliente pide en auditoría —con el «4 de 5»
   y su motivo—. Es otra plantilla y otra fase; se dejó fuera de la Fase 5 a
   propósito.

### Módulo de pólizas — Fase 3B en adelante

- **Cargar la quinta cotización, Mercado Libre Nexxus.** Extraída y verificada
  ($1,952,850.40 limpio, mismo 5% escondido que MXGT01); Santiago dijo todavía no.
- **Revisar la licuadora industrial de INOAC**: $7,280 contra ~$919 en MXNL02 y NGK.
  No se tocó porque INOAC cuadra exacto con su total impreso — no es contradicción
  interna, y ahí la regla es que el renglón manda.
- **Documento imprimible (Fase 5), en curso.** `docs/plantilla_poliza_forguard.html`
  se abre en pestaña nueva y recibe los datos por `sessionStorage`.
  - **Hecho:** fuentes embebidas (Poppins Regular/Bold/Italic, 30 KB, subconjunto
    latin); el puente `armarPayloadPoliza()` con todo resuelto —la plantilla no
    calcula—; el fallback de "sin datos" con su motivo (nunca demo); la paginación
    de las tres hojas que se desbordan con su aserción permanente; la portada
    réplica medida; y el **botón Imprimir** en el detalle — todos los estatus,
    todos los roles incluido Viewer, con el banner fijo de los tres ajustes de
    Chrome (Márgenes: Ninguno · Encabezados: apagados · **Gráficos de fondo:
    ACTIVADO** — sin el tercero el navy desaparece y parece bug de la app).
  - **Hecho el 18-ago, y con eso la fase cierra:** los siete centros de columna
    con desviación **0.00 pt**, paso de fila 21.53 uniforme, cuerpos 7.2 y 6.2, el
    calendario en su paso medido de 22.4, la columna de contenido en 119.6–561.4, y
    el aviso de captura calibrado en **36 caracteres** midiendo lo dibujado. Topes
    de 23 y 21 filas remedidos: se quedan.
  - **Lo único que queda, anotado a propósito:** la tabla arranca **24.3 pt más
    abajo** que el documento real. Parejo, así que no se ve torcida; subirla exige
    rediseñar el encabezado de las cinco hojas porque la barra de metadatos
    ocuparía el lugar del cuerpo.
  - **La pestaña se debe abrir SIN `noopener`** o no hereda el `sessionStorage` y
    llega vacía.
  - Las medidas reales del documento están en
    [docs/ESPECIFICACION-DOCUMENTO.md](docs/ESPECIFICACION-DOCUMENTO.md): sacadas
    de los cuatro PDF, con lo no extraíble marcado como tal.
- **Decidir qué mensual imprime el documento.** El nominal no cuadra por doce; o
  lleva nota al pie, o imprime la última mensualidad aparte. Es decisión comercial.
- **El 403 del congelado ya se vio de verdad** (18-ago-2026, cuenta Analyst
  `test1`). Los cuatro intentos de romperlo rebotaron: subir un precio, subir una
  cantidad, meter 30% de descuento, y el brinco en dos pasos pasando `activa` a
  `cotizacion`. Y de paso salió el bug de arriba: la regla rechazaba también lo
  legítimo. Lo que **no** está probado es el rol Viewer contra el servidor.
- **Excel de pólizas: no existe y no se tocó a propósito.** Si algún día se agrega
  una hoja, las letras de columna se calculan con `letraCol()`, nunca a mano, y el
  total del renglón va como fórmula, no tecleado.

### Generales

- **Dominio propio.** Verificado ago-2026: el DNS de `forguard.com` está en **AWS
  Route 53** y Santiago **no tiene acceso** — hay que pedir el CNAME. El
  subdominio acordado es **`control.forguard.com`** (`forpass.forguard.com` ya lo
  ocupa el portal del producto: **no tocarlo**). Al hacerlo, agregar el dominio en
  **dos** listas o el login truena: restricciones de la llave en Google Cloud
  **y** *Authorized domains* de Firebase Auth. Orden obligatorio: DNS primero,
  Pages después.
- **El equipo ya está dado de alta** (verificado en el servidor el 18-ago): seis
  cuentas — Santiago (Owner), Roberto y Marcelo (Admin), `test1` y Victor
  (Analyst), Pablo (Viewer). Todas con `activo` y `rol` bien puestos.
- **Falta probar el bloqueo y el cambio de contraseña de punta a punta.** Ya hay
  con qué (nadie se puede bloquear a sí mismo, y ahora sobran cuentas), pero no se
  ha hecho.
- **Outfit para los titulares.** La marca usa dos tipografías (Camber/Outfit para
  títulos, Manrope para cuerpo); hoy todo es Manrope. Camber es de paga; Outfit es
  el respaldo libre que el propio CSS de forguard.com declara. ~18 KB.
- Limpieza de respaldos viejos (opcional, sin urgencia).
- El historial dice *"entró **el** sesión"* en vez de *"entró **a la** sesión"*.
- Ideas sueltas: vista de "mis sitios" por encargado desde la portada, filtro por
  zona, casilla de "recordarme" que permita **no** persistir la sesión en una
  computadora compartida (hoy siempre persiste).

## Al trabajar en esto

- **Los arreglos de bugs se suben directo**, sin preguntar: probar, subir,
  verificar el build y reportar. Las **funciones nuevas** y los cambios de diseño
  sí se muestran antes de subir.
- **Las funciones se trabajan en rama** (decidido 13-ago-2026): `main` es deploy
  inmediato a Pages y el equipo ya tiene datos reales, así que un bloque a medias
  no puede vivir ahí. La rama **se pushea aunque no se mergee** —el trabajo no
  vive solo en una laptop— y se mergea a `main` por bloque completo, ya mostrado.
  Los bugs siguen yendo directo a `main`.
- **Probar en el sitio en vivo**, no solo leer el diff. Varios bugs se veían
  perfectos en el código y solo aparecieron al ejecutarlos.
- **Para ver la app sin cuenta**, copiar `index.html` con `CONFIG_NUBE` vacío
  (modo local) y servirla. Editar **siempre el archivo real**: si se edita la
  copia el cambio no llega a producción, y si se sube la copia se va el `apiKey`
  en blanco y todo el equipo entra a modo local con la base vacía.
- **Verificar el deploy** antes de decir "ya quedó", y decir claramente qué **no**
  se pudo probar.
- **Explicar en términos simples.** Santiago es nuevo en código: qué hace algo y
  por qué, no cómo está implementado, salvo que lo pida.
- **Avisar cuando algo tarda** (cada deploy son 1–3 minutos de espera).
