
#                                                                                 =======================================================
#                                                                                       1.💡📚📥 DESCARGA E IMPORTACIÓN DE LIBRERÍAS 
#                                                                                 =======================================================

# ===IMPORTACIÓN DE libreira strealit para (visualización de datos en la web)===========
import streamlit as st
# ======================================================================================

                                                # ==========================================
                                                # LIBRERÍAS DE DATOS Y API
                                                # ==========================================
from statsbombpy import sb            # Acceso directo a la base de datos gratuita de StatsBomb
import pandas as pd                   # Manipulación y análisis de datos en tablas (DataFrames)
import numpy as np                    # Operaciones matemáticas avanzadas y manejo de matrices
import requests                       # Realizar peticiones a servidores web (para APIs externas)
import json                           # Procesamiento de archivos de datos en formato JSON
import ast
# ==========================================
# VISUALIZACIÓN GRÁFICA (MATPLOTLIB)
# ==========================================
import matplotlib.pyplot as plt       # La base para crear cualquier gráfico o figura
import matplotlib.patheffects as path_effects  # Añade efectos como bordes o sombras al texto y líneas
from matplotlib.colors import to_rgba # Convierte nombres de colores (como 'red') a formato RGBA
from matplotlib.colors import LinearSegmentedColormap # Crea degradados de color personalizados para mapas de calor
from matplotlib.table import table    # Permite la creación y manipulación manual de tablas dentro de gráficos
import matplotlib.patches as mpatches # Para crear formas personalizadas (como círculos o rectángulos) en los gráficos
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import io 
# ==========================================
# LIBRERÍAS ESPECIALIZADAS EN FÚTBOL
# ==========================================
from mplsoccer import Pitch, VerticalPitch, Sbopen # Dibuja campos de juego (horizontal/vertical) y carga datos de StatsBomb
import seaborn as sns
# ==========================================
# MANEJO DE IMÁGENES Y URLs
# ==========================================
from urllib.request import urlopen, Request    # Permite abrir y leer datos directamente desde una URL (links de escudos)
from PIL import Image as PILImage     # Librería principal para abrir, editar y procesar imágenes (escudos de equipos)

# ==========================================
# EXPORTACIÓN Y FORMATO
# ==========================================
import dataframe_image as dfi         # Convierte tablas de datos (DataFrames) directamente en archivos de imagen (.png)
#=================================================================================================================================
#                                   ==========================================================
#                                                    ========================


#                                               +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                               ///////////////////////////////////////////CONFIGURACIÓN DE PÁGINA (DEBE IR PRIMERO)///////////////////////////////////////////
#                                               +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
st.set_page_config(
    page_title="Análisis mundial 2022", #el título de la pestaña del navegador
    layout="wide",
    page_icon="⚽"
)


#                                                                                           ===============             ===============
#                                                                                           ===============Título Página===============
#                                                                                           ===============             ===============
st.markdown(
    """<h1 style="text-align:center;">⚽Análisis mundial 2022📊<br><span style="font-size: 0.8em; opacity:0.7;">Por Mauricio Lozano</span></h1>""",
    unsafe_allow_html=True)



#                                                                                            ==========================================
#                                                                                            2. 🧠 CEREBRO: FUNCIONES Y CARGA DE DATOS
#                                                                                            ==========================================
#                                                   ···································                                                            ···························
#                                                   ··································Definimos funciones globales que usaremos en cualquier parte ···························
#                                                   ···································                                                            ···························



# Caché para que no se descargue todo cada vez que cambiamos de menú
@st.cache_data

#-----------------------------------
# Llamada de función para importar datos de statsbomb
#-----------------------------------

def cargar_datos_statsbomb():
    partidos = sb.matches(competition_id=43, season_id=106)
    events = sb.events(match_id=3869486)
    Alineacion_Portugal = sb.lineups(match_id=3869486)["Portugal"]
    Alineacion_Marruecos = sb.lineups(match_id=3869486)["Morocco"]
    return partidos, events, Alineacion_Portugal, Alineacion_Marruecos

# Ejecutamos la carga (esto solo tarda la primera vez)
partidos, events, Alineacion_Portugal, Alineacion_Marruecos = cargar_datos_statsbomb()
#-----------------------------------
# Llamada de función para escudos
#-----------------------------------
def descargar_imagen_stats(url):
    """
    Esta función encapsula toda la lógica de descarga.
    Usa 'with' para asegurar que la conexión se cierre sola.
    """
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as response:
        return PILImage.open(response)

#-----------------------------------
# Llamada de función para alineación en campo de fútbol
#-----------------------------------
def draw_player(x, y, name, number, color):
    """Dibuja jugador como círculo con número y nombre"""
    circle = plt.Circle((x, y), 3.5, color=color, ec='black', linewidth=2)
    ax.add_patch(circle)


    # Añadir efectos de contorno al texto para mejorar la legibilidad
    ax.text(x, y, f"{number}\n{name}",
             ha='center', va='center', 
             fontsize=7, color='yellow', weight='bold',
            path_effects=[path_effects.withStroke(linewidth=5, foreground='black')])
    
#------------------------------------
#  Llamada de función para obtener estadísticas del juego
# -----------------------------------

def obtener_estadisticas(events, equipo):
    """Calcula estadísticas básicas para un equipo"""
    df_equipo = events[events['team'] == equipo]
    stats = {}
    
    # Goles
    tiros = df_equipo[df_equipo['type'] == 'Shot']
    stats['Goles'] = len(tiros[tiros['shot_outcome'] == 'Goal'])
    
    # Pases
    stats['Pases'] = len(df_equipo[df_equipo['type'] == 'Pass'])
    
    # Faltas
    stats['Faltas'] = len(df_equipo[df_equipo['type'] == 'Foul Committed'])
    
    # Tarjetas
    col_tarjeta = 'foul_committed_card' if 'foul_committed_card' in df_equipo.columns else None
    if col_tarjeta and col_tarjeta in df_equipo.columns:
        stats['Tarjetas Amarillas'] = len(df_equipo[df_equipo[col_tarjeta] == 'Yellow Card'])
        stats['Tarjetas Rojas'] = len(df_equipo[df_equipo[col_tarjeta].isin(['Red Card', 'Second Yellow'])])
    else:
        stats['Tarjetas Amarillas'] = 0
        stats['Tarjetas Rojas'] = 0
    
    return stats

#-----------------------------------
# Llamada de campo de fútbol por tercios
#-----------------------------------

@st.cache_data
def generar_grafico_tercios(events):
    """Genera el gráfico de acciones por tercios del campo"""  
    # Procesamiento de datos
    events_with_loc = events[events['location'].notna()].copy()
    events_with_loc['x'] = events_with_loc['location'].apply(lambda loc: loc[0])

    def assign_third(x):
        if x < 40:
            return 'Acc terc defens'
        elif x < 80:
            return 'Acc terc med'
        else:
            return 'Acc terc offens'
        
    events_with_loc['third'] = events_with_loc['x'].apply(assign_third)
    counts = events_with_loc['third'].value_counts()
    counts = counts.reindex(['Acc terc defens', 'Acc terc med', 'Acc terc offens'], fill_value=0)
    values = counts.values
        
    # Colores
    norm = plt.Normalize(vmin=values.min(), vmax=values.max())
    colors = plt.cm.Reds(norm(values))

    # Campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw(figsize=(12, 8))

    # Rectángulos y etiquetas
    tercios = [(0, 40, 'Acc terc defens'), (40, 80, 'Acc terc med'), (80, 120, 'Acc terc offens')]
    for i, (x_start, x_end, name) in enumerate(tercios):
        rect = patches.Rectangle((x_start, 0), x_end - x_start, 80, linewidth=0, alpha=0.4, facecolor=colors[i])
        ax.add_patch(rect)
        ax.text((x_start + x_end) / 2, 40, f"{name}\n{counts[name]}", fontsize=14, ha='center', va='center', 
                color='orange', fontweight='bold', bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.3'))

    return fig

#-----------------------------------
# Llamada de función mapas de disparos
#-----------------------------------

@st.cache_data
def generar_mapa_disparos(portugal_No_gol, marruecos_No_gol, Goles_marruecos):
    """
    Genera el mapa de disparos con mplsoccer.
    Retorna la figura completa para Streamlit.
    """
    # --- CREAR FIGURA Y EJE ---
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # --- CONFIGURAR CAMPO VERTICAL ---
    pitch = VerticalPitch(
        pitch_type='statsbomb', 
        pitch_color='grass', 
        line_color='white', 
        stripe=True
    )
    
    # Dibujar campo en el eje
    pitch.draw(ax=ax)

    # Colores base
    colors = {'Portugal': 'red', 'Morocco': 'green'}

    # --- Portugal: no goles ---
    pitch.scatter(
        x=120 - portugal_No_gol.x,
        y=80 - portugal_No_gol.y,
        s=portugal_No_gol['shot_statsbomb_xg'] * 1500,
        color=colors['Portugal'],       
        edgecolor='black',
        ax=ax,  
        label='Portugal - No Gol'
    )

    # --- Marruecos: no goles ---
    pitch.scatter(
        x=marruecos_No_gol.x, 
        y=marruecos_No_gol.y,
        s=marruecos_No_gol['shot_statsbomb_xg'] * 1000,
        color=colors['Morocco'],       
        edgecolor='black',
        ax=ax,
        label='Marruecos - No Gol'
    )

    # --- Marruecos: goles ---
    pitch.scatter(
        x=Goles_marruecos.x,
        y=Goles_marruecos.y,
        s=Goles_marruecos['shot_statsbomb_xg'] * 1000,
        marker='football',
        ax=ax,
        label='Marruecos - Gol'
    )

    # --- Etiquetas de texto (Portugal No Gol) ---
    for _, shot in portugal_No_gol.iterrows():
        pitch.text(                               
            120 - shot['x'], 
            80 - shot['y'],
            shot['player'].split()[0],  
            ha='center', va='center', fontsize=7, rotation=60, color='black',
            ax=ax,
            path_effects=[path_effects.withStroke(linewidth=3, foreground='white')],
            weight='bold',
            bbox=dict(facecolor='white', alpha=0.1, boxstyle='circle,pad=0.5', linewidth=3, edgecolor='black')
        )

    # --- Etiquetas de texto (Marruecos No Gol) ---
    for _, shot in marruecos_No_gol.iterrows():
        pitch.text(
            shot['x'], shot['y'],
            shot['player'].split()[0],
            ha='center', va='bottom', fontsize=7, color='white',
            ax=ax,
            path_effects=[path_effects.withStroke(linewidth=3, foreground='black')],
            weight='bold',
            bbox=dict(facecolor='black', alpha=0.1, boxstyle='circle,pad=0.5', linewidth=3, edgecolor='white')
        )

    # --- Etiquetas de texto (Marruecos Gol) ---
    for _, shot in Goles_marruecos.iterrows():
        pitch.text(
            shot['x'], shot['y'],
            shot['player'].split()[0],
            ha='center', va='top', fontsize=8, rotation=90, color='gold',
            ax=ax,
            path_effects=[path_effects.withStroke(linewidth=3, foreground='black')],
            weight='bold',
            bbox=dict(facecolor='yellow', alpha=0.2, boxstyle='circle,pad=0.5', linewidth=3, edgecolor='gold')
        )

    # --- Título ---
    ax.set_title('Mapa de tiros – Portugal 0-1 Marruecos\n(Nombres de ejecutantes)', 
                 color='white', backgroundcolor='black', fontsize=12, pad=10)
    
    # --- Leyenda ---
    ax.legend(loc='upper right', facecolor='black', labelcolor='white', fontsize=10)
    
    # ✅ IMPORTANTE: Retornar la figura
    return fig

#----------------------------------------------------------------
# Llamar la función para crear redes de pases
#----------------------------------------------------------------

@st.cache_data
def preparar_datos_pases(events, equipo, minuto_corte_oponente=None):
    """
    Prepara los datos de pases para un equipo específico.
    Retorna: df_pases_completos, posicion_prom, conexiones
    """
    # Filtrar pases completados del equipo
    pases_compl = events[
        (events['type'] == 'Pass') & 
        (events['team'] == equipo) & 
        (events['pass_outcome'].isna())
    ].copy()
    
    # Filtrar por minuto de corte si se especifica (antes del primer cambio rival)
    if minuto_corte_oponente is not None:
        pases_compl = pases_compl[pases_compl['minute'] < minuto_corte_oponente]
    
    # Solo pases con ubicación - Procesar Coordenadas
    pases_con_loc = pases_compl[pases_compl['location'].notna()].copy()
    pases_con_loc['x'] = pases_con_loc['location'].apply(lambda loc: loc[0] if isinstance(loc, (list, tuple)) else None)
    pases_con_loc['y'] = pases_con_loc['location'].apply(lambda loc: loc[1] if isinstance(loc, (list, tuple)) else None)
    
    # Posición promedio por jugador
    posicion_prom = pases_con_loc.groupby('player').agg(
        x_mean=('x', 'mean'),
        y_mean=('y', 'mean'),
        pass_count=('x', 'count')
    ).reset_index()
    posicion_prom.columns = ['player', 'x', 'y', 'count']
    
    # Conexiones entre jugadores pasador y recpetor
    conexiones = pases_compl.groupby(['player', 'pass_recipient']).size().reset_index(name='pass_count')
    conexiones = conexiones.merge(posicion_prom, on='player')\
        .merge(posicion_prom, left_on='pass_recipient', right_on='player', suffixes=('_passer', '_receiver'))
    

    
    # Calcular tamaños visuales
    if len(conexiones) > 0:
        conexiones['tamaño'] = (conexiones['count_passer'] / conexiones['count_passer'].max() * 700)
        conexiones['ancho'] = (conexiones['pass_count'] / conexiones['pass_count'].max() * 15)
        conexiones["primer_nombre"] = conexiones["player_passer"].str.split().str[0]
    
    return pases_compl, posicion_prom, conexiones


@st.cache_data
def generar_red_pases(datos, color_nodo, color_borde, color_flecha, color_borde_flecha, nombre_equipo):
    """
    Genera la red de pases en un campo vertical.
    Retorna la figura completa para Streamlit.
    """
    # --- CREAR FIGURA Y EJE ---
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # --- CONFIGURAR CAMPO ---
    pitch = VerticalPitch(
        pitch_type='statsbomb', 
        pitch_color='grass', 
        line_color='white', 
        stripe=True
    )
    pitch.draw(ax=ax)

    # --- 1. Jugadores (nodos) ---
    if len(datos) > 0:
        pitch.scatter(
            datos['x_passer'], datos['y_passer'],
            s=datos["count_passer"] * 15,
            color=color_nodo,    
            ec=color_borde,      
            linewidth=1.5,
            ax=ax,
            label=f'Jugadores {nombre_equipo}',
            alpha=0.9,
            zorder=5
        )

        # --- 2. Flechas de pases ---
        for i, row in datos.iterrows():
            pitch.arrows(
                row['x_passer'], row['y_passer'],
                row['x_receiver'], row['y_receiver'],
                width=row['ancho'],
                headwidth=3, headlength=4,
                color=color_flecha,          
                edgecolor=color_borde_flecha, 
                linewidth=1.5, alpha=0.5,
                ax=ax,
                label=f'Pases {nombre_equipo}' if i == 0 else "",
                zorder=3
            )

        # --- 3. Nombres de jugadores ---
        for _, row in datos.iterrows():
            pitch.text(
                row['x_passer'], row['y_passer'] + 1,
                row['primer_nombre'],
                ha='center', va='bottom', rotation=60,
                fontsize=9, color='black', weight='bold',
                ax=ax,
                path_effects=[path_effects.withStroke(linewidth=1.5, foreground='white')],
                zorder=6
            )

    # --- Título y leyenda ---
    ax.set_title(
        f" Red de pases: {nombre_equipo}\nvs Oponente (Mundial 2022)",
        fontsize=14, backgroundcolor='black', color='red', pad=10, fontweight='bold',
        path_effects=[path_effects.withStroke(linewidth=1, foreground='white')]
    )
    ax.legend(loc='upper left', fontsize=10, frameon=True, facecolor='black', labelcolor='white')
    
    # ✅ IMPORTANTE: Retornar la figura
    return fig

#--------------------------------------------------------
# Llamar función para mapa de calor de jugador
#--------------------------------------------------------

@st.cache_data
def generar_mapa_calor_jugador(events, nombre_jugador_statsbomb, titulo_personalizado, color_mapa='Reds'):
    """
    Genera un mapa de calor para un jugador específico.
    
    Parámetros:
    - events: DataFrame completo de eventos StatsBomb
    - nombre_jugador_statsbomb: Nombre exacto como aparece en StatsBomb (ej: 'Kléper Laveran Lima Ferreira')
    - titulo_personalizado: Título que quieres mostrar en la app (ej: 'Pepe')
    - color_mapa: Esquema de colores de matplotlib (ej: 'Reds', 'Blues', 'Greens')
    
    Retorna: fig (objeto matplotlib)
    """
    # Filtrar eventos del jugador
    jugador = events[events['player'] == nombre_jugador_statsbomb].copy()
    
    # Agregar columnas para x, y desde location (con manejo seguro)
    jugador['x'] = jugador['location'].apply(lambda loc: loc[0] if isinstance(loc, (list, tuple)) else None)
    jugador['y'] = jugador['location'].apply(lambda loc: loc[1] if isinstance(loc, (list, tuple)) else None)
    
    # Eliminar filas sin coordenadas válidas
    jugador = jugador[jugador['x'].notna() & jugador['y'].notna()]
    
    # Crear figura y campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw(figsize=(12, 8))
    
    # Mapa de calor (solo si hay datos)
    if len(jugador) > 0:
        pitch.kdeplot(
            x=jugador['x'],
            y=jugador['y'],
            ax=ax,
            shade=True,
            cmap=color_mapa,
            alpha=0.6,
            bw_method='scott',
            levels=30
        )
    
    # Leyenda
    heatmap_patch = mpatches.Patch(color='red', alpha=0.6, label=f'Mapa de calor {titulo_personalizado}')
    ax.legend(handles=[heatmap_patch], loc='upper right', fontsize=12, frameon=True)
    
    # Título
    fig.suptitle(f"Mapa de calor de posiciones de {titulo_personalizado}\n(Portugal vs Marruecos, Mundial 2022)", 
                 fontsize=16, color='black', y=1.02)
    
    # ✅ IMPORTANTE: Retornar la figura
    return fig

#-------------------------------------------------
# Llamar función para disparos de jugador
#-------------------------------------------------

@st.cache_data
def generar_mapa_disparos_jugador(df_shots, nombre_jugador_statsbomb, titulo_personalizado):
    """
    Genera un mapa de disparos para un jugador específico.
    
    Parámetros:
    - df_shots: DataFrame filtrado con solo eventos de tipo 'Shot'
    - nombre_jugador_statsbomb: Nombre exacto como aparece en StatsBomb
    - titulo_personalizado: Título que quieres mostrar en la app (ej: 'Pepe')
    
    Retorna: fig (objeto matplotlib)
    """
    # 1. Filtramos los tiros del jugador
    shots_jugador = df_shots[df_shots['player'] == nombre_jugador_statsbomb].copy()
    
    # 2. DESEMPAQUETAR LOCATION: Crear columnas 'x' e 'y'
    if 'location' in shots_jugador.columns and 'x' not in shots_jugador.columns:
        shots_jugador[['x', 'y']] = pd.DataFrame(
            shots_jugador['location'].tolist(), 
            index=shots_jugador.index
        )
    
    # 3. DIBUJAR EL CAMPO
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white',
        stripe=True
    )
    fig, ax = pitch.draw(figsize=(12, 8))
    
    # 4. GRAFICAR (solo si hay disparos)
    if len(shots_jugador) > 0:
        # Manejar caso donde shot_statsbomb_xg pueda no existir
        if 'shot_statsbomb_xg' in shots_jugador.columns:
            sizes = shots_jugador['shot_statsbomb_xg'] * 2500
        else:
            sizes = 500  # Tamaño por defecto
        
        shot_nogol = pitch.scatter(
            x=shots_jugador['x'], 
            y=shots_jugador['y'],
            s=sizes,
            color='white',       
            edgecolor='red',
            ax=ax,  
            label=f'Disparos de {titulo_personalizado}',
        )

        # 5. AÑADIR TEXTO
        for i, row in shots_jugador.iterrows():
            ax.text(
                row['x'], 
                row['y'],
                row['player'].split()[0] if isinstance(row['player'], str) else str(row['player'])[:5],
                fontsize=10,
                color='black',
                ha='center',
                va='bottom',
                path_effects=[path_effects.withStroke(linewidth=3, foreground='white')],
            )
        
        ax.legend()
    
    # Título
    ax.set_title(f'Mapa de tiros de {titulo_personalizado} – Marruecos vs Portugal\nOctavos Mundial 2022', 
                 fontsize=14, pad=20, color='black')
    
    # ✅ IMPORTANTE: Retornar la figura
    return fig

