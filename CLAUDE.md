# Control de Forpass · CRM de kioscos

Tablero interno de **Forguard** para administrar los kioscos Forpass instalados
en los clientes: cuántos hay por sitio, en cuánto se fue cada uno, cuándo toca
cada mensualidad, con qué orden de compra se pagó y quién lleva cada cuenta.

- **En línea:** https://santiagogarza11.github.io/control-forpass/
- **Repo de la página** (público): `santiagogarza11/control-forpass`
- **Repo de respaldos** (privado): `santiagogarza11/control-forpass-backups`

Nació para reemplazar un Excel de captura manual (`Control_Forpass_2.xlsx`), y
sigue exportando a ese mismo formato para reportar.

---

## Cómo está armado

Tres piezas separadas, y conviene tenerlas claras porque se confunden:

| Pieza | Qué hace | Dónde vive |
|---|---|---|
| **La página** | Entrega el HTML y corre toda la lógica en el navegador | GitHub Pages |
| **La base de datos** | Guarda la información y las cuentas | Firebase (proyecto `control-de-forpass`) |
| **El respaldo** | Copia diaria de todo | GitHub Actions → repo privado |

GitHub Pages **solo sirve archivos**, no guarda nada. Toda la información vive en
Firebase; el navegador le habla directo.

### Un solo archivo, a propósito

Todo es **`index.html`** (~3,600 líneas). Adentro van embebidas las fuentes
Poppins, el logo de Forguard, los estilos, la lógica y hasta el generador de
Excel. **No hay dependencias, ni build, ni `npm install`.**

Se habla con Firestore y con Auth por **REST con `fetch`**, sin el SDK de
Firebase. Fue decisión deliberada: mantiene la página como un archivo que se
abre solo, funciona sin internet en modo local, y no tiene nada que actualizar.

Al editar: se hace en `index.html` directo. No hay paso de compilación — el
commit a `main` es lo que se publica.

---

## Estructura

```
index.html              ← toda la app (aquí se queda: es lo que Pages sirve)
README.md
config/firestore.rules  ← reglas de seguridad (se pegan a mano en la consola)
docs/CONECTAR-SERVIDOR.md
CLAUDE.md
```

`ControlForpassBackups/` es el **repo privado de respaldos**, que quedó anidado
dentro de esta carpeta. Está en `.gitignore` a propósito: adentro van clientes,
precios y pagos, y este repo es público. **Nunca debe entrar aquí.**

---

## Cómo funciona

### Login y permisos

Al abrir pide correo y contraseña (Firebase Auth, email/password). La sesión se
queda abierta y se renueva sola; solo la vuelve a pedir si cierras sesión, si te
revocan el acceso, o desde otra computadora. El correo se recuerda entre
sesiones para que solo se teclee la contraseña.

Cuatro permisos, en `ROLES`:

| Rol | Ve | Modifica | Panel de cuentas | Notas |
|---|---|---|---|---|
| **Owner** | ✅ | ✅ | ✅ | Nadie lo puede degradar ni bloquear. Único que nombra otro Owner. |
| **Admin** | ✅ | ✅ | ✅ | No puede tocar a un Owner. |
| **Analyst** | ✅ | ✅ | ❌ | Captura clientes, sitios y pagos. |
| **Viewer** | ✅ | ❌ | ❌ | Solo consulta y baja el Excel. |

El rol vive en `usuarios/{uid}` en Firestore, no en Auth. **Se aplica en dos
lugares y hay que cambiar los dos**: la interfaz (`esOwner`, `esAdmin`,
`puedeEditar`, `exigirPermiso`, `exigirAdmin`) y `config/firestore.rules`. Tocar
solo la interfaz no es seguridad — el botón se esconde pero el servidor acepta.

**Respaldar y restaurar** son solo de Owner y Admin: mueven toda la base de golpe.
Descargar Excel sí lo puede hacer cualquiera; es la herramienta del día a día.

### Control de kioscos

**Cliente** → tiene logo (recortable con zoom, se reduce a 256 px y se
recomprime antes de guardar) → **Sitios**.

Cada **sitio** guarda: nombre, **zona** (CDMX, GDL, MTY… lista sugerida pero
acepta cualquier texto) con uno de 10 colores de etiqueta, Forpass instalados,
estado, tipo de contratación, mensualidad, extras, fechas, y:

