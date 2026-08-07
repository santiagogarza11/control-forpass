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

**Todo es `index.html`** (~3,600 líneas): fuentes Poppins, logo, estilos, lógica
y generador de Excel embebidos. Sin dependencias, sin build, sin `npm install`.
Firestore y Auth por **REST con `fetch`**, sin SDK. Commit a `main` = deploy
(1–3 min).

```
index.html              ← toda la app
config/firestore.rules  ← se pegan a mano en la consola (no hay Firebase CLI)
docs/CONECTAR-SERVIDOR.md
README.md · CLAUDE.md
```

`ControlForpassBackups/` está anidado aquí pero es el repo privado. Está en
`.gitignore` a propósito: **nunca debe entrar a este repo público.**

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
- **Cachés del panel de admin** (`admin.usuarios`, `admin.bitacora`) se llenan
  desde varios lados; `modalEncargado` también carga `usuarios`. Revisar todas
  las que se van a usar antes de saltarse una consulta.
- **Solo se cierra sesión por problemas de la cuenta, nunca por red.** Un fetch
  fallido sin internet trabaja con la copia local y reintenta. Ver
  `esFalloDeRed()` y `manejarFalloDeArranque()`.
- **Fechas como texto `AAAA-MM-DD`**, con `sumarMeses`, `diasEntre`,
  `mesesTranscurridos`. No usar `Date` para aritmética de meses: las zonas
  horarias corren los días.
- **Un cambio puede estar committeado y el build de Pages fallado.** Verificar
  con `gh api repos/santiagogarza11/control-forpass/pages/builds/latest`;
  reconstruir con `gh api -X POST repos/santiagogarza11/control-forpass/pages/builds`.

## Pendientes

- **Dominio propio** (tipo `forpass.forguard.mx`), gratis con Pages. Falta
  decidirlo y agregar el DNS. **Al hacerlo hay que agregar el dominio a las
  restricciones de la llave en Google Cloud** o el login deja de funcionar.
- **Dar de alta al equipo** desde Admin → Crear cuenta. Hoy solo existe el Owner
  de Santiago.
- Limpieza de respaldos viejos (opcional, sin urgencia).
- El historial dice *"entró **el** sesión"* en vez de *"entró **a la** sesión"*.
- Ideas sueltas: más indicadores clicables (como "Vigencias por vencer"), vista
  de "mis sitios" por encargado desde la portada, filtro por zona.

## Al trabajar en esto

- **Probar en el sitio en vivo**, no solo leer el diff. Varios bugs se veían
  perfectos en el código y solo aparecieron al ejecutarlos.
- **Verificar el deploy** antes de decir "ya quedó".
- **Explicar en términos simples.** Santiago es nuevo en código: qué hace algo y
  por qué, no cómo está implementado, salvo que lo pida.
- **Avisar cuando algo tarda** (cada deploy son 1–3 minutos de espera).
