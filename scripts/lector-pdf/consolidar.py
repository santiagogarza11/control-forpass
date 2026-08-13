# -*- coding: utf-8 -*-
"""Consolida las cuatro cotizaciones de póliza y las deja como JSON del objeto POLIZA.

Agrupa SOLO cuando coinciden concepto + marca + precio unitario + frecuencia +
MESES DE MANTENIMIENTO. Ese último es el que importa: dos hornos idénticos
atendidos en meses distintos son dos renglones, porque el calendario se escalona
para repartir la carga y juntarlos obligaría a inventar un calendario que no existe.
"""
import sys, os, re, json, unicodedata
from collections import Counter, OrderedDict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leer

# Carpeta donde estan los PDF. Se puede cambiar con la variable de entorno
# POLIZAS_PDF, para no tener que editar el archivo.
DIR = os.environ.get('POLIZAS_PDF', os.path.expanduser('~/Downloads')).rstrip('/') + '/'
ARCH = OrderedDict([
    ('MXNL02', ('Cotizacion Poliza MXNL02.pdf',                    683134.00)),
    ('MXGT01', ('Cotización Póliza Forguard MXGT01.pdf',           1790257.88)),
    ('INOAC',  ('Cotización Póliza Forguard_INOAC_FInal.pdf',       288840.00)),
    ('NGK',    ('NGK Cotización Póliza Forguard.pdf',               373518.00)),
])
MES3 = leer.MES3

def dinero(t):
    m = re.findall(r'[\d,]+\.?\d*', t.replace(' ', ''))
    return float(m[0].replace(',', '')) if m else 0.0

def ultimo_entero(t):
    m = re.findall(r'(?<![\d.,])(\d{1,2})(?![\d.,])', t)
    return int(m[-1]) if m else 0

def limpiar(t):
    t = ' '.join(t.split())
    t = re.sub(r'\s*\b\d{1,3}\b\s*$', '', t)      # número de renglón pegado al final
    return t.strip(' -·')

def titulo(t):
    """Normaliza mayúsculas: INOAC viene TODO EN CAPS y MXNL02 en Title Case."""
    if t.isupper() and len(t) > 4:
        chicas = {'de','del','la','el','y','con','a','en','por'}
        ps = [p.capitalize() if p.lower() not in chicas else p.lower() for p in t.split()]
        if ps: ps[0] = ps[0].capitalize()
        return ' '.join(ps)
    return t

def sin_acentos(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

def leer_todo(nombre):
    ruta = DIR + ARCH[nombre][0]
    tab = leer.leer_tabla(ruta)
    cal, enc = leer.leer_calendario(ruta)
    filas = []
    for idx, concepto, marca, cant, precio, frec, total in tab:
        pu = dinero(precio)
        fr = ultimo_entero(frec)
        tot = dinero(total)
        c_expl = int(cant) if re.fullmatch(r'\d{1,2}', cant.strip()) else None
        filas.append(dict(idx=idx, concepto=titulo(limpiar(concepto)), marca=limpiar(marca),
                          cantExplicita=c_expl, pu=pu, frec=fr, totalPDF=tot,
                          meses=cal.get(idx, [])))
    return filas, enc

def analizar(nombre, verbose=True):
    filas, enc = leer_todo(nombre)
    esperado = ARCH[nombre][1]

    # --- ¿hay un factor global (descuento) o cantidades escondidas? ---
    razones = []
    for f in filas:
        base = f['pu'] * f['frec'] * (f['cantExplicita'] or 1)
        if base: razones.append(round(f['totalPDF'] / base, 4))
    comunes = Counter(razones).most_common()
    factor = 1.0
    if comunes and abs(comunes[0][0] - 0.95) < 0.002 and comunes[0][1] >= len(filas) * 0.6:
        factor = 0.95

    # --- cantidad: explícita, o deducida del total ---
    escondidas = []
    for f in filas:
        if f['cantExplicita'] is not None:
            f['cantidad'] = f['cantExplicita']
        else:
            base = f['pu'] * f['frec'] * factor
            q = f['totalPDF'] / base if base else 1
            f['cantidad'] = max(1, round(q))
            if f['cantidad'] > 1:
                escondidas.append(f)
        f['totalLimpio'] = f['pu'] * f['cantidad'] * f['frec']

    suma = sum(f['totalLimpio'] for f in filas)
    sumaPDF = sum(f['totalPDF'] for f in filas)

    if verbose:
        print(f'######## {nombre} — {len(filas)} renglones, arranca {enc[0]}')
        print(f'  factor detectado en los totales del PDF: {factor}')
        print(f'  suma de Total Mtto del PDF : ${sumaPDF:,.2f}')
        print(f'  suma con la fórmula limpia : ${suma:,.2f}')
        print(f'  total impreso en la cotización: ${esperado:,.2f}')
        d = suma - esperado
        print(f'  diferencia: ${d:,.2f}' + ('  ✓ CUADRA' if abs(d) < 1 else ''))
        if escondidas:
            print(f'  --- {len(escondidas)} renglones con CANTIDAD ESCONDIDA en el Total Mtto ---')
            for f in escondidas:
                print(f'     #{f["idx"]:<3} {f["concepto"][:34]:36} pu ${f["pu"]:>9,.2f} × frec {f["frec"]} '
                      f'× {f["cantidad"]} = ${f["totalLimpio"]:>10,.2f}   (PDF decía ${f["totalPDF"]:,.2f})')
    return filas, enc, factor, suma, esperado, escondidas

def consolidar(filas):
    """Junta solo si coinciden concepto+marca+pu+frecuencia+meses."""
    grupos = OrderedDict()
    for f in filas:
        llave = (sin_acentos(f['concepto']), sin_acentos(f['marca']), round(f['pu'], 2),
                 f['frec'], tuple(f['meses']))
        if llave in grupos:
            grupos[llave]['cantidad'] += f['cantidad']
            grupos[llave]['de'].append(f['idx'])
        else:
            grupos[llave] = dict(concepto=f['concepto'], marca=f['marca'], cantidad=f['cantidad'],
                                 precioUnitario=f['pu'], frecuencia=f['frec'],
                                 mesesServicio=list(f['meses']), de=[f['idx']])
    return list(grupos.values())

if __name__ == '__main__':
    for k in ARCH:
        filas, enc, factor, suma, esperado, esc = analizar(k)
        g = consolidar(filas)
        print(f'  consolidado: {len(filas)} → {len(g)} renglones '
              f'({sum(x["cantidad"] for x in g)} equipos)')
        sg = sum(x['precioUnitario'] * x['cantidad'] * x['frecuencia'] for x in g)
        print(f'  suma tras consolidar: ${sg:,.2f}' + ('  ✓ igual' if abs(sg - suma) < .01 else '  ✗ CAMBIÓ'))
        print()