#----------------------------------------------------------
# Llamar Función para dashboad de acciones del jugador
#----------------------------------------------------------

@st.cache_data
def generar_mapa_eventos_pepe(events, nombre_jugador):
    """
    Genera un dashboard de 4 paneles con las acciones individuales del jugador.
    
    Parámetros:
    - events: DataFrame completo de eventos StatsBomb
    - nombre_jugador: Nombre exacto como aparece en StatsBomb
    
    Retorna: fig (objeto matplotlib)
    """
    # 🔍 FILTRAR SOLO EVENTOS DEL JUGADOR (esto faltaba en tu código original)
    events_pepe = events[events['player'] == nombre_jugador].copy()
    
    # Filtrar por tipo de evento (SOLO de Pepe)
    recuperaciones = events_pepe[events_pepe['type'] == 'Ball Recovery'].copy()
    pases = events_pepe[events_pepe['type'] == 'Pass'].copy()
    faltas = events_pepe[events_pepe['type'] == 'Foul Committed'].copy()
    intercepciones = events_pepe[events_pepe['type'] == 'Interception'].copy()
    
    # Configuración visual
    bg_color = 'black'
    
    pitch = Pitch(
        pitch_type='statsbomb',
        stripe=True, 
        pitch_color='grass', 
        line_color='white'
    )
    
    # Crear figura 2x2
    fig, axs = plt.subplots(2, 2, figsize=(16, 10), facecolor=bg_color)
    axs = axs.flatten()
    
    # Configurar fondo de cada axis
    for ax in axs:
        ax.set_facecolor(bg_color)
    
    # =============================================================================
    # PANEL 1: RECUPERACIONES (verde)
    # =============================================================================
    pitch.draw(ax=axs[0])
    if len(recuperaciones) > 0 and 'location' in recuperaciones.columns:
        recuperaciones_validas = recuperaciones[recuperaciones['location'].notna()]
        if len(recuperaciones_validas) > 0:
            pitch.scatter(
                x=recuperaciones_validas['location'].apply(lambda loc: loc[0] if isinstance(loc, (list, tuple)) else None),
                y=recuperaciones_validas['location'].apply(lambda loc: loc[1] if isinstance(loc, (list, tuple)) else None),
                color='white',
                edgecolor='green',
                s=80,
                ax=axs[0],
            )
    axs[0].set_title(f"🛡️ Recuperaciones ({len(recuperaciones)})", color='white', fontsize=12)
    
    # =============================================================================
    # PANEL 2: PASES (flechas azules)
    # =============================================================================
    pitch.draw(ax=axs[1])
    if len(pases) > 0 and 'location' in pases.columns:
        pases_validos = pases[pases['location'].notna()]
        for _, row in pases_validos.iterrows():
            if isinstance(row['location'], (list, tuple)) and isinstance(row.get('pass_end_location'), (list, tuple)):
                pitch.arrows(
                    row['location'][0], row['location'][1],
                    row['pass_end_location'][0], row['pass_end_location'][1],
                    color='white',
                    edgecolor='blue',
                    linewidth=0.5,
                    ax=axs[1],
                    width=2,
                    alpha=0.5
                )
    axs[1].set_title(f"🔵 Pases ({len(pases)})", color='white', fontsize=12)
    
    # =============================================================================
    # PANEL 3: FALTAS (círculo rojo con X)
    # =============================================================================
    pitch.draw(ax=axs[2])
    if len(faltas) > 0 and 'location' in faltas.columns:
        faltas_validas = faltas[faltas['location'].notna()]
        if len(faltas_validas) > 0:
            # Círculo con borde
            pitch.scatter(
                x=faltas_validas['location'].apply(lambda loc: loc[0] if isinstance(loc, (list, tuple)) else None),
                y=faltas_validas['location'].apply(lambda loc: loc[1] if isinstance(loc, (list, tuple)) else None),
                color='none',
                edgecolor='red',
                linewidth=2,
                s=150,
                marker='o',
                ax=axs[2]
            )
            # X dentro del círculo
            pitch.scatter(
                x=faltas_validas['location'].apply(lambda loc: loc[0] if isinstance(loc, (list, tuple)) else None),
                y=faltas_validas['location'].apply(lambda loc: loc[1] if isinstance(loc, (list, tuple)) else None),
                color='red',
                edgecolor='white',
                linewidth=3,
                s=100,
                marker='x',
                ax=axs[2]
            )
    axs[2].set_title(f"❌ Faltas cometidas ({len(faltas)})", color='white', fontsize=12)
    
    # =============================================================================
    # PANEL 4: INTERCEPCIONES (naranja, ▲)
    # =============================================================================
    pitch.draw(ax=axs[3])
    if len(intercepciones) > 0 and 'location' in intercepciones.columns:
        intercepciones_validas = intercepciones[intercepciones['location'].notna()]
        if len(intercepciones_validas) > 0:
            pitch.scatter(
                x=intercepciones_validas['location'].apply(lambda loc: loc[0] if isinstance(loc, (list, tuple)) else None),
                y=intercepciones_validas['location'].apply(lambda loc: loc[1] if isinstance(loc, (list, tuple)) else None),
                color='orange',
                edgecolor='white',
                linewidth=2,
                s=100,
                marker='^',
                ax=axs[3]
            )
    axs[3].set_title(f"🎯 Intercepciones ({len(intercepciones)})", color='white', fontsize=12)
    
    # Título principal
    plt.suptitle("Mapa de eventos de Pepe (Portugal vs Marruecos, Mundial 2022)", 
                 fontsize=18, color='white', y=1.02)
    plt.tight_layout()
    
    # ✅ IMPORTANTE: Retornar la figura
    return fig


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Función para descargar imágenes
@st.cache_data
def descargar_imagen_stats(url):
    import requests
    from PIL import Image
    from io import BytesIO
    try:
        response = requests.get(url.strip())
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

# =============================================================================
# FUNCIONES QUE CREAN Y RETORNAN SU PROPIA FIGURA (para st.pyplot)
# =============================================================================

@st.cache_data
def generar_red_pases_marruecos_fig(conexiones_marruecos):
    """Versión que crea y retorna su propia figura"""
    fig, ax = plt.subplots(figsize=(10, 12))
    generar_red_pases(ax=ax, datos=conexiones_marruecos, color_nodo="green", 
                      color_borde="white", color_flecha="lightgreen", 
                      color_borde_flecha="darkgreen", nombre_equipo="Marruecos")
    return fig

@st.cache_data
def generar_red_pases_portugal_fig(conexiones_portugal):
    """Versión que crea y retorna su propia figura"""
    fig, ax = plt.subplots(figsize=(10, 12))
    generar_red_pases(ax=ax, datos=conexiones_portugal, color_nodo="white", 
                      color_borde="red", color_flecha="lightblue", 
                      color_borde_flecha="black", nombre_equipo="Portugal")
    return fig

@st.cache_data
def generar_mapa_disparos_fig(portugal_No_gol, marruecos_No_gol, Goles_marruecos):
    """Versión que crea y retorna su propia figura"""
    fig, ax = plt.subplots(figsize=(10, 12))
    generar_mapa_disparos(ax=ax, portugal_No_gol=portugal_No_gol, 
                          marruecos_No_gol=marruecos_No_gol, Goles_marruecos=Goles_marruecos)
    return fig
#----------------------------------------------------------
# 5. Llamar Función para Dashboard del Juego Marruecos VS Portugal
#----------------------------------------------------------

