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

En el **navegador** de la computadora que la captura (`localStorage`), no en un
servidor. Para pasarla a otra máquina o compartirla:

- **Respaldo JSON** descarga todo.
- **Restaurar** vuelve a cargar ese archivo en otro navegador.
- **Descargar Excel** genera un `.xlsx` con el formato de *Control de Kioskos
  Forpass*, con las columnas calculadas como fórmulas vivas.

## Publicar

Está pensado para GitHub Pages sobre la rama `main`, carpeta raíz.

```bash
git add -A && git commit -m "Actualiza el control de Forpass" && git push
```
