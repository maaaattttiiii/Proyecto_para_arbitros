import mysql.connector

# Tu lista oficial de árbitros
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
        # Acá usamos los datos exactos que me pasaste recién
        conn = mysql.connector.connect(
            host="mysql-1b1dd353-mnvvargas3-0969.g.aivencloud.com",
            port=18929,
            user="avnadmin",
            password="AVNS_RZDgcXOy7e_VdETAERG",
            database="legado_arbitral"  # <--- Ahora sí, apuntamos a la correcta
        )
        cursor = conn.cursor()
        print("Conectado a la base de datos correcta. Inyectando árbitros...")
        
        for categoria, lista in arbitros_cabm.items():
            for nombre_completo in lista:
                partes = nombre_completo.split(" ", 1)
                apellido = partes[0]
                nombre = partes[1] if len(partes) > 1 else ""
                
                cursor.execute("""
                    INSERT INTO ARBITROS (nombre, apellido, categoria_actual, estado, rol) 
                    VALUES (%s, %s, %s, 'ACTIVO', 'ARBITRO')
                """, (nombre, apellido, categoria))
                
        conn.commit()
        print("¡Migración exitosa! Los 70 árbitros ya están listos para salir a la cancha.")
    except Exception as e:
        print(f"Error detectado: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    migrar()