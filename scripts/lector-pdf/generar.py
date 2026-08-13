# -*- coding: utf-8 -*-
"""Escribe docs/poliza-<SITIO>.json con la forma del objeto POLIZA."""
import json, re, sys, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import consolidar as C, leer

# docs/ del repo, dos niveles arriba de este archivo.
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
             os.path.abspath(__file__)))), 'docs') + '/'
META = {
  'MXNL02': dict(cliente='Mercado Libre', sitio='MXNL02', fecha='29 de julio 2026'),
  'MXGT01': dict(cliente='Mercado Libre', sitio='MXGT01', fecha='29 de julio 2026'),
  'INOAC':  dict(cliente='INOAC',         sitio='',       fecha='15 de abril 2026'),
  'NGK':    dict(cliente='NGK',           sitio='',       fecha='09 de julio 2026'),
}
MESN = {m:i for i,m in enumerate(leer.MES3)}
VIGENCIA = ('La póliza se contrata y se presta por un periodo anual de doce (12) meses, '
            'independientemente de que la facturación se realice de forma anual o mensual. '
            'La vigencia iniciará en la fecha acordada por las partes y se mantendrá por el '
            'periodo anual establecido.')

# las 23 descripciones reales que traen INOAC y NGK, por concepto normalizado
def sa(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c)!='Mn')
DESC = {sa(k): v for k, v in {
 'camara de refrigeracion':'Lavado de condensador y evaporador, inspección del funcionamiento correcto de motores y ventiladores, revisión de voltaje y amperaje así como verificación de presión de gas. Limpieza y ajuste de contactores y reapriete de terminales y tornillería.',
 'camara de congelacion':'Lavado de condensador y evaporador, inspección del funcionamiento correcto de motores y ventiladores, revisión de voltaje y amperaje así como verificación de presión de gas. Limpieza y ajuste de contactores y reapriete de terminales y tornillería.',
 'horno rational':'Revisión de voltaje, amperaje y conexiones, ajuste y reapriete de conexiones, limpieza mecánica, lubricación de componentes y revisión de funcionamiento de componentes.',
 'campana de extraccion':'Limpieza a campana de extracción de humo con desengrasante y alta presión, incluye lavado de filtros.',
 'extraccion':'Medición de amperaje y voltaje del equipo, así como la revisión de las condiciones y funcionamiento de bandas y componentes del equipo, lubricación de chumaceras y limpieza del equipo con desengrasante.',
 'maquina de hielo':'Limpieza del motor y abanico, y limpieza con ice machine del evaporador y condensador, así como la inspección del cableado eléctrico y ajuste de terminales.',
 'maquina lavaloza':'Inspección visual de los componentes físicos del equipo, así como la revisión de mangueras y componentes hidráulicos, limpieza en general con desincrustante.',
 'estufon':'Revisión de válvulas de gas, perillas, quemadores (flautas), manguera de gas y regulador. Limpieza con desengrasante.',
 'estufon doble':'Revisión de válvulas de gas, perillas, quemadores (flautas), manguera de gas y regulador. Limpieza con desengrasante.',
 'plancha industrial':'Revisión de válvulas de gas, perillas, quemadores (flautas), manguera de gas y regulador. Limpieza con desengrasante.',
 'freidora':'Revisión de válvulas de gas, perillas, quemadores (flautas), manguera de gas y regulador. Limpieza con desengrasante.',
 'trampa de grasa':'Limpieza de trampa de grasa, raspado de paredes, deflectores y filtros para eliminar residuos, retiro de sólidos y revisión de tapa.',
 'barra caliente de servicio de gas':'Revisión de tubería, válvulas, estado de tanques de carga y descarga de agua y limpieza de quemadores y del equipo en general con ice machine.',
 'barra caliente de servicio gas':'Revisión de tubería, válvulas, estado de tanques de carga y descarga de agua y limpieza de quemadores y del equipo en general con ice machine.',
 'barra fria':'Revisión de tubería, válvulas, estado de tanques de carga y descarga de agua y limpieza de quemadores y del equipo en general con ice machine.',
 'barra fria 4 insertos':'Revisión de tubería, válvulas, estado de tanques de carga y descarga de agua y limpieza de quemadores y del equipo en general con ice machine.',
 'calenton doble':'Revisión de voltaje y amperaje del equipo y contacto, revisión de componentes eléctricos, verificación de funcionamiento y temperatura adecuada y revisión de empaques de puerta.',
 'barra caliente de servicio electrica':'Revisión de voltaje y amperaje del equipo y contacto, revisión de componentes eléctricos, verificación de funcionamiento y temperatura adecuada y revisión de empaques de puerta.',
 'pasarela caliente doble':'Revisión de voltaje y amperaje del equipo y contacto, revisión de componentes eléctricos, verificación de funcionamiento y temperatura adecuada y revisión de empaques de puerta.',
 'bascula de recibo':'Inspección del estado y funcionamiento de tarjeta y componentes, limpieza de componentes mecánicos.',
 'bascula de cocina':'Inspección del estado y funcionamiento de tarjeta y componentes, limpieza de componentes mecánicos.',
 'licuadora industrial':'Revisión del voltaje y amperaje del equipo, inspección del estado físico de los componentes y comprobación del funcionamiento adecuado del equipo.',
 'refrigerador sencillo':'Inspección visual del estado y funcionamiento de empaques de puertas, lámparas, ventiladores y motores, así como la revisión de temperatura adecuada, medición del voltaje y amperaje y la limpieza de evaporador.',
 'refrigerador doble':'Inspección visual del estado y funcionamiento de empaques de puertas, lámparas, ventiladores y motores, así como la revisión de temperatura adecuada, medición del voltaje y amperaje y la limpieza de evaporador.',
 'congelador horizontal':'Inspección visual del estado y funcionamiento de empaques de puertas, lámparas, ventiladores y motores, así como la revisión de temperatura adecuada, medición del voltaje y amperaje y la limpieza de evaporador.',
}.items()}

