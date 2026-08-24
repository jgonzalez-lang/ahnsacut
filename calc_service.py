# calc_service.py

import math
from data_tables import (
    TABLA_MATERIALES, 
    TABLA_INSERTOS, 
    MODIFICADORES_OPERACION, 
    CLASIFICACION_MATERIAL_INSERTO,
    MATRIZ_DIENTES_SUMITOMO,
    MATRIZ_PARAMETROS_FRESADO
)

def obtener_materiales():
    return [m["material"] for m in TABLA_MATERIALES]

def obtener_insertos_compatibles(nombre_material):
    mat = next((m for m in TABLA_MATERIALES if m["material"] == nombre_material), None)
    if not mat:
        return [i["codigo"] for i in TABLA_INSERTOS]
    
    compatibles = [i["codigo"] for i in TABLA_INSERTOS if i["geometria"] in mat.get("codigos_inserto", [])]
    resto = [i["codigo"] for i in TABLA_INSERTOS if i["codigo"] not in compatibles]
    return compatibles + resto if compatibles else [i["codigo"] for i in TABLA_INSERTOS]

def obtener_factores_operacion(operacion):
    op_lower = str(operacion).lower() if operacion else "desbaste"
    if "acabado" in op_lower:
        return {"vc_factor": 1.25, "fn_factor": 0.60, "ap_factor": 0.40}
    elif "pesado" in op_lower:
        return {"vc_factor": 0.80, "fn_factor": 1.30, "ap_factor": 1.50}
    elif "exterior" in op_lower:
        return {"vc_factor": 1.05, "fn_factor": 1.00, "ap_factor": 1.00}
    else:
        return {"vc_factor": 1.00, "fn_factor": 1.00, "ap_factor": 1.00}

def determinar_tipo_corte_automatico(familia_iso, geometria_inserto, operacion, tipo_corte_mat):
    geom = geometria_inserto.upper()
    op_lower = operacion.lower()

    if familia_iso == "H":
        return "Alta Velocidad (CBN)"
    if familia_iso == "N":
        return "General / PCD"
    if familia_iso == "K":
        if "pesado" in op_lower:
            return "Interrupción Pesada"
        return "Alta Velocidad (CBN)" if geom in ["SNMG", "RNMG"] else "Corte Interrumpido"
    if familia_iso == "M":
        if "acabado" in op_lower:
            return "Corte Continuo"
        return "Interrupción Ligera"
    if familia_iso == "S":
        return "Corte Continuo" if "acabado" in op_lower else "General a Interrumpido"
    
    if "acabado" in op_lower:
        return "Acabado / General"
    elif "pesado" in op_lower:
        return "General a Interrumpido"
    
    return tipo_corte_mat if tipo_corte_mat else "Continuo a General"

def obtener_grado_y_rompevirutas_estricto(familia_iso, geometria_inserto, operacion, grado_base_mat, rvp_base_mat):
    op_lower = operacion.lower()
    es_acabado = "acabado" in op_lower
    es_desbaste_pesado = "pesado" in op_lower
    es_forma_r = geometria_inserto in ["RNMG", "RCMT", "RCKT"]

    if familia_iso == "P":
        if es_acabado:
            return "AC8020P", "RF, SU, NRE" if es_forma_r else "SU, FA, FE, FB"
        elif es_desbaste_pesado:
            return "AC8035P", "RP, MP, H1" if es_forma_r else "GE, MP"
        return grado_base_mat, "RP, RM, GU" if es_forma_r else "GU, GE"

    elif familia_iso == "M":
        if es_acabado:
            return "AC6020M", "EX, EG, RF" if es_forma_r else "EG, EX, FA"
        elif es_desbaste_pesado:
            return "AC6135M", "RM, RS, EH" if es_forma_r else "EH, ET"
        return "AC6135M", "RM, GU" if es_forma_r else "GU, EH"

    elif familia_iso == "K":
        return grado_base_mat, "N/A"

    elif familia_iso == "N":
        return grado_base_mat, "N/A"

    elif familia_iso == "S":
        if es_acabado:
            return "AC5015S", "RS, NRE, EX" if es_forma_r else "EG, EX"
        elif es_desbaste_pesado:
            return "AC5025S", "RS, RM, EM" if es_forma_r else "EM, GU"
        return "AC5015S", "RS, RM" if es_forma_r else "EG, EX, EM"

    elif familia_iso == "H":
        return grado_base_mat, "N/A"

    return grado_base_mat, rvp_base_mat

