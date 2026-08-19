# data_tables.py

MODIFICADORES_OPERACION = {
    "Desbaste": {"vc_factor": 1.0, "fn_factor": 1.0, "ap_factor": 1.0},
    "Desbaste / Exterior": {"vc_factor": 1.05, "fn_factor": 1.1, "ap_factor": 1.1},
    "Desbaste Pesado": {"vc_factor": 0.85, "fn_factor": 1.3, "ap_factor": 1.4},
    "Exterior / Acabado": {"vc_factor": 1.15, "fn_factor": 0.7, "ap_factor": 0.5},
    "Exterior": {"vc_factor": 1.0, "fn_factor": 0.9, "ap_factor": 0.8},
    "Acabado": {"vc_factor": 1.25, "fn_factor": 0.5, "ap_factor": 0.3}
}

TABLA_MATERIALES = [
    {
        "material": "Acero AISI 1020 / Blando",
        "familia_iso": "P", "subclasificacion_iso": "P10–P30", "categoria": "Mild Steel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "120 HB", "kc": 1500,
        "vc_fres": 220, "vc_torn": 250, "vc_barr": 140, "vc_rosc": 250,
        "fn_min": 0.15, "fn_max": 0.40, "ap_min": 1.0, "ap_max": 5.0,
        "calidad_rec": "AC8025", "rompevirutas": "GU, GE", "tipo_corte": "General a Interrumpido"
    },
    {
        "material": "Acero Estructural A36",
        "familia_iso": "P", "subclasificacion_iso": "P10–P30", "categoria": "Mild Steel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "140 HB", "kc": 1600,
        "vc_fres": 210, "vc_torn": 230, "vc_barr": 130, "vc_rosc": 220,
        "fn_min": 0.15, "fn_max": 0.40, "ap_min": 1.0, "ap_max": 5.0,
        "calidad_rec": "AC8025", "rompevirutas": "GU, GE", "tipo_corte": "General a Interrumpido"
    },
    {
        "material": "Acero AISI 1045 / Medio Carbono",
        "familia_iso": "P", "subclasificacion_iso": "P10–P20", "categoria": "Carbon & Alloy",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "180 HB", "kc": 1800,
        "vc_fres": 190, "vc_torn": 210, "vc_barr": 120, "vc_rosc": 200,
        "fn_min": 0.10, "fn_max": 0.35, "ap_min": 0.5, "ap_max": 4.0,
        "calidad_rec": "AC8020", "rompevirutas": "GU, GE, SU", "tipo_corte": "Continuo a General"
    },
    {
        "material": "Acero AISI 4140 / Bonificado",
        "familia_iso": "P", "subclasificacion_iso": "P10–P20", "categoria": "Carbon & Alloy",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "280 HB", "kc": 2100,
        "vc_fres": 150, "vc_torn": 170, "vc_barr": 95, "vc_rosc": 150,
        "fn_min": 0.10, "fn_max": 0.35, "ap_min": 0.5, "ap_max": 4.0,
        "calidad_rec": "AC8020", "rompevirutas": "GU, GE, SU", "tipo_corte": "Continuo a General"
    },
    {
        "material": "Acero AISI 4340 / Alta Res.",
        "familia_iso": "P", "subclasificacion_iso": "P10–P20", "categoria": "Carbon & Alloy",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "320 HB", "kc": 2300,
        "vc_fres": 130, "vc_torn": 145, "vc_barr": 80, "vc_rosc": 120,
        "fn_min": 0.10, "fn_max": 0.35, "ap_min": 0.5, "ap_max": 4.0,
        "calidad_rec": "AC8020", "rompevirutas": "GU, GE, SU", "tipo_corte": "Continuo a General"
    },
    {
        "material": "Acero Herramienta D2 (Recocido)",
        "familia_iso": "P", "subclasificacion_iso": "P01–P20", "categoria": "Tool Steel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "220 HB", "kc": 2200,
        "vc_fres": 110, "vc_torn": 130, "vc_barr": 70, "vc_rosc": 100,
        "fn_min": 0.05, "fn_max": 0.25, "ap_min": 0.2, "ap_max": 3.0,
        "calidad_rec": "T1500Z / T1500A", "rompevirutas": "FB, FE, FA", "tipo_corte": "Acabado / General"
    },
    {
        "material": "Inoxidable AISI 304 (Austenítico)",
        "familia_iso": "M", "subclasificacion_iso": "M20–M40", "categoria": "Stainless Steel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "170 HB", "kc": 2000,
        "vc_fres": 120, "vc_torn": 140, "vc_barr": 75, "vc_rosc": 120,
        "fn_min": 0.08, "fn_max": 0.35, "ap_min": 0.3, "ap_max": 4.0,
        "calidad_rec": "AC6135", "rompevirutas": "GU, EH", "tipo_corte": "Interrupción Ligera"
    },
    {
        "material": "Inoxidable AISI 316 (Austenítico)",
        "familia_iso": "M", "subclasificacion_iso": "M20–M40", "categoria": "Stainless Steel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "185 HB", "kc": 2100,
        "vc_fres": 110, "vc_torn": 130, "vc_barr": 65, "vc_rosc": 100,
        "fn_min": 0.08, "fn_max": 0.35, "ap_min": 0.3, "ap_max": 4.0,
        "calidad_rec": "AC6135", "rompevirutas": "GU, EH", "tipo_corte": "Interrupción Ligera"
    },
    {
        "material": "Inoxidable AISI 420 (Martensítico)",
        "familia_iso": "M", "subclasificacion_iso": "M10–M30", "categoria": "Stainless Steel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "200 HB", "kc": 1900,
        "vc_fres": 140, "vc_torn": 160, "vc_barr": 85, "vc_rosc": 140,
        "fn_min": 0.08, "fn_max": 0.30, "ap_min": 0.3, "ap_max": 3.0,
        "calidad_rec": "AC6030", "rompevirutas": "EG, GU, EX", "tipo_corte": "Corte Continuo"
    },
    {
        "material": "Inoxidable Dúplex 2205",
        "familia_iso": "M", "subclasificacion_iso": "M20–M40", "categoria": "Stainless Steel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "260 HB", "kc": 2400,
        "vc_fres": 85, "vc_torn": 100, "vc_barr": 50, "vc_rosc": 80,
        "fn_min": 0.08, "fn_max": 0.35, "ap_min": 0.3, "ap_max": 4.0,
        "calidad_rec": "AC6135", "rompevirutas": "GU, EH", "tipo_corte": "Interrupción Ligera"
    },
    {
        "material": "Fundición Gris G25 / GG25",
        "familia_iso": "K", "subclasificacion_iso": "K10–K30", "categoria": "Cast Iron",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "SNMG", "TNMG"],
        "dureza": "200 HB", "kc": 1100,
        "vc_fres": 200, "vc_torn": 220, "vc_barr": 130, "vc_rosc": 200,
        "fn_min": 0.15, "fn_max": 0.50, "ap_min": 1.0, "ap_max": 6.0,
        "calidad_rec": "BN7125", "rompevirutas": "N/A", "tipo_corte": "Alta Velocidad (CBN)"
    },
    {
        "material": "Fundición Nodular GGG40",
        "familia_iso": "K", "subclasificacion_iso": "K10–K20", "categoria": "Cast Iron",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "SNMG", "TNMG"],
        "dureza": "160 HB", "kc": 1300,
        "vc_fres": 180, "vc_torn": 200, "vc_barr": 110, "vc_rosc": 180,
        "fn_min": 0.15, "fn_max": 0.45, "ap_min": 1.0, "ap_max": 5.0,
        "calidad_rec": "AC4015K", "rompevirutas": "N/A", "tipo_corte": "General a Interrumpido"
    },
    {
        "material": "Fundición Nodular GGG70",
        "familia_iso": "K", "subclasificacion_iso": "K10–K30", "categoria": "Cast Iron",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "SNMG", "TNMG"],
        "dureza": "260 HB", "kc": 1500,
        "vc_fres": 130, "vc_torn": 150, "vc_barr": 85, "vc_rosc": 140,
        "fn_min": 0.20, "fn_max": 0.50, "ap_min": 1.5, "ap_max": 6.0,
        "calidad_rec": "AC4125K", "rompevirutas": "N/A", "tipo_corte": "Interrupción Pesada"
    },
    {
        "material": "Aluminio 6061-T6",
        "familia_iso": "N", "subclasificacion_iso": "N10–N30", "categoria": "Aluminum",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "95 HB", "kc": 700,
        "vc_fres": 550, "vc_torn": 650, "vc_barr": 300, "vc_rosc": 450,
        "fn_min": 0.05, "fn_max": 0.30, "ap_min": 0.2, "ap_max": 4.0,
        "calidad_rec": "DA1000 / H1", "rompevirutas": "N/A", "tipo_corte": "General / PCD"
    },
    {
        "material": "Aluminio 7075-T6 (Aerospacial)",
        "familia_iso": "N", "subclasificacion_iso": "N10–N30", "categoria": "Aluminum",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "150 HB", "kc": 800,
        "vc_fres": 480, "vc_torn": 550, "vc_barr": 260, "vc_rosc": 400,
        "fn_min": 0.05, "fn_max": 0.30, "ap_min": 0.2, "ap_max": 4.0,
        "calidad_rec": "DA1000 / H1", "rompevirutas": "N/A", "tipo_corte": "General / PCD"
    },
    {
        "material": "Latón C36000 (Fácil Mecanizado)",
        "familia_iso": "N", "subclasificacion_iso": "N10–N20", "categoria": "Non-Ferrous",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "130 HB", "kc": 750,
        "vc_fres": 380, "vc_torn": 420, "vc_barr": 220, "vc_rosc": 350,
        "fn_min": 0.05, "fn_max": 0.30, "ap_min": 0.2, "ap_max": 3.0,
        "calidad_rec": "DA150 / H1", "rompevirutas": "N/A", "tipo_corte": "General / PCD"
    },
    {
        "material": "Bronce al Aluminio",
        "familia_iso": "N", "subclasificacion_iso": "N10–N20", "categoria": "Non-Ferrous",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "180 HB", "kc": 900,
        "vc_fres": 160, "vc_torn": 180, "vc_barr": 95, "vc_rosc": 180,
        "fn_min": 0.05, "fn_max": 0.30, "ap_min": 0.2, "ap_max": 3.0,
        "calidad_rec": "DA150 / H1", "rompevirutas": "N/A", "tipo_corte": "General / PCD"
    },
    {
        "material": "Titanio Grado 5 (Ti-6Al-4V)",
        "familia_iso": "S", "subclasificacion_iso": "S01–S15", "categoria": "HRSA / Titanium",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "330 HB", "kc": 2800,
        "vc_fres": 55, "vc_torn": 65, "vc_barr": 35, "vc_rosc": 60,
        "fn_min": 0.10, "fn_max": 0.35, "ap_min": 0.5, "ap_max": 4.0,
        "calidad_rec": "AC9115", "rompevirutas": "EG, EX, EM", "tipo_corte": "Corte Continuo"
    },
    {
        "material": "Inconel 718 (Base Níquel)",
        "familia_iso": "S", "subclasificacion_iso": "S01–S15", "categoria": "HRSA / Nickel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "360 HB", "kc": 3100,
        "vc_fres": 35, "vc_torn": 42, "vc_barr": 22, "vc_rosc": 40,
        "fn_min": 0.10, "fn_max": 0.35, "ap_min": 0.5, "ap_max": 4.0,
        "calidad_rec": "AC5015S", "rompevirutas": "EX, EG", "tipo_corte": "Corte Continuo"
    },
    {
        "material": "Hastelloy C276",
        "familia_iso": "S", "subclasificacion_iso": "S01–S15", "categoria": "HRSA / Nickel",
        "codigos_inserto": ["CNMG", "DNMG", "WNMG", "TNMG", "SNMG", "VNMG", "CCMT", "DCMT", "TCMT"],
        "dureza": "210 HB", "kc": 2900,
        "vc_fres": 40, "vc_torn": 48, "vc_barr": 25, "vc_rosc": 50,
        "fn_min": 0.10, "fn_max": 0.35, "ap_min": 0.5, "ap_max": 4.0,
        "calidad_rec": "AC5015S", "rompevirutas": "EX, EG", "tipo_corte": "Corte Continuo"
    },
    {
        "material": "Acero D2 Templado (58-60 HRC)",
        "familia_iso": "H", "subclasificacion_iso": "H20–H30", "categoria": "Hardened Steel",
        "codigos_inserto": ["CNMG", "SNMG", "VNMG"],
        "dureza": "58 HRC", "kc": 3500,
        "vc_fres": 50, "vc_torn": 60, "vc_barr": 30, "vc_rosc": 50,
        "fn_min": 0.10, "fn_max": 0.30, "ap_min": 0.3, "ap_max": 3.0,
        "calidad_rec": "BNC2125 / BNC2135", "rompevirutas": "N/A", "tipo_corte": "Alta Velocidad (CBN)"
    },
    {
        "material": "Acero H13 Templado (50 HRC)",
        "familia_iso": "H", "subclasificacion_iso": "H10–H20", "categoria": "Hardened Steel",
        "codigos_inserto": ["CNMG", "SNMG", "VNMG"],
        "dureza": "50 HRC", "kc": 3200,
        "vc_fres": 70, "vc_torn": 80, "vc_barr": 40, "vc_rosc": 70,
        "fn_min": 0.08, "fn_max": 0.30, "ap_min": 0.3, "ap_max": 3.0,
        "calidad_rec": "BNC2115 / BNC2125", "rompevirutas": "N/A", "tipo_corte": "Alta Velocidad (CBN)"
    }
]

