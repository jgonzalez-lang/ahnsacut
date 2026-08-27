# app.py

import os
import math
from flask import Flask, render_template, request, jsonify, current_app
from calc_service import (
    obtener_materiales, 
    obtener_insertos_compatibles, 
    calcular_torneado, 
    calcular_fresado_sumitomo
)
from data_tables import TABLA_MATERIALES, TABLA_INSERTOS

app = Flask(__name__)

# Desactivar cache del navegador para forzar la recarga limpia
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    lista_materiales = obtener_materiales()
    resultado = None
    material_sel = ""
    inserto_sel = ""
    operacion_sel = "Desbaste"
    diametro_inicial_sel = "50"
    diametro_final_sel = "40"
    longitud_sel = "100"

    if request.method == 'POST':
        material_sel = request.form.get('material', '').strip()
        inserto_sel = request.form.get('inserto', '').strip()
        operacion_sel = request.form.get('operacion', 'Desbaste')
        diametro_inicial_sel = request.form.get('diametro_inicial', '50')
        diametro_final_sel = request.form.get('diametro_final', '40')
        longitud_sel = request.form.get('longitud', '100')
        
        try:
            d_init_val = float(diametro_inicial_sel)
            d_fin_val = float(diametro_final_sel)
            longitud_val = float(longitud_sel)
            if material_sel:
                resultado = calcular_torneado(
                    nombre_material=material_sel,
                    codigo_inserto=inserto_sel,
                    diametro_inicial_mm=d_init_val,
                    diametro_final_mm=d_fin_val,
                    longitud_mm=longitud_val,
                    operacion=operacion_sel
                )
        except (ValueError, TypeError):
            resultado = None

    stats_dashboard = {
        "total_materiales": len(TABLA_MATERIALES),
        "total_insertos": len(TABLA_INSERTOS),
        "familias_iso": len(set(m["familia_iso"] for m in TABLA_MATERIALES if "familia_iso" in m)),
        "eficiencia_sistema": "99.8%"
    }

    return render_template(
        'index.html', 
        materiales=lista_materiales, 
        resultado=resultado, 
        material_sel=material_sel, 
        inserto_sel=inserto_sel, 
        operacion_sel=operacion_sel, 
        diametro_inicial_sel=diametro_inicial_sel,
        diametro_final_sel=diametro_final_sel,
        longitud_sel=longitud_sel,
        stats=stats_dashboard
    )

@app.route('/api/insertos', methods=['GET'])
def api_insertos():
    material = request.args.get('material', '').strip()
    if not material:
        return jsonify([])
    return jsonify(obtener_insertos_compatibles(material))

@app.route('/api/calcular_ajax', methods=['GET'])
def api_calcular_ajax():
    material = request.args.get('material', '').strip()
    if not material:
        return jsonify({})

    inserto = request.args.get('inserto', '').strip()
    operacion = request.args.get('operacion', 'Desbaste')
    
    try:
        d_init = float(request.args.get('diametro_inicial', 50))
    except (ValueError, TypeError):
        d_init = 50.0
    try:
        d_fin = float(request.args.get('diametro_final', 40))
    except (ValueError, TypeError):
        d_fin = 40.0
    try:
        longitud = float(request.args.get('longitud', 100))
    except (ValueError, TypeError):
        longitud = 100.0

    res = calcular_torneado(
        nombre_material=material,
        codigo_inserto=inserto,
        diametro_inicial_mm=d_init,
        diametro_final_mm=d_fin,
        longitud_mm=longitud,
        operacion=operacion
    )
    return jsonify(res if res else {})

