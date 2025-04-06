import streamlit as st
from utils.api_utils import (
    get_league_seasons,
    get_teams_by_league,
    get_team_fixtures
)
import pandas as pd
import matplotlib.pyplot as plt

def app():
    st.title("📊 Resultados recientes de un equipo")

    api_key = st.secrets["api"]["api_key"]

    ligas = {
        "🇬🇧 Premier League": 39,
        "🇪🇸 La Liga": 140,
        "🇮🇹 Serie A": 135,
        "🇩🇪 Bundesliga": 78,
        "🇫🇷 Ligue 1": 61
    }

    liga_seleccionada = st.selectbox("Selecciona una liga", ["Selecciona..."] + list(ligas.keys()))
    if liga_seleccionada == "Selecciona...":
        st.stop()

    league_id = ligas[liga_seleccionada]

    # Obtener temporadas ordenadas
    temporadas_disp = get_league_seasons(api_key, league_id, limit=None)
    temporadas_ordenadas = sorted(temporadas_disp, reverse=True)

    # Buscar temporada válida con equipos disponibles
    temporada_actual = None
    equipos = {}

    for temporada in temporadas_ordenadas:
        equipos_temp = get_teams_by_league(api_key, league_id, temporada)
        if equipos_temp:
            equipos = equipos_temp
            temporada_actual = temporada
            break

    if not temporada_actual or not equipos:
        st.warning("No se encontraron equipos disponibles para esta liga.")
        st.stop()

    equipo = st.selectbox("Selecciona un equipo", ["Selecciona equipo"] + sorted(equipos.keys()), key=f"equipo_{liga_seleccionada}")
    if equipo == "Selecciona equipo":
        st.stop()

    team_id = equipos[equipo]
    st.markdown("---")
    st.subheader(f"📅 Resultados del {equipo} por año")

    # Obtener todas las temporadas disponibles con fixtures
    temporadas_resultados = {}
    for temporada in temporadas_ordenadas:
        partidos = get_team_fixtures(api_key, league_id, temporada, team_id)
        partidos_filtrados = [
            p for p in partidos
            if p['teams']['home']['id'] == team_id or p['teams']['away']['id'] == team_id
        ]
        if partidos_filtrados:
            # Ordenar los partidos por fecha dentro de cada temporada, de la más reciente a la más antigua
            partidos_filtrados = sorted(partidos_filtrados, key=lambda p: p['fixture']['date'], reverse=True)
            temporadas_resultados[temporada] = partidos_filtrados

    # Resumen global por año
    resumen_anual = []
    for temporada, lista in temporadas_resultados.items():
        victorias = empates = derrotas = gf = gc = 0
        for p in lista:
            g_home = p['goals']['home']
            g_away = p['goals']['away']
            if g_home is None or g_away is None:
                continue
            home = p['teams']['home']['name']
            es_local = home == equipo
            goles_equipo = g_home if es_local else g_away
            goles_rival = g_away if es_local else g_home
            if goles_equipo > goles_rival:
                victorias += 1
            elif goles_equipo == goles_rival:
                empates += 1
            else:
                derrotas += 1
            gf += goles_equipo
            gc += goles_rival
        resumen_anual.append({"Año": temporada, "V": victorias, "E": empates, "D": derrotas, "GF": gf, "GC": gc})

    df_resumen = pd.DataFrame(resumen_anual).sort_values("Año", ascending=False)

    # Visualizaciones generales
    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots()
        ax.plot(df_resumen["Año"], df_resumen["V"], marker='o', label='Victorias', color='green')
        ax.plot(df_resumen["Año"], df_resumen["E"], marker='o', label='Empates', color='orange')
        ax.plot(df_resumen["Año"], df_resumen["D"], marker='o', label='Derrotas', color='red')
        ax.set_title("Evolución de resultados por año")
        ax.set_xlabel("Año")
        ax.set_ylabel("Partidos")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

    with c2:
        fig2, ax2 = plt.subplots()
        width = 0.35
        x = range(len(df_resumen))
        ax2.bar([i - width/2 for i in x], df_resumen["GF"], width=width, color='green', label='Goles a favor')
        ax2.bar([i + width/2 for i in x], df_resumen["GC"], width=width, color='red', label='Goles en contra')
        for i in x:
            ax2.text(i - width/2, df_resumen["GF"].iloc[i] + 0.5, str(df_resumen["GF"].iloc[i]), ha='center', color='black')
            ax2.text(i + width/2, df_resumen["GC"].iloc[i] + 0.5, str(df_resumen["GC"].iloc[i]), ha='center', color='black')
        ax2.set_xticks(list(x))
        ax2.set_xticklabels(df_resumen["Año"].astype(str))
        ax2.set_title("Goles a favor vs en contra")
        ax2.legend()
        st.pyplot(fig2)

    st.markdown("---")

    # Mostrar los resultados por temporada ordenados por fecha (de la más reciente a la más antigua)
    st.markdown("### Resultados por temporada")

    # Preparar los resultados de todos los partidos
    resumen_partidos = []
    for temporada, lista in temporadas_resultados.items():
        for p in lista:
            fecha = p['fixture']['date'][:10]
            home = p['teams']['home']['name']
            away = p['teams']['away']['name']
            g_home = p['goals']['home']
            g_away = p['goals']['away']
            competicion = p['league']['name']
            if g_home > g_away:
                resultado = f"<span style='color:green;'>V</span>"  # Victoria
            elif g_home == g_away:
                resultado = f"<span style='color:orange;'>E</span>"  # Empate
            else:
                resultado = f"<span style='color:red;'>D</span>"  # Derrota
            resumen_partidos.append({"Fecha": fecha, "Competición": competicion, "Resultado": resultado, "Partido": f"{home} {g_home} - {g_away} {away}"})

    # Crear un DataFrame de los partidos
    df_resumen_partidos = pd.DataFrame(resumen_partidos)

    # Mostrar la tabla de resultados con colores (Resultado con color en la misma celda)
    st.markdown("### Resumen de partidos")
    st.markdown(df_resumen_partidos.to_html(escape=False), unsafe_allow_html=True)  # Usamos to_html con escape=False para permitir el HTML en el resultado