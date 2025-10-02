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
asteroides = supabase.table("clasificaciones").select("Asteroide").execute()
asteroide_list = sorted(list({a["Asteroide"] for a in asteroides.data if a["Asteroide"]}))
asteroide = st.sidebar.selectbox("Asteroide:", ["Todos"] + asteroide_list)

# Filtro por clasificación
clasificaciones = supabase.table("clasificaciones").select("Clasificacion").execute()
clasificacion_list = sorted(list({c["Clasificacion"] for c in clasificaciones.data if c["Clasificacion"]}))
clasificacion = st.sidebar.selectbox("Clasificación:", ["Todas"] + clasificacion_list)


# --- Construcción de la consulta ---
query = supabase.table("clasificaciones").select("*")

if asteroide != "Todos":
    query = query.eq("Asteroide", asteroide)

if clasificacion != "Todas":
    query = query.eq("Clasificacion", clasificacion)


# --- Ejecutar consulta ---
rows = query.execute()

# --- Mostrar resultados ---
if rows.data:
    df = pd.DataFrame(rows.data)
    st.subheader("Resultados filtrados")
    st.write(f"Numero de asteroides con analisis preliminar: {len(df)}")
    st.dataframe(df[["Asteroide", "Nombre", "Familia", "Clasificacion", "Pendiente", "Intercepto", "comentario", "fecha_hora"]], use_container_width=True, hide_index=True)

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
st.write(f"Numero de asteroides con analisis preliminar: {len(pd.DataFrame(rows.data))}")
df = pd.DataFrame(rows.data)
st.dataframe(df[["Asteroide", "Nombre", "Familia", "Clasificacion", "Pendiente", "Intercepto", "comentario", "fecha_hora"]], use_container_width=True, hide_index=True)