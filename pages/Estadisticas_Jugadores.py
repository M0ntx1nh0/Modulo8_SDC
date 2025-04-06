import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from mplsoccer import PyPizza
from PIL import Image
import matplotlib.patheffects as path_effects
from matplotlib.transforms import Affine2D
from mpl_toolkits.axisartist import floating_axes
from mpl_toolkits.axisartist.floating_axes import GridHelperCurveLinear
from mpl_toolkits.axes_grid1 import Divider, Size
import textwrap as tw
import os
from utils.pdf_export import generar_pdf_resultados

# ------------------------
# CARGA DE DATOS
# ------------------------
@st.cache_data
def cargar_datos_jugadores():
    df = pd.read_excel("data/DatosUnif.xlsx")
    return df

@st.cache_data
def cargar_metricas_por_posicion():
    df_metricas = pd.read_excel("data/metricas_por_posicion.xlsx")
    return df_metricas

@st.cache_data
def cargar_metricas_nombres():
    df_metricas = pd.read_excel("data/metricas_nombres.xlsx")
    return df_metricas

# ------------------------
# APP
# ------------------------

def app():
    # Inicializar las variables en st.session_state si no están definidas
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False

    if 'pdf_path' not in st.session_state:
        st.session_state.pdf_path = None

    st.title("🌟 Análisis Comparativo de Jugadores por Posición")

    # Cargar datos
    df = cargar_datos_jugadores()
    metricas_df = cargar_metricas_por_posicion()
    metricas_nombres_df = cargar_metricas_nombres()

    # Filtrar competiciones y equipos
    competiciones = sorted(df['Competicion'].dropna().unique())
    competicion = st.selectbox("Selecciona una competición", competiciones)
    
    df_filtrado = df[df['Competicion'] == competicion]

    equipos = sorted(df_filtrado['Squad'].dropna().unique())
    equipo = st.selectbox("Selecciona un equipo", equipos)

    df_filtrado = df_filtrado[df_filtrado['Squad'] == equipo]

    jugadores = sorted(df_filtrado['Player'].dropna().unique())
    jugador = st.selectbox("Selecciona un jugador", jugadores)

    df_jugador = df_filtrado[df_filtrado['Player'] == jugador].copy()

    if not df_jugador.empty:
        # Obtener la posición del jugador
        posicion = df_jugador['Pos'].values[0]
        st.markdown(f"**Posición detectada:** `{posicion}`")

        partidos_min = st.slider("Número mínimo de partidos jugados para comparar", 1, 38, 5)

        # Filtrar jugadores por posición y partidos jugados
        df_comparables = df[(df['Pos'] == posicion) & (df['Partidos'] >= partidos_min)].copy()

        st.markdown(f"Jugadores encontrados para comparar: **{df_comparables.shape[0]}**")

        # Obtener las métricas para esta posición
        metricas = metricas_df[posicion].dropna().tolist()
        st.markdown("**Métricas para el radar:**")
        st.code(", ".join(metricas))

        # Mapear los nombres visuales para las métricas
        diccionario_nombres = dict(zip(metricas_nombres_df["columna_original"], metricas_nombres_df["nombre_visual"]))

        # Convertir las métricas a tipo numérico
        df_comparables[metricas] = df_comparables[metricas].apply(pd.to_numeric, errors='coerce')
        df_comparables = df_comparables.dropna(subset=metricas)

        # Gráfico radar y comparación de jugadores
        if st.button("Generar gráfico comparativo"):
            player_1 = df_comparables[df_comparables['Player'] == jugador].iloc[0]
            num_metrics = len(metricas)
            theta_mid = np.radians(np.linspace(0, 360, num_metrics+1))[:-1] + np.pi/2
            theta_mid = [x if x < 2*np.pi else x - 2*np.pi for x in theta_mid]
            theta_base = np.array(theta_mid) - np.mean(np.diff(theta_mid))/2
            r_base = np.linspace(0.25, 0.25, num_metrics+1)[:-1]
            x_base = 0.325 + r_base * np.cos(theta_mid)
            y_base = 0.3 + 0.89 * r_base * np.sin(theta_mid)

            fig = plt.figure(constrained_layout=False, figsize=(9, 10.2))
            fig.set_facecolor('#313332')
            theta = np.arange(0, 2*np.pi, 0.01)
            radar_ax = fig.add_axes([0.025, 0, 0.95, 0.95], polar=True)
            radar_ax.axis('off')

            for r in [0.17, 0.3425, 0.5150, 0.6875, 0.86]:
                radar_ax.plot(theta, theta*0 + r, color='grey', lw=1, alpha=0.3)

            ax_mins, ax_maxs = [], []

            for idx, metric in enumerate(metricas):
                fig_save, ax_save = plt.subplots(figsize=(4.5, 1.5))
                fig_save.set_facecolor('#313332')
                path_eff = [path_effects.Stroke(linewidth=2, foreground='#313332'), path_effects.Normal()]
                sns.swarmplot(x=df_comparables[metric], y=[""]*len(df_comparables), color='grey', edgecolor='w',
                              s=7, zorder=1)
                ax_save.patch.set_alpha(0)
                ax_save.spines['bottom'].set_position(('axes', 0.5))
                ax_save.spines['bottom'].set_color('w')
                ax_save.spines['top'].set_color(None)
                ax_save.spines['right'].set_color('w')
                ax_save.spines['left'].set_color(None)
                ax_save.set_xlabel("")
                ax_save.tick_params(left=False, bottom=True, axis='both', labelsize=8, zorder=10, pad=0, colors='w')
                if theta_mid[idx] < np.pi/2 or theta_mid[idx] > 3*np.pi/2:
                    plt.xticks(path_effects=path_eff, fontweight='bold')
                else:
                    plt.xticks(path_effects=path_eff, fontweight='bold', rotation=180)
                ax_mins.append(ax_save.get_xlim()[0])
                ax_maxs.append(ax_save.get_xlim()[1]*1.05)
                temp_path = f'temp_swarm_{idx}.png'
                fig_save.savefig(temp_path, dpi=300)
                t = Affine2D().scale(3, 1).rotate_deg(theta_mid[idx]*(180/np.pi))
                h = GridHelperCurveLinear(t, (0, 1, 0, 1))
                ax = floating_axes.FloatingSubplot(fig, 111, grid_helper=h)
                ax = fig.add_subplot(ax)
                aux_ax = ax.get_aux_axes(t)
                ax_div = Divider(fig, [x_base[idx], y_base[idx], 0.35, 0.35], [Size.Scaled(1.04)], [Size.Scaled(1)], aspect=True)
                ax.set_axes_locator(ax_div.new_locator(nx=0, ny=0))
                img = Image.open(temp_path)
                aux_ax.imshow(img, extent=[-0.18, 1.12, -0.15, 1.15])
                ax.axis('off')
                radar_ax.text(theta_mid[idx], 0.92, "\n".join(tw.wrap(diccionario_nombres.get(metric, metric), 18)), ha="center", va="center", fontweight="bold",
                              fontsize=10, color='w',
                              rotation=-90 + (180/np.pi)*theta_mid[idx] if theta_mid[idx] < np.pi else 90 + (180/np.pi)*theta_mid[idx])
                plt.close(fig_save)

            pizza_ax = fig.add_axes([0.09, 0.065, 0.82, 0.82], polar=True)
            pizza_ax.set_theta_offset(17)
            pizza_ax.axis('off')

            radar_object = PyPizza(
                params=metricas,
                background_color="w",
                straight_line_color="w",
                min_range=ax_mins,
                max_range=ax_maxs,
                straight_line_lw=1,
                straight_line_limit=100,
                last_circle_lw=0.1,
                other_circle_lw=0.1,
                inner_circle_size=18
            )

            radar_object.make_pizza(
                values=player_1[metricas].tolist(),
                color_blank_space='same',
                blank_alpha=0,
                bottom=5,
                kwargs_params=dict(fontsize=0, color='None'),
                kwargs_values=dict(fontsize=0, color='None'),
                kwargs_compare_values=dict(fontsize=0, color='None'),
                kwargs_slices=dict(
                    facecolor='lightskyblue', alpha=0.3, edgecolor='#313332', linewidth=1, zorder=1),
                ax=pizza_ax
            )

            fig.text(0.11, 0.953, player_1['Player'], fontweight="bold", fontsize=14, color='lightskyblue')
            fig.text(0.11, 0.931, player_1['Squad'], fontweight="bold", fontsize=12, color='w')
            fig.text(0.11, 0.909, player_1['Competicion'], fontweight="bold", fontsize=12, color='w')
            fig.text(0.975, 0.953, f"Posición: {player_1['Pos']}", fontweight="bold", fontsize=14, color='w', ha='right')
            fig.text(0.975, 0.935, f"{len(df_comparables)} comparables", fontweight="regular", fontsize=11, color='w', ha='right')
            fig.text(0.5, 0.02, "Visualización comparativa | Datos: DatosUnif.xlsx", fontstyle="italic", ha="center", fontsize=9, color="white")

            st.pyplot(fig)

            # GUARDAR IMAGEN
            radar_path = f"output/radar_{jugador.replace(' ', '_')}.png"
            os.makedirs("output", exist_ok=True)
            fig.savefig(radar_path, dpi=300)
            with open(radar_path, "rb") as img_file:
                st.download_button("📥 Descargar imagen del radar", data=img_file, file_name=os.path.basename(radar_path), mime="image/png")

           
            # Botón para generar el PDF con el gráfico del radar
            if st.button("📄 Exportar radar a PDF"):
                # Ruta donde guardar la imagen del radar
                radar_path = f"output/radar_{jugador.replace(' ', '_')}.png"
                
                # Verificar si la imagen ya existe
                if os.path.exists(radar_path):
                    # Generamos el PDF con la imagen del radar
                    resumen_path = generar_pdf_resultados(jugador, "2023/2024", radar_path)

                    # Mostrar el botón para descargar el PDF
                    with open(resumen_path, "rb") as pdf_file:
                        st.download_button("📥 Descargar PDF del radar", data=pdf_file, file_name=os.path.basename(resumen_path), mime="application/pdf")
                else:
                    st.error("No se encontró la imagen del radar para exportar.")