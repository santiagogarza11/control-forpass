# -*- coding: utf-8 -*-
"""Lee las cotizaciones de póliza de Forguard: tabla de precios + calendario.

El calendario NO es texto: son rectángulos rellenos. Se sacan con su posición y su
color y se cruzan contra las posiciones del encabezado de meses y de los nombres de
equipo para saber qué celda es cada uno.

Lo importante: la posición real no está en Tm sino en el CTM (operador `cm`), con su
pila de q/Q. Tm solo trae la escala de la fuente.
"""
import re, zlib, sys

def streams(ruta):
    d = open(ruta, 'rb').read()
    out = []
    for m in re.finditer(rb'stream\r?\n(.*?)endstream', d, re.S):
        b = m.group(1)
        try: out.append(zlib.decompress(b))
        except Exception: pass
    return out

TOK = re.compile(rb'''\((?:\\.|[^()\\])*\)|<[0-9A-Fa-f\s]*>|/[^\s/\[\]<>(){}]+|\[|\]|[-+]?[\d.]+|[A-Za-z*'"]+''')

def mul(m, n):
    """m · n, matrices PDF de 6 números."""
    a1,b1,c1,d1,e1,f1 = m; a2,b2,c2,d2,e2,f2 = n
    return [a1*a2+b1*c2, a1*b2+b1*d2, c1*a2+d1*c2, c1*b2+d1*d2, e1*a2+f1*c2+e2, e1*b2+f1*d2+f2]

def punto(m, x, y):
    return (m[0]*x + m[2]*y + m[4], m[1]*x + m[3]*y + m[5])

def analizar(b):
    """(textos, rects) en coordenadas de página.
       textos = [(x, y, texto)]   rects = [(x, y, w, h, color)]"""
    toks = [t.group(0) for t in TOK.finditer(b)]
    pila, textos, rects = [], [], []
    ctm = [1,0,0,1,0,0]
    guardadas = []
    color = None
    tm = [1,0,0,1,0,0]
    linea, lx, ly = [], 0.0, 0.0
    trazo = []          # puntos del trazado en curso, en coordenadas de página

    def num(t):
        try: return float(t)
        except Exception: return 0.0
    def nums(n):
        v = [num(p) for p in pila[-n:]] if len(pila) >= n else None
        return v
    def cerrar():
        nonlocal linea
        if linea:
            s = b''.join(linea).decode('mac_roman', 'replace')
            if s.strip(): textos.append((lx, ly, s))
        linea = []
    def pos():
        nonlocal lx, ly
        lx, ly = punto(mul(tm, ctm), 0, 0)

    for t in toks:
        if t.startswith(b'(') or t.startswith(b'<') or t.startswith(b'/') \
           or re.fullmatch(rb'[-+]?[\d.]+', t):
            pila.append(t); continue
        if t in (b'[', b']'):
            continue
        op = t
        if op == b'q':
            guardadas.append((list(ctm), color))
        elif op == b'Q':
            if guardadas: ctm, color = guardadas.pop(); ctm = list(ctm)
        elif op == b'cm':
            v = nums(6)
            if v: ctm = mul(v, ctm)
        elif op == b'BT':
            cerrar(); tm = [1,0,0,1,0,0]; pos()
        elif op == b'Tm':
            v = nums(6)
            if v: cerrar(); tm = v; pos()
        elif op in (b'Td', b'TD'):
            v = nums(2)
            if v: cerrar(); tm = mul([1,0,0,1,v[0],v[1]], tm); pos()
        elif op == b'T*':
            cerrar()
        elif op in (b'Tj', b"'", b'"'):
            for p in reversed(pila):
                if p.startswith(b'('):
                    linea.append(re.sub(rb'\\([()\\])', rb'\1', p[1:-1])); break
        elif op == b'TJ':
            for p in pila:
                if p.startswith(b'('):
                    linea.append(re.sub(rb'\\([()\\])', rb'\1', p[1:-1]))
        elif op == b'ET':
            cerrar()
        elif op in (b'sc', b'scn', b'rg'):
            v = [num(p) for p in pila if re.fullmatch(rb'[-+]?[\d.]+', p)]
            if len(v) >= 3: color = tuple(round(z,3) for z in v[-3:])
        elif op == b'g':
            v = nums(1)
            if v: color = (round(v[0],3),)*3
        elif op == b're':
            v = nums(4)
            if v:
                x, y = punto(ctm, v[0], v[1])
                x2, y2 = punto(ctm, v[0]+v[2], v[1]+v[3])
                trazo.extend([(min(x,x2), min(y,y2)), (max(x,x2), max(y,y2))])
        elif op in (b'm', b'l'):
            v = nums(2)
            if v: trazo.append(punto(ctm, v[0], v[1]))
        elif op == b'c':
            v = nums(6)
            if v: trazo.append(punto(ctm, v[4], v[5]))
        elif op in (b'v', b'y'):
            v = nums(4)
            if v: trazo.append(punto(ctm, v[2], v[3]))
        elif op in (b'f', b'F', b'f*', b'B', b'B*', b'b', b'b*'):
            # Las celdas del calendario son trazados m/l/h f, no rectángulos:
            # Canva exporta todo como path. Se guarda la caja que los envuelve.
            if trazo:
                xs = [p[0] for p in trazo]; ys = [p[1] for p in trazo]
                rects.append((min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys), color))
            trazo = []
        elif op in (b'n', b'S', b's', b'W'):
            if op != b'W': trazo = []
        pila = []
    cerrar()
    return textos, rects

