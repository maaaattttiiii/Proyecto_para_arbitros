import mysql.connector
import streamlit as st

arbitros_cabm = {
    "A": ["ROSAS ARIEL", "LEYTON PABLO", "PRADO MICAELA", "MELLADO SEBASTIAN", "OLIVER RODRIGO", "FLORES FRANCISCO", "CALDERON BELEN", "MONTBRUM JOAQUIN", "TORRES JIMENA", "OCHOA ALDO", "CIARAMITARO MILAGROS", "SCONFIENZA MICAELA"],
    "A1": ["FUNES GUILLERMO", "SANCHEZ FEDERICO", "FUNES RAMON", "NARVAEZ FERNANDO", "QUINI MARIELA", "CANER CRISTINA", "PEREZ LUIS", "GILI RODRIGO", "MUÑOZ GONZALO", "FERNANDEZ MARIO", "VONKUNOSKY LUCIA", "GONZALEZ NADIA"],
    "B": ["GARCIA SEBASTIAN", "NAMAN VICTORIA", "VENTURA IGNACIO", "MOYANO MELINA", "ARCE GABRIEL", "PICH VALENTINA", "BARRERA LAUREANO", "OCHOA AGOSTINA", "SILVEYRA ROMINA", "DEMARCO LUCAS", "CASTILLO MAURICIO", "CHAVEZ CRISTIAN"],
    "PROMOCIONALES": ["AGUILAR NICOLAS", "VERGARA LAURA", "VARGAS MATIAS", "CANALE LUCIA", "MAUGIERI RENZO", "MORENO LUCAS", "GONZALEZ THOMAS", "FLORES JOAQUIN", "GONGORA RODRIGO", "DIAZ RAMIRO", "MORENA LARA", "ABALLAY FELICITAS"],
    "FORMATIVAS": ["GONZALES AGUSTIN", "GIANGIULO LIHUE", "ENCINA FABRICIO", "BAIGORRIA MILAGROS", "CALDERON MELISA", "CATALDO MILAGROS", "CACERES LUCIO", "VILLALBA LAUTARO", "BENITO LUCIANO", "JARA FACUNDO", "ZUCCARINI ALESSANDRO", "MAUGERI AILEN", "MARTIN JOAQUIN"],
    "MAXI_MASTER": ["FIGUEROA JUAN CARLOS", "SQUEF LUIS", "GARCIA VILMA"]
}

def migrar():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
            # Sacamos el parámetro 'database' de acá para que no haya conflictos
        )
        cursor = conn.cursor()
        print("Conectado a la nube. Empezando a migrar...")
        
        for categoria, lista in arbitros_cabm.items():
            for nombre_completo in lista:
                partes = nombre_completo.split(" ", 1)
                apellido = partes[0]
                nombre = partes[1] if len(partes) > 1 else ""
                
                # Le aclaramos a MySQL: Metelos DENTRO de legado_arbitral
                cursor.execute("""
                    INSERT INTO legado_arbitral.ARBITROS (nombre, apellido, categoria_actual, estado, rol) 
                    VALUES (%s, %s, %s, 'ACTIVO', 'ARBITRO')
                """, (nombre, apellido, categoria))
                
        conn.commit()
        print("¡Migración exitosa! Andá a fijarte a Workbench.")
    except Exception as e:
        print(f"Error detectado: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    migrar()