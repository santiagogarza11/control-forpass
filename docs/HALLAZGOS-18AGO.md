# Hallazgos del escaneo completo — 18-ago-2026

Escaneo con 29 agentes: nueve lentes en paralelo (permisos, dinero, fechas,
modales, cola de sincronización, la agenda nueva, el documento imprimible,
inyección de HTML y el congelado de punta a punta) y **un verificador
independiente por hallazgo con la orden de refutarlo** leyendo el código real.
De 27 hallazgos crudos: 18 confirmados + 1 encontrado a mano = **19**, y 2
refutados con evidencia. Cero hallazgos de inyección de HTML: todo lo capturado
pasa por `esc()`.

> ✅ **Los 19 resueltos y verificados ejecutando** (19-ago-2026). Los dos del
> Excel salieron con el OK explícito de Santiago para tocar el generador, y las
> reglas del encargado ya están pegadas en la consola.

**Ninguno es hueco de seguridad** — el servidor siempre gana. Los de permisos
son capturas que se pierden con un aviso confuso: la clase de bug donde la
interfaz ofrece lo que el servidor va a negar.

Cada uno trae la línea del código, el síntoma como lo ve el usuario, la causa y
el arreglo propuesto. Las líneas son del código al 18-ago (rama
`agenda-servicios`).


## Graves (1)

### 1. El bloque de cierre (Precio Anual + notas) se encima con el pie y el corrector nunca lo mueve; con 19–20 renglones el traslape sale impreso EN SILENCIO

> ✅ **Resuelto el 18-ago-2026**, mismo día del escaneo. El corrector ahora mide
> también el final del bloque de cierre y manda filas a una hoja nueva mientras
> invada; la aserción cuenta además `.note` y `.totals`. Verificado con nueve
> casos (17–42 renglones, con y sin descuento): cero invasiones, cero bandas
> falsas, y los casos normales (17, 36) no se movieron.

`plantilla_poliza_forguard.html:808`

- **Cómo se ve:** Probado en navegador con payloads reales: una póliza cuya última hoja de tabla trae 19 o 20 renglones imprime las notas (Vigencia, «Precio más Iva», la cláusula de los doce meses) ENCIMA del bloque de Teléfono/Correo/Oficinas del pie —16 y 45 px de invasión medidos— sin banda roja, sin error en consola y con «Documento completo» reportado. Con 21 a 23 renglones el traslape alcanza a las filas de la tabla de totales y entonces sí sale la banda roja «NO LO MANDES»… sobre una póliza perfectamente válida, sin que el corrector pueda arreglarla. Con descuento activo (dos filas más en el cierre) el problema empieza ~2 renglones antes. Aplica también a pólizas multipágina: 42 renglones dejan 19 en la última hoja (42 = 23+19) y caen en el caso silencioso.
- **Por qué pasa:** evitarTraslapeConPie() solo revisa las FILAS de las tres tablas (TABLAS, líneas 789–793) contra el techo del pie: con 19–23 renglones la última fila de la tabla termina en ~636–700 pt, debajo del límite, así que no mueve nada — pero el cierre que viene después (.totals con margin-top 16px + .note) suma ~90–130 pt más y cruza el techo del pie (~715 pt). Además, verificarRenglonesImpresos() (línea 878) cuenta traslapes solo con '.body tbody tr': las filas de .totals sí son tr (por eso 21+ dispara la banda), pero las notas son un <ul> y su invasión no la ve nadie. Es exactamente la clase de bug que la sesión de Fase 5 peleó («el pie le salía escrito encima del texto») pero para el bloque de cierre en vez de las filas. Los topes de 23/21 filas se midieron para hojas SIN cierre; la hoja que lleva el cierre nunca tuvo tope propio.
- **Arreglo propuesto:** En evitarTraslapeConPie(), después de acomodar filas, medir también el bottom de .totals y .note contra el techo del pie: mientras invadan, mover la última fila de la última tabla grid a la hoja siguiente (creándola con nuevaHojaComo si no existe) y dejar que la relocación de cierre existente (líneas 836–847) lo siga — el while ya remide. Y en verificarRenglonesImpresos() incluir .totals y .note en el conteo de encimados, para que si aun así no cupiera, falle ruidoso y no silencioso.