def obtener_material_real_inserto(familia_iso, nombre_material):
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

def calcular_torneado(nombre_material, codigo_inserto, diametro_inicial_mm, diametro_final_mm=40.0, longitud_mm=100.0, operacion="Desbaste", tipo_corte=None):
    if not nombre_material or not str(nombre_material).strip():
        return None

    mat = next((m for m in TABLA_MATERIALES if m["material"] == nombre_material), None)
    if not mat:
        return None

    todos_compatibles_codigos = obtener_insertos_compatibles(mat["material"])
    if not codigo_inserto or codigo_inserto not in [i["codigo"] for i in TABLA_INSERTOS]:
        codigo_inserto = todos_compatibles_codigos[0] if todos_compatibles_codigos else "CNMG 120408"

    ins = next((i for i in TABLA_INSERTOS if i["codigo"] == codigo_inserto), TABLA_INSERTOS[0])

    iso = mat["familia_iso"]
    geom = ins.get("geometria", "CNMG")

    tipo_corte_final = determinar_tipo_corte_automatico(iso, geom, operacion, mat.get("tipo_corte"))

    mod = MODIFICADORES_OPERACION.get(operacion) or obtener_factores_operacion(operacion)

    vc_base = ins["vc_iso"].get(iso, mat.get("vc_torn", 150))
    vc = round(vc_base * mod["vc_factor"], 1)

    fn_min = max(mat.get("fn_min", 0.1), ins.get("fn_min", 0.1))
    fn_max = min(mat.get("fn_max", 0.5), ins.get("fn_max", 0.5))
    fn_auto = round(((fn_min + fn_max) / 2) * mod["fn_factor"], 3)

    ap_min = max(mat.get("ap_min", 0.5), ins.get("ap_min", 0.5))
    ap_max = min(mat.get("ap_max", 3.0), ins.get("ap_max", 3.0))
    ap_auto = round(((ap_min + ap_max) / 2) * mod["ap_factor"], 2)

    d_init = float(diametro_inicial_mm) if float(diametro_inicial_mm) > 0 else 50.0
    d_final = float(diametro_final_mm) if float(diametro_final_mm) > 0 else 40.0
    longitud_val = float(longitud_mm) if float(longitud_mm) > 0 else 100.0

    d_promedio = (d_init + d_final) / 2.0
    rpm = (vc * 1000) / (math.pi * d_promedio)
    vf = rpm * fn_auto
    mrr = (vc * ap_auto * fn_auto)

    kc = mat.get("kc", 1800)
    pc = (ap_auto * fn_auto * vc * kc) / (60000 * 0.8)
    mc = (pc * 9550) / rpm if rpm > 0 else 0
    tc_por_pasada = longitud_val / vf if vf > 0 else 0

    profundidad_radial_total = max(0.0, (d_init - d_final) / 2.0)
    if profundidad_radial_total > 0 and ap_auto > 0:
        num_pasadas = math.ceil(profundidad_radial_total / ap_auto)
        ap_real_pasada = round(profundidad_radial_total / num_pasadas, 2)
    else:
        num_pasadas = 1
        ap_real_pasada = ap_auto

    tiempo_total = round(tc_por_pasada * num_pasadas, 2)

    grado_sel, rvp_sel = obtener_grado_y_rompevirutas_estricto(
        iso, geom, operacion, mat.get("calidad_rec", "AC8025P"), mat.get("rompevirutas", "N/A")
    )

    mat_inserto_real = obtener_material_real_inserto(iso, mat["material"])

    lista_recomendaciones = []
    for idx, cod in enumerate(todos_compatibles_codigos, 1):
        g_item = cod.split()[0] if " " in cod else cod
        grado_i, rvp_i = obtener_grado_y_rompevirutas_estricto(
            iso, g_item, operacion, mat.get("calidad_rec", "AC8025P"), mat.get("rompevirutas", "N/A")
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
        "geometria_letra": geom[0] if len(geom) > 0 else "C",
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
        "tiempo_pasada": round(tc_por_pasada, 2),
        "tiempo": tiempo_total,
        "num_pasadas": num_pasadas,
        "ap_real_pasada": ap_real_pasada,
        "profundidad_radial_total": round(profundidad_radial_total, 2),
        "diametro_inicial": d_init,
        "diametro_final": d_final
    }