@st.cache_data
def descargar_imagen_stats(url):
    """
    Esta función encapsula toda la lógica de descarga.
    Usa 'with' para asegurar que la conexión se cierre sola.
    """
    try:
        req = Request(url.strip(), headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as response:
            return PILImage.open(response)
    except Exception as e:
        st.error(f"❌ Error al descargar imagen: {e}")
        return None


@st.cache_data
def generar_red_pases(datos, color_nodo, color_borde, color_flecha, color_borde_flecha, nombre_equipo):
    """Función maestra para redes de pases - Retorna su propia figura"""
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # 1. Configuramos el campo
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', stripe=True)
    pitch.draw(ax=ax)

    # 2. Jugadores
    if len(datos) > 0:
        pitch.scatter(
            datos['x_passer'], datos['y_passer'],
            s=datos["count_passer"] * 15,
            color=color_nodo,
            ec=color_borde,
            linewidth=1.5,
            ax=ax,
            label=f'Jugadores {nombre_equipo}'
        )

        # 3. Flechas
        for i, row in datos.iterrows():
            pitch.arrows(
                row['x_passer'], row['y_passer'],
                row['x_receiver'], row['y_receiver'],
                width=row['ancho'],
                headwidth=3, headlength=4,
                color=color_flecha,
                edgecolor=color_borde_flecha,
                linewidth=1.5, alpha=0.5,
                ax=ax,
                label=f'Pases {nombre_equipo}' if i == 0 else ""
            )

        # 4. Nombres
        for _, row in datos.iterrows():
            pitch.text(
                row['x_passer'], row['y_passer'] + 1,
                row['primer_nombre'],
                ha='center', va='bottom', rotation=60,
                fontsize=10, color='black', weight='bold',
                ax=ax,
                path_effects=[path_effects.withStroke(linewidth=1.5, foreground='white')]
            )

    # 5. Título y leyenda
    ax.set_title(
        f"Red de pases: {nombre_equipo}\nvs Oponente (Mundial 2022)",
        fontsize=14, backgroundcolor='black', color='white', pad=5,
        path_effects=[path_effects.withStroke(linewidth=1, foreground='red')]
    )
    ax.legend(loc='upper left', fontsize=10, frameon=True)
    
    return fig


@st.cache_data
def generar_mapa_disparos_fig(portugal_No_gol, marruecos_No_gol, Goles_marruecos):
    """Mapa de disparos - Retorna su propia figura"""
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # Configuramos el campo vertical
    pitch = VerticalPitch(
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white',
        stripe=True
    )
    pitch.draw(ax=ax)

    # Colores base
    colors = {'Portugal': 'red', 'Morocco': 'green'}

    # Portugal: no goles
    if len(portugal_No_gol) > 0:
        pitch.scatter(
            x=120 - portugal_No_gol.x,
            y=80 - portugal_No_gol.y,
            s=portugal_No_gol['shot_statsbomb_xg'] * 1500,
            color=colors['Portugal'],
            edgecolor='black',
            ax=ax,
            label='Portugal - No Gol'
        )

    # Marruecos: no goles
    if len(marruecos_No_gol) > 0:
        pitch.scatter(
            x=marruecos_No_gol.x,
            y=marruecos_No_gol.y,
            s=marruecos_No_gol['shot_statsbomb_xg'] * 1000,
            color=colors['Morocco'],
            edgecolor='black',
            ax=ax,
            label='Marruecos - No Gol'
        )

    # Marruecos: goles
    if len(Goles_marruecos) > 0:
        pitch.scatter(
            x=Goles_marruecos.x,
            y=Goles_marruecos.y,
            s=Goles_marruecos['shot_statsbomb_xg'] * 1000,
            marker='football',
            ax=ax,
            label='Marruecos - Gol'
        )

    # Etiquetas de texto (Portugal No Gol)
    for _, shot in portugal_No_gol.iterrows():
        pitch.text(
            120 - shot['x'],
            80 - shot['y'],
            shot['player'].split()[0] if isinstance(shot['player'], str) else 'Player',
            ha='center', va='center', fontsize=7, rotation=60, color='black',
            ax=ax,
            path_effects=[path_effects.withStroke(linewidth=3, foreground='white')],
            weight='bold',
            bbox=dict(facecolor='white', alpha=0.1, boxstyle='circle,pad=0.5', linewidth=3, edgecolor='black')
        )

    # Etiquetas de texto (Marruecos No Gol)
    for _, shot in marruecos_No_gol.iterrows():
        pitch.text(
            shot['x'], shot['y'],
            shot['player'].split()[0] if isinstance(shot['player'], str) else 'Player',
            ha='center', va='bottom', fontsize=7, color='white',
            ax=ax,
            path_effects=[path_effects.withStroke(linewidth=3, foreground='black')],
            weight='bold',
            bbox=dict(facecolor='black', alpha=0.1, boxstyle='circle,pad=0.5', linewidth=3, edgecolor='white')
        )

    # Etiquetas de texto (Marruecos Gol)
    for _, shot in Goles_marruecos.iterrows():
        pitch.text(
            shot['x'], shot['y'],
            shot['player'].split()[0] if isinstance(shot['player'], str) else 'Player',
            ha='center', va='top', fontsize=8, rotation=90, color='gold',
            ax=ax,
            path_effects=[path_effects.withStroke(linewidth=3, foreground='black')],
            weight='bold',
            bbox=dict(facecolor='yellow', alpha=0.2, boxstyle='circle,pad=0.5', linewidth=3, edgecolor='gold')
        )

    # Título
    ax.set_title('Mapa de tiros – Portugal 0-1 Marruecos\n(Nombres de ejecutantes)', 
                 color='white', backgroundcolor='black', fontsize=12, pad=10)
    
    return fig


@st.cache_data
def generar_grafico_tercios(events):
    """Genera el gráfico de acciones por tercios del campo"""
    # Procesamiento de datos
    events_with_loc = events[events['location'].notna()].copy()
    events_with_loc['x'] = events_with_loc['location'].apply(lambda loc: loc[0])

    def assign_third(x):
        if x < 40:
            return 'Acc terc defens'
        elif x < 80:
            return 'Acc terc med'
        else:
            return 'Acc terc offens'
        
    events_with_loc['third'] = events_with_loc['x'].apply(assign_third)
    counts = events_with_loc['third'].value_counts()
    counts = counts.reindex(['Acc terc defens', 'Acc terc med', 'Acc terc offens'], fill_value=0)
    values = counts.values
        
    # Colores
    norm = plt.Normalize(vmin=values.min(), vmax=values.max())
    colors = plt.cm.Reds(norm(values))

    # Campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw(figsize=(12, 8))

    # Rectángulos y etiquetas
    tercios = [(0, 40, 'Acc terc defens'), (40, 80, 'Acc terc med'), (80, 120, 'Acc terc offens')]
    for i, (x_start, x_end, name) in enumerate(tercios):
        rect = patches.Rectangle((x_start, 0), x_end - x_start, 80, linewidth=0, alpha=0.4, facecolor=colors[i])
        ax.add_patch(rect)
        ax.text((x_start + x_end) / 2, 40, f"{name}\n{counts[name]}", fontsize=14, ha='center', va='center', 
                color='orange', fontweight='bold', bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.3'))

    return fig
#----------------------------------------------------------
# 6.1. Llamar Función para Análisis xG Holanda vs Ecuador
#----------------------------------------------------------

def analizar_xg_partido(archivo_csv):
    """
    Función para analizar el xG (Expected Goals) de un partido de fútbol.
    
    Args:
        archivo_csv (str): Ruta del archivo CSV con los datos del partido
    
    Returns:
        dict: Diccionario con los resultados del análisis
    """   
    try:
        # Cargar datos
        df = pd.read_csv(archivo_csv)
        
        # Filtrar solo eventos de tiro (Shot)
        shots_df = df[df['type'] == 'Shot'].copy()
        
        if len(shots_df) == 0:
            return {
                'success': False,
                'message': 'No se encontraron eventos de tiro en los datos'
            }
        
        # Verificar si hay columna de xG
        if 'shot_statsbomb_xg' not in shots_df.columns:
            return {
                'success': False,
                'message': 'La columna shot_statsbomb_xg no existe en los datos'
            }
        
        # Limpiar datos - convertir xG a numérico
        shots_df['shot_statsbomb_xg'] = pd.to_numeric(
            shots_df['shot_statsbomb_xg'], 
            errors='coerce'
        ).fillna(0)
        
        # Filtrar solo tiros con xG > 0
        shots_with_xg = shots_df[shots_df['shot_statsbomb_xg'] > 0]
        
        if len(shots_with_xg) == 0:
            return {
                'success': False,
                'message': 'No se encontraron tiros con xG registrado'
            }
        
        # Agrupar por jugador y sumar xG
        player_xg = shots_with_xg.groupby(['player', 'player_id', 'team']).agg({
            'shot_statsbomb_xg': ['sum', 'count', 'max'],
        }).round(3)
        
        # Aplanar columnas
        player_xg.columns = ['xG_Total', 'Tiros', 'xG_Max_Tiro']
        player_xg = player_xg.reset_index()
        
        # Ordenar por xG total descendente
        player_xg = player_xg.sort_values('xG_Total', ascending=False)
        
        # Jugador con mayor xG
        top_player = player_xg.iloc[0]
        
        # xG por equipo
        team_xg = shots_with_xg.groupby('team')['shot_statsbomb_xg'].agg(['sum', 'count']).round(3)
        team_xg.columns = ['xG_Total', 'Tiros']
        
        return {
            'success': True,
            'top_player': {
                'nombre': top_player['player'],
                'equipo': top_player['team'],
                'xg_total': top_player['xG_Total'],
                'tiros': int(top_player['Tiros']),
                'xg_max_tiro': top_player['xG_Max_Tiro']
            },
            'top_5_jugadores': player_xg.head(5).to_dict('records'),
            'xg_por_equipo': team_xg.to_dict(),
            'total_shots': len(shots_with_xg),
            'dataframe': player_xg
        }
        
    except FileNotFoundError:
        return {
            'success': False,
            'message': f'No se encontró el archivo: {archivo_csv}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al procesar los datos: {str(e)}'
        }

#----------------------------------------------------------------
# 6.1.3. Llamar a función para anlizar juego Marruecos vs Francia
#----------------------------------------------------------------
def analizar_pases_marruecos_francia(archivo_csv):
    """
    Función para analizar los pases totales del partido Marruecos vs Francia.
    """
    import pandas as pd
    
    try:
        # Cargar datos
        df = pd.read_csv(archivo_csv)
        
        # Filtrar solo eventos de pase (Pass)
        passes_df = df[df['type'] == 'Pass'].copy()
        
        if len(passes_df) == 0:
            return {
                'success': False,
                'message': 'No se encontraron eventos de pase en los datos'
            }
        
        # Verificar columnas necesarias
        required_columns = ['player', 'team']
        for col in required_columns:
            if col not in passes_df.columns:
                return {
                    'success': False,
                    'message': f'La columna {col} no existe en los datos'
                }
        
        # ============================================
        # CALCULAR PASES INTENTADOS Y COMPLETADOS
        # ============================================
        
        # Pases intentados por equipo
        pases_intentados_equipo = passes_df.groupby('team').size().reset_index(name='Pases_Intentados')
        
        # Pases completados: pass_outcome es NaN (vacío)
        if 'pass_outcome' in passes_df.columns:
            pases_completados_df = passes_df[passes_df['pass_outcome'].isna()]
            pases_completados_equipo = pases_completados_df.groupby('team').size().reset_index(name='Pases_Completados')
            
            pases_fallidos_df = passes_df[passes_df['pass_outcome'].notna()]
            pases_fallidos_equipo = pases_fallidos_df.groupby('team').size().reset_index(name='Pases_Fallidos')
        else:
            pases_completados_equipo = pases_intentados_equipo.copy()
            pases_completados_equipo.columns = ['team', 'Pases_Completados']
            pases_fallidos_equipo = pd.DataFrame({'team': pases_intentados_equipo['team'], 'Pases_Fallidos': 0})
        
        # Merge de todas las estadísticas por equipo
        team_stats = pases_intentados_equipo.merge(pases_completados_equipo, on='team', how='left')
        team_stats = team_stats.merge(pases_fallidos_equipo, on='team', how='left')
        
        team_stats['Pases_Completados'] = team_stats['Pases_Completados'].fillna(0).astype(int)
        team_stats['Pases_Fallidos'] = team_stats['Pases_Fallidos'].fillna(0).astype(int)
        
        # Calcular precisión de pase
        team_stats['Precision'] = (team_stats['Pases_Completados'] / team_stats['Pases_Intentados'] * 100).round(2)
        
        # ============================================
        # ESTADÍSTICAS POR JUGADOR
        # ============================================
        
        player_stats = passes_df.groupby(['player', 'team']).size().reset_index(name='Pases_Intentados')
        
        if 'pass_outcome' in passes_df.columns:
            player_completados = pases_completados_df.groupby(['player', 'team']).size().reset_index(name='Pases_Completados')
            player_stats = player_stats.merge(player_completados, on=['player', 'team'], how='left')
            player_stats['Pases_Completados'] = player_stats['Pases_Completados'].fillna(0).astype(int)
        else:
            player_stats['Pases_Completados'] = player_stats['Pases_Intentados']
        
        player_stats['Pases_Fallidos'] = player_stats['Pases_Intentados'] - player_stats['Pases_Completados']
        player_stats['Precision'] = (player_stats['Pases_Completados'] / player_stats['Pases_Intentados'] * 100).round(2)
        
        # ============================================
        # TOTALES GENERALES
        # ============================================
        
        total_intentados = int(team_stats['Pases_Intentados'].sum())
        total_completados = int(team_stats['Pases_Completados'].sum())
        total_fallidos = int(team_stats['Pases_Fallidos'].sum())
        precision_general = (total_completados / total_intentados * 100) if total_intentados > 0 else 0
        
        # ============================================
        # TOP JUGADORES POR EQUIPO
        # ============================================
        
        # Obtener nombres reales de los equipos del DataFrame
        equipos_lista = team_stats['team'].unique().tolist()
        
        top_marruecos = player_stats[player_stats['team'] == 'Morocco'].sort_values(
            'Pases_Intentados', ascending=False
        ).head(5).to_dict('records')
        
        top_francia = player_stats[player_stats['team'] == 'France'].sort_values(
            'Pases_Intentados', ascending=False
        ).head(5).to_dict('records')
        
        return {
            'success': True,
            'team_stats_df': team_stats,  # ✅ Guardar DataFrame completo
            'equipos_lista': equipos_lista,  # ✅ Lista de equipos como strings
            'total_intentados': total_intentados,
            'total_completados': total_completados,
            'total_fallidos': total_fallidos,
            'precision_general': round(precision_general, 2),
            'top_marruecos': top_marruecos,
            'top_francia': top_francia,
            'total_pases': len(passes_df),
            'dataframe_team': team_stats,
            'dataframe_player': player_stats
        }
        
    except FileNotFoundError:
        return {
            'success': False,
            'message': f'No se encontró el archivo: {archivo_csv}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al procesar los datos: {str(e)}'
        }
#--------------------------------------------------------------
# 6.2. Llamar función para crear rankings
#--------------------------------------------------------------
# No creé codigo arriba, está abajo.

#--------------------------------------------------------------
# 6.3. Llamar función para crear Mapa de MESSI
#--------------------------------------------------------------

# ==============================================================================
# CARGA DE DATOS (Desde CSV local)
# ==============================================================================
@st.cache_data
def cargar_datos(ruta_csv):
    """Carga el DataFrame desde CSV local"""
    df = pd.read_csv(ruta_csv, encoding='utf-8', low_memory=False)
    return df

# ==============================================================================
# PREPARACIÓN DEL UNIVERSO MESSI
# ==============================================================================
def preparar_universo_messi(df_mundial):
    """Filtra a Messi y extrae coordenadas"""
    
    # 1. Filtrar a Messi
    filtro_messi = df_mundial['player'].str.contains('Messi', na=False)
    df_messi = df_mundial[filtro_messi].copy()
    
    # 2. Extraer coordenadas X, Y (con ast.literal_eval para strings)
    df_messi['x'] = df_messi['location'].apply(
        lambda loc: ast.literal_eval(loc)[0] if isinstance(loc, str) and loc != 'nan' else (loc[0] if isinstance(loc, list) else None)
    )
    df_messi['y'] = df_messi['location'].apply(
        lambda loc: ast.literal_eval(loc)[1] if isinstance(loc, str) and loc != 'nan' else (loc[1] if isinstance(loc, list) else None)
    )
    
    # 3. Limpiar valores nulos
    df_messi_calor = df_messi.dropna(subset=['x', 'y']).copy()
    
    return df_messi, df_messi_calor

# ==============================================================================
# CREACIÓN DE LAS CAJITAS (Goles, Faltas, Pases)
# ==============================================================================
def crear_cajitas(df_messi):
    """Crea los DataFrames filtrados para cada visualización"""
    
    # --- GOLES ---
    goles_messi = df_messi[(df_messi['type'] == 'Shot') & 
                           (df_messi['shot_outcome'] == 'Goal')].copy()
    goles_messi = goles_messi.dropna(subset=['x', 'y'])
    goles_messi['etiqueta'] = goles_messi['shot_type'].apply(
        lambda x: 'P' if x == 'Penalty' else 'G'
    )
    
    # --- FALTAS ---
    faltas_messi = df_messi[df_messi['type'] == 'Foul Won'].copy()
    faltas_messi = faltas_messi.dropna(subset=['x', 'y'])
    faltas_messi['etiqueta'] = 'F'
    
    # --- PASES ---
    pases_messi = df_messi[(df_messi['type'] == 'Pass') & 
                           (df_messi['pass_outcome'].isna())].copy()
    
    # Extraer coordenadas de destino para pases
    pases_messi['end_x'] = pases_messi['pass_end_location'].apply(
        lambda loc: ast.literal_eval(loc)[0] if isinstance(loc, str) and loc != 'nan' else (loc[0] if isinstance(loc, list) else None)
    )
    pases_messi['end_y'] = pases_messi['pass_end_location'].apply(
        lambda loc: ast.literal_eval(loc)[1] if isinstance(loc, str) and loc != 'nan' else (loc[1] if isinstance(loc, list) else None)
    )
    pases_messi = pases_messi.dropna(subset=['x', 'y', 'end_x', 'end_y'])
    pases_messi['etiqueta'] = ''
    
    return goles_messi, faltas_messi, pases_messi

# ==============================================================================
# FUNCIÓN DE DIBUJO (El dashboard 2x2)
# ==============================================================================
def dibujar_dashboard_messi(df_messi_calor, goles_messi, faltas_messi, pases_messi):
    """Crea el dashboard 2x2 con los 4 gráficos"""
    
    # Separar goles por tipo
    goles_jugada = goles_messi[goles_messi['etiqueta'] == 'G']
    goles_penal = goles_messi[goles_messi['etiqueta'] == 'P']
    
    # Crear figura 2x2
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 20))
    fig.patch.set_facecolor('#22312b')
    
    # ======================================================================
    # 1. TOP IZQUIERDA: Mapa de Calor
    # ======================================================================
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    pitch.draw(ax=axs[0, 0])
    pitch.kdeplot(df_messi_calor.x, df_messi_calor.y, ax=axs[0, 0], 
                  fill=True, levels=100, thresh=0, cmap='hot', alpha=0.5)
    axs[0, 0].set_title("🔥 Mapa de Calor", color='white', fontsize=20, pad=10)
    
    # ======================================================================
    # 2. TOP DERECHA: Goles
    # ======================================================================
    pitch.draw(ax=axs[0, 1])
    
    if len(goles_jugada) > 0:
        pitch.scatter(goles_jugada.x, goles_jugada.y, ax=axs[0, 1], 
                      s=300, color='green', edgecolors='white', zorder=2, label='Jugada')
    if len(goles_penal) > 0:
        pitch.scatter(goles_penal.x, goles_penal.y, ax=axs[0, 1], 
                      s=300, color='red', edgecolors='white', zorder=2, label='Penal', marker='*')
    
    for i, row in goles_messi.iterrows():
        pitch.annotate(row.etiqueta, xy=(row.x, row.y), ax=axs[0, 1], 
                       va='center', ha='center', color='white', fontweight='bold', fontsize=12)
    
    axs[0, 1].legend(loc='upper right', facecolor='#22312b', edgecolor='white', labelcolor='white')
    axs[0, 1].set_title("⚽ Goles (G=Jugada, P=Penal)", color='white', fontsize=20, pad=10)
    
    # ======================================================================
    # 3. BOTTOM IZQUIERDA: Faltas
    # ======================================================================
    pitch.draw(ax=axs[1, 0])
    pitch.scatter(faltas_messi.x, faltas_messi.y, ax=axs[1, 0], 
                  s=200, color='yellow', edgecolors='black', zorder=2, alpha=0.8)
    for i, row in faltas_messi.iterrows():
        pitch.annotate('F', xy=(row.x, row.y), ax=axs[1, 0], 
                       va='center', ha='center', color='black', fontweight='bold', fontsize=9)
    axs[1, 0].set_title("🟡 Faltas Recibidas", color='white', fontsize=20, pad=10)
    
    # ======================================================================
    # 4. BOTTOM DERECHA: Pases
    # ======================================================================
    pitch.draw(ax=axs[1, 1])
    if len(pases_messi) > 0:
        pitch.arrows(pases_messi.x, pases_messi.y, 
                     pases_messi.end_x, pases_messi.end_y, 
                     width=2, color='skyblue', alpha=0.3, ax=axs[1, 1], 
                     headwidth=4, headlength=6)
    axs[1, 1].set_title("➡️ Dirección de Pases", color='white', fontsize=20, pad=10)
    
    # Título general
    plt.suptitle("🇦🇷 Lionel Messi - Análisis Mundial Qatar 2022 🏆", 
                 color='white', fontsize=28, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    
    return fig

# ==============================================================================
# ESTADÍSTICAS RESUMEN
# ==============================================================================
def mostrar_estadisticas(goles_messi, faltas_messi, pases_messi, df_messi_calor):
    """Muestra las estadísticas en la sidebar"""
    
    st.sidebar.metric("📍 Puntos de calor", len(df_messi_calor))
    st.sidebar.metric("⚽ Goles", len(goles_messi))
    st.sidebar.metric("🟡 Faltas recibidas", len(faltas_messi))
    st.sidebar.metric("➡️ Pases completados", len(pases_messi))
    
    # Desglose de goles
    goles_jugada = len(goles_messi[goles_messi['etiqueta'] == 'G'])
    goles_penal = len(goles_messi[goles_messi['etiqueta'] == 'P'])
    
    st.sidebar.subheader("📊 Desglose de Goles")
    st.sidebar.write(f"**De jugada:** {goles_jugada}")
    st.sidebar.write(f"**De penal:** {goles_penal}")


#--------------------------------------------------------
# Llamar función creación mapas de dispersión
#---------------------------------------------------------
# ============================================================================
# 1️⃣ PRIMERO: Configurar matplotlib para emojis
# ============================================================================
import matplotlib
import sys

if sys.platform == 'win32':
    matplotlib.rcParams['font.family'] = 'Segoe UI Emoji'
elif sys.platform == 'darwin':
    matplotlib.rcParams['font.family'] = 'Apple Color Emoji'
else:
    matplotlib.rcParams['font.family'] = 'Noto Color Emoji'

# ============================================================================
# 2️⃣ SEGUNDO: Importar librerías
# ============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.size'] = 12

# ============================================================================
# 3️⃣ TERCERO: Paleta de colores
# ============================================================================
colores = {
    'fondo_figura': '#f8f9fa',
    'fondo_grafico': '#ffffff',
    'messi': '#e74c3c',
    'mbappe': '#3498db',
    'alvarez': '#2ecc71',
    'modric': '#2c3e50',
    'lineas': '#34495e',
    'texto': '#2c3e50'
}

# ============================================================================
# 4️⃣ CUARTO: Funciones de los 4 gráficos (EL CEREBRO)
# ============================================================================

def graficar_dispersion_xg_tiros(datos):
    """Gráfico 1: xG Total vs Tiros Totales"""
    col_x = 'tiros_totales'
    col_y = 'xg_total'
    
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(colores['fondo_figura'])
    ax.set_facecolor(colores['fondo_grafico'])
    
    protagonistas = {
        'Lionel Andrés Messi Cuccittini': colores['messi'],
        'Kylian Mbappé Lottin': colores['mbappe'],
        'Julián Álvarez': colores['alvarez'],
        'Luka Modrić': colores['modric']
    }
    
    for jugador, color in protagonistas.items():
        if jugador in datos.index:
            punto = datos.loc[jugador]
            ax.scatter(punto[col_x], punto[col_y], 
                      color=color, s=350, 
                      edgecolors='black', linewidth=3, 
                      zorder=10, marker='*')
            ax.text(punto[col_x], punto[col_y] * 1.08, 
                   f"{jugador.split()[0]}", 
                   color=color, fontweight='bold', fontsize=14, 
                   zorder=11, ha='center',
                   bbox=dict(boxstyle='round,pad=0.4', 
                            facecolor='white', alpha=0.9,
                            edgecolor=color, linewidth=2))
    
    media_x = datos[col_x].mean()
    media_y = datos[col_y].mean()
    ax.axvline(media_x, color=colores['lineas'], linestyle='--', linewidth=2, alpha=0.5)
    ax.axhline(media_y, color=colores['lineas'], linestyle='--', linewidth=2, alpha=0.5)
    
    ax.grid(True, linestyle=':', alpha=0.5, linewidth=1, color='#bdc3c7')
    ax.set_title("🏆 xG Total vs Tiros Totales - Copa Mundial 2022", 
                 fontsize=24, fontweight='bold', pad=30)
    ax.set_xlabel("Cantidad de Tiros Totales", fontsize=16, fontweight='bold')
    ax.set_ylabel("xG Acumulado (Goles Esperados)", fontsize=16, fontweight='bold')
    
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['messi'], 
               markersize=20, label='Messi', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['mbappe'], 
               markersize=20, label='Mbappé', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['alvarez'], 
               markersize=20, label='Álvarez', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['modric'], 
               markersize=20, label='Modrić', markeredgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, fontsize=12)
    plt.tight_layout()
    
    return fig, ax


def graficar_dispersion_intercepciones_faltas(datos):
    """Gráfico 2: Intercepciones vs Faltas Cometidas"""
    col_x = 'faltas'
    col_y = 'intercepciones'
    
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(colores['fondo_figura'])
    ax.set_facecolor(colores['fondo_grafico'])
    
    protagonistas = {
        'Lionel Andrés Messi Cuccittini': colores['messi'],
        'Kylian Mbappé Lottin': colores['mbappe'],
        'Julián Álvarez': colores['alvarez'],
        'Luka Modrić': colores['modric']
    }
    
    for jugador, color in protagonistas.items():
        if jugador in datos.index:
            punto = datos.loc[jugador]
            ax.scatter(punto[col_x], punto[col_y], 
                      color=color, s=350, 
                      edgecolors='black', linewidth=3, 
                      zorder=10, marker='*')
            ax.text(punto[col_x], punto[col_y] * 1.08, 
                   f"{jugador.split()[0]}", 
                   color=color, fontweight='bold', fontsize=14, 
                   zorder=11, ha='center',
                   bbox=dict(boxstyle='round,pad=0.4', 
                            facecolor='white', alpha=0.9,
                            edgecolor=color, linewidth=2))
    
    media_x = datos[col_x].mean()
    media_y = datos[col_y].mean()
    ax.axvline(media_x, color=colores['lineas'], linestyle='--', linewidth=2, alpha=0.5)
    ax.axhline(media_y, color=colores['lineas'], linestyle='--', linewidth=2, alpha=0.5)
    
    ax.grid(True, linestyle=':', alpha=0.5, linewidth=1, color='#bdc3c7')
    ax.set_title("🛡️ Intercepciones vs Faltas Cometidas - Copa Mundial 2022", 
                 fontsize=24, fontweight='bold', pad=30)
    ax.set_xlabel("Faltas Cometidas", fontsize=16, fontweight='bold')
    ax.set_ylabel("Intercepciones", fontsize=16, fontweight='bold')
    
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['messi'], 
               markersize=20, label='Messi', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['mbappe'], 
               markersize=20, label='Mbappé', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['alvarez'], 
               markersize=20, label='Álvarez', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['modric'], 
               markersize=20, label='Modrić', markeredgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, fontsize=12)
    plt.tight_layout()
    
    return fig, ax


def graficar_dispersion_pases_efectividad(datos):
    """Gráfico 3: Pases Completos vs % Efectividad"""
    col_x = 'pases_completos'
    col_y = 'pct_pases'
    
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(colores['fondo_figura'])
    ax.set_facecolor(colores['fondo_grafico'])
    
    protagonistas = {
        'Lionel Andrés Messi Cuccittini': colores['messi'],
        'Kylian Mbappé Lottin': colores['mbappe'],
        'Julián Álvarez': colores['alvarez'],
        'Luka Modrić': colores['modric']
    }
    
    for jugador, color in protagonistas.items():
        if jugador in datos.index:
            punto = datos.loc[jugador]
            ax.scatter(punto[col_x], punto[col_y], 
                      color=color, s=350, 
                      edgecolors='black', linewidth=3, 
                      zorder=10, marker='*')
            ax.text(punto[col_x], punto[col_y] * 1.02, 
                   f"{jugador.split()[0]}", 
                   color=color, fontweight='bold', fontsize=14, 
                   zorder=11, ha='center',
                   bbox=dict(boxstyle='round,pad=0.4', 
                            facecolor='white', alpha=0.9,
                            edgecolor=color, linewidth=2))
    
    media_x = datos[col_x].mean()
    media_y = datos[col_y].mean()
    ax.axvline(media_x, color=colores['lineas'], linestyle='--', linewidth=2, alpha=0.5)
    ax.axhline(media_y, color=colores['lineas'], linestyle='--', linewidth=2, alpha=0.5)
    
    ax.grid(True, linestyle=':', alpha=0.5, linewidth=1, color='#bdc3c7')
    ax.set_title("🎯 Pases Completos vs % Efectividad - Copa Mundial 2022", 
                 fontsize=24, fontweight='bold', pad=30)
    ax.set_xlabel("Pases Completos", fontsize=16, fontweight='bold')
    ax.set_ylabel("Efectividad de Pases (%)", fontsize=16, fontweight='bold')
    
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['messi'], 
               markersize=20, label='Messi', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['mbappe'], 
               markersize=20, label='Mbappé', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['alvarez'], 
               markersize=20, label='Álvarez', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['modric'], 
               markersize=20, label='Modrić', markeredgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, fontsize=12)
    plt.tight_layout()
    
    return fig, ax