@app.route('/api/calcular_barrenado_ajax')
def calcular_barrenado_ajax():
    material = request.args.get('material', '').strip()
    
    try:
        diametro = float(request.args.get('diametro') or 0)
        profundidad = float(request.args.get('profundidad') or 0)
        angulo = float(request.args.get('angulo') or 140.0)
    except (ValueError, TypeError):
        return jsonify({'error': 'Diámetro o profundidad inválidos'}), 400

    vc_raw = request.args.get('vc', '').strip()
    fn_raw = request.args.get('fn', '').strip()
    tipo_agujero = request.args.get('tipo_agujero', 'pasante')

    iso_detectado = 'P'
    if material:
        mat_lower = material.lower()
        if any(x in mat_lower for x in ['304', '316', 'inox', 'inoxidable', '420', '410', '430']):
            iso_detectado = 'M'
        elif any(x in mat_lower for x in ['gris', 'nodular', 'fundicion', 'fundición', 'cast iron']):
            iso_detectado = 'K'
        elif any(x in mat_lower for x in ['aluminio', 'al ', '6061', '7075', 'bronce', 'cobre']):
            iso_detectado = 'N'
        elif any(x in mat_lower for x in ['titanio', 'inconel', 'hastelloy', 'waspaloy']):
            iso_detectado = 'S'
        elif any(x in mat_lower for x in ['templado', 'hrc', 'd2', 'skd']):
            iso_detectado = 'H'

    TABLA_ISO_BARRENADO = {
        'P': {'vc_base': 85.0,  'k_fn': 0.012, 'kc': 1900, 'nombre': 'Aceros al Carbono / Aleados', 'recubrimiento': 'TiAlN / AlTiN (Multicapa)'},
        'M': {'vc_base': 45.0,  'k_fn': 0.010, 'kc': 2100, 'nombre': 'Aceros Inoxidables',         'recubrimiento': 'TiAlN Nano-Lube'},
        'K': {'vc_base': 95.0,  'k_fn': 0.015, 'kc': 1200, 'nombre': 'Fundición de Hierro',        'recubrimiento': 'TiCN / TiAlN (Anti-abrasión)'},
        'N': {'vc_base': 150.0, 'k_fn': 0.018, 'kc': 700,  'nombre': 'Aluminio / No Ferrosos',     'recubrimiento': 'Bright Polish / DLC'},
        'S': {'vc_base': 28.0,  'k_fn': 0.008, 'kc': 2600, 'nombre': 'Superaleaciones / Titanio',   'recubrimiento': 'AlTiN Fine-Grain'},
        'H': {'vc_base': 32.0,  'k_fn': 0.006, 'kc': 3100, 'nombre': 'Materiales Templados',       'recubrimiento': 'AlCrN / nACo (Ultra Dureza)'}
    }

    config_iso = TABLA_ISO_BARRENADO.get(iso_detectado, TABLA_ISO_BARRENADO['P'])

    veces_diametro = (profundidad / diametro) if diametro > 0 else 0
    if veces_diametro <= 3:
        factor_ld = 1.0
        broca_sugerida = "3×D"
    elif veces_diametro <= 5:
        factor_ld = 0.92
        broca_sugerida = "5×D"
    elif veces_diametro <= 8:
        factor_ld = 0.80
        broca_sugerida = "8×D"
    elif veces_diametro <= 12:
        factor_ld = 0.70
        broca_sugerida = "12×D"
    else:
        factor_ld = 0.60
        broca_sugerida = f"{math.ceil(veces_diametro)}×D"

    if iso_detectado in ['K', 'N'] and veces_diametro <= 5:
        flautas_sugeridas = "3 Flautas (Alta Productividad)"
    elif iso_detectado == 'P' and veces_diametro <= 3:
        flautas_sugeridas = "3 Flautas (Barrenado Corto)"
    else:
        flautas_sugeridas = "2 Flautas (Evacuación Segura)"

    if iso_detectado in ['H', 'S']:
        angulo_sugerido = "140° - 150°"
    elif iso_detectado == 'N':
        angulo_sugerido = "130° - 135°"
    else:
        angulo_sugerido = "140° (Estándar)"

    vc_sugerido = round(config_iso['vc_base'] * factor_ld, 1)
    fn_sugerido = round(config_iso['k_fn'] * (diametro ** 0.85), 2) if diametro > 0 else 0

    try:
        vc_final = float(vc_raw) if (vc_raw and float(vc_raw) > 0) else vc_sugerido
    except ValueError:
        vc_final = vc_sugerido

    try:
        fn_final = float(fn_raw) if (fn_raw and float(fn_raw) > 0) else fn_sugerido
    except ValueError:
        fn_final = fn_sugerido

    rpm = (vc_final * 1000) / (math.pi * diametro) if diametro > 0 else 0
    vf = fn_final * rpm
    mrr = (math.pi * (diametro ** 2) / 4) * vf / 1000 if diametro > 0 else 0

    kc_mat = config_iso['kc']
    potencia_kw = (mrr * kc_mat) / (60000 * 0.85) if mrr > 0 else 0
    torque_nm = (potencia_kw * 9550) / rpm if rpm > 0 else 0

    rad_angulo = math.radians(angulo / 2)
    distancia_punta = (diametro / 2) / math.tan(rad_angulo) if (rad_angulo > 0 and diametro > 0) else 0

    profundidad_efectiva = profundidad + distancia_punta if tipo_agujero == 'pasante' else profundidad
    tiempo = profundidad_efectiva / vf if vf > 0 else 0
    vtr = mrr * tiempo

    if veces_diametro <= 3:
        lubricacion = "Inundación Externa Suficiente (Refrigerante Interno Opcional)"
        tipo_alerta = "success"
    elif veces_diametro <= 8:
        lubricacion = "Refrigerante Interno Recomendado (Mínimo 10 - 15 Bar)"
        tipo_alerta = "warning"
    else:
        lubricacion = "Refrigerante Interno Alta Presión OBLIGATORIO (> 20 Bar / 300 PSI) + Picoteo"
        tipo_alerta = "danger"

    return jsonify({
        'iso_detectado': iso_detectado,
        'nombre_iso': config_iso['nombre'],
        'recubrimiento_sugerido': config_iso['recubrimiento'],
        'flautas_sugeridas': flautas_sugeridas,
        'angulo_sugerido': angulo_sugerido,
        'vc_sugerido': str(vc_sugerido),
        'fn_sugerido': str(fn_sugerido),
        'vc_final': str(round(vc_final, 1)),
        'fn_final': str(round(fn_final, 2)),
        'rpm': str(round(rpm, 2)),
        'vf': str(round(vf, 2)),
        'mrr': str(round(mrr, 2)),
        'potencia': str(round(potencia_kw, 2)),
        'torque': str(round(torque_nm, 2)),
        'tiempo': str(round(tiempo, 3)),
        'vtr': str(round(vtr, 2)),
        'distancia_punta': str(round(distancia_punta, 3)),
        'veces_diametro': str(round(veces_diametro, 2)),
        'broca_sugerida': broca_sugerida,
        'lubricacion': lubricacion,
        'tipo_alerta': tipo_alerta
    })

