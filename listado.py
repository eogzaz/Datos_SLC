import streamlit as st
import io
import zipfile
from concurrent.futures import ThreadPoolExecutor
from paq_Datos_SLC import DATA

# --------------------------
# Función de ejemplo
# (Aquí debes poner tu lógica real del notebook)
# --------------------------
@st.cache_data
def generar_txt(asteroide: str) -> str:
    fi = '1993-01-01'
    ff = '2025-10-01'
    df_ast = DATA().datos_SLC(asteroide, fi, ff,'Asteroide').to_pandas()
    txt_ast = df_ast.to_csv(sep='\t', index=False, header=False)

    # Simulación de lógica pesada
    import time
    time.sleep(1)  # Simula tiempo de consulta
    return txt_ast


# --------------------------
# Interfaz Streamlit
# --------------------------
# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Datos Fase-SLC",
    page_icon="☄️",
    layout="wide",
)

#st.markdown("<h1 style='text-align: center'>☄️Datos Fase y SLC (Obtención datos Listado) </h2>", unsafe_allow_html=True)
st.subheader("Obtencion de datos para un listado de objetos")

st.write("Ingresa los asteroides manualmente o sube un archivo .txt con la lista. (por ahora solo funciona con asteroides)")

col1, col2 = st.columns(2)

with col1:
    # Opción 1: entrada manual
    entrada_manual = st.text_area("Escribe los nombres o IDs de asteroides (uno por línea):")

with col2:
    # Opción 2: cargar archivo
    archivo_txt = st.file_uploader("O subir un archivo .txt con la lista de asteroides", type=["txt"])

# Determinar la lista de asteroides
asteroides = []
if archivo_txt is not None:
    contenido = archivo_txt.read().decode("utf-8")
    asteroides = [x.strip() for x in contenido.splitlines() if x.strip()]
    nombre_archivo = archivo_txt.name + "_datos"
elif entrada_manual.strip():
    asteroides = [x.strip() for x in entrada_manual.splitlines() if x.strip()]
    nombre_archivo = "Asteroides_seleccionados_datos"

if st.button("Procesar"):
    if asteroides:
        st.info(f"Procesando {len(asteroides)} asteroides, por favor espera...")

        # Procesar en paralelo
        with ThreadPoolExecutor() as executor:
            resultados = list(executor.map(generar_txt, asteroides))

        # Crear un ZIP en memoria
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for ast, contenido in zip(asteroides, resultados):
                zf.writestr(f"{ast}.txt", contenido)

        buffer.seek(0)

       
        # Botón para descargar ZIP
        st.success("✅ Procesamiento terminado. Puedes descargar los resultados.")
        st.download_button(
            label="📥 Descargar ZIP",
            data=buffer,
            file_name=nombre_archivo+".zip",
            mime="application/zip"
        )
    else:
        st.warning("⚠️ Ingresa asteroides manualmente o sube un archivo .txt.")

