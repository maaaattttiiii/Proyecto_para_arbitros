# app.py
import streamlit as st
import datetime
import pandas as pd

from config import LISTA_ARBITROS, LISTA_CT
from logic import validar_reglas_negocio, calcular_puntaje_final
from database import inicializar_sistema, conectar_db, guardar_evaluacion_db

def campo_evaluacion(label, key):
    col_slider, col_check = st.columns([5, 1])
    with col_check:
        st.write("##") 
        no_paso = st.checkbox("No paso", value=False, key=f"np_{key}")
    with col_slider:
        valor = st.slider(label, 1, 10, 5, key=f"sld_{key}", disabled=no_paso)
    return None if no_paso else valor

def renderizar_dashboard():
    st.header("Analisis de Rendimiento")
    arbitro_dash = st.selectbox("Seleccionar arbitro para analizar", LISTA_ARBITROS, key="dash_arb")
    if arbitro_dash != "-- Seleccionar --":
        conn = conectar_db()
        df = pd.read_sql(f"SELECT fecha, puntaje_final FROM Evaluaciones WHERE arbitro = '{arbitro_dash}' ORDER BY fecha", conn)
        if not df.empty:
            st.subheader(f"Evolucion historica de {arbitro_dash}")
            st.line_chart(data=df.set_index('fecha'))
            st.metric(label="Promedio General", value=f"{df['puntaje_final'].mean():.2f}")
            if len(df) >= 3 and df.tail(3)['puntaje_final'].mean() < 6.0:
                st.warning("Alerta: El promedio de los ultimos 3 partidos esta por debajo del estandar.")
        else:
            st.info("No hay datos cargados para este arbitro.")
        conn.close()