MES3 = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
RE_MES = re.compile(r'(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[-\s]?(\d\d)', re.I)

def leer_calendario(ruta, verbose=False):
    """({indice: [columnas 0..11]}, [meses del encabezado]).

    El calendario abarca VARIAS páginas cuando hay muchos renglones, así que se
    acumulan todas. Se llavea por el número de renglón y no por el nombre: el
    nombre viene partido en dos líneas cuando es largo y el número es exacto.
    """
    porIdx, encabezado = {}, None
    for b in streams(ruta):
        textos, rects = analizar(b)
        if 'Calendario' not in ''.join(t[2] for t in textos): continue

        cols = [(x, y, s2.strip().lower()) for x, y, s2 in textos if RE_MES.fullmatch(s2.strip())]
        if len(cols) < 12: continue
        yenc = max(c[1] for c in cols)
        cols = sorted([c for c in cols if abs(c[1]-yenc) < 6])[:12]
        if len(cols) != 12: continue
        if encabezado is None: encabezado = [c[2] for c in cols]

        tabla = max((r for r in rects if r[2] > 600 and r[3] > 200), key=lambda r: r[2]*r[3], default=None)
        ypiso = tabla[1] if tabla else 0

        cortos = [(x, y, int(s2.strip())) for x, y, s2 in textos
                  if re.fullmatch(r'\d{1,3}', s2.strip()) and ypiso <= y < yenc - 6]
        if not cortos: continue
        xmin = min(c[0] for c in cortos)
        nums = sorted([(y, n) for x, y, n in cortos if x < xmin + 16], key=lambda z: -z[0])
        if len(nums) < 2: continue
        alto = abs(nums[0][0] - nums[1][0])

        anchoCol = (cols[-1][0] - cols[0][0]) / 11
        cand = [r for r in rects
                if r[4] and r[2] < anchoCol*1.8 and r[3] < alto*1.8
                and r[0] > cols[0][0] - anchoCol and ypiso <= r[1] < yenc]
        from collections import Counter
        cuenta = Counter(r[4] for r in cand)
        tonos = [c for c in cuenta if len(c) >= 3 and max(c) < 0.97 and c[2] > c[0] + 0.04]
        if not tonos: continue
        sombra = max(tonos, key=lambda c: cuenta[c])

        for y, idx in nums:
            meses = set()
            for r in cand:
                if r[4] != sombra: continue
                if abs((r[1] + r[3]/2) - y) > alto*0.45: continue
                cx = r[0] + r[2]/2
                meses.add(min(range(12), key=lambda j2: abs(cols[j2][0] + anchoCol/2 - cx)))
            if idx in porIdx: porIdx[idx] |= meses
            else: porIdx[idx] = meses
        if verbose:
            print(f'  hoja: {len(nums)} renglones, {cuenta[sombra]} celdas, alto {alto:.0f}')
    if not porIdx: return None, None
    return {k: sorted(v) for k, v in porIdx.items()}, encabezado


