# Control de Forpass · Forguard

Tablero para administrar los kioskos Forpass instalados: por cliente, por sitio,
con su mensualidad, vigencia y estatus de pago.

Es una sola página (`index.html`), sin servidor y sin internet: las fuentes, el
logo y el generador de Excel van embebidos en el archivo.

## Cómo se usa

1. **Agregar cliente** en la portada.
2. Entrar al cliente y **Agregar sitio** (por ejemplo `MXCD13`) con:
   - Forpass instalados (módulos) y estado del sitio.
   - Si se fue como *Software + Hardware* o *Solo Software*.
   - Mensualidad del sitio, y si incluyó **onboarding** y/o **viáticos**.
   - Fecha de inicio y número de mensualidades (la vigencia se calcula sola).
3. Marcar las mensualidades pagadas con las casillas numeradas de cada sitio,
   o con el botón **Marcar pagada**.

La portada muestra Forpass activos, mensualidad total, sitios atrasados,
mensualidades por vencer en 7 días y vigencias que terminan en 45 días.

## Dónde se guarda la información

Funciona de dos maneras según si `CONFIG_NUBE` (arriba de `index.html`) está
lleno o vacío:

**Modo local** (por defecto) — en el navegador de la computadora que la captura.
Para moverla: **Respaldo JSON** descarga todo y **Restaurar** lo abre en otra
máquina.

**Modo servidor** — con Firebase configurado: pide correo y contraseña, guarda en
el servidor, todos ven lo mismo, hay cuatro permisos (Owner, Admin, Analyst,
Viewer) y queda historial de quién cambió qué. Los pasos están en
[CONECTAR-SERVIDOR.md](CONECTAR-SERVIDOR.md) y las reglas de seguridad en
[firestore.rules](firestore.rules).

En los dos modos, **Descargar Excel** genera un `.xlsx` con el formato de
*Control de Kioskos Forpass*, con las columnas calculadas como fórmulas vivas.

## Publicar

Está pensado para GitHub Pages sobre la rama `main`, carpeta raíz.

```bash
git add -A && git commit -m "Actualiza el control de Forpass" && git push
```