def main():
    st.set_page_config(page_title="Legado Arbitral", layout="wide")
    inicializar_sistema()
    
    st.title("Panel de Control: Legado Arbitral")
    t_dash, t_gen, t_ctx, t_mec, t_fal, t_vio, t_psi, t_fis, t_save = st.tabs([
        "Dashboard", "General", "Contexto", "Mecanica", "Faltas", "Violaciones", "Psicologia", "Fisico", "Guardar"
    ])

    with t_dash: renderizar_dashboard()

    with t_gen:
        st.header("Datos Basicos")
        fecha = st.date_input("Fecha", max_value=datetime.date.today(), min_value=datetime.date(2024, 1, 1))
        categoria = st.selectbox("Categoria", ["Mosquitos", "Premini", "U13", "U15", "U17", "U19", "Superliga"])
        
        c_eq1, c_eq2 = st.columns(2)
        with c_eq1: equipo_local = st.text_input("Equipo Local")
        with c_eq2: equipo_visitante = st.text_input("Equipo Visitante")
        
        cancha = st.text_input("Cancha / Estadio")
        
        c1, c2 = st.columns(2)
        with c1: arbitro = st.selectbox("Arbitro Principal", LISTA_ARBITROS)
        with c2: companero = st.selectbox("Segundo Juez", LISTA_ARBITROS)
        c3, c4 = st.columns(2)
        with c3:
            hubo_3er = st.checkbox("Hubo Tercer Juez")
            tercer_juez = st.selectbox("Tercer Juez", LISTA_ARBITROS, disabled=not hubo_3er)
        with c4:
            hubo_ct = st.checkbox("Hubo CT")
            ct = st.selectbox("Comisionado Tecnico", LISTA_CT, disabled=not hubo_ct)

    with t_ctx:
        d_descanso = st.number_input("Dias descanso", 0, 30, 2)
        d_km = st.number_input("Distancia (KM)", 0, 1000, 10)
        importancia = st.slider("Importancia", 1, 10, 5)
        conflictividad = st.slider("Conflictividad", 1, 10, 3)
        temp = st.number_input("Temperatura (C)", 0, 50, 24)
        publico = st.number_input("Publico", 0, 10000, 100)
        dif_rank = st.slider("Diferencia ranking", 1, 10, 4)

    with t_mec:
        st.subheader("Posicionamiento")
        l_pen = campo_evaluacion("Lider: penetracion", "l_pen")
        l_reb = campo_evaluacion("Lider: rebote", "l_reb")
        s_3pt = campo_evaluacion("Seguidor: tiro 3pt", "s_3pt")
        c_sin = campo_evaluacion("Centro: sin balon", "c_sin")
        t_rot = campo_evaluacion("Tiempo rotacion", "t_rot")
        v_blo = campo_evaluacion("Vision bloqueada", "v_blo")
        saques = campo_evaluacion("Saques", "saques")
        bocina = campo_evaluacion("Tiros bocina", "bocina")
        c_vis = campo_evaluacion("Comunicacion visual", "c_vis")
        
        st.markdown("---")
        st.subheader("Calidad del Silbato")
        s_marg = campo_evaluacion("Silbato marginal pitado", "s_marg")
        s_cruz = campo_evaluacion("Silbato cruzado", "s_cruz")
        s_rap = campo_evaluacion("Silbato rapido", "s_rap")
        s_eco = campo_evaluacion("Silbato eco", "s_eco")

        mecanica = [l_pen, l_reb, s_3pt, c_sin, t_rot, v_blo, saques, bocina, c_vis, s_marg, s_cruz, s_rap, s_eco]

    with t_fal:
        faltas = [
            campo_evaluacion("Bloqueo vs Carga", "b_c"), campo_evaluacion("Manos perimetro", "m_p"),
            campo_evaluacion("Pantallas ilegales", "p_i"), campo_evaluacion("Invasion cilindro", "i_c"),
            campo_evaluacion("Aterrizaje tirador", "a_t"), campo_evaluacion("Foul de saque", "f_saq"),
            campo_evaluacion("Anti C1/C2", "a_12"), campo_evaluacion("Anti C3/C4", "a_34"),
            campo_evaluacion("Consistencia Q1/Q4", "c_14"), campo_evaluacion("Compensacion", "comp")
        ]

    with t_vio:
        violaciones = [
            campo_evaluacion("Paso Cero", "p_0"), campo_evaluacion("Caminada salidas", "c_s"),
            campo_evaluacion("Dobles/Acarreos", "d_a"), campo_evaluacion("3 seg zona", "3_s"),
            campo_evaluacion("Interferencia al cesto", "goal"), campo_evaluacion("Jugar el balon con el pie", "u_p"),
            campo_evaluacion("8 segundos", "8_s"), campo_evaluacion("24 segundos", "24_s")
        ]

    with t_psi:
        psicologia = [
            campo_evaluacion("Com. DT Local", "c_l"), campo_evaluacion("Com. DT Visitante", "c_v"),
            campo_evaluacion("Desescalada conflictos", "d_c"), campo_evaluacion("Manejo publico", "m_p2"),
            campo_evaluacion("Claridad mesa", "c_m"), campo_evaluacion("Lenguaje presion", "l_p"),
            campo_evaluacion("Influencia protestas", "i_p"), campo_evaluacion("Momento de pitar tecnica", "t_t")
        ]

    with t_fis:
        hubo_fisico = st.checkbox("Cargar datos de rendimiento fisico", value=True)
        
        if hubo_fisico:
            distancia = st.number_input("Distancia recorrida (KM)", 0.0, 20.0, 4.5, step=0.1)
            sprints = st.number_input("Cantidad sprints", 0, 200, 30)
            fc_prom = st.number_input("FC Promedio", 0, 220, 140)
            fc_pico = st.number_input("FC Pico", 0, 220, 175)
            velocidad = st.number_input("Velocidad Max (KM/H)", 0.0, 40.0, 18.5, step=0.1)
            fatiga = st.slider("Indice fatiga Q4", 1, 10, 3)
            lucidez = st.slider("Lucidez post-esfuerzo", 1, 10, 5)
            lesion = st.checkbox("Sufrio lesion")
        else:
            distancia = sprints = fc_prom = fc_pico = velocidad = fatiga = lucidez = lesion = None

    with t_save:
        st.header("Guardar Reporte")
        if st.button("Guardar Evaluacion", type="primary"):
            datos = {
                'fecha': fecha, 'categoria': categoria, 'arbitro': arbitro, 'companero': companero,
                'equipo_local': equipo_local, 'equipo_visitante': equipo_visitante, 'cancha': cancha,
                'hubo_3er': hubo_3er, 'tercer_juez': tercer_juez, 'hubo_ct': hubo_ct, 'ct': ct,
                'final_3er': tercer_juez if (hubo_3er and tercer_juez != "-- Seleccionar --") else None,
                'final_ct': ct if (hubo_ct and ct != "-- Seleccionar --") else None,
                'd_descanso': d_descanso, 'd_km': d_km, 'importancia': importancia, 
                'conflictividad': conflictividad, 'temp': temp, 'publico': publico, 'dif_rank': dif_rank,
                'mecanica': mecanica, 'faltas': faltas, 'violaciones': violaciones, 'psicologia': psicologia,
                'hubo_fisico': hubo_fisico, 'distancia': distancia, 'sprints': sprints, 'fc_prom': fc_prom, 
                'fc_pico': fc_pico, 'velocidad': velocidad, 'fatiga': fatiga, 'lucidez': lucidez, 'lesion': lesion
            }

            errores = validar_reglas_negocio(datos)
            if errores:
                for err in errores: st.error(f"Error: {err}")
            else:
                puntaje = calcular_puntaje_final([mecanica, faltas, violaciones, psicologia])
                if guardar_evaluacion_db(datos, puntaje):
                    st.success(f"Registro exitoso. Puntaje calculado: {puntaje:.2f}/10")

if __name__ == "__main__":
    main()