- **`encargado`** — quién de Forguard lleva el sitio. Etiqueta que asoma por el
  borde de la tarjeta. Todos la ven; solo Owner y Admin asignan, eligiendo de las
  cuentas reales del equipo.
- **`contactos`** — quién del cliente manda la OC (nombre, puesto, correo,
  teléfono). Ícono de persona; se pinta ámbar cuando falta.

### Mensualidades

Los contratos van de 1 a **24** mensualidades (`MAX_MESES`), 12 lo normal.

**El onboarding y los viáticos se cobran una sola vez, en el pago 1.** Del mes 2
en adelante es solo la mensualidad. Esto está centralizado en `calcular()`, que
devuelve `montos[]` con el importe de cada mes — el dinero cobrado y el vencido
se suman de ese arreglo, nunca multiplicando la mensualidad.

Al marcar una mensualidad como pagada se pide **número de OC** (obligatorio) y
**quién captura** (su cuenta, no editable), más una casilla de **ya se facturó**.
Cada pago guarda su propio `{oc, quien, cuando, facturado}` en `pagosDetalle`.
Volver a hacer clic en una mensualidad pagada la reabre para corregir la OC,
marcar la factura después, o deshacerla.

El semáforo por sitio: **Atrasado** (rojo) si hay mensualidades vencidas sin
pagar, **Por pagar** (ámbar) si la siguiente cae en 7 días o menos, **Al día**
(verde), **Contrato cubierto**, o **Pausado/Baja**.

Los tres puntos junto al nombre abren el **plan de pagos**: mes por mes con su
importe, concepto, estado, OC y quién capturó.

### Excel

Dos hojas, generadas a mano armando el ZIP y el OOXML — sin librerías:

- **Control Forpass** — una fila por sitio, con el formato del Excel original.
  Las columnas de mes crecen según el contrato más largo que se exporte (12
  normalmente, hasta 24). Las columnas calculadas van como **fórmulas vivas**
  (`TODAY()`, `DATEDIF`, `SUM`) para que el archivo siga actualizándose.
- **Pagos con OC** — un renglón por mensualidad, con OC, quién capturó, si está
  facturada. Es la hoja para cuadrar pagos contra órdenes de compra.

**Las letras de columna de las fórmulas se calculan, nunca se escriben a mano.**
Al agregar una columna en medio, todo lo de después se corre y las fórmulas
quedarían apuntando en falso.

### Respaldos

Un robot en GitHub Actions corre **3 veces al día** (03:00, 09:00 y 15:00 de
Monterrey), lee Firestore con una cuenta de servicio, y guarda
`backups/AAAA-MM-DD.json` más `backups/ultimo.json` en el repo **privado**.

- Los archivos salen con la **misma forma que el botón "Respaldo JSON"** del
  tablero, así que se restauran directo desde la página.
- Si nada cambió desde la copia anterior, no genera commit.
- Deja la fecha en `sistema/respaldo` de Firestore; el tablero la lee y **avisa en
  la portada si el respaldo tiene más de 2 días** (`DIAS_RESPALDO_VIEJO`).
- **No hay limpieza automática.** Se acumulan: pesan ~67 KB cada uno y borrarlos
  no recuperaría espacio (Git guarda toda la historia de todos modos).

Restaurar **reemplaza el servidor para todo el equipo**. Antes de hacerlo,
descargar un Respaldo JSON del estado actual.

### Deploy

Commit a `main` → GitHub Pages publica solo, en 1–3 minutos.

**Si un cambio no aparece, revisa que el build no haya fallado** (`Settings →
Pages`, o `gh api repos/.../pages/builds/latest`). Ya pasó dos veces por caídas
de GitHub, no por el código. Se puede pedir reconstrucción con
`gh api -X POST repos/santiagogarza11/control-forpass/pages/builds`.

---

## Decisiones importantes

**Un solo archivo sin dependencias.** Cero mantenimiento, funciona offline, nada
que actualizar. El costo es un `index.html` grande; se asumió a gusto.

**Firebase por REST, sin SDK.** Para no romper lo anterior.

**El `apiKey` va en claro y no es secreto.** Es un identificador público de
Firebase, va dentro de cualquier página. Lo que protege los datos son las reglas
más el login. Está restringido por dominio en Google Cloud (solo
`santiagogarza11.github.io/*` y `control-de-forpass.firebaseapp.com/*`).
GitHub manda alertas de "secreto expuesto" por esa llave: son falsos positivos.