def obtener_dientes_automaticos(serie, dc):
    s_key = "DGC" if "DGC" in serie else "WEZ"
    matriz = MATRIZ_DIENTES_SUMITOMO.get(s_key, {})
    dc_int = int(dc)
    
    if dc_int in matriz:
        return matriz[dc_int]
    
    llaves = sorted(matriz.keys())
    cercana = min(llaves, key=lambda x: abs(x - dc_int))
    return matriz[cercana]

# MATRIZ OFICIAL DE ROMPEVIRUTAS SUMITOMO SEGÚN GRUPO ISO
    MATRIZ_ROMPEVIRUTAS_FRESADO = {
        "DGC": {
            "P": "FL / G / H (General a Pesado)",
            "M": "FG / G (Inoxidables)",
            "K": "G / H (Fundición)",
            "N": "S / L (Aluminio)",
            "S": "G / FG (Superaleaciones)",
            "H": "H (Templados)"
        },
        "WEZ": {
            "P": "G / L (General / Ligero)",
            "M": "F / G (Inoxidables)",
            "K": "G / H (Fundición)",
            "N": "S (Aluminio / No Ferrosos)",
            "S": "F / G (Titanio e Inconel)",
            "H": "H (Aceros Templados)"
        }
    }
    
    rompevirutas_fresado = MATRIZ_ROMPEVIRUTAS_FRESADO.get(serie_key, {}).get(iso, "General")