def graficar_dispersion_goles_reales_esperados(datos):
    """Gráfico 4: Goles Reales vs Goles Esperados (xG)"""
    col_x = 'xg_total'
    col_y = 'goles'
    
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(colores['fondo_figura'])
    ax.set_facecolor(colores['fondo_grafico'])
    
    protagonistas = {
        'Lionel Andrés Messi Cuccittini': colores['messi'],
        'Kylian Mbappé Lottin': colores['mbappe'],
        'Julián Álvarez': colores['alvarez'],
        'Luka Modrić': colores['modric']
    }
    
    for jugador, color in protagonistas.items():
        if jugador in datos.index:
            punto = datos.loc[jugador]
            ax.scatter(punto[col_x], punto[col_y], 
                      color=color, s=350, 
                      edgecolors='black', linewidth=3, 
                      zorder=10, marker='*')
            ax.text(punto[col_x], punto[col_y] * 1.08, 
                   f"{jugador.split()[0]}", 
                   color=color, fontweight='bold', fontsize=14, 
                   zorder=11, ha='center',
                   bbox=dict(boxstyle='round,pad=0.4', 
                            facecolor='white', alpha=0.9,
                            edgecolor=color, linewidth=2))
    
    # Línea de referencia (y = x)
    min_val = min(datos[col_x].min(), datos[col_y].min())
    max_val = max(datos[col_x].max(), datos[col_y].max())
    ax.plot([min_val, max_val], [min_val, max_val], 
            color=colores['lineas'], linestyle='-', linewidth=2, alpha=0.7)
    
    media_x = datos[col_x].mean()
    media_y = datos[col_y].mean()
    ax.axvline(media_x, color=colores['lineas'], linestyle='--', linewidth=2, alpha=0.5)
    ax.axhline(media_y, color=colores['lineas'], linestyle='--', linewidth=2, alpha=0.5)
    
    ax.grid(True, linestyle=':', alpha=0.5, linewidth=1, color='#bdc3c7')
    ax.set_title("⚽ Goles Reales vs Goles Esperados (xG) - Copa Mundial 2022", 
                 fontsize=24, fontweight='bold', pad=30)
    ax.set_xlabel("Goles Esperados (xG)", fontsize=16, fontweight='bold')
    ax.set_ylabel("Goles Reales Convertidos", fontsize=16, fontweight='bold')
    
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['messi'], 
               markersize=20, label='Messi', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['mbappe'], 
               markersize=20, label='Mbappé', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['alvarez'], 
               markersize=20, label='Álvarez', markeredgecolor='black'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=colores['modric'], 
               markersize=20, label='Modrić', markeredgecolor='black'),
        Line2D([0], [0], color=colores['lineas'], linewidth=2, label='Rendimiento Esperado')
    ]
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, fontsize=12)
    plt.tight_layout()
    
    return fig, ax


# ============================================================================
# 5️⃣ QUINTO: Preparación de datos (También es parte del cerebro)
# ============================================================================

@st.cache_data
def cargar_y_preparar_datos():
    """Carga datos_mundial.csv (datos YA PROCESADOS)"""
    df_resumen = pd.read_csv('datos_mundial.csv', index_col=0)
    return df_resumen

#                               ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                                                                           //////////////////////////////////////////////////////
#                                                                                                             *****************
#                                                                                                ==========================================
#                                                                                                4.  🧭 MENÚ DE NAVEGACIÓN (BARRA LATERAL)
#                                                                                                ==========================================
# --- Ocultar menú nativo de Streamlit ---

# --- Configuración de la página (Opcional, para que se vea mejor en móvil) ---
st.set_page_config(layout="wide", page_title="Análisis Mundial 2022")

# --- 1. Lógica del Menú (Session State) ---
# Esto recuerda si el usuario abrió el menú o no
if 'menu_abierto' not in st.session_state:
    st.session_state.menu_abierto = False

def toggle_menu():
    st.session_state.menu_abierto = not st.session_state.menu_abierto

