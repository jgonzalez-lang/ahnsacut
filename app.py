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

if __name__ == '__main__':
    app.run(debug=True)