**La cuenta de servicio del respaldo SÍ es un secreto real.** Da acceso total y
se salta todas las reglas. Vive solo en el secreto `CUENTA_SERVICIO` de GitHub
Actions. Nunca en el código, nunca por chat. *(Una se filtró por chat el 5 de
agosto de 2026; se revocó y se verificó que Google la rechaza.)*

**Los respaldos van en repo privado aparte.** El de la página es público:
committear ahí clientes, precios y pagos los publicaría para siempre, porque
quedan en la historia de Git aunque se borren después.

**Las reglas de Firestore se pegan a mano.** No hay Firebase CLI en el proyecto.
`config/firestore.rules` es la fuente de verdad; se copia a la consola.

**Modo local como respaldo del diseño.** Con `CONFIG_NUBE` vacío, la página
funciona guardando solo en el navegador, sin cuentas. Sirvió para desarrollar y
sigue siendo la salida si algún día se abandona Firebase.

**La primera conexión no pierde datos.** Si el servidor está vacío pero el
navegador tiene capturas, se suben en vez de borrarse.

**Nadie se puede borrar a sí mismo** ni quitarse su propio permiso: dejaría el
tablero sin dueño y sin vuelta.

---

## Trampas conocidas (ya nos mordieron)

**`leerForm()` solo devuelve los campos del formulario.** `normalizarSitio`
rellena en blanco lo que no venga, así que al guardar una edición hay que
**arrastrar explícitamente** `pagosDetalle`, `contactos` y `encargado`. Sin eso,
editar un sitio borraba todas las OC. Lo mismo aplica a cualquier campo nuevo que
se administre fuera del formulario.

**`cerrarModal()` reemplaza `#modalCuerpo` por un clon limpio** para tirar los
listeners. Consecuencia: **leer un campo del formulario después de cerrar el
modal devuelve `null`**. Hay que leer los valores antes.

**Listeners delegados en `#modalCuerpo` van una sola vez**, fuera de la función
que redibuja. Si se conectan dentro, se acumulan y una acción se ejecuta N veces.

**Cachés del panel de admin (`admin.usuarios`, `admin.bitacora`) se llenan desde
varios lados.** `modalEncargado` también carga `usuarios`. Al decidir si saltarse
una consulta hay que revisar **todas** las cachés que se van a usar.

**Solo se cierra sesión por problemas de la cuenta, nunca por red.** Un fetch
fallido sin internet no debe sacar al usuario: se trabaja con la copia local y se
reintenta. Ver `esFalloDeRed()` y `manejarFalloDeArranque()`.

**Fechas como texto `AAAA-MM-DD`**, con helpers propios (`sumarMeses`,
`diasEntre`, `mesesTranscurridos`). No usar `Date` para aritmética de meses: las
zonas horarias corren los días.

---

## Qué falta por hacer

**Dominio propio.** Hoy es `santiagogarza11.github.io/control-forpass`. Se puede
apuntar un subdominio (tipo `forpass.forguard.mx`) gratis con GitHub Pages. Falta
decidir el dominio y agregar un registro DNS. **Si se hace, hay que agregar el
dominio nuevo a las restricciones de la llave en Google Cloud**, o el login deja
de funcionar.

**Dar de alta al equipo.** Hoy solo existe la cuenta Owner de Santiago. Se hace
desde Admin → Crear cuenta, sin tocar la consola de Firebase.

**Limpieza de respaldos viejos** (opcional). Se propuso conservar uno diario los
últimos 30 días y de ahí uno mensual, solo por orden en la lista. Sin urgencia.

**Detalle cosmético.** El historial dice *"entró **el** sesión"* en vez de *"entró
**a la** sesión"*. Pulir cuando se toque esa zona.

### Ideas que quedaron en el aire

- Hacer clicables más indicadores, como ya lo es "Vigencias por vencer".
- Una vista de "mis sitios" filtrando por encargado desde la portada, no solo
  dentro de un cliente.
- Filtro por zona, ahora que los sitios la tienen.

---

## Al trabajar en esto

- **Probar en el sitio en vivo, no solo leer el código.** Varios bugs se veían
  perfectos en el diff y solo aparecieron al ejecutarlos.
- **Verificar el deploy antes de decir "ya quedó".** El commit puede estar
  publicado y el build fallado.
- **Explicar en términos simples.** Santiago es nuevo en código: describir qué
  hace algo y por qué, no cómo está implementado, salvo que lo pida.
- **Avisar cuando algo tarda.** Cada deploy son 1–3 minutos de espera.
