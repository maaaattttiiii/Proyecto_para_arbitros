# app.py
import streamlit as st
import pandas as pd

from logic import validar_reglas_negocio, calcular_puntaje_final
from database import conectar_db, obtener_arbitros, obtener_partidos_pendientes, guardar_evaluacion_db

def campo_evaluacion(label, key):
    col_slider, col_check = st.columns([5, 1])
    with col_check:
        st.write("##") 
        no_paso = st.checkbox("No pasó", value=False, key=f"np_{key}")
    with col_slider:
        valor = st.slider(label, 1, 10, 5, key=f"sld_{key}", disabled=no_paso)
    return None if no_paso else valor

def renderizar_dashboard():
    st.header("Análisis de Rendimiento")
    dicc_arbitros = obtener_arbitros()
    arbitro_dash = st.selectbox("Seleccionar árbitro para analizar", options=list(dicc_arbitros.keys()), key="dash_arb")
    id_arb = dicc_arbitros[arbitro_dash]
    
    if id_arb is not None:
        conn = conectar_db()
        # Traemos la nota del HUB y la fecha uniéndolo con la tabla Partidos
        query = f"""
            SELECT P.fecha, R.puntaje_final 
            FROM Rendimientos_Hub R 
            JOIN PARTIDOS P ON R.id_partido = P.id_partido 
            WHERE R.id_arbitro = {id_arb} 
            ORDER BY P.fecha
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            st.subheader(f"Evolución histórica de {arbitro_dash}")
            st.line_chart(data=df.set_index('fecha'))
            st.metric(label="Promedio General", value=f"{df['puntaje_final'].mean():.2f}")
            if len(df) >= 3 and df.tail(3)['puntaje_final'].mean() < 6.0:
                st.warning("Alerta: El promedio de los últimos 3 partidos está por debajo del estándar.")
        else:
            st.info("No hay evaluaciones cargadas para este árbitro.")

def main():
    st.set_page_config(page_title="Legado Arbitral", layout="wide")
    
    # --- SISTEMA DE LOGIN ---
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔒 Acceso Restringido")
        with st.form("login_form"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar")
            
            if submit:
                if usuario == st.secrets["login"]["usuario"] and clave == st.secrets["login"]["clave"]:
                    st.session_state.autenticado = True
                    st.rerun() 
                else:
                    st.error("Usuario o contraseña incorrectos.")
        return
    # --- FIN SISTEMA DE LOGIN ---
    
    col_titulo, col_salir = st.columns([8, 1])
    with col_titulo:
        st.title("Panel de Control: Legado Arbitral")
    with col_salir:
        st.write("##")
        if st.button("Salir 🚪"):
            st.session_state.autenticado = False
            st.rerun()

    t_dash, t_gen, t_ctx, t_mec, t_fal, t_vio, t_psi, t_fis, t_save = st.tabs([
        "Dashboard", "General", "Contexto", "Mecánica", "Faltas", "Violaciones", "Psicología", "Físico", "Guardar"
    ])

    with t_dash: 
        renderizar_dashboard()

    with t_gen:
        st.header("Selección de Evento")
        st.info("Para evaluar, seleccioná un partido programado y el árbitro a observar.")
        
        dicc_partidos = obtener_partidos_pendientes()
        dicc_arbitros = obtener_arbitros()
        
        partido_seleccionado = st.selectbox("Seleccionar Partido", options=list(dicc_partidos.keys()))
        arbitro_seleccionado = st.selectbox("Árbitro a Evaluar", options=list(dicc_arbitros.keys()))
        
        # Guardamos los IDs reales en variables de sesión para usarlos al guardar
        id_partido_actual = dicc_partidos[partido_seleccionado]
        id_arbitro_actual = dicc_arbitros[arbitro_seleccionado]

    with t_ctx:
        d_descanso = st.number_input("Días descanso", 0, 30, 2)
        d_km = st.number_input("Distancia (KM)", 0, 1000, 10)
        importancia = st.slider("Importancia", 1, 10, 5)
        conflictividad = st.slider("Conflictividad", 1, 10, 3)
        temp = st.number_input("Temperatura (C)", 0, 50, 24)
        publico = st.number_input("Público", 0, 10000, 100)
        dif_rank = st.slider("Diferencia ranking", 1, 10, 4)

    with t_mec:
        st.subheader("Posicionamiento")
        l_pen = campo_evaluacion("Líder: penetración", "l_pen")
        l_reb = campo_evaluacion("Líder: rebote", "l_reb")
        s_3pt = campo_evaluacion("Seguidor: tiro 3pt", "s_3pt")
        c_sin = campo_evaluacion("Centro: sin balón", "c_sin")
        t_rot = campo_evaluacion("Tiempo rotación", "t_rot")
        v_blo = campo_evaluacion("Visión bloqueada", "v_blo")
        saques = campo_evaluacion("Saques", "saques")
        bocina = campo_evaluacion("Tiros bocina", "bocina")
        c_vis = campo_evaluacion("Comunicación visual", "c_vis")
        
        st.markdown("---")
        st.subheader("Calidad del Silbato")
        s_marg = campo_evaluacion("Silbato marginal pitado", "s_marg")
        s_cruz = campo_evaluacion("Silbato cruzado", "s_cruz")
        s_rap = campo_evaluacion("Silbato rápido", "s_rap")
        s_eco = campo_evaluacion("Silbato eco", "s_eco")

        mecanica = [l_pen, l_reb, s_3pt, c_sin, t_rot, v_blo, saques, bocina, c_vis, s_marg, s_cruz, s_rap, s_eco]

    with t_fal:
        faltas = [
            campo_evaluacion("Bloqueo vs Carga", "b_c"), campo_evaluacion("Manos perímetro", "m_p"),
            campo_evaluacion("Pantallas ilegales", "p_i"), campo_evaluacion("Invasión cilindro", "i_c"),
            campo_evaluacion("Aterrizaje tirador", "a_t"), campo_evaluacion("Foul de saque", "f_saq"),
            campo_evaluacion("Anti C1/C2", "a_12"), campo_evaluacion("Anti C3/C4", "a_34"),
            campo_evaluacion("Consistencia Q1/Q4", "c_14"), campo_evaluacion("Compensación", "comp")
        ]

    with t_vio:
        violaciones = [
            campo_evaluacion("Paso Cero", "p_0"), campo_evaluacion("Caminada salidas", "c_s"),
            campo_evaluacion("Dobles/Acarreos", "d_a"), campo_evaluacion("3 seg zona", "3_s"),
            campo_evaluacion("Interferencia al cesto", "goal"), campo_evaluacion("Jugar el balón con el pie", "u_p"),
            campo_evaluacion("8 segundos", "8_s"), campo_evaluacion("24 segundos", "24_s")
        ]

    with t_psi:
        psicologia = [
            campo_evaluacion("Com. DT Local", "c_l"), campo_evaluacion("Com. DT Visitante", "c_v"),
            campo_evaluacion("Desescalada conflictos", "d_c"), campo_evaluacion("Manejo público", "m_p2"),
            campo_evaluacion("Claridad mesa", "c_m"), campo_evaluacion("Lenguaje presión", "l_p"),
            campo_evaluacion("Influencia protestas", "i_p"), campo_evaluacion("Momento de pitar técnica", "t_t")
        ]

    with t_fis:
        hubo_fisico = st.checkbox("Cargar datos de rendimiento físico", value=True)
        if hubo_fisico:
            distancia = st.number_input("Distancia recorrida (KM)", 0.0, 20.0, 4.5, step=0.1)
            sprints = st.number_input("Cantidad sprints", 0, 200, 30)
            fc_prom = st.number_input("FC Promedio", 0, 220, 140)
            fc_pico = st.number_input("FC Pico", 0, 220, 175)
            velocidad = st.number_input("Velocidad Max (KM/H)", 0.0, 40.0, 18.5, step=0.1)
            fatiga = st.slider("Índice fatiga Q4", 1, 10, 3)
            lucidez = st.slider("Lucidez post-esfuerzo", 1, 10, 5)
            lesion = st.checkbox("Sufrió lesión")
        else:
            distancia = sprints = fc_prom = fc_pico = velocidad = fatiga = lucidez = lesion = None

    with t_save:
        st.header("Guardar Reporte")
        if id_partido_actual is None or id_arbitro_actual is None:
            st.warning("⚠️ Debes seleccionar un Partido y un Árbitro en la pestaña 'General' para poder guardar.")
        else:
            if st.button("Guardar Evaluación", type="primary"):
                datos = {
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
                    if guardar_evaluacion_db(id_arbitro_actual, id_partido_actual, datos, puntaje):
                        st.success(f"Registro exitoso. Puntaje calculado: {puntaje:.2f}/10")

if __name__ == "__main__":
    main()