## Medios (8)

### 2. Un Analyst puede intentar borrar una cotización, pero el servidor niega TODO borrado de pólizas a quien no es Admin

`index.html:7082`

- **Cómo se ve:** Un Analyst le pica al bote de basura de una cotización o de una 'En espera de confirmar', confirma, la póliza desaparece de su pantalla y sale 'Póliza eliminada.' — y después llega el aviso de que la escritura a 'polizas' rebotó con 403. Al recargar, la póliza reaparece. Parece que la app se comió su trabajo.
- **Por qué pasa:** La regla dice `allow delete: if esAdmin();` sin condición (config/firestore.rules línea 134): NINGÚN borrado de póliza pasa para un Analyst, ni siquiera el de un borrador. Pero la interfaz pinta el botón de borrar para todo `puedeEditar()` (línea 3568) y el manejador solo exige Admin cuando `pol.estatus === 'activa'` (línea 7082) — el comentario del código incluso afirma que 'en el servidor es de Owner/Admin' solo para las cerradas, que no es lo que la regla dice. Cotización, enviada, perdida y cancelada quedan ofrecidas al Analyst y negadas por el servidor: borra local, encola el delete, 403, desfase hasta recargar.
- **Arreglo propuesto:** Decidir cuál de los dos manda y alinear: (a) si el Analyst SÍ debe poder borrar sus borradores, la regla cambia a `allow delete: if esAdmin() || (puedeEditar() && resource.data.estatus in ['cotizacion','enviada']);` y el manejador se queda como está; o (b) si borrar es de Admin siempre, el gate de la línea 7082 pierde el `pol.estatus === 'activa' &&` y el botón de la línea 3568 se pinta solo con `esAdmin()`.

### 3. El formulario le ofrece 'Cancelada' a un Analyst, pero el servidor solo le permite mover entre 'cotización' y 'enviada'

`index.html:5963`

- **Cómo se ve:** Un Analyst abre una cotización o una enviada (el selector de estatus está habilitado para él), la marca como 'Cancelada' porque el cliente dijo que no, guarda, y la ve cancelada en pantalla — pero el servidor la rechaza con 403 y al recargar la póliza sigue viva. La captura se pierde en silencio.
- **Por qué pasa:** El selector ofrece ESTATUS_OFRECIDOS = ['cotizacion','enviada','activa','cancelada'] (línea 1141) y se habilita para el Analyst en toda póliza abierta (polizaCongelada solo bloquea las cerradas). Al guardar, cerrarModalActual gatea únicamente `f.estatus === 'activa'` con exigirAdmin (línea 5963); 'cancelada' pasa sin pregunta. En la regla, la cláusula 2 exige que el estatus ENTRE y SALGA en ['cotizacion','enviada'] y la cláusula 3 exige estatus idéntico, así que abierta→cancelada por un Analyst rebota siempre. Es exactamente el patrón que la regla de oro del proyecto prohíbe: la interfaz ofrece lo que el servidor va a negar.
- **Arreglo propuesto:** En cerrarModalActual, junto al gate de 'activa': si `f.estatus === 'cancelada' && p && ESTATUS_ABIERTOS.includes(p.estatus) && !esAdmin()`, cortar con exigirAdmin('cancelar una póliza'). O mejor: construir las opciones del selector según el rol — a un Analyst en póliza abierta solo ofrecerle 'cotizacion' y 'enviada', que es lo único que el servidor le acepta.

### 4. Dos guardados rápidos del mismo registro: el segundo se pierde en silencio

`index.html:1853`

