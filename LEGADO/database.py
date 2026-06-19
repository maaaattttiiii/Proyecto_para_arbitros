import mysql.connector
from mysql.connector import Error
import streamlit as st

def conectar_db():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
    except Error as e:
        st.error(f"Error de conexión con la nube: {e}")
        return None

def inicializar_sistema():
    conn = conectar_db()
    if not conn: return
    try:
        cursor = conn.cursor()
        tablas_sql = [
            # 1. EL NUEVO HUB CENTRAL (Reemplaza a Evaluaciones)
            """CREATE TABLE IF NOT EXISTS Rendimientos_Hub (
                id_rendimiento BIGINT AUTO_INCREMENT PRIMARY KEY, 
                id_arbitro BIGINT NOT NULL, 
                id_partido BIGINT NOT NULL, 
                puntaje_final DECIMAL(4,2),
                FOREIGN KEY (id_arbitro) REFERENCES ARBITROS(id_arbitro) ON DELETE CASCADE,
                FOREIGN KEY (id_partido) REFERENCES PARTIDOS(id_partido) ON DELETE CASCADE
            )""",
            
            # 2. SUB-TABLAS (Conectadas al id_rendimiento en lugar del viejo id_evaluacion)
            """CREATE TABLE IF NOT EXISTS Contexto_Avanzado (
                id_contexto BIGINT AUTO_INCREMENT PRIMARY KEY, id_rendimiento BIGINT, dias_descanso INT, 
                distancia_km INT, importancia INT, conflictividad INT, temperatura INT, 
                publico INT, dif_ranking INT,
                FOREIGN KEY (id_rendimiento) REFERENCES Rendimientos_Hub(id_rendimiento) ON DELETE CASCADE)""",
            
            """CREATE TABLE IF NOT EXISTS Mecanica_Micro (
                id_mecanica BIGINT AUTO_INCREMENT PRIMARY KEY, id_rendimiento BIGINT, lider_penetracion INT, 
                lider_rebote INT, seguidor_3pt INT, centro_sin_balon INT, tiempo_rotacion INT, 
                vision_bloqueada INT, saques INT, bocina INT, com_visual INT,
                silbato_marginal INT, silbato_cruzado INT, silbato_rapido INT, silbato_eco INT,
                FOREIGN KEY (id_rendimiento) REFERENCES Rendimientos_Hub(id_rendimiento) ON DELETE CASCADE)""",
            
            """CREATE TABLE IF NOT EXISTS Analisis_Faltas (
                id_faltas BIGINT AUTO_INCREMENT PRIMARY KEY, id_rendimiento BIGINT, bloqueo_carga INT, 
                manos_perimetro INT, pantallas_ilegales INT, cilindro INT, id_aterrizaje INT, 
                foul_saque INT, antideportivas_c1c2 INT, antideportivas_c3c4 INT, consistencia_q1q4 INT, 
                compensacion INT,
                FOREIGN KEY (id_rendimiento) REFERENCES Rendimientos_Hub(id_rendimiento) ON DELETE CASCADE)""",
            
            """CREATE TABLE IF NOT EXISTS Analisis_Violaciones (
                id_violaciones BIGINT AUTO_INCREMENT PRIMARY KEY, id_rendimiento BIGINT, paso_cero INT, 
                salidas INT, dobles INT, tres_segundos INT, goaltending INT, pie INT, 
                ocho_segundos INT, veinticuatro_segundos INT,
                FOREIGN KEY (id_rendimiento) REFERENCES Rendimientos_Hub(id_rendimiento) ON DELETE CASCADE)""",
            
            """CREATE TABLE IF NOT EXISTS Psicologia_Manejo (
                id_psicologia BIGINT AUTO_INCREMENT PRIMARY KEY, id_rendimiento BIGINT, com_local INT, 
                com_visitante INT, desescalada INT, manejo_publico INT, mesa INT, 
                lenguaje_presion INT, influencia_protestas INT, timing_tecnicas INT,
                FOREIGN KEY (id_rendimiento) REFERENCES Rendimientos_Hub(id_rendimiento) ON DELETE CASCADE)""",
            
            """CREATE TABLE IF NOT EXISTS Biometria_Fisico (
                id_fisico BIGINT AUTO_INCREMENT PRIMARY KEY, id_rendimiento BIGINT, distancia DECIMAL(4,2), 
                sprints INT, fc_promedio INT, fc_pico INT, velocidad DECIMAL(4,2), fatiga_q4 INT, 
                lucidez_post INT, lesion BOOLEAN,
                FOREIGN KEY (id_rendimiento) REFERENCES Rendimientos_Hub(id_rendimiento) ON DELETE CASCADE)"""
        ]
        for query in tablas_sql: 
            cursor.execute(query)
        conn.commit()
    except Error as e:
        st.error(f"Error creando tablas en la nube: {e}")
    finally:
        cursor.close()
        conn.close()

# ATENCIÓN: Ahora la función pide id_arbitro e id_partido
def guardar_evaluacion_db(id_arbitro, id_partido, datos, puntaje_final):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # 1. Guardamos en el HUB (Ya no pasamos textos, pasamos los IDs)
        cursor.execute("INSERT INTO Rendimientos_Hub (id_arbitro, id_partido, puntaje_final) VALUES (%s, %s, %s)",
                       (id_arbitro, id_partido, puntaje_final))
        id_rend = cursor.lastrowid
        
        # 2. Guardamos en las sub-tablas (usando id_rend)
        cursor.execute("INSERT INTO Contexto_Avanzado VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (id_rend, datos['d_descanso'], datos['d_km'], datos['importancia'], datos['conflictividad'], datos['temp'], datos['publico'], datos['dif_rank']))
        
        cursor.execute("INSERT INTO Mecanica_Micro VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_rend, *datos['mecanica']))
        
        cursor.execute("INSERT INTO Analisis_Faltas VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_rend, *datos['faltas']))
        
        cursor.execute("INSERT INTO Analisis_Violaciones VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_rend, *datos['violaciones']))
        
        cursor.execute("INSERT INTO Psicologia_Manejo VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_rend, *datos['psicologia']))
        
        cursor.execute("INSERT INTO Biometria_Fisico VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (id_rend, datos['distancia'], datos['sprints'], datos['fc_prom'], datos['fc_pico'], datos['velocidad'], datos['fatiga'], datos['lucidez'], datos['lesion']))
        
        conn.commit()
        return id_rend
    except Error as e:
        st.error(f"Error al guardar datos en la nube: {e}")
        return False
    finally:
        cursor.close()
        conn.close()