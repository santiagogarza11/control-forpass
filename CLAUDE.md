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

**Todo es `index.html`** (~4,500 líneas): fuente Manrope, logo, estilos, lógica,
animaciones y generador de Excel embebidos. Sin dependencias, sin build, sin
`npm install`. Firestore y Auth por **REST con `fetch`**, sin SDK. Commit a
`main` = deploy (1–3 min).

```
index.html              ← toda la app
config/firestore.rules  ← se pegan a mano en la consola (no hay Firebase CLI)
docs/CONECTAR-SERVIDOR.md
README.md · CLAUDE.md
```

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

- **Dominio propio.** Verificado ago-2026: el DNS de `forguard.com` está en **AWS
  Route 53** y Santiago **no tiene acceso** — hay que pedir el CNAME. El
  subdominio acordado es **`control.forguard.com`** (`forpass.forguard.com` ya lo
  ocupa el portal del producto: **no tocarlo**). Al hacerlo, agregar el dominio en
  **dos** listas o el login truena: restricciones de la llave en Google Cloud
  **y** *Authorized domains* de Firebase Auth. Orden obligatorio: DNS primero,
  Pages después.
- **Falta probar con dos cuentas.** El cambio de contraseña contra Firebase y el
  bloqueo de accesos no se han probado de punta a punta: hacen falta dos cuentas
  (nadie se puede bloquear a sí mismo). Se desbloquea al dar de alta a la primera
  persona del equipo.
- **Dar de alta al equipo** desde Admin → Crear cuenta. Hoy solo existe el Owner
  de Santiago. El flujo ya está completo: se crea la cuenta, se pasa la
  contraseña, y el tablero mismo le recomienda cambiarla.
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
