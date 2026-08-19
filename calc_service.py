# calc_service.py

import math
from data_tables import TABLA_MATERIALES, TABLA_INSERTOS, MODIFICADORES_OPERACION

def obtener_materiales():
    """Devuelve la lista limpia de todos los nombres de materiales registrados."""
    return [m["material"] for m in TABLA_MATERIALES]

def obtener_insertos_compatibles(nombre_material):
    """Filtra y devuelve los códigos de insertos compatibles para un material dado."""
    mat = next((m for m in TABLA_MATERIALES if m["material"] == nombre_material), None)
    if not mat:
        return [i["codigo"] for i in TABLA_INSERTOS]
    
    compatibles = [i["codigo"] for i in TABLA_INSERTOS if i["geometria"] in mat.get("codigos_inserto", [])]
    resto = [i["codigo"] for i in TABLA_INSERTOS if i["codigo"] not in compatibles]
    return compatibles + resto if compatibles else [i["codigo"] for i in TABLA_INSERTOS]

def obtener_factores_operacion(operacion):
    """Define modificadores dinámicos para Vc, fn y ap según la operación seleccionada."""
    op_lower = operacion.lower()
    if "acabado" in op_lower:
        return {"vc_factor": 1.25, "fn_factor": 0.60, "ap_factor": 0.40}
    elif "pesado" in op_lower:
        return {"vc_factor": 0.80, "fn_factor": 1.30, "ap_factor": 1.50}
    elif "exterior" in op_lower:
        return {"vc_factor": 1.05, "fn_factor": 1.00, "ap_factor": 1.00}
    else:  # Desbaste estándar / General
        return {"vc_factor": 1.00, "fn_factor": 1.00, "ap_factor": 1.00}

def obtener_grado_y_rompevirutas_estricto(familia_iso, geometria_inserto, operacion, grado_base_mat, rvp_base_mat):
    """
    Asigna únicamente los Rompevirutas y Grados Sumitomo de las listas maestras,
    incluyendo la lógica especial para geometrías redondas Forma R (RNMG / RCMT).
    """
    op_lower = operacion.lower()
    es_acabado = "acabado" in op_lower
    es_desbaste_pesado = "pesado" in op_lower
    es_forma_r = geometria_inserto in ["RNMG", "RCMT", "RCKT"]

    # ISO P (Aceros Carbono y Aleados)
    if familia_iso == "P":
        if es_acabado:
            return "AC8020P", "RF, SU, NRE" if es_forma_r else "SU, FA, FE, FB"
        elif es_desbaste_pesado:
            return "AC8035P", "RP, MP, H1" if es_forma_r else "GE, MP"
        return grado_base_mat, "RP, RM, GU" if es_forma_r else "GU, GE"

    # ISO M (Aceros Inoxidables)
    elif familia_iso == "M":
        if es_acabado:
            return "AC6020M", "EX, EG, RF" if es_forma_r else "EG, EX, FA"
        elif es_desbaste_pesado:
            return "AC6135M", "RM, RS, EH" if es_forma_r else "EH, ET"
        return "AC6135M", "RM, GU" if es_forma_r else "GU, EH"

    # ISO K (Fundiciones) -> Rompevirutas N/A
    elif familia_iso == "K":
        return grado_base_mat, "N/A"

    # ISO N (Aluminio / Cobre / No Ferrosos) -> Rompevirutas N/A
    elif familia_iso == "N":
        return grado_base_mat, "N/A"

    # ISO S (Titanio e Inconel / Superaleaciones)
    elif familia_iso == "S":
        if es_acabado:
            return "AC5015S", "RS, NRE, EX" if es_forma_r else "EG, EX"
        elif es_desbaste_pesado:
            return "AC5025S", "RS, RM, EM" if es_forma_r else "EM, GU"
        return "AC5015S", "RS, RM" if es_forma_r else "EG, EX, EM"

    # ISO H (Aceros Templados) -> Rompevirutas N/A
    elif familia_iso == "H":
        return grado_base_mat, "N/A"

    return grado_base_mat, rvp_base_mat

def obtener_material_real_inserto(familia_iso, nombre_material):
    """Retorna strictly la composición del herramental/inserto."""
    if "D2 (Recocido)" in nombre_material:
        return "Coated Cermet / Cermet"
    
    if familia_iso in ["P", "M", "S"]:
        return "Coated Carbide"
    elif familia_iso == "N":
        return "PCD / Cemented Carbide"
    elif familia_iso == "K":
        if "G25" in nombre_material:
            return "Ceramic / CBN"
        return "Coated Carbide"
    elif familia_iso == "H":
        return "CBN"
    
    return "Coated Carbide"

