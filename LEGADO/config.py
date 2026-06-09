# config.py

arbitros_cabm_2026 = {
    "A": [
        "ROSAS ARIEL", "LEYTON PABLO", "PRADO MICAELA", "MELLADO SEBASTIAN",
        "OLIVER RODRIGO", "FLORES FRANCISCO", "CALDERON BELEN", "MONTBRUM JOAQUIN",
        "TORRES JIMΜΕΝΑ", "OCHOA ALDO", "CIARAMITARO MILAGROS", "SCONFIENZA MICAELA"
    ],
    "A1": [
        "FUNES GUILLERMO", "SANCHEZ FEDERICO", "FUNES RAMON", "NARVAEZ FERNANDO",
        "QUINI MARIELA", "CANER CRISTINA", "PEREZ LUIS", "GILI RODIRGO",
        "MUÑOZ GONZALO", "FERNANDEZ MARIO", "VONKUNOSKY LUCIA", "GONZALEZ NADIA"
    ],
    "B": [
        "GARCIA SEBATIAN", "NAMAN VICTORIA", "VENTURA IGNACIO", "MOYANO MELINA",
        "ARCE GABRIEL", "PICH VALENΝΤΙΝΑ", "BARRERA LAUREANO", "OCHOA AGOSTINA",
        "SILVEYRA ROMINA", "DEMARCO LUCAS", "CASTILLO MAURICIO", "CHAVEZ CRISTIAN",
        "STAND BY PELLERITTI JOSE"
    ],
    "PROMOCIONALES": [
        "AGUILAR NICOLAS", "VERGARA LAURA", "VARGAS MATIAS", "CANALE LUCIA",
        "MAUGIERI RENZO", "MORENO LUCAS", "GONZALEZ THOMAS", "FLORES JOAQUIN",
        "GONGORA RODRIGO", "DIAZ RAMIRO", "MORENA LARA", "ABALLAY FELICITAS"
    ],
    "FORMATIVAS": [
        "GONZALES AGUSTIN", "GIANGIULO LIHUE", "ENCINA FABRICIO", "BAIGORRIA MILAGROS",
        "CALDERON MELISA", "CATALDO MILAGROS", "CACERES LUCIO", "VILLALBA LAUTARO",
        "BENITO LUCIANO", "JARA FACUNDO", "ZUCCARINI ALESSANDRO", "MAUGERI AILEN",
        "MARTIN JOAQUIN"
    ],
    "MAXI-MASTER": [
        "FIGUEOA JUAN CARLOS", "LUIS SQUEF", "GARCIA VILMA"
    ]
}

arbitros_completos = []
for categoria, arbitros in arbitros_cabm_2026.items():
    arbitros_completos.extend(arbitros)


LISTA_ARBITROS = ["-- Seleccionar --"] + sorted(arbitros_completos)


LISTA_CT = [
    "-- Seleccionar --", "Rodrigo Gilli", "Mariela Quini"
]

LISTA_CATEGORIAS = [
    "-- Seleccionar --","Mosquitos", "Premini","Mini", "U13", "U15", "U17", "U19", "Superliga", "U13F", "U15F", "U17F", "U19F", "SuperligaF", "Mayores", "Liga Nacional","Liga Federal", "Liga Argentina", "Liga Femenina"
]

LISTA_EQUIPOS_MASCULINOS = [
    "-- Seleccionar --",
    "A.D. Anzorena",
    "Andes Talleres S.C.",
    "Atenas Sport Club",
    "Atlético Club San Martín",
    "Centro Deportivo Rivadavia",
    "Club Banco Mendoza (CPBM)",
    "Club Deportivo Godoy Cruz Antonio Tomba",
    "Club Israelita Macabi",
    "Club Mendoza de Regatas",
    "Club Obras Mendoza",
    "C.S.D. General San Martín (Pacífico)",
    "C.S.D. Huracán Las Heras",
    "C.S.D. Junín (Municipalidad de Junín)",
    "Instituto San Pablo",
    "Leonardo Murialdo",
    "Municipalidad de Capital",
    "Municipalidad de Luján de Cuyo",
    "Municipalidad de San Carlos",
    "Municipalidad de Tunuyán",
    "Municipalidad de Tupungato",
    "Petroleros YPF",
    "Social Las Heras",
    "Unión Deportiva San José",
    "Universidad Nacional de Cuyo (UNCuyo)",
    "Municipalidad de Maipú"
]

LISTA_EQUIPOS_FEMENINOS = [ 
    "-- Seleccionar --",
    "Andes Talleres S.C.",
    "Atenas Sport Club",
    "Centro Deportivo Rivadavia",
    "Club Banco Mendoza (CPBM)",
    "Club Deportivo Godoy Cruz Antonio Tomba",
    "Club Mendoza de Regatas",
    "C.S.D. General San Martín (Pacífico)",
    "Juventud Mendocina",
    "Municipalidad de Junín",
    "Municipalidad de Luján de Cuyo",
    "Municipalidad de Maipú",
    "Obras Mendoza",
    "Petroleros YPF",
    "Unión Deportiva San José",
    "Universidad Nacional de Cuyo (UNCuyo)"
]