# app.py
import streamlit as st
import pandas as pd

from logic import validar_reglas_negocio, calcular_puntaje_final
from database import (inicializar_sistema, conectar_db, obtener_arbitros, 
                      obtener_partidos_pendientes, crear_partido_db, 
                      asignar_arbitro_partido, calcular_arancel_exacto, guardar_evaluacion_db)

# --- LISTAS OFICIALES DE CLUBES DE MENDOZA ---
EQUIPOS_MASCULINOS = [
    "-- Seleccionar --", "A.D. Anzorena", "Andes Talleres S.C.", "Atenas Sport Club",
    "Atlético Club San Martín", "Centro Deportivo Rivadavia", "Club Banco Mendoza (CPBM)",
    "Club Deportivo Godoy Cruz Antonio Tomba", "Club Israelita Macabi", "Club Mendoza de Regatas",
    "Club Obras Mendoza", "C.S.D. General San Martín (Pacífico)", "C.S.D. Huracán Las Heras",
    "C.S.D. Junín (Municipalidad de Junín)", "Instituto San Pablo", "Leonardo Murialdo",
    "Municipalidad de Capital", "Municipalidad de Luján de Cuyo", "Municipalidad de San Carlos",
    "Municipalidad de Tunuyán", "Municipalidad de Tupungato", "Petroleros YPF", "Social Las Heras",
    "Unión Deportiva San José", "Universidad Nacional de Cuyo (UNCuyo)", "Municipalidad de Maipú"
]