# --- 2. CSS Personalizado ---
# Ocultamos elementos nativos molestos y damos estilo a nuestro botón
st.markdown(
    """
    <style>
    /* Ocultar el menú de los 3 puntos nativo de Streamlit */
    #MainMenu {visibility: hidden;}
    
    /* Estilo para nuestro botón de menú personalizado */
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #45a049;
        color: white;
    }
    
    /* Ocultar la sidebar en móviles si queremos forzar el uso del menú central, 
       pero dejaremos la sidebar activa para escritorio */
    @media (max-width: 768px) {
        /* Aquí podrías ocultar la sidebar si prefieres, pero es mejor dejarla como respaldo */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. Botón de Menú Visible (Cabecera) ---
# Creamos una columna para poner el botón arriba a la derecha o centrado
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    # Este botón es muy visible y dice explícitamente "MENÚ"
    if st.button("📂 ABRIR MENÚ DE NAVEGACIÓN", on_click=toggle_menu):
        pass

# --- 4. Lógica de Navegación ---

# Si el usuario está en móvil y pulsó el botón, mostramos el menú en el centro
if st.session_state.menu_abierto:
    st.markdown("### 📌 Selecciona una sección:")
    
    # Usamos un selectbox o radio buttons grandes en el centro para móvil
    opcion = st.radio(
        "Ir a:",
        [
            "1 Obtener información del partido",
            "2 Análisis estadístico del Juego Marruecos vs Portugal",
            "3 Mapas de equipos",
            "4 Análisis individual del jugador",
            "5 Dashboard del Partido",
            "6 Análisis completo del mundial 2022",
        ],
        label_visibility="collapsed"
    )
    
    # Botón para cerrar el menú una vez elegido
    if st.button("Cerrar Menú"):
        st.session_state.menu_abierto = False
        st.rerun()
        
    st.divider() # Línea separadora

else:
    # Si el menú NO está abierto (o estamos en escritorio), usamos la Sidebar tradicional
    with st.sidebar:
        st.title("📌 Menú ")
        opcion = st.radio(
            "Selecciona una sección:",
            [
                "1 Obtener información del partido",
                "2 Análisis estadístico del Juego Marruecos vs Portugal",
                "3 Mapas de equipos",
                "4 Análisis individual del jugador",
                "5 Dashboard del Partido",
                "6 Análisis completo del mundial 2022",
            ]
        )
        
        st.markdown(
            "<div style='background-color:black;color:white; padding:10px; border-radius:8px; text-align:center;'>"
            "📘 <b>Datos statsbom mundial 2022</b><br>"
            "<i style='color: #cccccc;'>por Mauricio Lozano</i>"
            "</div>",
            unsafe_allow_html=True
        )

#------------------------------------------------
# Llamar Función para analizar Inglaterra vs Iran
#------------------------------------------------
def analizar_pases_partido(archivo_csv):
    """
    Función para analizar los pases de un partido de fútbol.
    
    Args:
        archivo_csv (str): Ruta del archivo CSV con los datos del partido
    
    Returns:
        dict: Diccionario con los resultados del análisis de pases
    """
    import pandas as pd
    
    try:
        # Cargar datos
        df = pd.read_csv(archivo_csv)
        
        # Filtrar solo eventos de pase (Pass)
        passes_df = df[df['type'] == 'Pass'].copy()
        
        if len(passes_df) == 0:
            return {
                'success': False,
                'message': 'No se encontraron eventos de pase en los datos'
            }
        
        # Verificar columnas necesarias
        required_columns = ['player', 'team']
        for col in required_columns:
            if col not in passes_df.columns:
                return {
                    'success': False,
                    'message': f'La columna {col} no existe en los datos'
                }
        
        # Calcular pases intentados por jugador
        pases_intentados = passes_df.groupby(['player', 'player_id', 'team']).size().reset_index(name='Pases_Intentados')
        
        # Verificar si hay columna de resultado de pase
        if 'pass_outcome' in passes_df.columns:
            # Pases completados (outcome == 'Complete' o vacío)
            passes_df['pass_outcome'] = passes_df['pass_outcome'].fillna('Complete')
            pases_completados = passes_df[passes_df['pass_outcome'].isin(['Complete', ''])]
            pases_completados = pases_completados.groupby(['player', 'player_id', 'team']).size().reset_index(name='Pases_Completados')
        else:
            # Si no hay columna de outcome, asumimos todos como completados
            pases_completados = pases_intentados.copy()
            pases_completados.columns = ['player', 'player_id', 'team', 'Pases_Completados']
        
        # Merge de intentados y completados
        player_stats = pases_intentados.merge(
            pases_completados, 
            on=['player', 'player_id', 'team'], 
            how='left'
        )
        player_stats['Pases_Completados'] = player_stats['Pases_Completados'].fillna(0).astype(int)
        
        # Calcular precisión de pase
        player_stats['Precision'] = (player_stats['Pases_Completados'] / player_stats['Pases_Intentados'] * 100).round(2)
        
        # Calcular pases fallidos
        player_stats['Pases_Fallidos'] = player_stats['Pases_Intentados'] - player_stats['Pases_Completados']
        
        # Ordenar por pases intentados
        top_intentados = player_stats.sort_values('Pases_Intentados', ascending=False)
        
        # Ordenar por pases completados
        top_completados = player_stats.sort_values('Pases_Completados', ascending=False)
        
        # Ordenar por precisión (mínimo 10 pases intentados)
        top_precision = player_stats[player_stats['Pases_Intentados'] >= 10].sort_values('Precision', ascending=False)
        
        # Estadísticas por equipo
        team_stats = passes_df.groupby('team').size().reset_index(name='Pases_Intentados')
        
        if 'pass_outcome' in passes_df.columns:
            team_completados = passes_df[passes_df['pass_outcome'].isin(['Complete', ''])].groupby('team').size().reset_index(name='Pases_Completados')
            team_stats = team_stats.merge(team_completados, on='team', how='left')
            team_stats['Pases_Completados'] = team_stats['Pases_Completados'].fillna(0).astype(int)
        else:
            team_stats['Pases_Completados'] = team_stats['Pases_Intentados']
        
        team_stats['Precision'] = (team_stats['Pases_Completados'] / team_stats['Pases_Intentados'] * 100).round(2)
        
        # Jugador con más pases intentados
        top_intentado_player = top_intentados.iloc[0]
        
        # Jugador con más pases completados
        top_completado_player = top_completados.iloc[0]
        
        return {
            'success': True,
            'top_intentados': {
                'nombre': top_intentado_player['player'],
                'equipo': top_intentado_player['team'],
                'pases_intentados': int(top_intentado_player['Pases_Intentados']),
                'pases_completados': int(top_intentado_player['Pases_Completados']),
                'precision': top_intentado_player['Precision']
            },
            'top_completados': {
                'nombre': top_completado_player['player'],
                'equipo': top_completado_player['team'],
                'pases_intentados': int(top_completado_player['Pases_Intentados']),
                'pases_completados': int(top_completado_player['Pases_Completados']),
                'precision': top_completado_player['Precision']
            },
            'top_5_intentados': top_intentados.head(5).to_dict('records'),
            'top_5_completados': top_completados.head(5).to_dict('records'),
            'top_5_precision': top_precision.head(5).to_dict('records'),
            'team_stats': team_stats.to_dict(),
            'total_pases': len(passes_df),
            'dataframe_intentados': top_intentados,
            'dataframe_completados': top_completados
        }
        
    except FileNotFoundError:
        return {
            'success': False,
            'message': f'No se encontró el archivo: {archivo_csv}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al procesar los datos: {str(e)}'
        }

#------------------------------------------------------------
# Llamar a Función de Ranking
#------------------------------------------------------------

def cargar_datos_mundial_2022():
    """
    Carga los datos del archivo CSV del Mundial 2022.
    Ajusta la ruta según donde tengas guardado el archivo en tu proyecto.
    """
    try:
        # Opción 1: Si el archivo está en la misma carpeta que tu script
        df = pd.read_csv('ranking_completo_mundial_2022.csv')
        return df
    except FileNotFoundError:
        # Opción 2: Ruta alternativa (ajusta según tu estructura de carpetas)
        df = pd.read_csv('./data/ranking_completo_mundial_2022.csv')
        return df

def generar_rankings_mundial_2022():
    """
    Genera los 4 rankings solicitados:
    1. Más Tiros
    2. Más Recuperaciones
    3. Más Pases Completados
    4. Más Faltas Recibidas
    """
    # Cargar datos
    df = cargar_datos_mundial_2022()
    
    # Crear contenedores para los rankings
    rankings = {}
    
    # Ranking 1: Más Tiros
    ranking_tiros = df.nlargest(15, 'Total_Tiros')[['player', 'team', 'Total_Tiros', 'Partidos_Jugados', 'Tiros_por_Partido']]
    ranking_tiros.columns = ['Jugador', 'Selección', 'Total Tiros', 'Partidos', 'Tiros/Partido']
    rankings['tiros'] = ranking_tiros
    
    # Ranking 2: Más Recuperaciones
    ranking_recuperaciones = df.nlargest(15, 'Recuperaciones')[['player', 'team', 'Recuperaciones', 'Partidos_Jugados', 'Recuperaciones_por_Partido']]
    ranking_recuperaciones.columns = ['Jugador', 'Selección', 'Total Recuperaciones', 'Partidos', 'Recuperaciones/Partido']
    rankings['recuperaciones'] = ranking_recuperaciones
    
    # Ranking 3: Más Pases Completados
    ranking_pases = df.nlargest(15, 'Pases_Completados')[['player', 'team', 'Pases_Completados', 'Partidos_Jugados', 'Pases_por_Partido']]
    ranking_pases.columns = ['Jugador', 'Selección', 'Total Pases', 'Partidos', 'Pases/Partido']
    rankings['pases'] = ranking_pases
    
    # Ranking 4: Más Faltas Recibidas
    ranking_faltas = df.nlargest(15, 'Faltas_Recibidas')[['player', 'team', 'Faltas_Recibidas', 'Partidos_Jugados', 'Faltas_por_Partido']]
    ranking_faltas.columns = ['Jugador', 'Selección', 'Total Faltas', 'Partidos', 'Faltas/Partido']
    rankings['faltas'] = ranking_faltas
    
    return rankings

def mostrar_rankings_mundial_2022():
    """
    Muestra los rankings en la interfaz de Streamlit con formato visual atractivo.
    """
    st.markdown("### 🏆 Rankings Mundial Qatar 2022")
    st.markdown("---")
    
    # Crear pestañas para cada ranking
    tab1, tab2, tab3, tab4 = st.tabs(["⚽ Más Tiros", "🔄 Más Recuperaciones", "📬 Más Pases", "🟨 Más Faltas Recibidas"])
    
    rankings = generar_rankings_mundial_2022()
    
    with tab1:
        st.markdown("#### 👟 Top 15 Jugadores con Más Tiros")
        st.dataframe(rankings['tiros'].style.format({'Total Tiros': '{:.0f}', 'Tiros/Partido': '{:.2f}'}), use_container_width=True)
        
        # Gráfico de barras
        st.markdown("##### 📊 Visualización")
        st.bar_chart(rankings['tiros'].set_index('Jugador')['Total Tiros'].head(10))
    
    with tab2:
        st.markdown("#### 🛡️ Top 15 Jugadores con Más Recuperaciones")
        st.dataframe(rankings['recuperaciones'].style.format({'Total Recuperaciones': '{:.0f}', 'Recuperaciones/Partido': '{:.2f}'}), use_container_width=True)
        
        # Gráfico de barras
        st.markdown("##### 📊 Visualización")
        st.bar_chart(rankings['recuperaciones'].set_index('Jugador')['Total Recuperaciones'].head(10))
    
    with tab3:
        st.markdown("#### 🎯 Top 15 Jugadores con Más Pases Completados")
        st.dataframe(rankings['pases'].style.format({'Total Pases': '{:.0f}', 'Pases/Partido': '{:.2f}'}), use_container_width=True)
        
        # Gráfico de barras
        st.markdown("##### 📊 Visualización")
        st.bar_chart(rankings['pases'].set_index('Jugador')['Total Pases'].head(10))
    
    with tab4:
        st.markdown("#### ⚠️ Top 15 Jugadores con Más Faltas Recibidas")
        st.dataframe(rankings['faltas'].style.format({'Total Faltas': '{:.0f}', 'Faltas/Partido': '{:.2f}'}), use_container_width=True)
        
        # Gráfico de barras
        st.markdown("##### 📊 Visualización")
        st.bar_chart(rankings['faltas'].set_index('Jugador')['Total Faltas'].head(10))
    
    # Información adicional
    st.markdown("---")
    st.info("💡 **Nota:** Los datos corresponden al Mundial de Qatar 2022. Los rankings muestran el Top 15 de cada categoría.")


#--------------------------------------------------
# Llamar función de creación campos de futbol Messi
#--------------------------------------------------
    # ==========================================================================
    # 1. CARGA DE DATOS DESDE CSV (En lugar de StatsBomb API)
    # ==========================================================================
    try:
        # Cargamos el CSV que exportaste desde Kaggle
        df_mundial = pd.read_csv('messi_mundial_2022_completo.csv')
        st.success("✅ Datos cargados correctamente")
        
        # Mostrar información básica
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Eventos", len(df_mundial))
        with col2:
            st.metric("Partidos", df_mundial['match_id'].nunique())
        with col3:
            st.metric("Rivales", df_mundial['rival'].nunique())
            
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'messi_mundial_2022_completo.csv'")
        st.info("💡 Asegúrate de tener el CSV en la misma carpeta que tu app.py")
        st.stop()
        # ==========================================================================
    # 2. PREPARACIÓN DEL UNIVERSO MESSI (Base de todo)
    # ==========================================================================
    st.subheader("📊 Preparación de Datos")
    
    # Filtramos a Messi (usamos str.contains por si hay variaciones en el nombre)
    filtro_messi = df_mundial['player'].str.contains('Messi', na=False)
    df_messi = df_mundial[filtro_messi].copy()
    
    # ==========================================================================
    # 3. EXTRACCIÓN DE COORDENADAS (UNA SOLA VEZ)
    # ==========================================================================
    # IMPORTANTE: Las coordenadas vienen como STRING "[x, y]" en el CSV
    # Necesitamos convertirlas a lista para extraer x e y
    
    def extraer_coordenada(loc_string, indice):
        """
        Función segura para extraer coordenadas del CSV
        loc_string: viene como "[75.2, 45.1]" (string)
        indice: 0 para x, 1 para y
        """
        try:
            if pd.isna(loc_string):
                return None
            # Convertimos string "[x, y]" a lista real
            loc_lista = ast.literal_eval(loc_string)
            return loc_lista[indice] if isinstance(loc_lista, list) else None
        except:
            return None
    
    # Extraemos x e y UNA SOLA VEZ para todo el universo Messi
    df_messi['x'] = df_messi['location'].apply(lambda x: extraer_coordenada(x, 0))
    df_messi['y'] = df_messi['location'].apply(lambda x: extraer_coordenada(x, 1))
    
    # Para pases, también necesitamos el destino
    df_messi['end_x'] = df_messi['pass_end_location'].apply(lambda x: extraer_coordenada(x, 0))
    df_messi['end_y'] = df_messi['pass_end_location'].apply(lambda x: extraer_coordenada(x, 1))
    
    st.info(f"📍 Eventos de Messi con coordenadas: {df_messi['x'].notna().sum()}")
    
    # ==========================================================================
    # 4. CREACIÓN DE LAS CAJITAS (Ya heredan 'x' e 'y')
    # ==========================================================================
    st.subheader("📦 Filtrado de Eventos")
    
    # --- Cajita de Calor (TODOS los eventos con ubicación) ---
    df_messi_calor = df_messi.dropna(subset=['x', 'y'])
    
    # --- Cajita de Goles ---
    goles_messi = df_messi[
        (df_messi['type'] == 'Shot') & 
        (df_messi['shot_outcome'] == 'Goal')
    ].copy()
    goles_messi['etiqueta'] = goles_messi['shot_type'].apply(
        lambda x: '⚽ P' if x == 'Penalty' else '⚽ G'
    )
    
    # --- Cajita de Faltas ---
    faltas_messi = df_messi[df_messi['type'] == 'Foul Won'].copy()
    faltas_messi['etiqueta'] = '🟡 F'
    
    # --- Cajita de Pases Completados ---
    pases_messi = df_messi[
        (df_messi['type'] == 'Pass') & 
        (df_messi['pass_outcome'].isna()) &
        (df_messi['end_x'].notna()) &
        (df_messi['end_y'].notna())
    ].copy()
    
    # --- Cajita de Tiros (todos, no solo goles) ---
    tiros_messi = df_messi[df_messi['type'] == 'Shot'].copy()
    tiros_messi['etiqueta'] = tiros_messi['shot_outcome'].apply(
        lambda x: '🎯 Gol' if x == 'Goal' else '❌ ' + str(x) if pd.notna(x) else '❌'
    )
    
    # Mostrar estadísticas en columnas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Goles", len(goles_messi))
    with col2:
        st.metric("Faltas Recibidas", len(faltas_messi))
    with col3:
        st.metric("Pases Completados", len(pases_messi))
    with col4:
        st.metric("Total Tiros", len(tiros_messi))
    
    # ==========================================================================
    # 5. FUNCIÓN DE DIBUJO (Adaptada para Streamlit)
    # ==========================================================================
    from mplsoccer import VerticalPitch
    import matplotlib.pyplot as plt
    
    def dibujar_cancha_streamlit(datos, titulo, color_base='red', tipo_grafico='puntos'):
        """
        Función para dibujar en Streamlit
        tipo_grafico: 'calor', 'flechas', o 'puntos'
        """
        # Configurar la cancha
        pitch = VerticalPitch(
            pitch_type='statsbomb',
            pitch_color='#22312b',
            line_color='#c7d5cc',
            linewidth=2
        )
        
        # Crear figura con tamaño adecuado para Streamlit
        fig, ax = pitch.draw(figsize=(8, 10))
        
        if tipo_grafico == 'calor':
            # --- MAPA DE CALOR ---
            pitch.kdeplot(
                datos.x, datos.y, 
                ax=ax, 
                fill=True, 
                levels=100,
                thresh=0, 
                cmap='hot', 
                alpha=0.6, 
                zorder=0
            )
            
        elif tipo_grafico == 'flechas':
            # --- PASES (FLECHAS) ---
            pitch.arrows(
                datos.x, datos.y, 
                datos.end_x, datos.end_y,
                width=2.5, 
                color=color_base, 
                alpha=0.5, 
                ax=ax,
                headwidth=8,
                headlength=10
            )
            # Puntos de origen
            pitch.scatter(datos.x, datos.y, ax=ax, s=50, color=color_base, alpha=0.8)
            
        else:
            # --- PUNTOS (Goles/Faltas/Tiros) ---
            pitch.scatter(
                datos.x, datos.y, 
                ax=ax, 
                s=300,
                color=color_base, 
                edgecolors='white', 
                linewidth=2,
                zorder=2,
                alpha=0.8
            )
            
            # Anotaciones si existen etiquetas
            if 'etiqueta' in datos.columns:
                for i, row in datos.iterrows():
                    if pd.notna(row.etiqueta) and row.etiqueta != '':
                        pitch.annotate(
                            row.etiqueta, 
                            xy=(row.x, row.y), 
                            ax=ax,
                            va='center', 
                            ha='center', 
                            color='white',
                            fontsize=10, 
                            fontweight='bold', 
                            zorder=3
                        )
        
        # Título
        ax.set_title(titulo, fontsize=16, color='white', pad=20, fontweight='bold')
        
        return fig





#                               ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                                                                           //////////////////////////////////////////////////////
#                                                                                                             *****************
#                                                                                          =======================================================
#                                                                                          5.🗂️ SECCIONES DEL CÓDIGO (SEGÚN EL MENÚ DE NAVEGACIÓN)
#                                                                                          =======================================================


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#//////////////////////////////////////////////           SECCIÓN 1: OBTENER INFORMACIÓN DEL PARTIDO         /////////////////////////////////////////////
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#                                                                                                                                                       ---------------------------------------------------------
#                                                                                                                                                        SECCIÓN 1: Obtener información del partido
#                                                                                                                                                       ---------------------------------------------------------
if opcion == "1 Obtener información del partido": #Hacemos el link con la  portada del proyecto.
    st.markdown("""<h2 style="text-align:center;">💻1. Exploración de los juegos del mundial 2022 👇👇</h2>""", unsafe_allow_html=True)
    
    st.info(f" **Partidos disponibles:** {len(partidos)}") # Muestra la cantidad total de partidos disponibles en la base de datos
    Columnas_a_mostrar = ['competition','season', 'home_team', 'away_team', 'home_score', 'away_score']
    df_matches = sb.matches(competition_id=43, season_id=106)[Columnas_a_mostrar]
    st.dataframe(df_matches.head(64))# Muestra los primeros partidos de la copa del mundo
#=========================================================================================================================================================
#                                                                                                                                                        ---------------------------------------------------------
#                                                                                                                                                         SECCIÓN 1.1: Escudos
#                                                                                                                                                        ---------------------------------------------------------
    st.markdown("---")
    st.markdown("""<h2 style="text-align:center;">📊1.1 Juego Marruecos vs Portugal</h2>""", unsafe_allow_html=True)
    #Meteré el escudo de Portugal para llamarlo en el dashboard
    Marruecos_Escudo_url = "https://i.pinimg.com/736x/0d/21/bb/0d21bb56591cfc6f248daf74f7c9e071.jpg"
    Portugal_Escudo_url = "https://i.pinimg.com/1200x/2e/d4/06/2ed4060c70ab6fb46213359e4e7e45dd.jpg"

    # 1. Descargamos las imágenes usando la función definida
    try:
        img_marruecos = descargar_imagen_stats(Marruecos_Escudo_url)
        img_portugal = descargar_imagen_stats(Portugal_Escudo_url)
    except Exception as e:
        st.warning(f'⚠️ No se pudieron cargar los escudos: {e}')
        img_marruecos,img_portugal =None, None 
   
    #crear 3 columnas:[espacio,escudo,espacio]
    col_left, col_center, col_right = st.columns([1, 3, 1]) # Ajustamos el ancho para centrar los escudos
    with col_center:
        col_esc1, col_esc2 = st.columns(2)
    with col_esc1:    
        st.image(img_marruecos, caption="Marruecos", width=120) # Mostramos el escudo de Marruecos para verificar que se descargó correctamente
    with col_esc2:
        st.image(img_portugal, caption="Portugal", width=120) # Mostramos el escudo de Portugal para verificar que se descargó correctamente

#==========================================================================================================================================================
#                                                                                                                                                          ----------------------------------------------------------
#                                                                                                                                                           SECCIÓN 1.2: Resultado del partido
#                                                                                                                                                          ----------------------------------------------------------

# =====                              ======
# =====       DF Disparos Portugal   ======
# =====                              ======
# 1. Filtrar solo los disparos
    df_shots = events[events['type'] == 'Shot']

    # 2. Filtrar solo los disparos de Portugal
    df_shots_portugal = df_shots[df_shots['team'] == 'Portugal']

#========================================================================================

# =====                                  ======
# =====       DF Disparos Marruecos      ======
# =====                                  ======
    df_shots_marruecos = df_shots[df_shots['team'] == 'Morocco']

#========================================================================================

    # Agregar columnas de coordenadas X e Y
    df_shots['x'] = df_shots['location'].apply(lambda loc: loc[0])
    df_shots['y'] = df_shots['location'].apply(lambda loc: loc[1])

    # Filtrar por equipo Y resultado (forma segura)
    Goles_portugal = df_shots[(df_shots['team'] == 'Portugal') & (
        df_shots['shot_outcome'] == 'Goal')]
    portugal_No_gol = df_shots[(df_shots['team'] == 'Portugal') & (
        df_shots['shot_outcome'] != 'Goal')]

    Goles_marruecos = df_shots[(df_shots['team'] == 'Morocco') & (
        df_shots['shot_outcome'] == 'Goal')]
    marruecos_No_gol = df_shots[(df_shots['team'] == 'Morocco') & (
        df_shots['shot_outcome'] != 'Goal')]



#=====                                       =====
#=====      Estadístico de goles y no goles  =====
#=====                                       =====
    
    st.markdown("---")
    st.markdown("""<h2 style="text-align:center;"><span style="font-size:0.5em;">⚽ 🤌🥅</span>Recuento de acciones Gol y No Gol.</h2>""", unsafe_allow_html=True)

    # Usar SOLO un conjunto de columnas
    col_left, col_center, col_right = st.columns([1, 3, 1])

    with col_center:
        col_esc1, col_esc2 = st.columns(2)
        with col_esc1:
            st.subheader("🇲🇦 Marruecos")
            st.markdown(f"⚽ Goles: **{len(Goles_marruecos)}**")
            st.markdown(f"❌ No goles: **{len(marruecos_No_gol)}**")

        with col_esc2:
            st.subheader("🇵🇹 Portugal")
            st.markdown(f"⚽ Goles: **{len(Goles_portugal)}**")
            st.markdown(f"❌ No goles: **{len(portugal_No_gol)}**")

#                                                                                                                                                           ----------------------------------------------------------
#                                                                                                                                                            SECCIÓN 1.3: Alineaciones
#                                                                                                                                                           ----------------------------------------------------------


    # 1. Filtrar eventos de "Starting XI" POR EQUIPO (más seguro que iloc[0])
    alineaciones = events[events['type'] == 'Starting XI']
    
    # === MARRUECOS ===
    alineacion_marruecos = alineaciones[alineaciones['team'] == 'Morocco'].iloc[0]
    formacion_marruecos = alineacion_marruecos['tactics']
    
    # 2. Crear DataFrame desde la lista 'lineup'
    df_marruecos = pd.DataFrame(formacion_marruecos['lineup'])
    
    # 3. Extraer nombres de columnas anidadas (diccionarios)
    df_marruecos['position'] = df_marruecos['position'].apply(
        lambda x: x.get('name') if isinstance(x, dict) else x
    )
    df_marruecos['player'] = df_marruecos['player'].apply(
        lambda x: x.get('name') if isinstance(x, dict) else x
    )
    
    # 4. Mostrar formación y tabla ✅ SIN .to_string()
    st.subheader("🇲🇦 Marruecos") # El MA es el Emoji de Marruecos. 
    st.info(f"Formación: **{formacion_marruecos.get('formation', 'N/A')}**")
    
    # ✅ Opción A: Tabla interactiva (recomendada)
    st.dataframe(
        df_marruecos[['jersey_number', 'position', 'player']].reset_index(drop=True),
        hide_index=True,
        use_container_width=True
    )
#------------------------------------------------------------------------------------
    # === PORTUGAL ===
    Alineacion_Portugal = alineaciones[alineaciones['team']== 'Portugal'].iloc[0]
    formacion_Portugal = Alineacion_Portugal['tactics']

    # 2. Crear Dataframe desde la lista 'lineup'
    df_Portugal = pd.DataFrame(formacion_Portugal['lineup'])

    # 3. Extraer nombres de columnas anidadas ()
    df_Portugal ['position']= df_Portugal['position'].apply(
        lambda x: x.get('name') if isinstance(x,dict) else x
    )
    df_Portugal ['player']= df_Portugal['player'].apply(
        lambda x: x.get('name') if isinstance(x,dict) else x
    )

    # 4. Mostrar formación y tabla SIN .to_string()
    st.subheader("🇵🇹 Portugal") # El PT es el Emoji de Portugal
    st. info(f"Formación: **{formacion_Portugal.get('formation', 'N/A')}**")

    # Opción B: Tabla interactiva 
    st.dataframe(
        df_Portugal[['jersey_number', 'position', 'player']].reset_index(drop=True),
        hide_index=True,
        use_container_width=True
    )

#                                                                                                                                                               -------------------------------------------------------
#                                                                                                                                                               SECCIÓN 1.4 : Posiciones iniciales en el campo.
#                                                                                                                                                               -------------------------------------------------------

    st.markdown("---")
    st.markdown("""<h3 style="text-align:center;">🗺️ Posiciones Iniciales en el Campo</h3>""", unsafe_allow_html=True)
    # Crear el campo de juego
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white',
        stripe=True,
        axis=False,
        label=False, #Quitamos los numeros de los ejes X e Y
    )

    fig, ax = pitch.draw(figsize=(14, 8))

    # Alineación de Marruecos (4-1-4-1) - lado izquierdo
    morocco_players = [
        (50, 40, "En-Nesyri", 19),
        (35, 70, "Boufal", 17), (35, 55, "Ounahi", 8), (35, 25, "Amallah", 15), (35, 10, "Ziyech", 7),
        (30, 40, "Amrabat", 4),
        (20, 10, "Attiat-Allah", 25), (20, 20, "Saïss", 6), (20, 60, "El Yamiq", 18), (20, 70, "Hakimi", 2),
        (5, 40, "Bounou", 1)
    ]

    for x, y, name, number in morocco_players:
        draw_player(x, y, name, number, color='red')

    # Alineación de Portugal (4-3-3) - lado derecho
    portugal_players = [
        (70, 40, "Ramos", 26),
        (70, 55, "João Félix", 11), (90, 40, "Neves", 18), (70, 25, "Bruno F.", 8),
        (90, 55, "Otávio", 25), (90, 25, "Bernardo", 10), 
        (100, 70, "Guerreiro", 5), (100, 60, "Dias", 4), (100, 20, "Pepe", 3), (100, 10, "Dalot", 2),
        (115, 40, "Diogo Costa", 22)
    ]

    for x, y, name, number in portugal_players:
        draw_player(x, y, name, number, color='white')

    # Etiquetas
    plt.text(10, 78, "Morocco (4-1-4-1)", color='white', fontsize=12)
    plt.text(90, 78, "Portugal (4-3-3)", color='white', fontsize=12)

    # Título del gráfico
    ax.set_title("Formaciones iniciales: Marruecos vs Portugal", fontsize=14, color='black', pad=20)

# Opcional: Guardar el gráfico como PNG para descargar
    import io

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)

    st.download_button(
        label="📥 Alineaciones del Juego Marruecos vs Portugal",
        data=buf,
        file_name="alineaciones_marruecos_portugal.png",
        mime="image/png"
    )

    # Mostar el gráfico
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

#----------------------------------------
# Llamar función Dashboard Messi
#----------------------------------------
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#////////////////////////////          SECCIÓN 2: ANÁLISIS ESTADÍSTICO DEL JUEGO MARRUECOS VS PORTUAL MUNDIAL 2022      /////////////////////////////////////////////
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#                                                                                                                                                        ---------------------------------------------------------
#                                                                                                                                                        SECCIÓN 2: Análisis estadístico del Juego Marruecos vs Portugal
#                                                                                                                                                        ---------------------------------------------------------

elif opcion == "2 Análisis estadístico del Juego Marruecos vs Portugal":
    
    st.markdown("""<h2 style="text-align:center;">📊 Estadísticas del Partido</h2>""", unsafe_allow_html=True)
    
    # === OBTENER ESTADÍSTICAS (la función ya está definida arriba) ===
    estadisticas_mar = obtener_estadisticas(events, 'Morocco')
    estadisticas_port = obtener_estadisticas(events, 'Portugal')
    
    # === CREAR TABLA VISUAL ===
    df_stats_visual = pd.DataFrame({
        '🇲🇦 MAR': [
            estadisticas_mar['Goles'], 
            estadisticas_mar['Pases'], 
            estadisticas_mar['Faltas'], 
            estadisticas_mar['Tarjetas Amarillas'], 
            estadisticas_mar['Tarjetas Rojas']
        ],
        'Concepto': ['⚽ Goles', '🔄 Pases', '🩹💊 Faltas', '🟨 T. Amarillas', '🟥 T. Rojas'],
        '🇵🇹 POR': [
            estadisticas_port['Goles'], 
            estadisticas_port['Pases'], 
            estadisticas_port['Faltas'], 
            estadisticas_port['Tarjetas Amarillas'], 
            estadisticas_port['Tarjetas Rojas']
        ]
    })
    
    # === MOSTRAR TABLA ===
    st.markdown("---")
    st.dataframe(df_stats_visual, hide_index=True, use_container_width=True)


#                                                                                                                                                               -------------------------------------------
#                                                                                                                                                               SECCIÓN 2.1 : XG de cada equipo
#                                                                                                                                                               -------------------------------------------
    
    st.markdown("---")
    st.markdown("""<h3 style="text-align:center;">⚽ Expected Goals (xG) por Equipo</h3>""", unsafe_allow_html=True)

# Calcular xG por equipo
    shots = events[events['type'] == 'Shot']
    xg_por_equipo = shots.groupby('team')['shot_statsbomb_xg'].sum()

    # Crear 3 columnas: [espacio] [contenido] [espacio]
    col_izq, col_centro, col_der = st.columns([1, 3, 1])

    with col_centro:
        # Sub-columnas para los dos equipos
        col_marruecos, col_portugal = st.columns(2)
        
        with col_marruecos:
            st.subheader("🇲🇦 Marruecos")
            xg_marruecos = xg_por_equipo.get('Morocco', 0)
            st.metric(label="Expected Goals (xG)", value=f"{xg_marruecos:.2f}")
            st.info(f"Total tiros: {len(shots[shots['team'] == 'Morocco'])}")
        
        with col_portugal:
            st.subheader("🇵🇹 Portugal")
            xg_portugal = xg_por_equipo.get('Portugal', 0)
            st.metric(label="Expected Goals (xG)", value=f"{xg_portugal:.2f}")
            st.info(f"Total tiros: {len(shots[shots['team'] == 'Portugal'])}")
        
        # Barra de comparación visual
        st.markdown("### 📊 Comparación Visual")
        
        # Calcular porcentajes para la barra
        total_xg = xg_marruecos + xg_portugal
        if total_xg > 0:
            pct_marruecos = (xg_marruecos / total_xg) * 100
            pct_portugal = (xg_portugal / total_xg) * 100
            
            st.progress(int(pct_marruecos))
            st.caption(f"🇲🇦 Marruecos: {pct_marruecos:.1f}% | 🇵🇹 Portugal: {pct_portugal:.1f}%")
        
        # Tabla completa (mostrar el dataframe también)
        with st.expander("📋 Ver tabla completa de xG"):
            st.dataframe(xg_por_equipo.reset_index(), hide_index=True, use_container_width=True)

#                                                                                                                                                       ----------------------------------------------------------
#                                                                                                                                                        SECCIÓN 2.2: El jugador con más pases
#                                                                                                                                                       ----------------------------------------------------------
    # 1. Procesamiento de datos (pandas)
    player_pass= events[events['type']=='Pass']
    player_count_passes = player_pass.groupby(['team','player']).size().reset_index(name='num_passes')
    player_count_passes = player_count_passes.sort_values(by='num_passes', ascending=False)
  
    # 2.vamos a obtener el nombre del jugador y el número de pases
    top_player_passes =player_count_passes.iloc[0]['player']
    num_passes = int(player_count_passes.iloc[0]['num_passes']) #Aqui obtenemos el número de pases del jugador con más pases (numeros enteros)
    
    # 3. Descarga de la imagen del jugador con más pases (PEPE)
    top_player_passes = player_count_passes.iloc[0]['player']
    pepe_url = "https://i.pinimg.com/1200x/19/a9/ce/19a9ce95e66e004bbedcd66df7632f82.jpg"
    img_pepe = descargar_imagen_stats(pepe_url.strip())

#                                                                                                                                                           ----------------------------------------------------------
#                                                                                                                                                           SECCIÓN 2.2: El jugador con más pases
#                                                                                                                                                           ----------------------------------------------------------

    # 1. Filtrar y procesar datos (una sola vez, sin redundancia)
    recovery_events = events[events['type'] == 'Ball Recovery']

    # 2. Agrupar por jugador y equipo, luego contar
    recoveries_by_player = recovery_events.groupby(['team', 'player']).size().reset_index(name='recoveries')

    # 3. Ordenar de mayor a menor
    top_recoverers = recoveries_by_player.sort_values('recoveries', ascending=False)

    # 4. Obtener datos del top jugador
    top_player_recovery = top_recoverers.iloc[0]['player']
    num_recoveries = int(top_recoverers.iloc[0]['recoveries'])

    # 5. Descarga de la imagen (URL corregida sin espacios)
    Bruno_url = "https://i.pinimg.com/1200x/c3/87/f5/c387f5bd3e507cb046f29d6789911c14.jpg"
    img_bruno = descargar_imagen_stats(Bruno_url.strip())  # ¡Faltaba llamar a la función!

#                                                                                       ----------------------------------------------------------
#                                                                                                   VAMOS A CREAR LOS TABS DE NAVEGACIÓN
#                                                                                       ----------------------------------------------------------

    # 2. CREAR TABS DE NAVEGACIÓN ✨
    st.subheader("📊 Estadísticas Destacadas del Partido")

    tab1, tab2 = st.tabs(["🏆 Más Pases", "🛡️ Más Recuperaciones"])

    # TAB 1: Jugador con más pases
    with tab1:
        st.markdown(f"### {top_player_passes}")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(img_pepe, caption=f"{top_player_passes}", width="stretch")
            st.metric(label="Total de pases completados", value=num_passes, delta="Líder de pases")
            st.caption("Datos del juego: Marruecos vs Portugal")

    # TAB 2: Jugador con más recuperaciones
    with tab2:
        st.markdown(f"### {top_player_recovery}")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(img_bruno, caption=f"{top_player_recovery}", width="stretch")
            st.metric(label="Total de recuperaciones", value=num_recoveries, delta="Líder de recuperaciones")
            st.caption("Datos del juego: Marruecos vs Portugal")

#                                                                                                                                           ----------------------------------------------------------
#                                                                                                                                           SECCIÓN 2.4: La zona de la cancha (en tercios) con más toques o acciones
#                                                                                                                                           ----------------------------------------------------------

    st.subheader("📍 Distribución de Acciones por Tercios del Campo")

    # Generar y mostrar gráfico (caché automático)
    fig_tercios = generar_grafico_tercios(events)
    st.pyplot(fig_tercios, use_container_width=True)
    plt.close(fig_tercios)  # Liberar memoria

    # Leyenda explicativa
    with st.expander("📖 ¿Cómo interpretar este gráfico?"):
        st.markdown("""
        - 🔴 **Tonos más oscuros** = Más acciones en ese tercio
        - 📊 **Números en cada zona** = Cantidad total de eventos
        - 🎯 **Objetivo**: Identificar dónde se concentra el juego del equipo
        """)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#//////////////////////////////////////////////           SECCIÓN 3: MAPAS DE EQUIPOS                 ////////////////////////////////////////////////////
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#                                                                                                                                                       ---------------------------------------------------------
#                                                                                                                                                       SECCIÓN 3: Mapas de disparos de ambos equipos
#                                                                                                                                                       ---------------------------------------------------------

elif opcion == "3 Mapas de equipos":


    st.subheader("⚽ Mapa de Disparos del Partido")

    # 🔄 1. FILTRAR SOLO LOS DISPAROS
    df_shots = events[events['type'] == 'Shot'].copy()

    # Verificación de datos
    if len(df_shots) == 0:
        st.error("❌ No se encontraron disparos en los datos.")
        st.stop()
    else:
        st.success(f"✅ {len(df_shots)} disparos encontrados")

    # 🔄 2. AGREGAR COLUMNAS DE COORDENADAS X e Y
    if 'x' not in df_shots.columns:
        df_shots['x'] = df_shots['location'].apply(lambda loc: loc[0] if isinstance(loc, (list, tuple)) else None)
    if 'y' not in df_shots.columns:
        df_shots['y'] = df_shots['location'].apply(lambda loc: loc[1] if isinstance(loc, (list, tuple)) else None)

    # 🔄 3. FILTRAR POR EQUIPO Y RESULTADO
    Goles_portugal = df_shots[(df_shots['team'] == 'Portugal') & (df_shots['shot_outcome'] == 'Goal')]
    portugal_No_gol = df_shots[(df_shots['team'] == 'Portugal') & (df_shots['shot_outcome'] != 'Goal')]

    Goles_marruecos = df_shots[(df_shots['team'] == 'Morocco') & (df_shots['shot_outcome'] == 'Goal')]
    marruecos_No_gol = df_shots[(df_shots['team'] == 'Morocco') & (df_shots['shot_outcome'] != 'Goal')]

    # 📊 4. MOSTRAR RESUMEN DE DATOS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🇵🇹 Portugal Goles", len(Goles_portugal))
    with col2:
        st.metric("🇵🇹 Portugal Tiros", len(portugal_No_gol))
    with col3:
        st.metric("🇲🇦 Marruecos Goles", len(Goles_marruecos))
    with col4:
        st.metric("🇲🇦 Marruecos Tiros", len(marruecos_No_gol))

    st.divider()

    # 🎛️ 5. CONTROLES OPCIONALES (Sidebar)
    st.sidebar.header("🎛️ Opciones del Mapa")
    mostrar_nombres = st.sidebar.checkbox("Mostrar nombres de jugadores", value=True)
    tamaño_puntos = st.sidebar.slider("Tamaño de puntos", min_value=50, max_value=3000, value=1500)

    # 🧠 6. LLAMAR A LA FUNCIÓN CACHÉ
    fig_disparos = generar_mapa_disparos(portugal_No_gol, marruecos_No_gol, Goles_marruecos)

    # 🖼️ 7. MOSTRAR EN STREAMLIT
    st.pyplot(fig_disparos, use_container_width=True, bbox_inches='tight')

    # 🧹 8. LIMPIAR MEMORIA (¡IMPORTANTE!)
    plt.close(fig_disparos)

    # 📖 9. LEYENDA EXPLICATIVA
    with st.expander("📖 ¿Cómo interpretar este mapa?"):
        st.markdown("""
        - 🔴 **Círculos rojos** = Disparos de Portugal (tamaño = xG)
        - 🟢 **Círculos verdes** = Disparos de Marruecos sin gol
        - ⚽ **Icono fútbol** = Goles de Marruecos
        - 📏 **Tamaño del círculo** = Probabilidad de gol (xG)
        - 🏃 **Nombres** = Jugador que ejecutó el disparo
        """)

#                                                                                                                                        -----------------------------------------------------------------------------
#                                                                                                                                           SECCIÓN 3.1: Redes de pases de ambos equipos
#                                                                                                                                        -----------------------------------------------------------------------------

    st.subheader("🔗 Redes de Pases por Equipo")

    # 🎛️ CONTROLES EN SIDEBAR - ¡CON KEYS ÚNICAS! ✨
    st.sidebar.header("🎛️ Opciones de Visualización")

    # 🔑 IMPORTANTE: Agregamos 'key' único SOLO a widgets interactivos
    equipo_seleccionado = st.sidebar.radio(
        "Selecciona equipo:", 
        ["Marruecos", "Portugal", "Ambos"],
        key="radio_equipo_red_pases"  # ← Key única
    )

    mostrar_nombres = st.sidebar.checkbox(
        "Mostrar nombres de jugadores", 
        value=True,
        key="checkbox_nombres_red_pases"  # ← Key única
    )

    mostrar_estadisticas = st.sidebar.checkbox(
        "Mostrar estadísticas", 
        value=True,
        key="checkbox_stats_red_pases"  # ← Key única
    )

    # 🔄 1. OBTENER MINUTOS DE PRIMER CAMBIO (para filtrar pases)
    # ⚠️ StatsBomb usa nombres en inglés: 'Morocco' y 'Portugal'
    primer_cambio_marruecos = events[
        (events['type'] == 'Substitution') & (events['team'] == 'Morocco')
    ]['minute'].min() if len(events[(events['type'] == 'Substitution') & (events['team'] == 'Morocco')]) > 0 else 90

    primer_cambio_portugal = events[
        (events['type'] == 'Substitution') & (events['team'] == 'Portugal')
    ]['minute'].min() if len(events[(events['type'] == 'Substitution') & (events['team'] == 'Portugal')]) > 0 else 90

    st.info(f"🔄 Primer cambio Marruecos: min {primer_cambio_marruecos} | Portugal: min {primer_cambio_portugal}")

    # 🔍 PANEL DE DIAGNÓSTICO (opcional: comenta si no lo necesitas)
    with st.expander("🔍 Ver diagnóstico de datos"):
        st.write(f"**Marruecos**: Pases filtrados antes del min {primer_cambio_portugal}")
        st.write(f"   → Jugadores únicos: {len(pos_marruecos) if 'pos_marruecos' in locals() else 'N/A'}")
        st.write(f"**Portugal**: Pases filtrados antes del min {primer_cambio_marruecos}")
        st.write(f"   → Jugadores únicos: {len(pos_portugal) if 'pos_portugal' in locals() else 'N/A'}")
        st.caption("💡 Los números pueden diferir porque cada equipo se filtra con el minuto de cambio del RIVAL")

    # 🔄 2. PREPARAR DATOS PARA CADA EQUIPO
    # ⚠️ Lógica clave: cada equipo se filtra con el minuto de cambio del OPONENTE
    with st.spinner("⏳ Preparando datos de pases..."):
        # Marruecos: sus pases completados ANTES del primer cambio de Portugal (rival)
        _, pos_marruecos, conn_marruecos = preparar_datos_pases(
            events, equipo='Morocco', minuto_corte_oponente=primer_cambio_portugal
        )
        
        # Portugal: sus pases completados ANTES del primer cambio de Marruecos (rival)  
        _, pos_portugal, conn_portugal = preparar_datos_pases(
            events, equipo='Portugal', minuto_corte_oponente=primer_cambio_marruecos
        )

    # 📊 3. MOSTRAR ESTADÍSTICAS (si se selecciona)
    if mostrar_estadisticas:
        col1, col2 = st.columns(2)
        with col1:
           st.metric(" Marruecos - Conexiones", len(conn_marruecos))
        with col2:
             st.metric("🇵🇹 Portugal - Conexiones", len(conn_portugal))    
        
        # ✅ st.expander SIN key (compatible con tu versión)
        with st.expander("📋 Ver tabla de conexiones"):
            if equipo_seleccionado == "Marruecos":
                st.dataframe(conn_marruecos.head(10))
            elif equipo_seleccionado == "Portugal":
                st.dataframe(conn_portugal.head(10))
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("🇲🇦 Marruecos")
                    st.dataframe(conn_marruecos.head(5))
                with col_b:
                    st.write("🇵🇹 Portugal")
                    st.dataframe(conn_portugal.head(5))

    st.divider()

    # 🖼️ 4. MOSTRAR GRÁFICOS SEGÚN SELECCIÓN
    if equipo_seleccionado == "Marruecos" or equipo_seleccionado == "Ambos":
        st.markdown("### 🇲🇦 Red de Pases - Marruecos")
        
        # Configurar colores para Marruecos
        fig_marruecos = generar_red_pases(
            datos=conn_marruecos,
            color_nodo="red",
            color_borde="green", 
            color_flecha="yellow",
            color_borde_flecha="darkgreen",
            nombre_equipo="Marruecos"
        )
        # ✅ st.pyplot SIN key (evita error con matplotlib)
        st.pyplot(fig_marruecos, use_container_width=True, bbox_inches='tight')
        plt.close(fig_marruecos)  # 🧹 Limpiar memoria
        
        if equipo_seleccionado == "Marruecos":
            st.stop()  # No continuar si solo se seleccionó Marruecos

    if equipo_seleccionado == "Portugal" or equipo_seleccionado == "Ambos":
        st.markdown("### 🇵🇹 Red de Pases - Portugal")
        
        # Configurar colores para Portugal
        fig_portugal = generar_red_pases(
            datos=conn_portugal,
            color_nodo="white",
            color_borde="red",
            color_flecha="lightblue", 
            color_borde_flecha="black",
            nombre_equipo="Portugal"
        )
        # ✅ st.pyplot SIN key
        st.pyplot(fig_portugal, use_container_width=True, bbox_inches='tight')
        plt.close(fig_portugal)  # 🧹 Limpiar memoria

    # 📖 5. LEYENDA EXPLICATIVA
    with st.expander("📖 ¿Cómo interpretar esta red de pases?"):
        st.markdown("""
        - 🔵⚪ **Círculos** = Jugadores (tamaño = cantidad de pases realizados)
        - ➡️ **Flechas** = Dirección de los pases entre jugadores
        - 📏 **Grosor de flecha** = Frecuencia de la conexión entre dos jugadores
        - 🏷️ **Nombres** = Primer nombre del jugador que realiza el pase
        - 🎯 **Posición** = Ubicación promedio desde donde el jugador inició sus pases
        - ⏱️ **Filtro temporal** = Solo pases ANTES del primer cambio del equipo rival
        """)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#//////////////////////////////////////////////           SECCIÓN 4: ANÁLISIS INDIVIDUAL DEL JUGADOR      /////////////////////////////////////////////
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                                                                                                                                           ------------------------------------------------------
#                                                                                                                                                               SECCIÓN 4: Mapa de calor del jugador
#                                                                                                                                                           ------------------------------------------------------
elif opcion == "4 Análisis individual del jugador":

    st.subheader("🔥 Mapa de Calor - Kléper Laveran Lima Ferreira (Pepe)")

    # 🎛️ Controles opcionales en sidebar
    st.sidebar.header("🎨 Personalizar Mapa de Calor")
    color_seleccionado = st.sidebar.selectbox(
        "Esquema de colores:",
        ['Reds', 'Blues', 'Greens', 'Purples', 'Oranges', 'viridis'],
        index=0,
        key="select_color_pepe"
    )
    mostrar_leyenda = st.sidebar.checkbox("Mostrar leyenda", value=True, key="chk_leyenda_pepe")

    # 🔄 Generar y mostrar el mapa de calor
    with st.spinner("⏳ Generando mapa de calor..."):
        fig_pepe = generar_mapa_calor_jugador(
            events=events,
            nombre_jugador_statsbomb='Kléper Laveran Lima Ferreira',  # ← Nombre exacto de StatsBomb
            titulo_personalizado='Pepe',                               # ← Título visible en la app
            color_mapa=color_seleccionado
        )

    # 🖼️ Mostrar en Streamlit
    st.pyplot(fig_pepe, use_container_width=True, bbox_inches='tight')

    # 🧹 Limpiar memoria
    plt.close(fig_pepe)

    # 📊 Estadísticas rápidas del jugador
    pepe_events = events[events['player'] == 'Kléper Laveran Lima Ferreira']
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📍 Eventos totales", len(pepe_events))
    with col2:
        st.metric("⚽ Tipo principal", pepe_events['type'].mode()[0] if len(pepe_events) > 0 else "N/A")

    # 📖 Leyenda explicativa
    with st.expander("📖 ¿Cómo interpretar este mapa de calor?"):
        st.markdown("""
        - 🔴 **Zonas más intensas** = Donde Pepe pasó más tiempo durante el partido
        - 📏 **Difusión del color** = Área de influencia del jugador
        - 🎯 **Enfoque defensivo** = Como central, se espera mayor concentración en zona defensiva
        - 🔄 **Movilidad** = Zonas claras indican desplazamientos tácticos específicos
        """)
#                                                                                                                                               ----------------------------------------------------------------
#                                                                                                                                                   SECCIÓN 4.1: MAPA DE DISPAROS DEL JUGADOR
#                                                                                                                                               ----------------------------------------------------------------

    st.subheader("⚽ Mapa de Disparos - Kléper Laveran Lima Ferreira (Pepe)")

    # 🎛️ Controles opcionales en sidebar
    st.sidebar.header("🎨 Personalizar Mapa de Disparos")
    tamaño_puntos = st.sidebar.slider(
        "Tamaño de puntos", 
        min_value=500, max_value=5000, value=2500,
        key="slider_tamano_disparos_pepe"
    )
    mostrar_nombres = st.sidebar.checkbox(
        "Mostrar nombres", 
        value=True,
        key="checkbox_nombres_disparos_pepe"
    )

    # 🔄 Preparar datos (asegurar que df_shots existe)
    if 'df_shots' not in locals():
        df_shots = events[events['type'] == 'Shot'].copy()

    # 🔄 Generar y mostrar el mapa de disparos
    with st.spinner("⏳ Generando mapa de disparos..."):
        fig_disparos_pepe = generar_mapa_disparos_jugador(
            df_shots=df_shots,
            nombre_jugador_statsbomb='Kléper Laveran Lima Ferreira',  # ← Nombre exacto de StatsBomb
            titulo_personalizado='Pepe'                                # ← Título visible en la app
        )

    # 🖼️ Mostrar en Streamlit
    st.pyplot(fig_disparos_pepe, use_container_width=True, bbox_inches='tight')

    # 🧹 Limpiar memoria
    plt.close(fig_disparos_pepe)

    # 📊 Estadísticas rápidas del jugador
    shots_Pepe = df_shots[df_shots['player'] == 'Kléper Laveran Lima Ferreira']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⚽ Total de disparos", len(shots_Pepe))
    with col2:
        st.metric("🎯 xG total", round(shots_Pepe['shot_statsbomb_xg'].sum(), 3) if 'shot_statsbomb_xg' in shots_Pepe.columns else "N/A")
    with col3:
        st.metric("📍 xG promedio", round(shots_Pepe['shot_statsbomb_xg'].mean(), 3) if 'shot_statsbomb_xg' in shots_Pepe.columns and len(shots_Pepe) > 0 else "N/A")

    # 📖 Leyenda explicativa
    with st.expander("📖 ¿Cómo interpretar este mapa de disparos?"):
        st.markdown("""
        - ⚪ **Círculos blancos** = Ubicación de cada disparo
        - 📏 **Tamaño del círculo** = Probabilidad de gol (xG) - más grande = más peligroso
        - 🏷️ **Nombres** = Jugador que ejecutó el disparo
        - 🎯 **Zonas cercanas al arco** = Disparos de mayor peligro
        - 🔴 **Borde rojo** = Para destacar los disparos de Pepe
        """)

#                                                                                                                                    ----------------------------------------------------------------
#                                                                                                                                    SECCIÓN 4.2: MAPA DE ACCIONES (RECUPERACIONES, PASES, FALTAS, INTERCEPCIONES)
#                                                                                                                                    ---------------------------------------------------------------

    st.subheader("📊 Dashboard Multi-Panel - Kléper Laveran Lima Ferreira (Pepe)")

    # 🎛️ CONTROLES EN SIDEBAR
    st.sidebar.header("🎛️ Opciones del Dashboard")

    # Verificar nombre exacto del jugador
    NOMBRE_PEPE_STATS = 'Kléper Laveran Lima Ferreira'  # ← Con acento en 'é'

    # 🔍 Verificar si el nombre existe en los datos
    if NOMBRE_PEPE_STATS not in events['player'].values:
        # Intentar búsqueda alternativa
        candidatos = events[events['player'].str.contains('Pepe|Kleper|Laveran', case=False, na=False)]['player'].unique()
        if len(candidatos) > 0:
            st.warning(f"⚠️ Nombre exacto no encontrado. Posibles alternativas: {list(candidatos[:5])}")
            NOMBRE_PEPE_STATS = st.selectbox("Selecciona el nombre correcto:", candidatos, key="select_pepe_nombre")
        else:
            st.error("❌ No se encontró ningún jugador similar a Pepe en los datos")
            st.stop()

    # Controles adicionales
    mostrar_resumen = st.sidebar.checkbox("Mostrar resumen numérico", value=True, key="chk_resumen_pepe_panel")
    tamaño_figura = st.sidebar.slider("Tamaño de figura", min_value=10, max_value=20, value=16, key="slider_tamano_pepe")

    # 🔄 GENERAR Y MOSTRAR EL DASHBOARD
    with st.spinner("⏳ Generando dashboard multi-panel..."):
        fig_eventos_pepe = generar_mapa_eventos_pepe(events, NOMBRE_PEPE_STATS)

    # 🖼️ Mostrar en Streamlit
    st.pyplot(fig_eventos_pepe, use_container_width=True, bbox_inches='tight')

    # 🧹 Limpiar memoria
    plt.close(fig_eventos_pepe)

    # 📊 RESUMEN NUMÉRICO (opcional)
    if mostrar_resumen:
        st.markdown("### 📈 Resumen Numérico de Acciones")
        
        events_pepe = events[events['player'] == NOMBRE_PEPE_STATS]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🛡️ Recuperaciones", len(events_pepe[events_pepe['type']=='Ball Recovery']))
        with col2:
            st.metric("🔵 Pases", len(events_pepe[events_pepe['type']=='Pass']))
        with col3:
            st.metric("❌ Faltas", len(events_pepe[events_pepe['type']=='Foul Committed']))
        with col4:
            st.metric("🎯 Intercepciones", len(events_pepe[events_pepe['type']=='Interception']))
        
        st.divider()

    # 📋 TABLA DETALLADA
    with st.expander("📋 Ver tabla detallada de eventos"):
        st.write(f"**Total de eventos de Pepe**: {len(events_pepe)}")
        
        # Selector de tipo de evento
        tipo_filtro = st.selectbox(
            "Filtrar por tipo:",
            ["Todos"] + list(events_pepe['type'].unique()),
            key="select_tipo_pepe_panel"
        )
        
        if tipo_filtro == "Todos":
            st.dataframe(events_pepe[['minute', 'type', 'team', 'location']].head(50))
        else:
            filtro = events_pepe[events_pepe['type'] == tipo_filtro]
            st.dataframe(filtro[['minute', 'type', 'team', 'location']].head(50))
            st.write(f"Mostrando {len(filtro)} eventos de tipo '{tipo_filtro}'")

    # 📖 LEYENDA EXPLICATIVA
    with st.expander("📖 ¿Cómo interpretar este dashboard?"):
        st.markdown("""
        ### 🛡️ Panel 1: Recuperaciones
        - ⚪ **Círculos blancos** = Ubicación donde recuperó el balón
        - 🟢 **Borde verde** = Acción defensiva exitosa
        
        ### 🔵 Panel 2: Pases
        - ➡️ **Flechas** = Dirección de cada pase realizado
        - 🔵 **Color** = Pases de Pepe
        
        ### ❌ Panel 3: Faltas Cometidas
        - ⭕ **Círculo rojo** = Ubicación de la falta
        - ❌ **X roja** = Indica infracción
        
        ### 🎯 Panel 4: Intercepciones
        - 🔺 **Triángulo naranja** = Ubicación donde interceptó el balón
        - ⚪ **Borde blanco** = Para destacar sobre el césped
        
        ### 📊 Datos del Partido
        - Portugal vs Marruecos
        - Octavos de final - Mundial 2022
        - Todos los eventos son exclusivos de Pepe
        """)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#============================================================== SECCIÓN 5: DASHBOARD DEL PARTIDO  ====================================================================
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# ----------------------------------------------------------------------------
# 🔄 PREPARACIÓN DE DATOS - DEBE IR ANTES DEL DASHBOARD
# ----------------------------------------------------------------------------

elif opcion == "5 Dashboard del Partido":
                                                            
    st.title("⚽ Dashboard Portugal vs Marruecos - Mundial 2022")

    # Verificar que 'events' existe
    if 'events' not in locals():
        st.error("❌ La variable 'events' no está definida. Carga los datos de StatsBomb primero.")
        st.stop()

    # --- 1. ESCUDOS DE AMBOS EQUIPOS ---
    Marruecos_Escudo_url = "https://i.pinimg.com/736x/0d/21/bb/0d21bb56591cfc6f248daf74f7c9e071.jpg"
    Portugal_Escudo_url = "https://i.pinimg.com/1200x/2e/d4/06/2ed4060c70ab6fb46213359e4e7e45dd.jpg"

    img_marruecos = descargar_imagen_stats(Marruecos_Escudo_url)
    img_portugal = descargar_imagen_stats(Portugal_Escudo_url)

    # --- 2. FICHA DEL PARTIDO ---
    partidos = sb.matches(competition_id=43, season_id=106)
    marruecos_portugal = partidos[
        ((partidos['home_team'] == 'Morocco') & (partidos['away_team'] == 'Portugal')) |
        ((partidos['home_team'] == 'Portugal') & (partidos['away_team'] == 'Morocco'))
    ].copy()

    marruecos_portugal.rename(columns={
        'home_team': 'Local',
        'away_team': 'Visitante',
        'home_score': 'Goles_Local',
        'away_score': 'Goles_Visitante'
    }, inplace=True)

    traducciones = {'Morocco': 'Marruecos', 'Portugal': 'Portugal'}
    marruecos_portugal['Local'] = marruecos_portugal['Local'].replace(traducciones)
    marruecos_portugal['Visitante'] = marruecos_portugal['Visitante'].replace(traducciones)

    fila = marruecos_portugal.iloc[0]
    ficha = f"""
    {fila['Local']}      vs      {fila['Visitante']}
    ----------              ----------
    {fila['Goles_Local']} Goles                {fila['Goles_Visitante']} Goles
    """

    # --- 3. ALINEACIONES ---
    alineaciones = events[events['type'] == 'Starting XI']
    formacion_dict_marruecos = alineaciones.iloc[0]['tactics']
    df_marruecos = pd.DataFrame(formacion_dict_marruecos['lineup'])
    df_marruecos['position'] = df_marruecos['position'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)
    df_marruecos['player'] = df_marruecos['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)

    formacion_dict_portugal = alineaciones.iloc[1]['tactics']
    df_portugal = pd.DataFrame(formacion_dict_portugal['lineup'])
    df_portugal['position'] = df_portugal['position'].apply(lambda x: x['name'] if isinstance(x, dict) else x)
    df_portugal['player'] = df_portugal['player'].apply(lambda x: x['name'] if isinstance(x, dict) else x)

    # --- 4. ESTADÍSTICAS DEL JUEGO ---
    nombre_mar = "Morocco"
    nombre_port = "Portugal"

    def obtener_estadisticas(eventos, equipo_nombre):
        estadisticas = {}
        df_equipo = eventos[eventos['team'] == equipo_nombre]
        tiros = df_equipo[df_equipo['type'] == 'Shot']
        estadisticas['Goles'] = len(tiros[tiros['shot_outcome'] == 'Goal'])
        estadisticas['Pases'] = len(df_equipo[df_equipo['type'] == 'Pass'])
        estadisticas['Faltas'] = len(df_equipo[df_equipo['type'] == 'Foul Committed'])
        col_tarjeta = 'foul_committed_card' if 'foul_committed_card' in df_equipo.columns else 'foul_committed_card_name'
        if col_tarjeta in df_equipo.columns:
            estadisticas['Tarjetas Amarillas'] = len(df_equipo[df_equipo[col_tarjeta] == 'Yellow Card'])
            estadisticas['Tarjetas Rojas'] = len(df_equipo[df_equipo[col_tarjeta].isin(['Red Card', 'Second Yellow'])])
        else:
            estadisticas['Tarjetas Amarillas'] = 0
            estadisticas['Tarjetas Rojas'] = 0
        return estadisticas

    estadisticas_mar = obtener_estadisticas(events, nombre_mar)
    estadisticas_port = obtener_estadisticas(events, nombre_port)

    df_stats_visual = pd.DataFrame({
        'MAR': [
            estadisticas_mar['Goles'],
            estadisticas_mar['Pases'],
            estadisticas_mar['Faltas'],
            estadisticas_mar['Tarjetas Amarillas'],
            estadisticas_mar['Tarjetas Rojas']
        ],
        'VS': ['GOLES', 'PASES', 'FALTAS', 'T. AMARILLAS', 'T. ROJAS'],
        'POR': [
            estadisticas_port['Goles'],
            estadisticas_port['Pases'],
            estadisticas_port['Faltas'],
            estadisticas_port['Tarjetas Amarillas'],
            estadisticas_port['Tarjetas Rojas']
        ]
    })

    # --- 5. JUGADOR CON MÁS PASES (PEPE) ---
    player_pass = events[events['type']=='Pass']
    player_count_passes = player_pass.groupby(['team','player']).size().reset_index(name='num_passes')
    player_count_passes = player_count_passes.sort_values(by='num_passes', ascending=False)
    top_player_passes = player_count_passes.iloc[0]['player']
    num_passes = int(player_count_passes.iloc[0]['num_passes'])  # ← ¡ESTO FALTABA!

    pepe_url = "https://i.pinimg.com/1200x/19/a9/ce/19a9ce95e66e004bbedcd66df7632f82.jpg"
    img_pepe = descargar_imagen_stats(pepe_url)

    # --- 6. JUGADOR CON MÁS RECUPERACIONES (BERNARDO) ---
    recovery_events = events[events['type'] == 'Ball Recovery']
    recoveries_by_player = recovery_events.groupby(['team','player']).size().reset_index(name='recoveries')
    top_recoverers = recoveries_by_player.sort_values('recoveries', ascending=False)
    top_player_recovery = top_recoverers.iloc[0]['player']

    Bruno_url = "https://i.pinimg.com/1200x/c3/87/f5/c387f5bd3e507cb046f29d6789911c14.jpg"
    img_Bruno = descargar_imagen_stats(Bruno_url)

    # --- 7. DATOS PARA MAPA DE DISPAROS ---
    df_shots = events[events['type'] == 'Shot'].copy()
    if 'location' in df_shots.columns and 'x' not in df_shots.columns:
        df_shots[['x', 'y']] = pd.DataFrame(df_shots['location'].tolist(), index=df_shots.index)

    portugal_No_gol = df_shots[(df_shots['team']=='Portugal') & (df_shots['shot_outcome']!='Goal')]
    marruecos_No_gol = df_shots[(df_shots['team']=='Morocco') & (df_shots['shot_outcome']!='Goal')]
    Goles_marruecos = df_shots[(df_shots['team']=='Morocco') & (df_shots['shot_outcome']=='Goal')]

    # --- 8. DATOS PARA REDES DE PASES ---
    pases_compl_Portugal = player_pass[(player_pass['team']=='Portugal') & (player_pass['pass_outcome'].isna())]
    pases_compl_Marruecos = player_pass[(player_pass['team']=='Morocco') & (player_pass['pass_outcome'].isna())]

    # Posiciones promedio
    pases_con_loc = pases_compl_Portugal[pases_compl_Portugal['location'].notna()].copy()
    pases_con_loc['x'] = pases_con_loc['location'].apply(lambda loc: loc[0])
    pases_con_loc['y'] = pases_con_loc['location'].apply(lambda loc: loc[1])
    posicion_prom_Portugal = pases_con_loc.groupby('player').agg(
        x_mean=('x', 'mean'), y_mean=('y', 'mean'), pass_count=('x', 'count')
    ).reset_index()
    posicion_prom_Portugal.columns = ['player', 'x', 'y', 'count']

    pases_con_loc = pases_compl_Marruecos[pases_compl_Marruecos['location'].notna()].copy()
    pases_con_loc['x'] = pases_con_loc['location'].apply(lambda loc: loc[0])
    pases_con_loc['y'] = pases_con_loc['location'].apply(lambda loc: loc[1])
    posicion_prom_Marruecos = pases_con_loc.groupby('player').agg(
        x_mean=('x', 'mean'), y_mean=('y', 'mean'), pass_count=('x', 'count')
    ).reset_index()
    posicion_prom_Marruecos.columns = ['player', 'x', 'y', 'count']

    # Conexiones de pases
    conexiones_pases_marruecos = pases_compl_Marruecos.groupby(['player', 'pass_recipient']).size().reset_index(name='pass_count')
    conexiones_pases_portugal = pases_compl_Portugal.groupby(['player', 'pass_recipient']).size().reset_index(name='pass_count')

    # Merge para Marruecos
    conexiones_marruecos = conexiones_pases_marruecos.merge(posicion_prom_Marruecos, on='player')\
        .merge(posicion_prom_Marruecos, left_on='pass_recipient', right_on='player', suffixes=('_passer', '_receiver'))
    conexiones_marruecos["primer_nombre"] = conexiones_marruecos["player_passer"].str.split().str[0]
    conexiones_marruecos['tamaño'] = (conexiones_marruecos['count_passer'] / conexiones_marruecos['count_passer'].max() * 700)
    conexiones_marruecos['ancho'] = (conexiones_marruecos['pass_count'] / conexiones_marruecos['pass_count'].max() * 15)

    # Merge para Portugal
    conexiones_portugal = conexiones_pases_portugal.merge(posicion_prom_Portugal, on='player')\
        .merge(posicion_prom_Portugal, left_on='pass_recipient', right_on='player', suffixes=('_passer', '_receiver'))
    conexiones_portugal["primer_nombre"] = conexiones_portugal["player_passer"].str.split().str[0]
    conexiones_portugal['tamaño'] = (conexiones_portugal['count_passer'] / conexiones_portugal['count_passer'].max() * 700)
    conexiones_portugal['ancho'] = (conexiones_portugal['pass_count'] / conexiones_portugal['pass_count'].max() * 15)

    st.success("✅ Todos los datos preparados correctamente")
    st.divider()

# =============================================================================
# 💻 DASHBOARD PUNTO 5 - ADAPTADO PARA STREAMLIT
# =============================================================================

    # 🎛️ CONTROLES EN SIDEBAR
    st.sidebar.header("🎛️ Opciones del Dashboard")
    vista_seleccionada = st.sidebar.radio(
        "Selecciona vista:",
        ["📊 Dashboard Completo", "🔗 Red de Pases Marruecos", "🔗 Red de Pases Portugal", "⚽ Mapa de Disparos", "📍 Tercios del Campo"],
        key="radio_vista_dashboard"
    )

    # --- VISTA 1: DASHBOARD COMPLETO ---
    if vista_seleccionada == "📊 Dashboard Completo" or vista_seleccionada == "🔗 Red de Pases Marruecos":
        st.subheader("🔗 Red de Pases - Marruecos")
        if len(conexiones_marruecos) > 0:
            fig_marruecos = generar_red_pases(
                datos=conexiones_marruecos,
                color_nodo="green", color_borde="white",
                color_flecha="lightgreen", color_borde_flecha="darkgreen",
                nombre_equipo="Marruecos"
            )
            st.pyplot(fig_marruecos, use_container_width=True, bbox_inches='tight')
            plt.close(fig_marruecos)
        else:
            st.warning("⚠️ No hay datos de pases para Marruecos")
        
        if vista_seleccionada == "🔗 Red de Pases Marruecos":
            st.stop()

    if vista_seleccionada == "📊 Dashboard Completo" or vista_seleccionada == "🔗 Red de Pases Portugal":
        st.subheader("🔗 Red de Pases - Portugal")
        if len(conexiones_portugal) > 0:
            fig_portugal = generar_red_pases(
                datos=conexiones_portugal,
                color_nodo="white", color_borde="red",
                color_flecha="lightblue", color_borde_flecha="black",
                nombre_equipo="Portugal"
            )
            st.pyplot(fig_portugal, use_container_width=True, bbox_inches='tight')
            plt.close(fig_portugal)
        else:
            st.warning("⚠️ No hay datos de pases para Portugal")
        
        if vista_seleccionada == "🔗 Red de Pases Portugal":
            st.stop()

    if vista_seleccionada == "📊 Dashboard Completo" or vista_seleccionada == "⚽ Mapa de Disparos":
        st.subheader("⚽ Mapa de Disparos")
        fig_disparos = generar_mapa_disparos_fig(portugal_No_gol, marruecos_No_gol, Goles_marruecos)
        st.pyplot(fig_disparos, use_container_width=True, bbox_inches='tight')
        plt.close(fig_disparos)
        
        if vista_seleccionada == "⚽ Mapa de Disparos":
            st.stop()

    if vista_seleccionada == "📊 Dashboard Completo" or vista_seleccionada == "📍 Tercios del Campo":
        st.subheader("📍 Acciones por Tercios del Campo")
        fig_tercios = generar_grafico_tercios(events)
        st.pyplot(fig_tercios, use_container_width=True, bbox_inches='tight')
        plt.close(fig_tercios)

    # --- SECCIÓN DE JUGADORES DESTACADOS ---
    st.divider()
    st.subheader("🏆 Jugadores Destacados del Partido")

    col_pepe, col_bruno = st.columns(2)

    with col_pepe:
        st.markdown("### 🛡️ Jugador con Más Pases")
        if img_pepe:
            st.image(img_pepe, caption=f"Top Pases: {top_player_passes}", use_container_width=True)
            st.metric("🔵 Total de pases", num_passes)
            st.write(f"**Jugador:** {top_player_passes}")

    with col_bruno:
        st.markdown("### 🔄 Jugador con Más Recuperaciones")
        if img_Bruno:
            st.image(img_Bruno, caption=f"Top Recuperaciones: {top_player_recovery}", use_container_width=True)
            st.metric("🛡️ Total de recuperaciones", top_recoverers.iloc[0]['recoveries'])
            st.write(f"**Jugador:** {top_player_recovery}")

    # --- ESTADÍSTICAS DEL PARTIDO ---
    st.divider()
    st.subheader("📊 Estadísticas del Partido")
    st.dataframe(df_stats_visual, use_container_width=True, hide_index=True)

    # --- ALINEACIONES ---
    st.divider()
    col_align_m, col_align_p = st.columns(2)

    with col_align_m:
        st.markdown("### 🇲🇦 Alineación Marruecos")
        st.dataframe(df_marruecos[['jersey_number', 'player', 'position']], use_container_width=True, hide_index=True)

    with col_align_p:
        st.markdown("### 🇵🇹 Alineación Portugal")
        st.dataframe(df_portugal[['jersey_number', 'player', 'position']], use_container_width=True, hide_index=True)

    # --- LEYENDA ---
    st.divider()
    with st.expander("📖 ¿Cómo interpretar este dashboard?"):
        st.markdown("""
        ### 🔗 Redes de Pases
        - **Círculos**: Jugadores (tamaño = cantidad de pases)
        - **Flechas**: Dirección y frecuencia de conexiones
        
        ### ⚽ Mapa de Disparos
        - **Círculos**: Ubicación de cada disparo
        - **Tamaño**: Probabilidad de gol (xG)
        - **Icono fútbol**: Goles anotados
        
        ### 📍 Tercios del Campo
        - **Colores intensos**: Mayor concentración de acciones
        - **Números**: Cantidad de eventos por tercio
        
        ### 📊 Datos del Partido
        - Portugal vs Marruecos
        - Octavos de Final - Mundial 2022
        - Fuente: StatsBomb Open Data
        """)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#//////////////////////////////////////////////           SECCIÓN 6: ANÁLISIS COMPLETO DEL MUNDIAL 2022      /////////////////////////////////////////////
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                                                                                                                           --------------------------------------------------------------------
#                                                                                                                                           6. Análisis de xG - Holanda vs Ecuador
#                                                                                                                                           --------------------------------------------------------------------

elif opcion == "6 Análisis completo del mundial 2022":
    
    st.header("🏆 Análisis de xG - Holanda vs Ecuador")
    st.markdown("---")
    
    # Ruta del archivo CSV (ajusta según tu estructura de carpetas)
    archivo_csv = 'HolandavsEcuador.csv'
    
    # Llamar a la función de análisis
    resultado = analizar_xg_partido(archivo_csv)
    
    if resultado['success']:
        # Mostrar jugador con mayor xG
        st.subheader("🥅 Jugador con Mayor xG del Partido")
        
        top = resultado['top_player']
        
        # Crear 4 columnas para métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👤 Jugador", 
                value=top['nombre']
            )
        with col2:
            st.metric(
                label="🏅 Equipo", 
                value=top['equipo']
            )
        with col3:
            st.metric(
                label="⚽ xG Total", 
                value=f"{top['xg_total']:.3f}"
            )
        with col4:
            st.metric(
                label="🎯 Total Tiros", 
                value=top['tiros']
            )
        
        st.markdown("---")
        
        # Top 5 jugadores por xG
        st.subheader("📈 Top 5 Jugadores por xG Acumulado")
        
        # Mostrar tabla
        top5_df = pd.DataFrame(resultado['top_5_jugadores'])
        top5_df = top5_df[['player', 'team', 'xG_Total', 'Tiros', 'xG_Max_Tiro']]
        top5_df.columns = ['Jugador', 'Equipo', 'xG Total', 'Tiros', 'xG Máximo']
        
        st.dataframe(
            top5_df.style.format({
                'xG Total': '{:.3f}',
                'xG Máximo': '{:.3f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # xG por equipo
        st.subheader("📊 xG por Equipo")
        
        team_data = resultado['xg_por_equipo']
        
        col_team1, col_team2 = st.columns(2)
        
        equipos = list(team_data['xG_Total'].keys())
        
        if len(equipos) >= 2:
            with col_team1:
                st.info(
                    f"**{equipos[0]}**\n\n"
                    f"xG: {team_data['xG_Total'][equipos[0]]:.3f}\n\n"
                    f"Tiros: {int(team_data['Tiros'][equipos[0]])}"
                )
            
            with col_team2:
                st.info(
                    f"**{equipos[1]}**\n\n"
                    f"xG: {team_data['xG_Total'][equipos[1]]:.3f}\n\n"
                    f"Tiros: {int(team_data['Tiros'][equipos[1]])}"
                )
        
        st.markdown("---")
        
        # Gráfico de barras
        st.subheader("📉 Distribución de xG por Jugador (Top 10)")
        
        chart_data = resultado['dataframe'].head(10).set_index('player')['xG_Total']
        st.bar_chart(chart_data, use_container_width=True)
        
        st.markdown("---")
        
        # Botón de descarga
        st.subheader("💾 Descargar Datos")
        
        csv = resultado['dataframe'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar xG por Jugador (CSV)",
            data=csv,
            file_name='xg_jugadores_holanda_ecuador.csv',
            mime='text/csv'
        )
        
        # Información adicional
        st.markdown("---")
        st.info(f"ℹ️ Total de tiros analizados: {resultado['total_shots']}")
        
    else:
        st.error(f"❌ {resultado['message']}")
        st.info("💡 Asegúrate de que el archivo CSV esté en la carpeta correcta")

#                                                                                                                                           --------------------------------------------------------------------
#                                                                                                                                           6.1 Pases intentados y el que más pases completó en Iran vs Inglaterra
#                                                                                                                                           --------------------------------------------------------------------
   
    st.header("🎯 Análisis de Pases - Inglaterra vs Irán")
    st.markdown("---")
    
    # Ruta del archivo CSV (ajusta según tu estructura de carpetas)
    archivo_csv = 'InglaterravsIran.csv'
    
    # Llamar a la función de análisis
    resultado = analizar_pases_partido(archivo_csv)
    
    if resultado['success']:
        # Mostrar información general
        st.info(f"ℹ️ Total de pases analizados: {resultado['total_pases']}")
        
        st.markdown("---")
        
        # ============================================
        # JUGADOR CON MÁS PASES INTENTADOS
        # ============================================
        st.subheader("📤 Jugador con Más Pases Intentados")
        
        top_int = resultado['top_intentados']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👤 Jugador", 
                value=top_int['nombre']
            )
        with col2:
            st.metric(
                label="🏅 Equipo", 
                value=top_int['equipo']
            )
        with col3:
            st.metric(
                label="📤 Pases Intentados", 
                value=top_int['pases_intentados']
            )
        with col4:
            st.metric(
                label="✅ Pases Completados", 
                value=top_int['pases_completados']
            )
        
        st.markdown("---")
        
        # ============================================
        # JUGADOR CON MÁS PASES COMPLETADOS
        # ============================================
        st.subheader("✅ Jugador con Más Pases Completados")
        
        top_comp = resultado['top_completados']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👤 Jugador", 
                value=top_comp['nombre']
            )
        with col2:
            st.metric(
                label="🏅 Equipo", 
                value=top_comp['equipo']
            )
        with col3:
            st.metric(
                label="✅ Pases Completados", 
                value=top_comp['pases_completados']
            )
        with col4:
            st.metric(
                label="📊 Precisión", 
                value=f"{top_comp['precision']:.1f}%"
            )
        
        st.markdown("---")
        
        # ============================================
        # TOP 5 PASES INTENTADOS
        # ============================================
        st.subheader("📈 Top 5 Jugadores por Pases Intentados")
        
        top5_int_df = pd.DataFrame(resultado['top_5_intentados'])
        top5_int_df = top5_int_df[['player', 'team', 'Pases_Intentados', 'Pases_Completados', 'Precision']]
        top5_int_df.columns = ['Jugador', 'Equipo', 'Pases Intentados', 'Pases Completados', 'Precisión (%)']
        
        st.dataframe(
            top5_int_df.style.format({
                'Precisión (%)': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # ============================================
        # TOP 5 PASES COMPLETADOS
        # ============================================
        st.subheader("📈 Top 5 Jugadores por Pases Completados")
        
        top5_comp_df = pd.DataFrame(resultado['top_5_completados'])
        top5_comp_df = top5_comp_df[['player', 'team', 'Pases_Completados', 'Pases_Intentados', 'Precision']]
        top5_comp_df.columns = ['Jugador', 'Equipo', 'Pases Completados', 'Pases Intentados', 'Precisión (%)']
        
        st.dataframe(
            top5_comp_df.style.format({
                'Precisión (%)': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # ============================================
        # TOP 5 PRECISIÓN DE PASE
        # ============================================
        st.subheader("🎯 Top 5 Jugadores por Precisión de Pase (Mín. 10 pases)")
        
        top5_prec_df = pd.DataFrame(resultado['top_5_precision'])
        top5_prec_df = top5_prec_df[['player', 'team', 'Pases_Intentados', 'Pases_Completados', 'Precision']]
        top5_prec_df.columns = ['Jugador', 'Equipo', 'Pases Intentados', 'Pases Completados', 'Precisión (%)']
        
        st.dataframe(
            top5_prec_df.style.format({
                'Precisión (%)': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # ============================================
        # ESTADÍSTICAS POR EQUIPO
        # ============================================
        st.subheader("📊 Estadísticas de Pases por Equipo")
        
        team_data = resultado['team_stats']
        
        col_team1, col_team2 = st.columns(2)
        
        equipos = list(team_data['Pases_Intentados'].keys())
        
        if len(equipos) >= 2:
            with col_team1:
                st.info(
                    f"**{equipos[0]}**\n\n"
                    f"Pases Intentados: {int(team_data['Pases_Intentados'][equipos[0]])}\n\n"
                    f"Pases Completados: {int(team_data['Pases_Completados'][equipos[0]])}\n\n"
                    f"Precisión: {team_data['Precision'][equipos[0]]:.1f}%"
                )
            
            with col_team2:
                st.info(
                    f"**{equipos[1]}**\n\n"
                    f"Pases Intentados: {int(team_data['Pases_Intentados'][equipos[1]])}\n\n"
                    f"Pases Completados: {int(team_data['Pases_Completados'][equipos[1]])}\n\n"
                    f"Precisión: {team_data['Precision'][equipos[1]]:.1f}%"
                )
        
        st.markdown("---")
        
        # ============================================
        # GRÁFICOS
        # ============================================
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📊 Top 10 Pases Intentados")
            chart_data_int = resultado['dataframe_intentados'].head(10).set_index('player')['Pases_Intentados']
            st.bar_chart(chart_data_int, use_container_width=True)
        
        with col_chart2:
            st.subheader("✅ Top 10 Pases Completados")
            chart_data_comp = resultado['dataframe_completados'].head(10).set_index('player')['Pases_Completados']
            st.bar_chart(chart_data_comp, use_container_width=True)
        
        st.markdown("---")
        
        # ============================================
        # DESCARGAR DATOS
        # ============================================
        st.subheader("💾 Descargar Datos")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            csv_int = resultado['dataframe_intentados'].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Pases Intentados (CSV)",
                data=csv_int,
                file_name='pases_intentados_inglaterra_iran.csv',
                mime='text/csv'
            )
        
        with col_dl2:
            csv_comp = resultado['dataframe_completados'].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Pases Completados (CSV)",
                data=csv_comp,
                file_name='pases_completados_inglaterra_iran.csv',
                mime='text/csv'
            )
        
    else:
        st.error(f"❌ {resultado['message']}")
        st.info("💡 Asegúrate de que el archivo CSV esté en la carpeta correcta")
#                                                                                                                                    --------------------------------------------------------------------
#                                                                                                                                     6.1.1 Pases intentados y completados en Marruecos vs Francia
#                                                                                                                                    --------------------------------------------------------------------
    
    st.header("🎯 Análisis de Pases - Marruecos vs Francia")
    st.markdown("---")
    
    archivo_csv = 'Marruecosvsfrancia.csv'
    resultado = analizar_pases_marruecos_francia(archivo_csv)
    
    if resultado['success']:
        # ============================================
        # RESPUESTA DIRECTA A LA PREGUNTA
        # ============================================
        st.subheader("❓ ¿Cuántos pases intentados y completados hubo?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="📤 Total Pases Intentados", value=resultado['total_intentados'])
        with col2:
            st.metric(label="✅ Total Pases Completados", value=resultado['total_completados'])
        with col3:
            st.metric(label="❌ Total Pases Fallidos", value=resultado['total_fallidos'])
        with col4:
            st.metric(label="📊 Precisión General", value=f"{resultado['precision_general']:.1f}%")
        
        st.info(f"ℹ️ Total de eventos de pase analizados: {resultado['total_pases']}")
        
        st.markdown("---")
        
        # ============================================
        # ESTADÍSTICAS POR EQUIPO - CORREGIDO
        # ============================================
        st.subheader("🏆 Estadísticas de Pases por Equipo")
        
        # ✅ USAR EL DATAFRAME DIRECTAMENTE, NO EL DICCIONARIO
        df_team = resultado['dataframe_team']
        equipos_lista = resultado['equipos_lista']
        
        if len(equipos_lista) >= 2:
            col_team1, col_team2 = st.columns(2)
            
            # ✅ Encontrar índices correctamente
            idx_marruecos = 0 if 'Morocco' in equipos_lista[0] else 1
            idx_francia = 1 - idx_marruecos
            
            equipo_marruecos = equipos_lista[idx_marruecos]
            equipo_francia = equipos_lista[idx_francia]
            
            with col_team1:
                st.markdown("### 🇲🇦 Marruecos")
                fila_marruecos = df_team[df_team['team'] == equipo_marruecos].iloc[0]
                st.metric(label="Pases Intentados", value=int(fila_marruecos['Pases_Intentados']))
                st.metric(label="Pases Completados", value=int(fila_marruecos['Pases_Completados']))
                st.metric(label="Pases Fallidos", value=int(fila_marruecos['Pases_Fallidos']))
                st.metric(label="Precisión", value=f"{fila_marruecos['Precision']:.1f}%")
            
            with col_team2:
                st.markdown("### 🇫🇷 Francia")
                fila_francia = df_team[df_team['team'] == equipo_francia].iloc[0]
                st.metric(label="Pases Intentados", value=int(fila_francia['Pases_Intentados']))
                st.metric(label="Pases Completados", value=int(fila_francia['Pases_Completados']))
                st.metric(label="Pases Fallidos", value=int(fila_francia['Pases_Fallidos']))
                st.metric(label="Precisión", value=f"{fila_francia['Precision']:.1f}%")
        
        st.markdown("---")
        
        # ============================================
        # TABLA COMPARATIVA
        # ============================================
        st.subheader("📈 Tabla Comparativa de Pases")
        
        df_tabla = df_team.copy()
        df_tabla.columns = ['Equipo', 'Pases Intentados', 'Pases Completados', 'Pases Fallidos', 'Precisión (%)']
        
        df_tabla['Equipo'] = df_tabla['Equipo'].replace({
            'Morocco': '🇲🇦 Marruecos',
            'France': '🇫🇷 Francia'
        })
        
        st.dataframe(
            df_tabla.style.format({'Precisión (%)': '{:.1f}%'}),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # ============================================
        # TOP 5 JUGADORES POR EQUIPO
        # ============================================
        st.subheader("🎯 Top 5 Jugadores por Equipo")
        
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            st.markdown("### 🇲🇦 Top 5 Marruecos")
            if len(resultado['top_marruecos']) > 0:
                top_marruecos_df = pd.DataFrame(resultado['top_marruecos'])
                top_marruecos_df = top_marruecos_df[['player', 'Pases_Intentados', 'Pases_Completados', 'Precision']]
                top_marruecos_df.columns = ['Jugador', 'Pases Intentados', 'Pases Completados', 'Precisión (%)']
                st.dataframe(
                    top_marruecos_df.style.format({'Precisión (%)': '{:.1f}%'}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No hay datos disponibles")
        
        with col_top2:
            st.markdown("### 🇫🇷 Top 5 Francia")
            if len(resultado['top_francia']) > 0:
                top_francia_df = pd.DataFrame(resultado['top_francia'])
                top_francia_df = top_francia_df[['player', 'Pases_Intentados', 'Pases_Completados', 'Precision']]
                top_francia_df.columns = ['Jugador', 'Pases Intentados', 'Pases Completados', 'Precisión (%)']
                st.dataframe(
                    top_francia_df.style.format({'Precisión (%)': '{:.1f}%'}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No hay datos disponibles")
        
        st.markdown("---")
        
        # ============================================
        # GRÁFICOS
        # ============================================
        st.subheader("📊 Comparación Visual de Pases")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            chart_data = df_team.set_index('team')[['Pases_Intentados', 'Pases_Completados']]
            chart_data.index = ['🇲🇦 Marruecos' if 'Morocco' in idx else '🇫🇷 Francia' for idx in chart_data.index]
            st.bar_chart(chart_data, use_container_width=True)
        
        with col_chart2:
            precision_data = df_team.set_index('team')['Precision']
            precision_data.index = ['🇲🇦 Marruecos' if 'Morocco' in idx else '🇫🇷 Francia' for idx in precision_data.index]
            st.bar_chart(precision_data, use_container_width=True)
        
        st.markdown("---")
        
        # ============================================
        # DESCARGAR DATOS
        # ============================================
        st.subheader("💾 Descargar Datos")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            csv_team = df_team.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Pases por Equipo (CSV)",
                data=csv_team,
                file_name='pases_equipos_marruecos_francia.csv',
                mime='text/csv'
            )
        
        with col_dl2:
            csv_player = resultado['dataframe_player'].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Pases por Jugador (CSV)",
                data=csv_player,
                file_name='pases_jugadores_marruecos_francia.csv',
                mime='text/csv'
            )
        
    else:
        st.error(f"❌ {resultado['message']}")
        st.info("💡 Asegúrate de que el archivo CSV esté en la carpeta correcta")
#                                                                                                                                           --------------------------------------------------------------------
#                                                                                                                                               6.2 Rankings
#                                                                                                                                           --------------------------------------------------------------------
#Llamado de la función para los rankings
    mostrar_rankings_mundial_2022()
       
#                                                                                                                                           --------------------------------------------------------------------
#                                                                                                                                               6.3 Dashboard Messi
#                                                                                                                                           --------------------------------------------------------------------

# ==============================================================================
# ESTRUCTURA CON ELIF (Para tu proyecto)
# ==============================================================================


    
    st.header("🇦🇷 Dashboard de Lionel Messi - Mundial 2022")
        
# ======================================================================
# CARGA DE DATOS (Desde CSV local)
# ======================================================================
    with st.spinner("📂 Cargando datos..."):
        try:
            # RUTA DEL CSV (ajustá según tu estructura de carpetas)
            ruta_csv = "messi_mundial_2022_completo.csv"
            df_mundial = cargar_datos(ruta_csv)
            
            st.success(f"✅ Datos cargados: {len(df_mundial)} eventos")
            
        except FileNotFoundError:
            st.error("❌ No se encontró el archivo CSV. Verificá la ruta.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error al cargar datos: {str(e)}")
            st.stop()
        
# ======================================================================
# PREPARACIÓN DE DATOS (Usando tus variables)
# ======================================================================
    df_messi, df_messi_calor = preparar_universo_messi(df_mundial)
    goles_messi, faltas_messi, pases_messi = crear_cajitas(df_messi)
    
# ======================================================================
# MOSTRAR ESTADÍSTICAS EN SIDEBAR
# ======================================================================
    mostrar_estadisticas(goles_messi, faltas_messi, pases_messi, df_messi_calor)
    
# ======================================================================
# MOSTRAR DASHBOARD
# ======================================================================
    st.subheader("📈 Visualización Completa")
    
    with st.spinner("🎨 Generando gráficos..."):
        fig = dibujar_dashboard_messi(df_messi_calor, goles_messi, faltas_messi, pases_messi)
        st.pyplot(fig)
    
# ======================================================================
# BOTÓN DE DESCARGA (CORREGIDO)
# ======================================================================

    # Crear un buffer en memoria
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, facecolor='#22312b', edgecolor='none')
    buf.seek(0)  # Volver al inicio del buffer

    # Botón de descarga
    st.download_button(
        label="📥 Descargar Dashboard (PNG)",
        data=buf.getvalue(),  # Usar getvalue() del buffer
        file_name="dashboard_messi_mundial_2022.png",
        mime="image/png"
    )   
# ==============================================================================
# FOOTER
# ==============================================================================
    st.markdown("---")
    st.write("📌 **Nota:** Los datos se cargan desde CSV local para mayor velocidad.")
    st.write("🛠️ **Tecnologías:** Streamlit + mplsoccer + pandas")
#                                                                                                                                           --------------------------------------------------------------------
#                                                                                                                                               6.4 Gráficos de Dispersión
#                                                                                                                                           --------------------------------------------------------------------
# ============================================================================
# 6️⃣ SEXTO: Dashboard Streamlit (EL CUERPO - AL FINAL)
# ============================================================================

    # Configuración de la página
    st.set_page_config(page_title="🏆 Mundial 2022 - Análisis", layout="wide")

    # Título principal
    st.title("🏆 Copa Mundial 2022 - Análisis de Jugadores")
    st.markdown("---")

    # Cargar datos (llama a la función del cerebro)
    df_resumen = cargar_y_preparar_datos()

    # Mostrar información de datos
    st.sidebar.header("📊 Información")
    st.sidebar.write(f"**Jugadores analizados:** {len(df_resumen)}")
    st.sidebar.write(f"**Columnas disponibles:** {len(df_resumen.columns)}")

    # Columnas para los gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Ataque: Tiros vs xG")
        fig1, ax1 = graficar_dispersion_xg_tiros(df_resumen)
        st.pyplot(fig1)
        
        st.subheader("🛡️ Defensa: Intercepciones vs Faltas")
        fig2, ax2 = graficar_dispersion_intercepciones_faltas(df_resumen)
        st.pyplot(fig2)

    with col2:
        st.subheader("🎯 Pases: Volumen vs Efectividad")
        fig3, ax3 = graficar_dispersion_pases_efectividad(df_resumen)
        st.pyplot(fig3)
        
        st.subheader("⚽ Definición: Goles Reales vs Esperados")
        fig4, ax4 = graficar_dispersion_goles_reales_esperados(df_resumen)
        st.pyplot(fig4)

    # Pie de página
    st.markdown("---")

    st.caption("📊 Datos fuente: StatsBomb | Jugadores destacados: Messi, Mbappé, Álvarez, Modrić")