- **Cómo se ve:** Se hacen dos cambios seguidos al mismo registro (marcar un pago y de inmediato palomear 'facturado', o corregir una OC recién guardada). El segundo cambio se ve en pantalla, pero al siguiente refresco de 30 segundos se revierte solo al valor anterior y ya no vuelve: nunca llegó al servidor.
- **Por qué pasa:** Carrera entre encolar() y vaciarCola(). vaciarCola toma op = cola[0] y hace `await escribirNube(...)`. Si durante ese await el usuario vuelve a guardar el MISMO registro, encolar (línea 1817) hace `cola = cola.filter(x => !(x.coleccion === op.coleccion && x.id === op.id))` — quita de la cola la operación en vuelo — y agrega la nueva: cola = [op2]. Cuando el escribirNube de op1 termina, `cola.shift()` (línea 1853) quita cola[0]... que ya es op2, la que nunca se mandó. El servidor queda con op1, la copia local con op2, y el siguiente bajarDeLaNube pisa la copia local con la versión del servidor: el segundo guardado se pierde de forma permanente y sin ningún aviso. La rama de SIN_PERMISO (línea 1843) tiene el mismo shift ciego. La ventana es el tiempo del PATCH (100 ms–segundos en red lenta), alcanzable con dos clics seguidos.
- **Arreglo propuesto:** En vaciarCola, quitar de la cola solo si la operación sigue siendo la misma: en las dos ramas, reemplazar `cola.shift()` por `if(cola[0] === op){ cola.shift(); guardarCola(); }` — si encolar la reemplazó durante el await, no se quita nada y el while vuelve a leer cola[0] (la versión nueva) y la manda.

### 5. La regla permite que cada quien guarde su teléfono, pero 'Mi cuenta' no tiene el campo — y un aviso manda al usuario justo ahí

`index.html:6632`

- **Cómo se ve:** Al crear una cotización sin teléfono en el perfil sale el aviso 'Tu perfil no tiene teléfono. Escríbelo aquí… o guárdalo en Mi cuenta.' El usuario abre Mi cuenta y no hay ningún lugar donde ponerlo: solo nombre, correo, permiso y cambio de contraseña. El teléfono del vendedor hay que teclearlo a mano en CADA cotización nueva, para siempre.
- **Por qué pasa:** config/firestore.rules línea 179 permite explícitamente el self-update de 'telefono' (con comentario que dice que se agregó para que cada quien ponga su celular sin molestar a un administrador), y sesion.telefono se LEE del documento propio al entrar (línea 1626). Pero en todo index.html no existe ninguna escritura de 'telefono' a usuarios/{uid} — el único PATCH propio es ultimoAcceso (línea 1629) — y modalPerfil (línea 6632) no pinta el campo. Es el desfase inverso: el servidor permite algo que la interfaz nunca ofrece, y encima el aviso de la línea 5494 promete que sí existe.
- **Arreglo propuesto:** Agregar en modalPerfil un campo de teléfono que haga PATCH a usuarios/{uid} con updateMask.fieldPaths=telefono (la regla ya lo acepta tal cual), actualizar sesion.telefono al guardar, o — si se decide no hacerlo — quitar del aviso de la línea 5494 la parte de 'o guárdalo en Mi cuenta'.

### 6. Los servicios parciales desaparecen de la agenda: `parcial` y `hechos` se calculan y nunca se usan

`index.html:2751`

- **Cómo se ve:** Un renglón de 5 hornos marcado «4 de 5, faltó 1 porque estaba en uso» no aparece en ningún bloque de la agenda — ni en Atrasados ni en Toca ahora. La unidad que quedó pendiente, con su motivo capturado obligatorio, se vuelve invisible justo en la pantalla que dice «qué toca ahora»; el calendario por póliza sí la pinta en ámbar.
- **Por qué pasa:** agendaServicios() calcula `parcial: !!det && det.hechas < x.cantidad` (línea 2751) y empuja todo item con registro a la lista `hechos` (línea 2753), pero vistaAgenda() solo consume ag.atrasados, ag.ahora, ag.proximos y ag.seguristas — `ag.hechos` y `it.parcial` no se leen en ninguna parte del archivo (verificado con grep). Los dos campos muertos delatan que la intención de enseñar los parciales existió y se quedó a medias. Los números sí cuadran con la portada (calcularPoliza también cuenta un registro parcial como hecho vía servicioHecho), así que no hay desfase de conteos — lo que hay es trabajo pendiente real que ninguna pantalla global enseña.
- **Arreglo propuesto:** Decidir una de dos: (a) pintar los items con `parcial:true` en su bloque por mes con la insignia «4 de 5» (los datos ya viajan en el item), o (b) si se decide que parcial cuenta como hecho también aquí, borrar el campo `parcial` y la lista `hechos` del retorno para no dejar código muerto que promete lo que no hace.

### 7. Una captura hecha mientras baja el refresco de 30 s se revierte en pantalla (y en el arranque con cola pendiente, puede perderse)

