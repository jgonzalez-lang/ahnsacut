# app.py

from flask import Flask, render_template, request, jsonify
from calc_service import obtener_materiales, obtener_insertos_compatibles, calcular_torneado
from data_tables import TABLA_MATERIALES, TABLA_INSERTOS

app = Flask(__name__)

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
        material_sel = request.form.get('material', '')
        inserto_sel = request.form.get('inserto', '')
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
                    material_sel, inserto_sel, d_init_val, d_fin_val, longitud_val, operacion_sel
                )
        except (ValueError, TypeError):
            resultado = None

    lista_insertos_dash = [
        {"codigo": "CNMG 120408", "tipo_operacion": "Desbaste / Exterior", "iso_principal": "P"},
        {"codigo": "DNMG 150408", "tipo_operacion": "Exterior", "iso_principal": "P"},
        {"codigo": "WNMG 080408", "tipo_operacion": "Exterior", "iso_principal": "P"},
        {"codigo": "TNMG 160408", "tipo_operacion": "Desbaste", "iso_principal": "P"},
        {"codigo": "DCMT 070204", "tipo_operacion": "Acabado", "iso_principal": "M"},
        {"codigo": "TCMT 110204", "tipo_operacion": "Acabado", "iso_principal": "M"},
        {"codigo": "SNMG 120408", "tipo_operacion": "Desbaste Pesado", "iso_principal": "K"},
        {"codigo": "CCMT 060204", "tipo_operacion": "Acabado", "iso_principal": "N"},
        {"codigo": "RNMG 120400", "tipo_operacion": "Desbaste Pesado / Perfilado", "iso_principal": "S"},
        {"codigo": "VNMG 160404", "tipo_operacion": "Acabado", "iso_principal": "H"},
        {"codigo": "RCMT 1003MO", "tipo_operacion": "Acabado / Perfilado Redondo", "iso_principal": "M"}
    ]

    stats_dashboard = {
        "total_materiales": len(TABLA_MATERIALES),
        "total_insertos": len(TABLA_INSERTOS),
        "familias_iso": len(set(m["familia_iso"] for m in TABLA_MATERIALES)),
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
        stats=stats_dashboard,
        insertos_dash=lista_insertos_dash
    )

@app.route('/api/insertos', methods=['GET'])
def api_insertos():
    material = request.args.get('material')
    if not material:
        return jsonify([])
    return jsonify(obtener_insertos_compatibles(material))

@app.route('/api/calcular_ajax', methods=['GET'])
def api_calcular_ajax():
    material = request.args.get('material', '')
    inserto = request.args.get('inserto', '')
    operacion = request.args.get('operacion', 'Desbaste')
    try:
        d_init = float(request.args.get('diametro_inicial', 50))
    except ValueError:
        d_init = 50.0
    try:
        d_fin = float(request.args.get('diametro_final', 40))
    except ValueError:
        d_fin = 40.0
    try:
        longitud = float(request.args.get('longitud', 100))
    except ValueError:
        longitud = 100.0

    res = calcular_torneado(material, inserto, d_init, d_fin, longitud, operacion)
    return jsonify(res if res else {})

if __name__ == '__main__':
    app.run(debug=True)