TABLA_INSERTOS = [
    {"codigo": "CNMG 120408", "geometria": "CNMG", "tipo_operacion": "Desbaste Pesado", "vc_iso": {"P": 220, "M": 140, "K": 180, "N": 500, "S": 65, "H": 70}, "fn_min": 0.20, "fn_max": 0.45, "ap_min": 1.5, "ap_max": 5.0},
    {"codigo": "CNMG 120404", "geometria": "CNMG", "tipo_operacion": "Desbaste / Exterior", "vc_iso": {"P": 230, "M": 150, "K": 190, "N": 520, "S": 70, "H": 75}, "fn_min": 0.15, "fn_max": 0.30, "ap_min": 1.0, "ap_max": 4.0},
    {"codigo": "DNMG 150408", "geometria": "DNMG", "tipo_operacion": "Exterior", "vc_iso": {"P": 210, "M": 130, "K": 170, "N": 480, "S": 60, "H": 65}, "fn_min": 0.18, "fn_max": 0.38, "ap_min": 1.0, "ap_max": 4.0},
    {"codigo": "DNMG 150404", "geometria": "DNMG", "tipo_operacion": "Exterior / Acabado", "vc_iso": {"P": 220, "M": 140, "K": 180, "N": 500, "S": 65, "H": 70}, "fn_min": 0.10, "fn_max": 0.25, "ap_min": 0.5, "ap_max": 3.0},
    {"codigo": "VNMG 160404", "geometria": "VNMG", "tipo_operacion": "Acabado", "vc_iso": {"P": 240, "M": 160, "K": 200, "N": 550, "S": 75, "H": 80}, "fn_min": 0.08, "fn_max": 0.20, "ap_min": 0.3, "ap_max": 2.0},
    {"codigo": "WNMG 080408", "geometria": "WNMG", "tipo_operacion": "Exterior", "vc_iso": {"P": 210, "M": 130, "K": 170, "N": 480, "S": 60, "H": 65}, "fn_min": 0.18, "fn_max": 0.38, "ap_min": 1.0, "ap_max": 4.0},
    {"codigo": "TNMG 160408", "geometria": "TNMG", "tipo_operacion": "Desbaste Pesado", "vc_iso": {"P": 200, "M": 120, "K": 160, "N": 450, "S": 55, "H": 60}, "fn_min": 0.20, "fn_max": 0.45, "ap_min": 1.5, "ap_max": 5.0},
    {"codigo": "CCMT 060204", "geometria": "CCMT", "tipo_operacion": "Acabado", "vc_iso": {"P": 250, "M": 170, "K": 210, "N": 580, "S": 80, "H": 85}, "fn_min": 0.05, "fn_max": 0.18, "ap_min": 0.2, "ap_max": 2.0}
]