`index.html:1887`

- **Cómo se ve:** El usuario guarda algo y medio segundo después el cambio desaparece de la pantalla como si no hubiera guardado; regresa solo hasta 30 segundos más tarde. Peor al abrir la página con capturas offline pendientes: desaparecen del tablero al instante, y si la subida rebota con 403, el aviso dice 'Se quedó guardado aquí' cuando la copia local ya fue machacada.
- **Por qué pasa:** refrescarDesdeNube revisa `if(cola.length || vaciando) return` (línea 7923) ANTES del `await bajarDeLaNube()` (7928), pero la descarga tarda 0.5–2 s (cuatro fetch paginados en Promise.all). Un encolar que caiga dentro de esa ventana no la detiene: bajarDeLaNube termina y en la línea 1887 hace `datos = {…copia del servidor…}` + guardarLocal(), pisando en memoria Y en localStorage la edición recién hecha. La op sigue en la cola y sí llega al servidor, pero la pantalla y la copia local muestran el valor viejo hasta el siguiente refresco. El mismo reemplazo pasa en arrancarNube (7979): con cola pendiente de una sesión offline, bajarDeLaNube pisa la copia local ANTES de que vaciarCola suba — y si esa subida rebota con SIN_PERMISO, la op se descarta (línea 1843) y el dato ya no existe en ningún lado, contradiciendo el aviso de la línea 1845.
- **Arreglo propuesto:** En bajarDeLaNube, justo antes de la línea 1887, agregar `if(cola.length || vaciando) return 'ok';` — con cambios pendientes se sigue trabajando con la copia local y el siguiente refresco (ya con la cola vacía) descarga limpio. Cubre las dos entradas: el refresco de 30 s y el arranque.

### 8. Las hojas interiores de una póliza ACTIVA siguen diciendo «Cotización de Servicios Extras» y «Concepto Cotizado:»

`plantilla_poliza_forguard.html:407`

- **Cómo se ve:** Al imprimir una póliza con estatus 'activa', la portada dice correctamente «Póliza de / Mtto Prev.» (sin «Cotización»), pero las cuatro hojas interiores llevan arriba el eyebrow «Cotización de Servicios Extras» y la etiqueta «Concepto Cotizado:». El cliente recibe un contrato cerrado que se presenta a sí mismo como cotización en cada página menos la primera.
- **Por qué pasa:** armarPayloadPoliza() (index.html línea 2845) resuelve deliberadamente el título según el estatus —«quitarle Cotización es exactamente lo que distingue a la póliza cerrada»— y manda `estatus` en el payload (línea 2869), pero la plantilla nunca lo usa: sheetHead() (línea 407) teclea el eyebrow y la metabar fijos. Los cuatro PDF de referencia eran todos cotizaciones, así que replicarlos no decide qué debe decir una póliza activa; la decisión ya tomada para la portada no se propagó al encabezado de las hojas.
- **Arreglo propuesto:** Que el payload traiga el texto resuelto (p.ej. `eyebrow: estatus==='activa' ? 'Póliza de Servicios' : 'Cotización de Servicios Extras'` y la etiqueta de la metabar), fiel a la regla de que la plantilla no decide títulos, y que sheetHead() lo imprima. Si se confirma que debe decir «Cotización» siempre, documentarlo como decisión junto al título de la portada.

### 9. Guardar cualquier póliza activa exige Admin, sin distinguir cerrarla de reeditarla

`index.html:5963`

- **Cómo se ve:** El aviso ámbar de póliza congelada le dice al Analyst que sí puede corregir el sitio, el folio, el vendedor y las notas — pero al darle Guardar lo detiene «Solo un Admin puede cerrar una póliza como activa». Los dos textos se contradicen en producción.
- **Por qué pasa:** cerrarModalActual gatea `f.estatus === 'activa'` con exigirAdmin sin preguntar si la póliza YA estaba activa. La regla del servidor sí distingue: la cláusula 3 deja a un Analyst reescribir una activa mientras no toque lo congelado, que es exactamente la corrección de textos que el aviso promete.
- **Arreglo propuesto:** Exigir Admin solo en la TRANSICIÓN: `if(f.estatus === 'activa' && (!p || p.estatus !== 'activa'))`. La reedición de una activa pasa a la regla del servidor, que ya la protege campo por campo.