EQUIPOS_FEMENINOS = [
    "-- Seleccionar --", "Andes Talleres S.C.", "Atenas Sport Club", "Centro Deportivo Rivadavia",
    "Club Banco Mendoza (CPBM)", "Club Deportivo Godoy Cruz Antonio Tomba", "Club Mendoza de Regatas",
    "C.S.D. General San Martín (Pacífico)", "Juventud Mendocina", "Municipalidad de Junín",
    "Municipalidad de Luján de Cuyo", "Municipalidad de Maipú", "Obras Mendoza", "Petroleros YPF",
    "Unión Deportiva San José", "Universidad Nacional de Cuyo (UNCuyo)"
]

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
    
    inicializar_sistema()
    
    col_titulo, col_salir = st.columns([8, 1])
    with col_titulo:
        st.title("Panel de Control: Legado Arbitral")
    with col_salir:
        st.write("##")
        if st.button("Salir 🚪"):
            st.session_state.autenticado = False
            st.rerun()

    t_dash, t_gen, t_ctx, t_mec, t_fal, t_vio, t_psi, t_fis, t_save, t_tesoreria = st.tabs([
        "Dashboard", "General", "Contexto", "Mecánica", "Faltas", "Violaciones", "Psicología", "Físico", "Guardar", "💰 Tesorería"
    ])

    with t_dash: 
        renderizar_dashboard()

    with t_gen:
        st.header("Selección de Evento")
        st.info("Para evaluar, seleccioná un partido de la lista y el árbitro que querés observar.")
        
        dicc_partidos = obtener_partidos_pendientes()
        dicc_arbitros = obtener_arbitros()
        
        partido_seleccionado = st.selectbox("Seleccionar Partido", options=list(dicc_partidos.keys()))
        arbitro_seleccionado = st.selectbox("Árbitro a Evaluar", options=list(dicc_arbitros.keys()))
        
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
                    'hubo_fisico': hubo_fisico, 'distancia': distance, 'sprints': sprints, 'fc_prom': fc_prom, 
                    'fc_pico': fc_pico, 'velocidad': velocidad, 'fatiga': fatiga, 'lucidez': lucidez, 'lesion': lesion
                }

                errores = validar_reglas_negocio(datos)
                if errores:
                    for err in errores: st.error(f"Error: {err}")
                else:
                    puntaje = calcular_puntaje_final([mecanica, faltas, violaciones, psicologia])
                    if guardar_evaluacion_db(id_arbitro_actual, id_partido_actual, datos, puntaje):
                        st.success(f"Registro exitoso. Puntaje calculated: {puntaje:.2f}/10")

    # --- PESTAÑA DE TESORERÍA BLINDADA ---
    with t_tesoreria:
        st.header("💰 Panel de Registro Expreso de Tesorería")
        st.write("Carga los partidos de la semana acá. Las liquidaciones se calculan cruzando el nivel del árbitro con la tabla oficial.")
        
        # 1. Selector de categoría (Se pone primero para mapear los equipos correspondientes)
        cat_t = st.selectbox("Categoría del Encuentro", [
            "SUPER LIGA", "ASCENSO", "PROMOCION", "SUPER LIGA FEM", 
            "MASTER", "U23/PROMOCIONAL", "U19", "JUVENILES", "CADETES", 
            "INFANTILES", "U11_x_2", "U11", "U9"
        ], key="t_cat")
        
        # Filtro de equipos dinámicos para evitar mezclar ramas masculinas y femeninas
        lista_equipos_dinamica = EQUIPOS_FEMENINOS if cat_t == "SUPER LIGA FEM" else EQUIPOS_MASCULINOS
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            loc_t = st.selectbox("Equipo Local", options=lista_equipos_dinamica, key="t_loc")
            vis_t = st.selectbox("Equipo Visitante", options=lista_equipos_dinamica, key="t_vis")
        with c_m2:
            fec_t = st.date_input("Fecha Partido", key="t_fec")
            hor_t = st.text_input("Hora (HH:MM)", "21:30", key="t_hor")
        
        st.markdown("---")
        st.subheader("Trío Arbitral Directo")
        dicc_arb_t = obtener_arbitros()
        
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            juez_p = st.selectbox("Juez Principal", options=list(dicc_arb_t.keys()), key="expr_j1")
        with col_t2:
            juez_1 = st.selectbox("1° Juez", options=["-- Seleccionar --"] + list(dicc_arb_t.keys())[1:], key="expr_j2")
        with col_t3:
            juez_2 = st.selectbox("2° Juez (Tercero / Opcional)", options=["-- Seleccionar --"] + list(dicc_arb_t.keys())[1:], key="expr_j3")
            
        if st.button("Registrar y Liquidar Todo ⚡", type="primary"):
            # --- REGLAS DE VALIDACIÓN DE INTERFAZ ---
            if loc_t == "-- Seleccionar --" or vis_t == "-- Seleccionar --":
                st.error("❌ Error: Debes seleccionar obligatoriamente un Equipo Local y un Equipo Visitante.")
            elif loc_t == vis_t:
                st.error("❌ Error lógico: El Equipo Local y el Visitante no pueden ser el mismo club.")
            elif dicc_arb_t[juez_p] is None or juez_1 == "-- Seleccionar --":
                st.error("❌ Error: Todo partido requiere como mínimo la designación del Juez Principal y del 1° Juez.")
            elif juez_p == juez_1 or (juez_2 != "-- Seleccionar --" and (juez_p == juez_2 or juez_1 == juez_2)):
                st.error("❌ Error de duplicación: Un mismo árbitro no puede ocupar dos roles en el mismo partido.")
            elif cat_t == "SUPER LIGA" and juez_2 == "-- Seleccionar --":
                # VALIDACIÓN CRÍTICA: Fuerza la carga del 3° Juez si es Superliga Masculina
                st.error("❌ Validación de Torneo: Los partidos de SUPER LIGA se dirigen obligatoriamente con terna (falta designar el 2° Juez).")
            else:
                # Si pasa todos los filtros, inserta en MySQL
                id_partido_creado = crear_partido_db(loc_t, vis_t, fec_t, hor_t, cat_t)
                if id_partido_creado:
                    # Liquida e inserta Principal
                    id_juez_p = dicc_arb_t[juez_p]
                    p_p = calcular_arancel_exacto(cat_t, id_juez_p, "JUEZ_PRINCIPAL")
                    asignar_arbitro_partido(id_partido_creado, id_juez_p, "JUEZ_PRINCIPAL", p_p, 0.0)
                    st.success(f"✓ {juez_p} liquidado con ${p_p:,.2f}")
                    
                    # Liquida e inserta Segundo Juez
                    id_juez_1 = dicc_arb_t[juez_1]
                    p_1 = calcular_arancel_exacto(cat_t, id_juez_1, "JUEZ_1")
                    asignar_arbitro_partido(id_partido_creado, id_juez_1, "JUEZ_1", p_1, 0.0)
                    st.success(f"✓ {juez_1} liquidado con ${p_1:,.2f}")
                    
                    # Liquida e inserta Tercer Juez si fue seleccionado
                    if juez_2 != "-- Seleccionar --":
                        id_juez_2 = dicc_arb_t[juez_2]
                        p_2 = calcular_arancel_exacto(cat_t, id_juez_2, "JUEZ_2")
                        asignar_arbitro_partido(id_partido_creado, id_juez_2, "JUEZ_2", p_2, 0.0)
                        st.success(f"✓ {juez_2} (3° Juez) liquidado con ${p_2:,.2f}")
                    
                    st.balloons()
                    st.rerun()

if __name__ == "__main__":
    main()