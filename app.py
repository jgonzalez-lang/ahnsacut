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
    tipo_corte_sel = ""
    diametro_sel = "50"
    longitud_sel = "100"

    if request.method == 'POST':
        material_sel = request.form.get('material', '')
        inserto_sel = request.form.get('inserto', '')
        operacion_sel = request.form.get('operacion', 'Desbaste')
        tipo_corte_sel = request.form.get('tipo_corte', '')
        diametro_sel = request.form.get('diametro', '50')
        longitud_sel = request.form.get('longitud', '100')
        
        try:
            diametro_val = float(diametro_sel)
            longitud_val = float(longitud_sel)
            if material_sel:
                resultado = calcular_torneado(material_sel, inserto_sel, diametro_val, longitud_val, operacion_sel, tipo_corte_sel)
        except (ValueError, TypeError):
            resultado = None

    # Modelos representativos principales para la galería (8 estándar + 3 Tipo R)
    modelos_representativos = [
        "CNMG 120408", "DNMG 150408", "WNMG 080408", "TNMG 160408",
        "CCMT 060204", "DCMT 070204", "SNMG 120408", "VNMG 160404",
        "RNMG 120400", "RCMT 1003MO", "RNMG 190600"
    ]

    lista_insertos_dash = []
    for ins in TABLA_INSERTOS:
        if ins.get("codigo") in modelos_representativos:
            vc_map = ins.get("vc_iso", {})
            iso_p = list(vc_map.keys())[0] if isinstance(vc_map, dict) and len(vc_map) > 0 else "P"
            lista_insertos_dash.append({
                "codigo": str(ins.get("codigo", "-")),
                "tipo_operacion": str(ins.get("tipo_operacion", "General")),
                "iso_principal": str(iso_p)
            })

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
        tipo_corte_sel=tipo_corte_sel,
        diametro_sel=diametro_sel, 
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
    tipo_corte = request.args.get('tipo_corte', '')
    try:
        diametro = float(request.args.get('diametro', 50))
    except ValueError:
        diametro = 50.0
    try:
        longitud = float(request.args.get('longitud', 100))
    except ValueError:
        longitud = 100.0

    res = calcular_torneado(material, inserto, diametro, longitud, operacion, tipo_corte)
    return jsonify(res if res else {})

if __name__ == '__main__':
    app.run(debug=True)