## Bajos (10)

### 10. El candado de 'solo un Admin asigna encargado' vive únicamente en la interfaz: la regla de sitios deja escribir a cualquier Analyst

`index.html:6304`

- **Cómo se ve:** No hay síntoma en la app (la interfaz esconde el botón), pero el candado es de mentira: un Analyst con su propio token puede reasignarse cualquier sitio o quitarle sitios a un compañero con un PATCH directo a /sitios, y el tablero lo mostraría como si lo hubiera hecho un Admin.
- **Por qué pasa:** modalEncargado corta con exigirAdmin (línea 6304) y la etiqueta solo es botón para esAdmin() (línea 3329), pero config/firestore.rules línea 44 dice `allow write: if puedeEditar();` para sitios, sin comparar campos: el servidor acepta que un Analyst cambie 'encargado'. El propio CLAUDE.md del proyecto dice que un cambio de permisos se aplica EN DOS LUGARES y que 'tocar solo la interfaz no es seguridad'; este es el caso que se quedó en uno. El mismo hueco existe con el descuento en pólizas ABIERTAS: la casilla se le esconde al Analyst (línea 5440) pero la cláusula 2 le deja escribir el documento completo, descuento incluido, mientras la póliza esté en cotización/enviada — el congelado del descuento solo opera en las cerradas.
- **Arreglo propuesto:** Si el candado de encargado debe ser real, la regla de sitios necesita una cláusula al estilo de la 3 de pólizas: Analyst pasa solo si `request.resource.data.get('encargado', {}) == resource.data.get('encargado', {})` (con get(), por la trampa documentada del campo ausente). Si se decide que la convención basta, documentarlo como decisión para que nadie lo asuma como candado de servidor.

### 11. La tarjeta y los KPI de pólizas redondean a pesos enteros dinero que trae centavos

`index.html:3554`

- **Cómo se ve:** La tarjeta de la póliza dice «Precio anual $683,134» y al abrirla el detalle dice $683,133.60: la tarjeta enseña 40 centavos que no existen, redondeados hacia arriba. Lo mismo en los KPI: «Pólizas activas — $1,952,850 al año» no cuadra al centavo contra la suma de los detalles. Es exactamente el «no cuadra» que el módulo existe para matar, ahora entre dos pantallas de la misma app.
- **Por qué pasa:** La línea 3554 (tarjeta de póliza) usa dinero(c.precioAnual), y las líneas 3465 y 3467 (KPI 'Pólizas activas' y 'En espera de confirmar') usan dinero(r.valorActivo) y dinero(r.montoEnLaCalle). dinero() hace Math.round a pesos enteros (línea 2349) y su propio comentario (línea 2474-2476) dice que es «el de Forpass» y que las cifras de póliza van con dineroCent porque «casi nunca son redondas». Todo el resto del módulo de pólizas —detalle, cobranza, documento, modal de cobro— usa dineroCent.
- **Arreglo propuesto:** Usar dineroCent() en la línea 3554 y en los dos KPI de las líneas 3465 y 3467 (r.valorActivo y r.montoEnLaCalle ya vienen de precioAnual, que es exacto a centavos).

### 12. El Excel escribe la «Fecha de captura» en horario UTC: un pago capturado en la tarde-noche sale con la fecha del día siguiente

`index.html:7479`

- **Cómo se ve:** Alguien marca una mensualidad como pagada el 18 de agosto a las 6:01 pm o más tarde (hora de Monterrey). En la pantalla el detalle dice «18 ago 2026»; al descargar el Excel, la hoja «Pagos con OC» dice 19 de agosto en «Fecha de captura». El mismo pago tiene dos fechas según dónde se mire.
- **Por qué pasa:** `pagosDetalle[m].cuando` se guarda con `new Date().toISOString()` (línea 6882), que es un sello en UTC — Monterrey va 6 horas atrás, así que de las 18:00 en adelante el texto ISO ya trae la fecha de mañana (18-ago 8:30 pm → «2026-08-19T02:30:00Z»). La pantalla lo muestra con `fechaHora()`, que convierte a hora local y da el día correcto; pero el Excel hace `String(d.cuando).slice(0, 10)` en la línea 7479, que corta la fecha UTC cruda sin convertirla. Es exactamente el corrimiento de día por zona horaria que el repo prohíbe («las zonas horarias corren los días»), colado por la puerta del timestamp.
- **Arreglo propuesto:** En la línea 7479, en lugar de rebanar el texto ISO, convertir el timestamp a fecha local antes de pasarlo a `cF()`: un pequeño helper que haga `const t = new Date(d.cuando)` y arme `t.getFullYear() + '-' + … getMonth()/getDate()` con getters locales (el mismo patrón de `hoyISO()`), o reusar la parte de fecha de `fechaHora()`. Alternativa equivalente: guardar junto al timestamp la fecha local del día de captura.

