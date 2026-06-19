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
        st.error(f"Error de conexión con la nube: {e}")
        return None

def obtener_arbitros():
    conn = conectar_db()
    if not conn: return {"-- Seleccionar --": None}
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_arbitro, CONCAT(nombre, ' ', apellido) as nombre_completo FROM ARBITROS WHERE estado = 'ACTIVO'")
    arbitros = cursor.fetchall()
    conn.close()
    
    dicc = {"-- Seleccionar --": None}
    for arb in arbitros: dicc[arb['nombre_completo']] = arb['id_arbitro']
    return dicc

def obtener_partidos_pendientes():
    conn = conectar_db()
    if not conn: return {"-- Seleccionar --": None}
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_partido, CONCAT(equipo_local, ' vs ', equipo_visitante, ' (', fecha, ')') as desc_partido FROM PARTIDOS")
    partidos = cursor.fetchall()
    conn.close()
    
    dicc = {"-- Seleccionar --": None}
    for part in partidos: dicc[part['desc_partido']] = part['id_partido']
    # Si no hay partidos, avisamos
    if len(dicc) == 1: dicc = {"No hay partidos creados en el sistema": None}
    return dicc

def guardar_evaluacion_db(id_arbitro, id_partido, datos, puntaje_final):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Guardamos en el HUB
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