def portada(ruta):
    """Cliente, sitio y fecha, leídos de la portada del PDF.

    La portada trae los campos etiquetados —«Cliente : X», «Fecha : Y»—, así que
    se leen de ahí en vez de adivinarlos del nombre del archivo. Lo que salga se
    IMPRIME para que se pueda revisar: estas portadas se copian de una cotización
    a otra y a veces traen el sitio de la anterior. Se corrige con --cliente y
    --sitio, que siempre le ganan a lo leído.
    """
    textos = []
    for b in leer.streams(ruta)[:2]:                 # la portada es la hoja 1
        try: textos += [t.strip() for _, _, t in leer.analizar(b)[0]]
        except Exception: pass
    textos = [t for t in textos if t]

    def campo(etiqueta, hasta):
        try: i = next(k for k, t in enumerate(textos) if t.rstrip(':').strip().lower() == etiqueta)
        except StopIteration: return []
        out = []
        for t in textos[i+1:]:
            if t.rstrip(':!').strip().lower() == hasta: break
            v = t.lstrip(':').strip().rstrip('!').strip()
            if v: out.append(v)
            if len(out) >= 3: break
        return out

    partes = campo('cliente', 'fecha')
    fechas = campo('fecha', 'proyecto')
    # «Cliente: Mercado Libre / MXGT01» → cliente y sitio. Con una sola parte no
    # hay sitio aparte, salvo que sea un código tipo MXNL02 y entonces ES el sitio.
    cliente = partes[0] if partes else ''
    sitio   = partes[1] if len(partes) > 1 else ''
    if not sitio and re.fullmatch(r'[A-Z]{2,4}\d{2,3}', cliente or ''):
        sitio, cliente = cliente, ''
    fecha = ''
    for f in fechas:
        if re.search(r'\d{1,2}\s+de\s+\w+\s+\d{4}', f): fecha = ' '.join(f.split()); break
    return dict(cliente=cliente, sitio=sitio, fecha=fecha)