# ======================= TABLA DE PRECIOS =======================
CAB = ['Concepto','Marca','Cantidad','Precio','Frecuencia','Total']

def leer_tabla(ruta, verbose=False):
    """[(concepto, marca, cantidad, precioUnitario, frecuencia, totalPDF)] en orden."""
    filas = []
    for b in streams(ruta):
        textos, rects = analizar(b)
        junto = ''.join(t[2] for t in textos)
        if 'Frecuencia' not in junto or 'Concepto' not in junto: continue

        # Encabezados de columna. Se elige el RENGLÓN donde coinciden más palabras
        # de encabezado: "Concepto Cotizado:" del título también empieza con
        # "Concepto" y si se toma el primero que aparece, la tabla no se encuentra.
        cands = []
        for x, y, s in textos:
            t = ' '.join(s.split())
            for c in CAB:
                if t.lower().startswith(c.lower()): cands.append((y, c, x))
        if not cands: continue
        porY = {}
        for y, c, x in cands:
            k = round(y)
            porY.setdefault(k, {})[c] = x
        ycab = max(porY, key=lambda k: len(porY[k]))
        heads = {c: (x, ycab) for c, x in porY[ycab].items()}
        if 'Total' not in heads or 'Concepto' not in heads: continue
        xs = sorted((x, c) for c, (x, y) in heads.items())

        # Anclas de renglón: la columna "#". Se detecta como el grupo de números
        # cortos más a la izquierda, NO por la x del encabezado "Concepto": el texto
        # del concepto queda a la izquierda de su encabezado (que está centrado) y
        # filtrarlo por ahí lo borraba entero.
        cortos = [(x, y, int(s.strip())) for x, y, s in textos
                  if re.fullmatch(r'\d{1,3}', s.strip()) and y < ycab - 6]
        if not cortos: continue
        xmin = min(c[0] for c in cortos)
        nums = [(y, n) for x, y, n in cortos if x < xmin + 16]
        nums.sort(key=lambda z: -z[0])
        if not nums: continue
        xIzq = xmin + 14
        alto = abs(nums[0][0]-nums[1][0]) if len(nums) > 1 else 30

        def col_de(x):
            mejor, dmin = None, 1e9
            for cx, c in xs:
                d = abs(x - cx)
                if d < dmin: dmin, mejor = d, c
            return mejor

        for y, idx in nums:
            celdas = {c: [] for c in CAB}
            for x, yy, s in textos:
                if abs(yy - y) > alto*0.45: continue
                if x < xIzq: continue
                t = ' '.join(s.split())
                if not t: continue
                celdas[col_de(x)].append((x, t))
            for c in celdas: celdas[c].sort()
            g = lambda c: ' '.join(t for _, t in celdas[c]).strip()
            filas.append((idx, g('Concepto'), g('Marca'), g('Cantidad'), g('Precio'), g('Frecuencia'), g('Total')))
        if verbose: print('  columnas:', [(round(x), c) for x, c in xs], '· renglones en esta hoja:', len(nums))
    # ordena por índice y quita repetidos
    vistos, out = set(), []
    for r in sorted(filas):
        if r[0] in vistos: continue
        vistos.add(r[0]); out.append(r)
    return out