### 13. El refresco de 30 s roba el foco al que está escribiendo en un buscador (incluida la agenda nueva)

`index.html:7930`

- **Cómo se ve:** Estás escribiendo en el buscador de la agenda (o el de clientes, pólizas o equipos) y, si un compañero cambió algo en ese medio minuto, la pantalla se redibuja: el texto tecleado se conserva, pero el cursor sale del campo a media palabra y lo que sigas tecleando no va a ningún lado. Si el desplegable de horizonte estaba abierto, se cierra solo.
- **Por qué pasa:** Los cuatro buscadores (buscaCliente, buscaPoliza, buscaEquipo y el buscaAgenda nuevo) sí usan renderConservandoFoco en su propio 'input' (líneas 4111–4129), pero el render que dispara refrescarDesdeNube cuando `JSON.stringify(datos) !== antes` (línea 7930) es un render() pelón: rehace #vista completo y el input activo se destruye. El valor sobrevive porque el HTML lo pinta de estado.busca, pero el foco y la posición del cursor no. La guardia de la línea 7924 solo cubre modales (telon), no un buscador con foco. El render de revisarCuenta al detectar cambio de rol (línea 1680) tiene el mismo hueco, aunque es un evento raro.
- **Arreglo propuesto:** En refrescarDesdeNube, antes del render: si document.activeElement es uno de los buscadores conocidos, guardar su id y selectionStart y, tras render(), volver a enfocar y restaurar el cursor — la misma mecánica de renderConservandoFoco (línea 4196), reutilizándola con el elemento activo.

### 14. La primera sincronización de un Analyst intenta subir el catálogo, que solo un Admin puede escribir

`index.html:7995`

- **Cómo se ve:** Escenario estrecho: alguien capturó en modo local (donde la app se comporta como Owner y deja guardar catálogo y cerrar pólizas), y la primera cuenta que conecta contra un servidor vacío es un Analyst. Sale 'Subiendo al servidor lo que tenías capturado…' y de inmediato el aviso de que la escritura a 'catalogo' rebotó con 403 — y si en local se cerró alguna póliza como activa, esa también rebota (el create de Analyst solo acepta cotización/enviada).
- **Por qué pasa:** arrancarNube llama subirTodo() con el gate `puedeEditar()` (líneas 7994–7995), y subirTodo encola el catálogo (línea 2000) y todas las pólizas tal cual estén, pero la regla de /catalogo exige esAdmin (rules línea 147) y el create de pólizas limita al Analyst a estatus abiertos (rules líneas 116–118). En modo local `esAdmin()` devuelve true (línea 1507), así que esos datos pueden existir legítimamente en el navegador.
- **Arreglo propuesto:** En subirTodo (o en su llamada de la línea 7995), encolar el catálogo solo si esAdmin(); y para un Analyst, avisar en vez de encolar las pólizas locales cuyo estatus no esté en ESTATUS_ABIERTOS, para que un Admin haga esa primera subida.

### 15. El estado vacío de la agenda miente cuando sí hay pólizas activas: «Cierra una cotización como activa» con todo ya registrado o con la activa vencida

`index.html:3925`