@app.route('/api/calcular_fresado_ajax')
def calcular_fresado_ajax():
    material = request.args.get('material', '').strip()
    serie = request.args.get('serie', 'DGC').strip().upper()
    tipo_inserto = request.args.get('tipo_inserto', 'SNMT 13T6').strip()
    
    try:
        dc = float(request.args.get('diametro') or 50)
        z = int(request.args.get('dientes') or 4)
        ap = float(request.args.get('ap') or 2.0)
        ae = float(request.args.get('ae') or 25.0)
        longitud = float(request.args.get('longitud') or 100.0)
        fz_in = request.args.get('fz', '').strip()
    except (ValueError, TypeError):
        return jsonify({'error': 'Parámetros numéricos inválidos'}), 400

    if not material:
        return jsonify({})

    iso_detectado = 'P'
    mat_lower = material.lower()
    
    if any(x in mat_lower for x in ['304', '316', 'inox', 'inoxidable']):
        iso_detectado = 'M'
    elif any(x in mat_lower for x in ['gris', 'nodular', 'fundicion', 'fundición', 'cast iron']):
        iso_detectado = 'K'
    elif any(x in mat_lower for x in ['aluminio', 'al ', '6061', '7075', 'bronce', 'cobre']):
        iso_detectado = 'N'
    elif any(x in mat_lower for x in ['titanio', 'inconel', 'hastelloy', 'waspaloy']):
        iso_detectado = 'S'
    elif any(x in mat_lower for x in ['templado', 'hrc', 'd2', 'skd']):
        iso_detectado = 'H'

    MAPA_ROMPEVIRUTAS_DGC = {
        'P': {'rvp': 'G (Corte General / Aceros)',        'vc': 180.0, 'fz': 0.15},
        'M': {'rvp': 'FL (Ligero / Anti-Adherente Inox)', 'vc': 120.0, 'fz': 0.12},
        'K': {'rvp': 'H (Corte Pesado / Fundición)',       'vc': 160.0, 'fz': 0.18},
        'N': {'rvp': 'FG (Filo Afilado / Pulido No-Ferrosos)', 'vc': 350.0, 'fz': 0.20},
        'S': {'rvp': 'S (Alta Tenacidad / Titanio)',     'vc': 45.0,  'fz': 0.10},
        'H': {'rvp': 'H (Alta Dureza / Reforzado)',       'vc': 60.0,  'fz': 0.08}
    }

    MAPA_ROMPEVIRUTAS_WEZ = {
        'P': {'rvp': 'G (Geometría Universal Aceros)',    'vc': 200.0, 'fz': 0.14},
        'M': {'rvp': 'F (Filo Afilado / Acero Inox)',     'vc': 130.0, 'fz': 0.10},
        'K': {'rvp': 'H (Filo Reforzado Fundición)',      'vc': 170.0, 'fz': 0.16},
        'N': {'rvp': 'F (Bajo Esfuerzo / No Ferrosos)',   'vc': 400.0, 'fz': 0.18},
        'S': {'rvp': 'S (Corte Térmico Superaleaciones)','vc': 50.0,  'fz': 0.09},
        'H': {'rvp': 'P (Corte Interrumpido Templados)', 'vc': 70.0,  'fz': 0.07}
    }

    if 'WEZ' in serie:
        config = MAPA_ROMPEVIRUTAS_WEZ.get(iso_detectado, MAPA_ROMPEVIRUTAS_WEZ['P'])
    else:
        config = MAPA_ROMPEVIRUTAS_DGC.get(iso_detectado, MAPA_ROMPEVIRUTAS_DGC['P'])

    rompevirutas_oficial = config['rvp']
    vc_base = config['vc']
    fz_base = config['fz']

    fz_final = float(fz_in) if (fz_in and float(fz_in) > 0) else fz_base
    
    rpm = (vc_base * 1000) / (math.pi * dc) if dc > 0 else 0
    vf = fz_final * z * rpm
    mrr = (ap * ae * vf) / 1000.0
    tiempo = longitud / vf if vf > 0 else 0
    vtr = mrr * tiempo

    return jsonify({
        'iso_detectado': iso_detectado,
        'rompevirutas': rompevirutas_oficial,
        'vc': str(round(vc_base, 1)),
        'fz': str(round(fz_final, 2)),
        'rpm': str(round(rpm, 1)),
        'vf': str(round(vf, 1)),
        'mrr': str(round(mrr, 2)),
        'tiempo': str(round(tiempo, 3)),
        'vtr': str(round(vtr, 2))
    })

