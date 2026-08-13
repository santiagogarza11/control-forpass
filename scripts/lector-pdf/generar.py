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

resumen = []
for k in C.ARCH:
    filas, enc, factor, suma, esperado, esc = C.analizar(k, verbose=False)
    g = C.consolidar(filas)
    m0 = leer.RE_MES.fullmatch(enc[0])
    mes, anio = MESN[m0.group(1).lower()], 2000 + int(m0.group(2))
    meta = META[k]
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
    ruta = SALIDA + f'poliza-{k}.json'
    json.dump(P, open(ruta,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    anual = sum(p['precioUnitario']*p['cantidad']*p['frecuencia'] for p in P['partidas'])
    conDesc = sum(1 for p in P['partidas'] if p['descripcion'])
    resumen.append((k, len(filas), len(g), sum(p['cantidad'] for p in P['partidas']),
                    anual, esperado, len(esc), conDesc, enc[0]))
    print(f'escrito docs/poliza-{k}.json')

print()
print(f'{"":8} {"orig":>5} {"cons":>5} {"equip":>6} {"anual limpio":>15} {"impreso":>14} {"dif":>11}  desc')
for k,n0,n1,eq,anual,esp,nesc,cd,ini in resumen:
    print(f'{k:8} {n0:5} {n1:5} {eq:6} {anual:15,.2f} {esp:14,.2f} {anual-esp:11,.2f}  {cd}/{n1}')
