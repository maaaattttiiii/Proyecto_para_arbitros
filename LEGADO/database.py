# database.py
import mysql.connector
from mysql.connector import Error
import streamlit as st

@st.cache_resource
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
    
@st.cache_data(ttl=600)
def inicializar_sistema():
    conn = conectar_db()
    if not conn: return
    try:
        cursor = conn.cursor()
        tablas_sql = [
            # HUB CENTRAL DE RENDIMIENTO
            """CREATE TABLE IF NOT EXISTS Rendimientos_Hub (
                id_rendimiento BIGINT AUTO_INCREMENT PRIMARY KEY, 
                id_arbitro BIGINT NOT NULL, 
                id_partido BIGINT NOT NULL, 
                puntaje_final DECIMAL(4,2),
                FOREIGN KEY (id_arbitro) REFERENCES ARBITROS(id_arbitro) ON DELETE CASCADE,
                FOREIGN KEY (id_partido) REFERENCES PARTIDOS(id_partido) ON DELETE CASCADE
            )""",
            
            # SUB-TABLAS DE MÉTRICAS ANALÍTICAS
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
        st.error(f"Error inicializando tablas analíticas: {e}")
    finally:
        cursor.close()
        conn.close()

@st.cache_data(ttl=600)
def obtener_arbitros():
    conn = conectar_db()
    if not conn: return {"-- Seleccionar --": None}
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_arbitro, CONCAT(nombre, ' ', apellido) as nombre_completo FROM ARBITROS WHERE estado = 'ACTIVO' ORDER BY apellido ASC")
    arbitros = cursor.fetchall()
    conn.close()
    
    dicc = {"-- Seleccionar --": None}
    for arb in arbitros: dicc[arb['nombre_completo']] = arb['id_arbitro']
    return dicc

@st.cache_data(ttl=600)
def obtener_partidos_pendientes():
    conn = conectar_db()
    if not conn: return {"-- Seleccionar --": None}
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_partido, CONCAT(equipo_local, ' vs ', equipo_visitante, ' (', fecha, ')') as desc_partido FROM PARTIDOS ORDER BY fecha DESC")
    partidos = cursor.fetchall()
    conn.close()
    
    dicc = {"-- Seleccionar --": None}
    for part in partidos: dicc[part['desc_partido']] = part['id_partido']
    return dicc

def crear_partido_db(equipo_local, equipo_visitante, fecha, hora, categoria):
    conn = conectar_db()
    if not conn: return None
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO PARTIDOS (equipo_local, equipo_visitante, fecha, hora, categoria, estado)
            VALUES (%s, %s, %s, %s, %s, 'PROGRAMADO')
        """
        cursor.execute(query, (equipo_local, equipo_visitante, fecha, hora, categoria))
        id_partido = cursor.lastrowid
        conn.commit()
        return id_partido
    except Error as e:
        st.error(f"Error al crear partido: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def asignar_arbitro_partido(id_partido, id_arbitro, rol_cancha, arancel, viatico):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO DESIGNACIONES (id_arbitro, id_partido, rol_en_cancha, arancel, viatico, estado_pago)
            VALUES (%s, %s, %s, %s, %s, 'PENDIENTE')
        """
        cursor.execute(query, (id_arbitro, id_partido, rol_cancha, arancel, viatico))
        conn.commit()
        return True
    except Error as e:
        st.error(f"Error al asignar árbitro: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def calcular_arancel_exacto(categoria_partido, id_arbitro, rol_en_cancha):
    conn = conectar_db()
    if not conn: return 0.0
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT categoria_actual FROM ARBITROS WHERE id_arbitro = %s", (id_arbitro,))
        arb_data = cursor.fetchone()
        if not arb_data: return 0.0
        
        cat_arbitro = arb_data['categoria_actual']
        
        # Regla especial: 3° Juez en Super Liga tiene arancel fijo
        if rol_en_cancha == "JUEZ_2" and categoria_partido == "SUPER LIGA":
            cat_arbitro = "3_JUEZ"

        query_precio = """
            SELECT arancel FROM ARANCELES_CONFIG 
            WHERE categoria_partido = %s AND (categoria_arbitro = %s OR categoria_arbitro = 'TODAS')
            ORDER BY categoria_arbitro DESC LIMIT 1
        """
        cursor.execute(query_precio, (categoria_partido, cat_arbitro))
        precio_data = cursor.fetchone()
        return float(precio_data['arancel']) if precio_data else 0.0
    except Error as e:
        st.error(f"Error calculando arancel: {e}")
        return 0.0
    finally:
        cursor.close()
        conn.close()

def guardar_evaluacion_db(id_arbitro, id_partido, datos, puntaje_final):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Rendimientos_Hub (id_arbitro, id_partido, puntaje_final) VALUES (%s, %s, %s)",
                       (id_arbitro, id_partido, puntaje_final))
        id_rend = cursor.lastrowid
        
        cursor.execute("""INSERT INTO Contexto_Avanzado (id_rendimiento, dias_descanso, distancia_km, importancia, conflictividad, temperatura, publico, dif_ranking) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                       (id_rend, datos['d_descanso'], datos['d_km'], datos['importancia'], datos['conflictividad'], datos['temp'], datos['publico'], datos['dif_rank']))
        
        cursor.execute("""INSERT INTO Mecanica_Micro (id_rendimiento, lider_penetracion, lider_rebote, seguidor_3pt, centro_sin_balon, tiempo_rotacion, vision_bloqueada, saques, bocina, com_visual, silbato_marginal, silbato_cruzado, silbato_rapido, silbato_eco) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (id_rend, *datos['mecanica']))
        
        cursor.execute("""INSERT INTO Analisis_Faltas (id_rendimiento, bloqueo_carga, manos_perimetro, pantallas_ilegales, cilindro, id_aterrizaje, foul_saque, antideportivas_c1c2, antideportivas_c3c4, consistencia_q1q4, compensacion) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (id_rend, *datos['faltas']))
        
        cursor.execute("""INSERT INTO Analisis_Violaciones (id_rendimiento, paso_cero, salidas, dobles, tres_segundos, goaltending, pie, ocho_segundos, veinticuatro_segundos) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (id_rend, *datos['violaciones']))
        
        cursor.execute("""INSERT INTO Psicologia_Manejo (id_rendimiento, com_local, com_visitante, desescalada, manejo_publico, mesa, lenguaje_presion, influencia_protestas, timing_tecnicas) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (id_rend, *datos['psicologia']))
        
        cursor.execute("""INSERT INTO Biometria_Fisico (id_rendimiento, distancia, sprints, fc_promedio, fc_pico, velocidad, fatiga_q4, lucidez_post, lesion) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                       (id_rend, datos['distancia'], datos['sprints'], datos['fc_prom'], datos['fc_pico'], datos['velocidad'], datos['fatiga'], datos['lucidez'], datos['lesion']))
        
        conn.commit()
        return id_rend
    except Error as e:
        st.error(f"Error al guardar datos en la nube: {e}")
        return False
    finally:
        cursor.close()
        conn.close()