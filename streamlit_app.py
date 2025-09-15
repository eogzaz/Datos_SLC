import streamlit as st

st.set_page_config(layout="wide", page_icon="☄️", page_title="Datos SLC")

# --- BANNER / TÍTULO ---
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg,#6a11cb,#2575fc);
        color: white;
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 8px;">
        <h1>
       ☄️Datos para Curva de luz secular (SLC)
       </h1>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- NAVEGACIÓN (se dibuja debajo del banner y con el CSS aplicado) ---
pg = st.navigation({
    "Menu de navegación:": [
        st.Page("main.py", title="Análisis individual preliminar"),
        st.Page("reporte.py", title="Reporte preliminar de actividad"),
        st.Page("listado.py", title="Obtención datos listado"),
        st.Page("Documentacion.py", title="Documentación"),
    ]}
)

pg.run()