def calcular_torneado(nombre_material, codigo_inserto, diametro_mm, longitud_mm=100.0, operacion="Desbaste", tipo_corte=None):
    mat = next((m for m in TABLA_MATERIALES if m["material"] == nombre_material), None)
    if not mat:
        mat = TABLA_MATERIALES[0]

    todos_compatibles_codigos = obtener_insertos_compatibles(mat["material"])
    if not codigo_inserto or codigo_inserto not in [i["codigo"] for i in TABLA_INSERTOS]:
        codigo_inserto = todos_compatibles_codigos[0] if todos_compatibles_codigos else "CNMG 120408"

    ins = next((i for i in TABLA_INSERTOS if i["codigo"] == codigo_inserto), TABLA_INSERTOS[0])

    tipo_corte_final = tipo_corte if tipo_corte else mat.get("tipo_corte", "General")

    mod = MODIFICADORES_OPERACION.get(operacion) or obtener_factores_operacion(operacion)

    iso = mat["familia_iso"]
    vc_base = ins["vc_iso"].get(iso, mat.get("vc_torn", 150))
    vc = round(vc_base * mod["vc_factor"], 1)

    fn_min = max(mat.get("fn_min", 0.1), ins.get("fn_min", 0.1))
    fn_max = min(mat.get("fn_max", 0.5), ins.get("fn_max", 0.5))
    fn_auto = round(((fn_min + fn_max) / 2) * mod["fn_factor"], 3)

    ap_min = max(mat.get("ap_min", 0.5), ins.get("ap_min", 0.5))
    ap_max = min(mat.get("ap_max", 3.0), ins.get("ap_max", 3.0))
    ap_auto = round(((ap_min + ap_max) / 2) * mod["ap_factor"], 2)

    diametro_val = float(diametro_mm) if float(diametro_mm) > 0 else 50.0
    longitud_val = float(longitud_mm) if float(longitud_mm) > 0 else 100.0

    rpm = (vc * 1000) / (math.pi * diametro_val)
    vf = rpm * fn_auto
    mrr = (vc * ap_auto * fn_auto)

    kc = mat.get("kc", 1800)
    pc = (ap_auto * fn_auto * vc * kc) / (60000 * 0.8)
    mc = (pc * 9550) / rpm if rpm > 0 else 0
    tc = longitud_val / vf if vf > 0 else 0

    grado_sel, rvp_sel = obtener_grado_y_rompevirutas_estricto(
        iso, ins.get("geometria", "CNMG"), operacion, mat.get("calidad_rec", "AC8025P"), mat.get("rompevirutas", "N/A")
    )

    mat_inserto_real = obtener_material_real_inserto(iso, mat["material"])

    lista_recomendaciones = []
    for idx, cod in enumerate(todos_compatibles_codigos, 1):
        geom = cod.split()[0] if " " in cod else cod
        grado_i, rvp_i = obtener_grado_y_rompevirutas_estricto(
            iso, geom, operacion, mat.get("calidad_rec", "AC8025P"), mat.get("rompevirutas", "N/A")
        )
        
        lista_recomendaciones.append({
            "numero": idx,
            "codigo_inserto": cod,
            "grado_sumitomo": grado_i,
            "rompevirutas": rvp_i,
            "es_principal": (cod == codigo_inserto)
        })

    return {
        "material": mat["material"],
        "familia_iso": iso,
        "subclasificacion_iso": mat.get("subclasificacion_iso", "-"),
        "dureza": mat.get("dureza", "-"),
        "categoria_inserto": mat_inserto_real,
        "grado_calidad": grado_sel,
        "rompevirutas": rvp_sel,
        "tipo_corte": tipo_corte_final,
        "inserto": ins["codigo"],
        "operacion_seleccionada": operacion,
        "tipo_operacion": ins.get("tipo_operacion", "General"),
        "todos_compatibles": todos_compatibles_codigos,
        "lista_recomendaciones": lista_recomendaciones,
        "vc": vc,
        "fn": fn_auto,
        "fn_min": fn_min,
        "fn_max": fn_max,
        "ap": ap_auto,
        "ap_min": ap_min,
        "ap_max": ap_max,
        "rpm": round(rpm, 0),
        "vf": round(vf, 1),
        "mrr": round(mrr, 1),
        "potencia": round(pc, 2),
        "torque": round(mc, 1),
        "tiempo": round(tc, 2)
    }