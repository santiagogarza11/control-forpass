# Conectar el tablero a un servidor

Hoy la información se guarda **en el navegador** de cada computadora. Siguiendo
estos pasos se guarda en un servidor: todos ven lo mismo, hay cuentas con
permisos, y queda historial de quién cambió qué.

Es gratis. No pide tarjeta. Son unos 10 minutos, **una sola vez**.

Lo único que yo no puedo hacer por ti es crear la cuenta y escribir contraseñas.
Lo demás ya está programado y esperando estos datos.

---

## Paso 1 — Crear el proyecto

1. Entra a **https://console.firebase.google.com** con tu cuenta de Google.
2. **Crear un proyecto** → nombre: `Control Forpass` → Continuar.
3. Cuando pregunte por Google Analytics, **desactívalo** (no hace falta).
4. Espera a que termine y entra al proyecto.

## Paso 2 — Prender la base de datos

1. Menú de la izquierda → **Compilación → Firestore Database**.
2. **Crear base de datos**.
3. Ubicación: **nam5 (us-central)** o la que te ofrezca por defecto.
4. Elige **Iniciar en modo de producción** (cerrado). Las reglas buenas se pegan
   en el paso 5.

## Paso 3 — Prender el acceso por correo y contraseña

1. Menú → **Compilación → Authentication** → **Comenzar**.
2. Pestaña **Sign-in method** → **Correo electrónico/contraseña** → **Habilitar**
   → Guardar. *(Deja apagado «Vínculo de correo electrónico».)*

## Paso 4 — Copiar los dos datos de configuración

1. Arriba a la izquierda, el engrane ⚙ → **Configuración del proyecto**.
2. Baja hasta **Tus apps** → ícono **`</>`** (Web) → nombre `Control Forpass` →
   **Registrar app**.
3. Te va a mostrar un bloque de código. De ahí solo necesitas dos líneas:
   - `apiKey: "AIza…"`
   - `projectId: "control-forpass-xxxx"`
4. Abre `index.html` y pégalas arriba, en el bloque `CONFIG_NUBE`:

```js
const CONFIG_NUBE = {
  apiKey:    'AIza…',
  projectId: 'control-forpass-xxxx'
};
```

5. Sube el cambio:

```bash
git add -A && git commit -m "Conecta el tablero al servidor" && git push
```

> Estos dos datos **no son secretos**: van dentro de cualquier página web de
> Firebase. Quien los vea no puede entrar sin una cuenta autorizada. Lo que
> protege la información son las reglas del paso 5 y el login.

## Paso 5 — Pegar las reglas de seguridad

**Este paso no se puede saltar.** Sin él, la base de datos queda abierta.

1. **Firestore Database** → pestaña **Reglas**.
2. Borra todo lo que haya y pega el contenido completo del archivo
   [`config/firestore.rules`](../config/firestore.rules) de este repo.
3. **Publicar**.

## Paso 6 — Crear tu cuenta de Owner

Esta es la única cuenta que se crea a mano. Desde ella ya puedes crear todas las
demás desde el tablero.

1. **Authentication** → pestaña **Users** → **Agregar usuario**.
   - Correo: `santiago.garza@platoexpress.com`
   - Contraseña: la que tú quieras (mínimo 6 caracteres).
2. Copia el **UID** que aparece en la lista (una cadena larga, tipo
   `k3Jd8sPq...`). Lo necesitas en el siguiente punto.
3. **Firestore Database** → pestaña **Datos** → **Iniciar colección**:
   - ID de la colección: `usuarios`
   - ID del documento: **pega el UID** del punto anterior
   - Agrega estos campos, todos de tipo **string** menos `activo`:

   | Campo         | Tipo    | Valor                             |
   |---------------|---------|-----------------------------------|
   | `correo`      | string  | `santiago.garza@platoexpress.com` |
   | `nombre`      | string  | `Santiago Garza`                  |
   | `rol`         | string  | `owner`                           |
   | `activo`      | boolean | `true`                            |
   | `creado`      | string  | `2026-08-05`                      |
   | `creadoPor`   | string  | `consola`                         |
   | `ultimoAcceso`| string  | *(déjalo vacío)*                  |

4. Guardar.

## Paso 7 — Entrar

Abre https://santiagogarza11.github.io/control-forpass/ — ahora pide correo y
contraseña. Entra con la cuenta del paso 6.

- Arriba a la derecha aparece **Guardado en la nube** y el botón **Admin**.
- Si ya tenías clientes y sitios capturados en esa computadora, **se suben solos**
  al servidor en ese momento. No se pierde nada.
- En **Admin → Crear cuenta** ya puedes dar de alta al resto del equipo.

---

## Los cuatro permisos

| Permiso     | Ve | Modifica | Administra cuentas | Notas |
|-------------|----|----------|--------------------|-------|
| **Owner**   | ✅ | ✅       | ✅                 | Tu cuenta. Nadie la puede bloquear ni bajarle el permiso, y es la única que puede nombrar a otro Owner. |
| **Admin**   | ✅ | ✅       | ✅                 | Puede crear cuentas y dar permisos, menos Owner. |
| **Analyst** | ✅ | ✅       | ❌                 | Captura clientes, sitios y pagos. |
| **Viewer**  | ✅ | ❌       | ❌                 | Solo consulta y descarga el Excel. |

## Sobre las contraseñas

**No se pueden ver, ni tú ni nadie.** Firebase las guarda encriptadas de un solo
sentido; eso es justamente lo que protege las cuentas. En la práctica:

- Al crear una cuenta le pones una **contraseña temporal** y se la pasas. El
  tablero te la muestra una sola vez, con un botón para copiar los datos.
- Si alguien la olvida: **Admin → Mandar correo para cambiarla**, o el enlace de
  «¿Olvidaste tu contraseña?» en la pantalla de entrada.
- Para quitarle el acceso a alguien: **Bloquear**. Es inmediato y la cuenta no se
  borra, la puedes reactivar después.

## Qué pasa si se cae el internet

Los cambios se guardan primero en la computadora y se apuntan en una cola. La
pastilla de arriba dice **Sin conexión · N por guardar**, y en cuanto vuelve la
señal se suben solos. No cierres sesión con cambios pendientes: el tablero te
avisa si lo intentas.

## Respaldos

- Firebase guarda la información en la infraestructura de Google.
- El botón **Respaldo JSON** sigue ahí para tener una copia propia.
- El **Excel** sirve como respaldo legible y para reportar.