def calcular_fresado_sumitomo(nombre_material, serie_fresa, tipo_inserto_dgc="SNMT 13T6", diametro_mm=50.0, dientes=None, ap_mm=2.0, ae_mm=25.0, longitud_mm=100.0, fz_manual=None, tipo_corte="General"):
    mat_name = str(nombre_material).strip().lower() if nombre_material else ""
    
    mat = None
    if mat_name:
        # Búsqueda por coincidencia parcial (encuentra "1045", "4140", "304", "inox", "aluminio", etc.)
        mat = next((m for m in TABLA_MATERIALES if mat_name in m["material"].lower()), None)
    
    # Si no hay coincidencia o la casilla está vacía, no retorna vacío si hay texto
    if not mat and mat_name:
        mat = TABLA_MATERIALES[0] # Toma el primer material como base para evitar responder {}

    if not mat:
        return {}

    iso = mat.get("familia_iso", "P")
    serie_upper = str(serie_fresa).upper()
    serie_key = "WEZ" if "WEZ" in serie_upper else "DGC"

    dc = float(diametro_mm) if diametro_mm and float(diametro_mm) > 0 else 50.0
    z = int(dientes) if dientes and int(dientes) > 0 else obtener_dientes_automaticos(serie_key, dc)
    ap = float(ap_mm) if ap_mm and float(ap_mm) > 0 else 2.0
    ae = float(ae_mm) if ae_mm and float(ae_mm) > 0 else (dc * 0.5)
    longitud = float(longitud_mm) if longitud_mm and float(longitud_mm) > 0 else 100.0

    vc = float(mat.get("vc_fres", 210.0))
    fz = 0.25
    grado = "ACP2000"
    codigo_inserto_sug = "SNMT 13T6ANER-G"
    geom_cuerpo = "Planeado 45°"

    if serie_key in MATRIZ_PARAMETROS_FRESADO and iso in MATRIZ_PARAMETROS_FRESADO[serie_key]:
        params_iso = MATRIZ_PARAMETROS_FRESADO[serie_key][iso]
        
        if serie_key == "DGC":
            sub_key = "ONMT" if "ONMT" in str(tipo_inserto_dgc).upper() else "SNMT"
            config = params_iso.get(sub_key, {}) if isinstance(params_iso, dict) else {}
            vc = float(config.get("vc", vc))
            fz = float(config.get("fz_opt", 0.25))
            grado = config.get("grado", "ACP2000")
            insertos = config.get("insertos", ["SNMT 13T6ANER-G"])
            codigo_inserto_sug = insertos[0] if insertos else "SNMT 13T6ANER-G"
            geom_cuerpo = f"Planeado 45° ({sub_key})"
        else:
            config = params_iso if isinstance(params_iso, dict) else {}
            vc = float(config.get("vc", vc))
            fz = float(config.get("fz_opt", 0.18))
            grado = config.get("grado", "ACP2000")
            insertos = config.get("insertos", ["AOMT 110350-G"])
            codigo_inserto_sug = insertos[0] if insertos else "AOMT 110350-G"
            geom_cuerpo = "Escuadrado 90° (AOMT)"

    if fz_manual and float(fz_manual) > 0:
        fz = float(fz_manual)
    else:
        if (ae / dc) < 0.3:
            fz *= 1.20

    rpm = (vc * 1000.0) / (math.pi * dc) if dc > 0 else 0
    vf = rpm * fz * z
    vc_calc = (math.pi * dc * rpm) / 1000.0
    mrr = (ap * ae * vf) / 1000.0
    tiempo_maquinado = longitud / vf if vf > 0 else 0
    vtr = mrr * tiempo_maquinado

    kc = mat.get("kc", 1800)
    pc = (mrr * kc) / (60000.0 * 0.8)

    # MATRIZ DE ROMPEVIRUTAS DE FRESADO
    MATRIZ_ROMPEVIRUTAS = {
        "DGC": {"P": "FL / G / H", "M": "FG / G", "K": "G / H", "N": "S / L", "S": "G / FG", "H": "H"},
        "WEZ": {"P": "G / L", "M": "F / G", "K": "G / H", "N": "S", "S": "F / G", "H": "H"}
    }
    rompevirutas_fresado = MATRIZ_ROMPEVIRUTAS.get(serie_key, {}).get(iso, "General")

    return {
        "material": mat["material"],
        "familia_iso": iso,
        "dureza": mat.get("dureza", "-"),
        "serie_fresa": serie_fresa,
        "geometria_cuerpo": geom_cuerpo,
        "codigo_inserto": codigo_inserto_sug,
        "grado_sumitomo": grado,
        "rompevirutas": rompevirutas_fresado,
        "material_inserto_tipo": CLASIFICACION_MATERIAL_INSERTO.get(grado, "CVD Coated Carbide"),
        "diametro": dc,
        "dientes": z,
        "ap": ap,
        "ae": ae,
        "longitud": longitud,
        "vc": round(vc_calc, 1),
        "fz": round(fz, 3),
        "rpm": round(rpm, 1),
        "vf": round(vf, 2),
        "mrr": round(mrr, 2),
        "tiempo": round(tiempo_maquinado, 2),
        "vtr": round(vtr, 2),
        "potencia": round(pc, 2)
    }
