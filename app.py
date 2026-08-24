# app.py

import os
from flask import Flask, render_template, request, jsonify
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

@app.route('/api/calcular_fresado_ajax', methods=['GET'])
def api_calcular_fresado_ajax():
    try:
        material = request.args.get('material', '').strip()
        serie = request.args.get('serie', 'DGC')
        tipo_inserto = request.args.get('tipo_inserto', 'SNMT 13T6')
        tipo_corte = request.args.get('tipo_corte', 'General')
        
        try:
            dc = float(request.args.get('diametro', 50))
        except (ValueError, TypeError):
            dc = 50.0

        try:
            z_val = request.args.get('dientes', '')
            z = int(z_val) if z_val and str(z_val).isdigit() else None
        except (ValueError, TypeError):
            z = None

        try:
            ap = float(request.args.get('ap', 2.0))
        except (ValueError, TypeError):
            ap = 2.0

        try:
            ae = float(request.args.get('ae', 25.0))
        except (ValueError, TypeError):
            ae = 25.0

        try:
            longitud = float(request.args.get('longitud', 100.0))
        except (ValueError, TypeError):
            longitud = 100.0

        try:
            fz_raw = request.args.get('fz', '')
            fz_manual = float(fz_raw) if fz_raw and str(fz_raw).replace('.', '', 1).isdigit() and float(fz_raw) > 0 else None
        except (ValueError, TypeError):
            fz_manual = None

        res = calcular_fresado_sumitomo(
            nombre_material=material,
            serie_fresa=serie,
            tipo_inserto_dgc=tipo_inserto,
            diametro_mm=dc,
            dientes=z,
            ap_mm=ap,
            ae_mm=ae,
            longitud_mm=longitud,
            fz_manual=fz_manual,
            tipo_corte=tipo_corte
        )
        return jsonify(res if res else {})
    except Exception as err:
        print("Error en api_calcular_fresado_ajax:", err)
        return jsonify({})

if __name__ == '__main__':
    app.run(debug=True)