def total_impreso(ruta, sumaPDF):
    """Busca en el PDF el gran total, para poder verificar la extracción.

    Se elige la cifra más cercana a la suma de la columna Total Mtto y solo si
    queda a menos del 1%: si no aparece, se devuelve None y el script lo dice.
    Adivinar un total contra el cual verificar sería peor que no verificar.
    """
    txt = []
    for b in leer.streams(ruta):
        try: txt += [t for _, _, t in leer.analizar(b)[0]]
        except Exception: pass
    cifras = set()
    for m in re.findall(r'\$\s?([\d,]{6,}\.?\d*)', ' '.join(txt)):
        try: cifras.add(float(m.replace(',', '')))
        except ValueError: pass
    if not cifras or not sumaPDF: return None
    mejor = min(cifras, key=lambda c: abs(c - sumaPDF))
    return mejor if abs(mejor - sumaPDF) / sumaPDF < 0.01 else None


def procesar(etiqueta, ruta, meta, esperado):
    filas, enc, factor, suma, esperado, esc = C.analizar(etiqueta, verbose=False,
                                                         ruta=ruta, esperado=esperado)
    # Las correcciones a mano van DESPUÉS de verificar contra el total impreso,
    # no antes: así esa verificación sigue midiendo la extracción, y lo que mueve
    # cada corrección se ve aparte en vez de esconderse en el mismo número.
    hechas = C.aplicar_correcciones(etiqueta, filas)
    g = C.consolidar(filas)
    m0 = leer.RE_MES.fullmatch(enc[0])
    mes, anio = MESN[m0.group(1).lower()], 2000 + int(m0.group(2))
    P = {
      'cliente': meta['cliente'], 'sitio': meta['sitio'], 'fecha': meta['fecha'],
      'proyecto': 'Póliza de Mantenimiento Preventivo',
      'tituloPortada': ['Cotización', 'Póliza de', 'Mtto Prev.'],
      'inicioCalendario': {'mes': mes, 'anio': anio},
      'contacto': {'tel': '811 60 71 051', 'correo': 'pablo.quiroga@forguard.com'},
      'telOficina': '+(52) 81 8458 8845',
      'oficinas': ['Lázaro Garza Ayala, 1213', 'SPGG, Nuevo León'],
      'vigencia': VIGENCIA,
      'partidas': [{
          'concepto': x['concepto'], 'marca': x['marca'], 'cantidad': x['cantidad'],
          'precioUnitario': x['precioUnitario'], 'frecuencia': x['frecuencia'],
          'mesesServicio': x['mesesServicio'],
          'descripcion': DESC.get(sa(x['concepto']), ''),
      } for x in g],
    }
    destino = SALIDA + f'poliza-{etiqueta}.json'
    json.dump(P, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    anual = sum(p['precioUnitario']*p['cantidad']*p['frecuencia'] for p in P['partidas'])
    print(f'escrito docs/poliza-{etiqueta}.json')
    return dict(k=etiqueta, orig=len(filas), cons=len(g),
                equipos=sum(p['cantidad'] for p in P['partidas']),
                extraido=suma, anual=anual, esperado=esperado,
                desc=sum(1 for p in P['partidas'] if p['descripcion']),
                correcciones=hechas)


AYUDA = """Saca los datos de una cotización de póliza en PDF y escribe docs/poliza-<SITIO>.json

  python3 scripts/lector-pdf/generar.py
      Rehace las cotizaciones ya conocidas (las de ARCH en consolidar.py).

  python3 scripts/lector-pdf/generar.py ruta.pdf [otra.pdf ...]
      Cualquier PDF. El cliente, el sitio y la fecha se leen de la portada y se
      imprimen para que los revises.

  Banderas (solo con UN PDF, para corregir lo que la portada traiga mal):
      --cliente "Mercado Libre"      --sitio MXNL03
      --fecha "26 de junio 2026"     --total 1855207.88
"""

if __name__ == '__main__':
    argv = sys.argv[1:]
    if argv and argv[0] in ('-h', '--help'):
        print(AYUDA); sys.exit(0)

    banderas, rutas = {}, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            if i + 1 >= len(argv):
                print(f'Falta el valor de {a}.'); sys.exit(1)
            banderas[a[2:]] = argv[i+1]; i += 2
        else:
            rutas.append(a); i += 1

    if banderas and len(rutas) > 1:
        print('Las banderas son para UN solo PDF: con varios no se sabe a cuál le tocan.')
        sys.exit(1)

    trabajos = []          # (etiqueta, ruta, meta, total esperado)
    if not rutas:
        for k in C.ARCH:
            trabajos.append((k, C.ruta_de(k), META[k], None))
    else:
        for r in rutas:
            r = os.path.expanduser(r)
            if not os.path.exists(r):
                print(f'No existe: {r}'); sys.exit(1)
            leido = portada(r)
            meta = dict(cliente=banderas.get('cliente', leido['cliente']),
                        sitio=banderas.get('sitio', leido['sitio']),
                        fecha=banderas.get('fecha', leido['fecha']))
            etiqueta = meta['sitio'] or meta['cliente'] or os.path.splitext(os.path.basename(r))[0]
            etiqueta = re.sub(r'[^A-Za-z0-9_-]+', '-', etiqueta).strip('-') or 'poliza'
            total = banderas.get('total')
            print(f'--- {os.path.basename(r)}')
            print(f'    portada dice: cliente «{leido["cliente"]}» · sitio «{leido["sitio"]}» · fecha «{leido["fecha"]}»')
            if banderas:
                print(f'    con tus banderas: cliente «{meta["cliente"]}» · sitio «{meta["sitio"]}» · fecha «{meta["fecha"]}»')
            for campo in ('cliente', 'fecha'):
                if not meta[campo]:
                    print(f'    OJO: no se pudo leer {campo}. Pásalo con --{campo}.')

            # Candado real, no teórico: la portada de la cotización de Nexxus dice
            # «MXGT01» porque la copiaron de la anterior, y sin esto el script
            # habría machacado docs/poliza-MXGT01.json —ya verificado— con otra
            # cotización, en silencio. El nombre lo endereza --sitio.
            destino = SALIDA + f'poliza-{etiqueta}.json'
            if os.path.exists(destino) and 'sitio' not in banderas:
                print(f'    ALTO: ya existe docs/poliza-{etiqueta}.json y no lo voy a machacar.')
                print(f'    Si de verdad es ese sitio, bórralo tú. Si la portada trae el sitio')
                print(f'    equivocado —pasa, la copian entre cotizaciones—, pásalo con --sitio.')
                sys.exit(1)

            trabajos.append((etiqueta, r, meta, float(total) if total else None))

    resumen = []
    for etiqueta, ruta, meta, total in trabajos:
        if total is None and etiqueta not in C.ARCH:
            filas, _ = C.leer_todo(ruta)
            total = total_impreso(ruta, sum(f['totalPDF'] for f in filas))
            if total: print(f'    total impreso encontrado en el PDF: ${total:,.2f}')
            else:     print('    no se encontró el total impreso: no se va a poder verificar (usa --total)')
        resumen.append(procesar(etiqueta, ruta, meta, total))

    print()
    print(f'{"":10} {"orig":>5} {"cons":>5} {"equip":>6} {"extraído":>15} {"impreso":>14} {"dif":>11}  desc')
    for r in resumen:
        esp = f'{r["esperado"]:14,.2f}' if r['esperado'] is not None else f'{"—":>14}'
        dif = f'{r["extraido"]-r["esperado"]:11,.2f}' if r['esperado'] is not None else f'{"—":>11}'
        print(f'{r["k"]:10} {r["orig"]:5} {r["cons"]:5} {r["equipos"]:6} {r["extraido"]:15,.2f} {esp} {dif}  {r["desc"]}/{r["cons"]}')
    print('  («extraído» es lo que dice el PDF, antes de las correcciones a mano.)')

    corregidas = [r for r in resumen if r['correcciones']]
    if corregidas:
        print()
        print('--- correcciones a mano, donde el PDF se contradice a sí mismo ---')
        for r in corregidas:
            for c in r['correcciones']:
                print(f'  {r["k"]} renglón #{c["idx"]} del papel · {c["concepto"]}')
                print(f'     {c["campo"]}: {c["antes"]} → {c["ahora"]}')
                print(f'     {c["porque"]}')
        print()
        print(f'{"":10} {"extraído":>15} {"ya corregido":>15}   diferencia')
        for r in corregidas:
            print(f'{r["k"]:10} {r["extraido"]:15,.2f} {r["anual"]:15,.2f} {r["anual"]-r["extraido"]:>13,.2f}')