# ==========================================
# API DE ROSCADO CNC (UNIFICADA Y GARANTIZADA)
# ==========================================
@app.route('/api/calcular_roscado_ajax')
def calcular_roscado_ajax():
    material = request.args.get('material', '').strip()
    metodo = request.args.get('metodo', 'machuelo').strip().lower()
    tipo_machuelo = request.args.get('tipo_machuelo', 'corte').strip().lower()
    
    try:
        d_machuelo = float(request.args.get('diametro') or 0)
        paso = float(request.args.get('paso') or 0)
        pct_rosca = float(request.args.get('pct_rosca') or 75.0)
        profundidad = float(request.args.get('profundidad') or 0)

        d_fresa = float(request.args.get('d_fresa') or 0)
        z_fresa = int(float(request.args.get('z_fresa') or 1))
        fz_fresa = float(request.args.get('fz_fresa') or 0.05)
    except (ValueError, TypeError):
        d_machuelo, paso, pct_rosca, profundidad = 0.0, 0.0, 75.0, 0.0
        d_fresa, z_fresa, fz_fresa = 0.0, 1, 0.05

    vc_raw = request.args.get('vc', '').strip()

    # 1. Identificación de Grupo ISO
    iso_detectado = 'P'
    if material:
        mat_lower = material.lower()
        if any(x in mat_lower for x in ['304', '316', 'inox', 'inoxidable', '420', '410', '430']):
            iso_detectado = 'M'
        elif any(x in mat_lower for x in ['gris', 'nodular', 'fundicion', 'fundición', 'cast iron']):
            iso_detectado = 'K'
        elif any(x in mat_lower for x in ['aluminio', 'al ', '6061', '7075', 'bronce', 'cobre']):
            iso_detectado = 'N'
        elif any(x in mat_lower for x in ['titanio', 'inconel', 'hastelloy', 'waspaloy']):
            iso_detectado = 'S'
        elif any(x in mat_lower for x in ['templado', 'hrc', 'd2', 'skd']):
            iso_detectado = 'H'

    TABLA_ROSCADO = {
        'P': {'vc_machuelo': 15.0, 'vc_fresa': 120.0, 'sustrato': 'HSS-E (Cobalto) / HSS-PM'},
        'M': {'vc_machuelo': 8.0,  'vc_fresa': 80.0,  'sustrato': 'HSS-E-PM (Sinterizado)'},
        'K': {'vc_machuelo': 18.0, 'vc_fresa': 140.0, 'sustrato': 'Carburo Sólido (Solid Carbide)'},
        'N': {'vc_machuelo': 30.0, 'vc_fresa': 250.0, 'sustrato': 'HSS-E / Carburo Sólido'},
        'S': {'vc_machuelo': 4.5,  'vc_fresa': 40.0,  'sustrato': 'HSS-E-PM / Carburo Micrograno'},
        'H': {'vc_machuelo': 5.0,  'vc_fresa': 50.0,  'sustrato': 'Carburo Sólido (Ultra Dureza)'}
    }

    config = TABLA_ROSCADO.get(iso_detectado, TABLA_ROSCADO['P'])
    vc_sugerido = config['vc_fresa'] if metodo == 'fresa' else config['vc_machuelo']
    sustrato_sugerido = 'Carburo Sólido (Thread Mill)' if metodo == 'fresa' else config['sustrato']

    try:
        vc_final = float(vc_raw) if (vc_raw and float(vc_raw) > 0) else vc_sugerido
    except ValueError:
        vc_final = vc_sugerido

    # 2. Brocas Previas
    if d_machuelo > 0 and paso > 0:
        if tipo_machuelo == 'laminacion' and metodo == 'machuelo':
            b_std = d_machuelo - (0.5 * paso)
            b_pct = d_machuelo - (0.53 * (pct_rosca / 100.0) * paso)
        else:
            b_std = d_machuelo - paso
            b_pct = d_machuelo - (1.08253 * (pct_rosca / 100.0) * paso)
        txt_std = f"{round(b_std, 2)} mm"
        txt_pct = f"{round(b_pct, 2)} mm"
    else:
        txt_std, txt_pct = "-", "-"

    # 3. Métricas de Operación (RPM, Vf y Tiempo)
    if metodo == 'fresa' and d_fresa > 0 and d_machuelo > 0 and paso > 0:
        rpm = (vc_final * 1000.0) / (math.pi * d_fresa)
        vf_periferia = rpm * z_fresa * fz_fresa
        factor_correccion = (d_machuelo - d_fresa) / d_machuelo if d_machuelo > d_fresa else 1.0
        vf_centro = vf_periferia * factor_correccion
        
        txt_rpm = f"{round(rpm, 2)}"
        txt_vf = f"{round(vf_centro, 2)}"
        
        if profundidad > 0 and vf_centro > 0:
            pasadas_helice = profundidad / paso
            tiempo_total_min = (pasadas_helice * math.pi * (d_machuelo - d_fresa)) / vf_centro
            txt_tiempo = f"{round(tiempo_total_min, 3)}"
            txt_tiempo_seg = f"{round(tiempo_total_min * 60.0, 1)} seg"
        else:
            txt_tiempo, txt_tiempo_seg = "-", "- seg"
    else:
        if d_machuelo > 0:
            rpm = (vc_final * 1000.0) / (math.pi * d_machuelo)
            vf = rpm * paso if paso > 0 else 0
            txt_rpm = f"{round(rpm, 2)}"
            txt_vf = f"{round(vf, 2)}" if vf > 0 else "-"
        else:
            txt_rpm, txt_vf = "-", "-"

        if profundidad > 0 and d_machuelo > 0 and paso > 0 and rpm > 0 and paso > 0:
            vf_val = rpm * paso
            tiempo_total_min = (2.0 * (profundidad + 5.0)) / vf_val
            txt_tiempo = f"{round(tiempo_total_min, 3)}"
            txt_tiempo_seg = f"{round(tiempo_total_min * 60.0, 1)} seg"
        else:
            txt_tiempo, txt_tiempo_seg = "-", "- seg"

    return jsonify({
        'iso_detectado': iso_detectado,
        'sustrato_sugerido': sustrato_sugerido,
        'vc_sugerido': str(round(vc_sugerido, 1)),
        'broca_estandar': txt_std,
        'broca_porcentaje': txt_pct,
        'rpm': txt_rpm,
        'vf': txt_vf,
        'tiempo': txt_tiempo,
        'tiempo_segundos': txt_tiempo_seg
    })

if __name__ == '__main__':
    app.run(debug=True)
