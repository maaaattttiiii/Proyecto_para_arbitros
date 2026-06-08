# database.py
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
        st.error(f"Error de conexion con la nube: {e}")
        return None

def inicializar_sistema():
    conn = conectar_db()
    if not conn: return
    try:
        cursor = conn.cursor()
        tablas_sql = [
            """CREATE TABLE IF NOT EXISTS Evaluaciones (
                id_evaluacion INT AUTO_INCREMENT PRIMARY KEY, fecha DATE, arbitro VARCHAR(100), 
                companero VARCHAR(100), tercer_juez VARCHAR(100) NULL, ct VARCHAR(100) NULL,
                categoria VARCHAR(50), equipo_local VARCHAR(100), equipo_visitante VARCHAR(100),
                puntaje_final DECIMAL(4,2))""",
            """CREATE TABLE IF NOT EXISTS Contexto_Avanzado (
                id_contexto INT AUTO_INCREMENT PRIMARY KEY, id_evaluacion INT, dias_descanso INT, 
                distancia_km INT, importancia INT, conflictividad INT, temperatura INT, 
                publico INT, dif_ranking INT,
                FOREIGN KEY (id_evaluacion) REFERENCES Evaluaciones(id_evaluacion) ON DELETE CASCADE)""",
            """CREATE TABLE IF NOT EXISTS Mecanica_Micro (
                id_mecanica INT AUTO_INCREMENT PRIMARY KEY, id_evaluacion INT, lider_penetracion INT, 
                lider_rebote INT, seguidor_3pt INT, centro_sin_balon INT, tiempo_rotacion INT, 
                vision_bloqueada INT, saques INT, bocina INT, com_visual INT,
                silbato_marginal INT, silbato_cruzado INT, silbato_rapido INT, silbato_eco INT,
                FOREIGN KEY (id_evaluacion) REFERENCES Evaluaciones(id_evaluacion) ON DELETE CASCADE)""",
            """CREATE TABLE IF NOT EXISTS Analisis_Faltas (
                id_faltas INT AUTO_INCREMENT PRIMARY KEY, id_evaluacion INT, bloqueo_carga INT, 
                manos_perimetro INT, pantallas_ilegales INT, cilindro INT, id_aterrizaje INT, 
                foul_saque INT, antideportivas_c1c2 INT, antideportivas_c3c4 INT, consistencia_q1q4 INT, 
                compensacion INT,
                FOREIGN KEY (id_evaluacion) REFERENCES Evaluaciones(id_evaluacion) ON DELETE CASCADE)""",
            """CREATE TABLE IF NOT EXISTS Analisis_Violaciones (
                id_violaciones INT AUTO_INCREMENT PRIMARY KEY, id_evaluacion INT, paso_cero INT, 
                salidas INT, dobles INT, tres_segundos INT, goaltending INT, pie INT, 
                ocho_segundos INT, veinticuatro_segundos INT,
                FOREIGN KEY (id_evaluacion) REFERENCES Evaluaciones(id_evaluacion) ON DELETE CASCADE)""",
            """CREATE TABLE IF NOT EXISTS Psicologia_Manejo (
                id_psicologia INT AUTO_INCREMENT PRIMARY KEY, id_evaluacion INT, com_local INT, 
                com_visitante INT, desescalada INT, manejo_publico INT, mesa INT, 
                lenguaje_presion INT, influencia_protestas INT, timing_tecnicas INT,
                FOREIGN KEY (id_evaluacion) REFERENCES Evaluaciones(id_evaluacion) ON DELETE CASCADE)""",
            """CREATE TABLE IF NOT EXISTS Biometria_Fisico (
                id_fisico INT AUTO_INCREMENT PRIMARY KEY, id_evaluacion INT, distancia DECIMAL(4,2), 
                sprints INT, fc_promedio INT, fc_pico INT, velocidad DECIMAL(4,2), fatiga_q4 INT, 
                lucidez_post INT, lesion BOOLEAN,
                FOREIGN KEY (id_evaluacion) REFERENCES Evaluaciones(id_evaluacion) ON DELETE CASCADE)"""
        ]
        for query in tablas_sql: cursor.execute(query)
        conn.commit()
    except Error as e:
        st.error(f"Error creando tablas en la nube: {e}")
    finally:
        cursor.close()
        conn.close()

def guardar_evaluacion_db(datos, puntaje_final):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Evaluaciones (fecha, arbitro, companero, tercer_juez, ct, categoria, equipo_local, equipo_visitante, puntaje_final) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (datos['fecha'], datos['arbitro'], datos['companero'], datos['final_3er'], datos['final_ct'], datos['categoria'], datos['equipo_local'], datos['equipo_visitante'], puntaje_final))
        id_eval = cursor.lastrowid
        
        cursor.execute("INSERT INTO Contexto_Avanzado VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (id_eval, datos['d_descanso'], datos['d_km'], datos['importancia'], datos['conflictividad'], datos['temp'], datos['publico'], datos['dif_rank']))
        
        # Correccion: 14 variables = 14 %s
        cursor.execute("INSERT INTO Mecanica_Micro VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_eval, *datos['mecanica']))
        
        # Correccion: 11 variables = 11 %s
        cursor.execute("INSERT INTO Analisis_Faltas VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_eval, *datos['faltas']))
        
        # Correccion: 9 variables = 9 %s
        cursor.execute("INSERT INTO Analisis_Violaciones VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_eval, *datos['violaciones']))
        
        # Correccion: 9 variables = 9 %s
        cursor.execute("INSERT INTO Psicologia_Manejo VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_eval, *datos['psicologia']))
        
        # Correccion: 9 variables = 9 %s
        cursor.execute("INSERT INTO Biometria_Fisico VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (id_eval, datos['distancia'], datos['sprints'], datos['fc_prom'], datos['fc_pico'], datos['velocidad'], datos['fatiga'], datos['lucidez'], datos['lesion']))
        
        conn.commit()
        return id_eval
    except Error as e:
        st.error(f"Error al guardar datos en la nube: {e}")
        return False
    finally:
        cursor.close()
        conn.close()