- **Cómo se ve:** Con una póliza activa cuyos 12 meses de servicio ya están todos registrados, la agenda dice «Todavía no hay servicios programados — La agenda se llena con las pólizas activas. Cierra una cotización como activa…», cuando lo cierto es que está todo al día. Y con una única activa ya vencida, el botón «Agenda» de la portada sí se ofrece y lleva a ese mismo mensaje falso.
- **Por qué pasa:** La condición de la línea 3925 (`!ag.atrasados.length && !ag.ahora.length && !ag.proximos.length`) no distingue «no hay pólizas activas» de «hay activas pero todo está hecho»: en el segundo caso todos los items caen en ag.hechos (que existe y no se consulta) y las tres listas quedan vacías. Además, el botón «Agenda» en vistaPolizas (línea 3449) se ofrece con `p.estatus === 'activa'` a secas, mientras agendaServicios filtra con `c.activa` (estatus Y vigente, línea 2736): una activa vencida enseña el botón que desemboca en el vacío engañoso.
- **Arreglo propuesto:** En el estado vacío, ramificar con `ag.hechos.length`: si hay hechos, decir «Todos los servicios de las pólizas activas ya están registrados» en vez de pedir cerrar una cotización. Y alinear el gate del botón Agenda de la línea 3449 con el mismo criterio `calcularPoliza(p).activa` que usa la agenda.

### 16. En el Excel, «Primer pago» y «Valor del contrato» van tecleados aunque la hoja promete columnas vivas

`index.html:7401`

- **Cómo se ve:** La fila de instrucciones del Excel dice «Las columnas calculadas se actualizan solas al abrir el archivo», pero si alguien corrige la Mensualidad, el Onboarding o los Viáticos en el archivo (el Excel reemplazó al Control_Forpass_2.xlsx que sí se editaba a mano), «Primer pago ($)» y «Valor del contrato ($)» se quedan con el número viejo sin ningún aviso — dinero desactualizado en la hoja que se comparte.
- **Por qué pasa:** En construirHoja, las líneas 7401-7402 escriben cN(c.primerPago, 7) y cN(c.valorContrato, 7): totales derivados (mensualidad + extras, y mensualidad × meses + extras) tecleados como número estático, mientras Pagados, Pendientes, Debió pagar, Estatus y Días restantes sí van como fórmulas (líneas 7395-7398, 7405). Es el caso exacto de la regla del propio CLAUDE.md: «el total del renglón va como fórmula, no tecleado».
- **Arreglo propuesto:** Emitirlas como cX con referencias calculadas por L(): Primer pago = colMensualidad + colOnboarding + colViáticos de la misma fila; Valor del contrato = colMensualidad*meses + colOnboarding + colViáticos (meses es estructural, va como literal igual que en la fórmula de Pendientes). Usar c.primerPago y c.valorContrato como caché, igual que las demás fórmulas.

### 17. El calendario de una póliza ya terminada sigue marcando su mes 12 como «este mes» para siempre

`index.html:5246`

- **Cómo se ve:** Una póliza activa cuya vigencia terminó en marzo se abre en agosto con el botón de calendario (que se ofrece en todos los estatus): la tarjeta de su último mes («feb 26») aparece resaltada con la insignia «este mes», cinco meses después de que el contrato acabó. Se lee como que todavía toca trabajar ahí.
- **Por qué pasa:** `modalCalendario` calcula `mesActual = Math.min(MESES_POLIZA - 1, mesesTranscurridos(p.fechaInicio, hoy))` sin revisar si la vigencia sigue viva. Con 17 meses transcurridos el `Math.min` lo deja clavado en 11, y la comparación `esAhora = z.m === mesActual` (línea 5279) prende la insignia del mes 12 eternamente. En `calcularPoliza` existe el mismo clamp (línea 2625) pero ahí no estorba porque sus consumidores —la agenda nueva y `resumirPolizas`— filtran por `c.activa` antes de usar `mesActual`; el modal del calendario es el único que lo pinta sin ese filtro.
- **Arreglo propuesto:** En la línea 5246, considerar también el fin de la vigencia: `const mesActual = diasEntre(p.fechaInicio, hoy) < 0 || diasEntre(hoy, c.fin) < 0 ? -1 : Math.min(MESES_POLIZA - 1, mesesTranscurridos(p.fechaInicio, hoy));` — con -1 ningún mes se marca «este mes», que es la verdad de una póliza terminada. `c` ya está calculada dos líneas arriba.

### 18. En pólizas que arrancan el 29, 30 o 31, el día frontera propone una fecha de servicio de un mes atrás mientras la agenda dice «toca ahora»

