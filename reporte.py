import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# --- Conexión a Supabase ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.set_page_config(layout="wide", page_icon="☄️", page_title="Datos SLC")
st.subheader("Reporte preliminar de actividad")

# --- Filtros ---
st.sidebar.header("Filtros")

# Filtro por asteroide
asteroides = supabase.table("clasificaciones").select("asteroide").execute()
asteroide_list = sorted(list({a["asteroide"] for a in asteroides.data if a["asteroide"]}))
asteroide = st.sidebar.selectbox("Asteroide:", ["Todos"] + asteroide_list)

# Filtro por clasificación
clasificaciones = supabase.table("clasificaciones").select("clasificacion").execute()
clasificacion_list = sorted(list({c["clasificacion"] for c in clasificaciones.data if c["clasificacion"]}))
clasificacion = st.sidebar.selectbox("Clasificación:", ["Todas"] + clasificacion_list)

# Filtro por rango de fechas
fecha_min = st.sidebar.date_input("Fecha mínima")
fecha_max = st.sidebar.date_input("Fecha máxima")

# --- Construcción de la consulta ---
query = supabase.table("clasificaciones").select("*")

if asteroide != "Todos":
    query = query.eq("asteroide", asteroide)

if clasificacion != "Todas":
    query = query.eq("clasificacion", clasificacion)

if fecha_min and fecha_max:
    query = query.gte("fecha_hora", str(fecha_min)).lte("fecha_hora", str(fecha_max))

# --- Ejecutar consulta ---
rows = query.execute()

# --- Mostrar resultados ---
if rows.data:
    df = pd.DataFrame(rows.data)
    st.subheader("Resultados filtrados")
    st.dataframe(df, use_container_width=True)

    # Botón de descarga CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar CSV",
        csv,
        "resultados.csv",
        "text/csv",
        key="download-csv"
    )
else:
    st.info("No se encontraron resultados con los filtros seleccionados.")


# --- Mostrar datos ---
rows = supabase.table("clasificaciones").select("*").execute()
st.subheader("Clasificaciones almacenadas")
st.write(f"Numero de asteroides con analisis preliminar: {len(pd.DataFrame(rows.data))}") # poner aca un groupby mejor
st.dataframe(rows.data)