`index.html:5067`

- **Cómo se ve:** Póliza con vigencia desde el 31 de enero. El 28 de febrero la agenda y el calendario dicen que el servicio del mes 1 «toca ahora» (correcto: su mes corre hasta fin de febrero), pero al picar el equipo para registrarlo, el campo «Fecha en que se hizo» llega pre-llenado con 31 de enero — cuatro semanas atrás — en vez de hoy. Si quien captura no se fija, el servicio queda registrado con fecha de enero, y esa fecha es la que se le enseña al cliente.
- **Por qué pasa:** Hay dos definiciones del «mes de la vigencia» conviviendo: `mesesTranscurridos` (estilo DATEDIF: el mes N termina cuando el día del mes iguala o rebasa el día de inicio) gobierna `mesActual`/`mesesCumplidos` en la agenda y el calendario, mientras `dentroDelMes` en la línea 5067 usa el intervalo `[sumarMeses(inicio, mes), sumarMeses(inicio, mes+1))`. Con días 1–28 coinciden siempre; con inicios en día 29/30/31 el recorte de `sumarMeses` (31 ene + 1 mes = 28 feb) las desalinea exactamente en el día recortado: el 28 de febrero `mesesTranscurridos(31-ene, 28-feb)` da 0 (el mes 0 sigue en curso), pero `diasEntre(hoy, sumarMeses(inicio,1)) > 0` da falso porque hoy ES la frontera recortada. `dentroDelMes` queda en falso y `propuesta` cae a `inicioMes` (31 de enero) en lugar de `hoy` (línea 5068).
- **Arreglo propuesto:** Alinear `dentroDelMes` con el mismo juez que usa todo lo demás: `const dentroDelMes = diasEntre(inicioMes, hoy) >= 0 && mesesTranscurridos(p.fechaInicio, hoy) === mes;` — así la frontera del mes la decide `mesesTranscurridos`, igual que en la agenda, el calendario y la cobranza, y la definición del mes vive en un solo lugar.

### 19. Un payload al que le falte cualquier campo no validado deja la página EN BLANCO con el botón «Guardar como PDF» vivo, en vez de la hoja «Sin datos»

`plantilla_poliza_forguard.html:706`

- **Cómo se ve:** Si el payload trae renglones/calendario/totales pero le falta cualquiera de los otros campos que la plantilla desreferencia (descripciones, cliente, fechas, vendedor, contacto, pie, titulo), el render truena a medias, #doc queda vacío y lo único visible es la barra negra con el botón verde: darle imprime hojas en blanco. No sale ni el documento ni la hoja «Sin datos» con su motivo.
- **Por qué pasa:** leerPayload() (línea 369) solo valida `renglones`, `calendario` y `totales`; el render de la línea 706 no tiene try/catch, así que un TypeError en pageCover()/pageDescripcion() aborta la asignación de innerHTML y el aviso de impresión no se quita (la línea 713 solo lo quita cuando !POLIZA). El escenario realista es el desfase de versiones ya documentado: la plantilla SIEMPRE se abre fresca (?v= del momento) pero el index.html se sirve cacheado hasta 10 minutos, así que un tablero viejo puede alimentar una plantilla nueva que exija un campo que ese payload aún no traía — hoy es hipotético campo por campo, pero el módulo tiene más fases anunciadas y el payload va a seguir creciendo.
- **Arreglo propuesto:** Envolver la construcción del documento en try/catch y, si truena, pintar pageSinDatos('Los datos llegaron de una versión distinta del tablero: recarga el tablero (Cmd+Shift+R) y vuelve a imprimir.') y quitar el banner — el mismo camino que ya existe para payload ausente. Opcional: validar meta.version contra la que la plantilla espera.

## Refutados por el verificador (no son bugs)

- **«Editar una póliza activa sin fecha de cierre le inventa una y da 403»** — el
  403 no puede ocurrir: la interfaz corta antes con exigirAdmin. (De esa revisión
  salió el hallazgo real de arriba sobre el guardado de activas.)
- **«Los indicadores y la agenda cuentan pólizas distintas»** — era cierto y se
  arregló durante el mismo escaneo: la agenda usa el mismo `c.activa` que los
  indicadores, verificado con una póliza vencida inyectada.
