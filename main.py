import streamlit as st
from supabase import create_client, Client
from paq_Datos_SLC import DATA, Information
import datetime as dt
from datetime import datetime
from astropy.time import Time
from obtaining_graphics import *
import pandas as pd
import numpy as np


# --- Inicialización ---
if "object_type" not in st.session_state:
    st.session_state.object_type = None

if "df_inicial" not in st.session_state:
    st.session_state.df_inicial = pd.DataFrame(columns=["Anio","Mes","Dia","t-Tq","Delta","r","Fase","Magn_obs","Magn_redu","Magn_Corr_Fase","Date","JD"])

if "df_inicial_COBS" not in st.session_state:
    st.session_state.df_inicial_COBS = pd.DataFrame(columns=["Anio","Mes","Dia","t-Tq","Delta","r","Fase","Magn_obs","Magn_redu","Magn_Corr_Fase","Date","JD"])

if "selected_object" not in st.session_state:
    st.session_state.selected_object = None

if "orbital_period" not in st.session_state:
    st.session_state.orbital_period = None

if "datos_cargados" not in st.session_state:
    st.session_state.datos_cargados = False


# --- Conexión a Supabase ----------------------------------
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)
#-----------------------------------------------------------



#-----------------Configuración de pagina-------------------
st.set_page_config(layout="wide", page_icon="☄️", page_title="Datos SLC")

#-----------------Titulo------------------------------------
st.subheader("Obtención de datos y Análisis preliminar individual")
#----------------------------------------------------------
st.divider()

col1, col3,col2 = st.columns([0.475,0.05,0.475])
#---------------Eleccion del objeto------------------------ 
with col1:  
    st.subheader("🔭 Elección de objeto")
    initial_selected_object = st.text_input("Ingrese algún identificador de algún objeto del MPC. (Ej: Bennu, 1, 401P, 3I , 2024 AA)",
                                    value=None, placeholder='Ceres',help='Ingrese cualquier identificador valido del MPC')

#-------------Verificacion de la existencia del objeto--------------------------
    object_exists = Information(initial_selected_object).object_exists()                       #Verificacion de la exixtencia en el MPC
    if not initial_selected_object==None:
        if object_exists:       
            initial_object_type = Information(initial_selected_object).object_type()
            id_object = Information(initial_selected_object).ID_object()
            initial_orbital_period = Information(initial_selected_object).orbital_period()
            # --- AJUSTE PARA CONSISTENCIA ---
            if initial_object_type == 'Asteroide' and initial_orbital_period is None:
                initial_object_type = 'Asteroide (Sin periodo definido)'
            if initial_object_type == 'Cometa' and initial_orbital_period is None:
                initial_object_type = 'Cometa (Sin periodo definido)'
            # ---------------------------------                      #ID oficial en el MPC
            if not id_object==None: 
                st.markdown(f"""**El {initial_object_type} seleccionado es:** <span style="color:blue;" title="Designacion oficial de IAU">**{id_object}**</span>""", unsafe_allow_html=True)
                selected_object = id_object
            else:
                provisional_designation_object = Information(initial_selected_object).provisional_designation()            #Sino tiene ID entonces se usa la designacion provisional
                st.markdown(f"""**El {initial_object_type} seleccionado es:** <span style="color:blue;" title="Designacion provisional">**{provisional_designation_object}**</span>""", unsafe_allow_html=True)
                selected_object = provisional_designation_object
        else:
                st.warning('⚠️ Objeto no encontrado en el MPC')
    else:
        a=0
        st.markdown(f"""**El objeto seleccionado es:** """, unsafe_allow_html=True)

#-----------------------Rango de fechas de observaciones en el MPC-------------------------------------
with col2:
    st.subheader("🕒 Fechas de observaciones")
    col4,col5 = st.columns(2)
    with col4:
        fecha_inicial = str(st.date_input('Ingrese fecha de inicio', 
                                    value=dt.date(1993, 1, 1),
                                    min_value=dt.date(1600, 1, 1),
                                    max_value="today",
                                    help='''Desde esta fecha se tomaran las observaciones 
                                    del objeto registradas en el MPC'''))#.replace('-',' ')
    with col5:
        fecha_final = str(st.date_input('Ingrese fecha final',
                                            value="today",
                                            min_value = pd.to_datetime(fecha_inicial),
                                            max_value="today",
                                            help='''Hasta esta fecha se tomaran las observaciones
                                            del objeto registradas en el MPC'''))#.replace('-',' ')
    st.success(f"Rango seleccionado: **{fecha_inicial} → {fecha_final}**")

#-----------------------Obtención de datos--------------------------------------------------
if object_exists:
    col6,col7,col8=st.columns([0.45,0.2,0.35])
    with col7:
        
        if st.button('Obtener datos', type='primary'):   
            object_type = Information(selected_object).object_type()
            orbital_period = Information(selected_object).orbital_period()  
            if object_type == 'Asteroide' and orbital_period is None:
                object_type = 'Asteroide (Sin periodo definido)'
            if object_type == 'Cometa' and orbital_period is None:
                object_type = 'Cometa (Sin periodo definido)'
            st.session_state.object_type = object_type
            st.session_state.orbital_period = orbital_period

            #Asteroides
            if object_type=='Asteroide':
                with st.spinner("_Procesando..._"):
                    #orbital_period = Info.orbital_period()                    #Periodo orbital 
                    #st.session_state.orbital_period = orbital_period                         
                    date_perihelion = Information(selected_object).date_perihelion()                  #Fecha del perihelio
                    st.session_state.date_perihelion = date_perihelion
                    name = Information(selected_object).name_object()                                 #Nombre del asteroide
                    st.session_state.name = name 
                    family = Information(selected_object).family_object()                             #Familia del asteroide
                    st.session_state.family = family
                    
                    #DATOS PARA LA SLC (Año, Mes, Dia, t-Tq, Delta, r, Fase, Magn_obs, Magn_redu)
                    st.session_state.df_inicial = DATA().datos_SLC(
                        selected_object,
                        fecha_inicial,
                        fecha_final,
                        object_type
                    ).to_pandas()
                    #st.write(st.session_state.df_inicial)
                    st.session_state.selected_object = selected_object    
                    st.session_state.datos_cargados = True  

            #Cometas 
            elif object_type=='Cometa':
                with st.spinner("_Procesando..._"):
                    #orbital_period = Information(selected_object).orbital_period()                    #Periodo orbital
                    #st.session_state.orbital_period = orbital_period
                    date_perihelion = Information(selected_object).date_perihelion()                  #Fecha del perihelio
                    st.session_state.date_perihelion = date_perihelion
                    name = Information(selected_object).name_object()                               #Nombre del cometa
                    st.session_state.name = name
                
                    #DATOS DEL MPC PARA LA SLC (Año, Mes, Dia, t-Tq, Delta, r, Fase, Magn_obs, Magn_redu)                
                    st.session_state.df_inicial = DATA().datos_SLC(
                        selected_object,
                        fecha_inicial,
                        fecha_final,
                        object_type
                    ).to_pandas()

                    #DATOS DE COBS PARA LA SLC (Año, Mes, Dia, t-Tq, Delta, r, Fase, Magn_obs, Magn_redu)                    
                    st.session_state.df_inicial_COBS = DATA().datos_SLC_COBS(
                        selected_object,
                        fecha_inicial,
                        fecha_final,
                        object_type
                    ).to_pandas()

                    st.session_state.selected_object = selected_object
                    st.session_state.datos_cargados = True  

        #Objetos interestelares
            elif object_type=='Objeto Interestelar':
                with st.spinner("_Procesando..._"):
                    date_perihelion = Information(selected_object).date_perihelion()                  #Fecha del perihelio
                    st.session_state.date_perihelion = date_perihelion
                    name = Information(selected_object).name_object()
                    st.session_state.name = name

                    #DATOS DEL MPC PARA LA SLC (Año, Mes, Dia, t-Tq, Delta, r, Fase, Magn_obs, Magn_redu)
                    st.session_state.df_inicial = DATA().datos_SLC(
                        selected_object,
                        fecha_inicial,
                        fecha_final,
                        object_type
                    ).to_pandas()

                    #DATOS DE COBS PARA LA SLC (Año, Mes, Dia, t-Tq, Delta, r, Fase, Magn_obs, Magn_redu)                    
                    st.session_state.df_inicial_COBS = DATA().datos_SLC_COBS(
                        selected_object,
                        fecha_inicial,
                        fecha_final,
                        object_type
                    ).to_pandas()

                    st.session_state.selected_object = selected_object                    
                    st.session_state.datos_cargados = True  

            else:
                st.warning('Escoge un asteroide, cometa (con periodo definido) u objeto interestelar para obtener sus datos')

#--------------------------------Muestra de datos-----------------------------------------------
#---------ASTEROIDES-----------------------------------------
    if st.session_state.object_type=='Asteroide':
        if st.session_state.get("datos_cargados", False):
            df_inicial = st.session_state.df_inicial
            df = st.session_state.df_inicial.copy()
            orbital_period = st.session_state.orbital_period
            date_perihelion = st.session_state.date_perihelion
            name = st.session_state.name
            family = st.session_state.family
            selected_object = st.session_state.selected_object
            
            # --- Barra de navegación (Tabs) ---
            tab1, tab2 = st.tabs(["Información y Descargar datos", "Graficas y reporte preliminares"])

            #Informacion
            with tab1:
                col9, col10 = st.columns([0.5,0.5],border=True)
                with col9:
                    st.subheader('Información')
                    st.write(f"Asteroide ID: {selected_object}")
                    st.write(f"Nombre: {name}")
                    if not family==None:
                        st.write(f"Familia: {family}")
                    st.write(f'Periodo: {round(float(orbital_period),2)} años ({round(float(orbital_period)*365,2)} días)')
                    st.write(f'Fecha del perihelio: {date_perihelion} (JD: {round(Time(date_perihelion.to_pydatetime(), scale="utc").jd,2)})')  
                    # pendiente agragar mas informacion del objeto     

                #Descargas
                with col10:
                    st.header('Descargar datos')
                    st.write(f'Desde {fecha_inicial.replace(' ','/')} hasta {fecha_final.replace(' ','/')}')
                    Total_obs = len(df_inicial)
                    st.write(f'Total observaciones: {Total_obs}')

                    st.subheader('Datos SLC: ')
                    def convert_for_download(df):
                        return df.to_csv(sep='\t', index=False, header=False).encode("utf-8")
                    df_txt = convert_for_download(df_inicial)

                    st.download_button(label=f"Descargar datos {selected_object} (.txt)",
                                    data=df_txt,
                                    file_name=selected_object + ".txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore")
                    
                    st.subheader('Datos SLC sin efecto de oposición: ')
                    oposicion = float(st.text_input("Ingresa desde que grado desea quitar la oposición:", value="5", key="grado_oposicion"))
                    df_txt_oposicion = convert_for_download(fase_menor_5(df_inicial,oposicion))
                    st.download_button(label=f"Descargar datos {selected_object} con oposicon desde {oposicion} (.txt)",
                                    data=df_txt_oposicion,
                                    file_name=selected_object + f"_oposicion({oposicion}).txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore")
                    
                    st.subheader('Datos SLC con correción por fase: ')
                           
                    pendiente_down = float(st.text_input('Pendiente',value=0,key='pendiente_down'))

                    intercepto_down = float(st.text_input('Intercepto',value=0,key='intercepto_down'))
                    df_corr_fase   = df.copy()
                    df_corr_fase['Magn_Corr_Fase'] = df_corr_fase['Magn_redu']-pendiente_down*df_corr_fase['Fase']
                    df_txt_corr_fase = convert_for_download(df_corr_fase)
                    st.download_button(label=f"Descargar datos {selected_object} con correción por fase (.txt)",
                                    data=df_txt_corr_fase,
                                    file_name=selected_object + f"_corr_fase.txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore")

            #GRAFICAS
            with tab2:
                col11,col12 = st.columns([0.2,0.8],border=True)
                
                #Configuracion y variaciones en las graficas
                with col11:
                    with st.container():
                        #Efecto de oposicion
                        on_oposicion = st.toggle("**Quitar efecto de oposición**",value=False)
                        if on_oposicion:
                            desde = float(st.text_input('Quitar hasta: [°]',value=5))
                            df = fase_menor_5(df,desde)
                        

                        #Recta envolvente
                        on_recta = st.toggle("**Recta envolvente**",value=False)
                        params_recta = calc_envolvente(df,bin_width=.1)
                        pendiente_inicial = params_recta[0]
                        intercepto_inicial = params_recta[1]
                        alpha_max=  params_recta[2]
                        magn_max= params_recta[3]

                        col14,col15 = st.columns(2)
                        with col14:
                            pendiente = float(st.text_input('Pendiente',value=round(pendiente_inicial,3)))
                        with col15:
                            intercepto = float(st.text_input('Intercepto',value=round(intercepto_inicial,2)))

                        #Corrección por fase
                        on_corrfase = st.toggle("**Correción por fase**",value=False)
                        df['Magn_Corr_Fase'] = df['Magn_redu']-pendiente*df['Fase']

                        #Clasificacion por periodos
                        on_colores = st.toggle("**Colores periodos orbitales**",value=False)
                        clasificacion, lim_peri = clasificacion_periodos(df,float(orbital_period)*365,Time(date_perihelion.to_pydatetime(), scale="utc").jd)
                        if on_colores:
                            fechas_periodos = [st.checkbox(f'{julian_to_date(lim_peri[i+1])} - {julian_to_date(lim_peri[i])}',value=True) for i in range(len(lim_peri)-1)]
                            #clasificacion_final=clasificacion.copy()
                            for i in range(len(clasificacion)):
                                if fechas_periodos[i]==False:
                                    clasificacion[i]=pd.DataFrame({'Anio':[],'Mes':[],'Dia':[],'t-Tq':[],'Delta':[],'r':[],'Fase':[],'Magn_obs':[],'Magn_redu':[],'Magn_Corr_Fase':[],'Date':[],'JD':[]})

                        #Promedio corrido
                        on_prom_corr = st.toggle("**Promedio corrido**",value=False)
                        if on_prom_corr:
                            ventana = int(st.text_input('De:',value=9))
                            df = promedio_corrido(df,'Magn_redu',ventana)

                        #Configuracion de grafico
                        with st.expander("⚙️ Configuración grafico de curva de fase"):
                            col16, col17, col18 = st.columns([0.2,0.4,0.4])
                            with col16:
                                st.write('**Eje X:**')
                            with col17:
                                xmin = st.text_input('X_Min',value=0)
                            with col18:
                                xmax = st.text_input('X_Max',value=int(max(df['Fase'])+2))
                            st.divider()
                            col19, col20, col21 = st.columns([0.2,0.4,0.4])
                            with col19:
                                st.write('**Eje Y:**')
                            with col20:
                                ymin = st.text_input('Y_Min',value=int(max(df['Magn_redu']))+1)
                            with col21:
                                ymax = st.text_input('Y_Max',value=int( min(df['Magn_redu'])-1))

                        #Configuración grafico SLC
                        with st.expander("⚙️ Configuración grafico de SLC"):
                            col22, col23, col24 = st.columns([0.2,0.4,0.4])
                            with col22:
                                st.write('**Eje X:**')
                            with col23:
                                xmin_slc = st.text_input('X_Min',value=-max(abs(min(df['t-Tq'])),abs(max(df['t-Tq'])))-20)
                            with col24:
                                xmax_slc = st.text_input('X_Max',value= max(abs(min(df['t-Tq'])),abs(max(df['t-Tq'])))+20)
                            st.divider()
                            col25, col26, col27 = st.columns([0.2,0.4,0.4])
                            with col25:
                                st.write('**Eje Y:**')
                            with col26:
                                ymin_slc = st.text_input('Y_Min',value=int(max(df['Magn_redu']))+1,key=1)
                            with col27:
                                ymax_slc = st.text_input('Y_Max',value=int( min(df['Magn_redu'])-1),key=2)


                #--- --------------------VISUALIZACIÓN DE GRÁFICOS ---------------------------
        
                #-------Curva de fase--------------------
                with col12:
                    col13, col14 = st.columns([0.5,0.5])
                    with col13:
                        st.subheader("Curva de Fase")
                        limites_ejes = np.array([float(xmin),float(xmax),float(ymin),float(ymax)])
                        params_recta = [pendiente,intercepto]
                                    
                        if on_recta:
                            intercepto1 = intercepto
                            if on_colores:
                                st.pyplot(grafica_fase_colores(clasificacion, title=selected_object+" "+name,familia=family,recta_pendiente=True, pendiente_param = params_recta, limites=limites_ejes))
                            else:
                                st.pyplot(grafica_fase(df, alpha_max, magn_max,title=selected_object+" "+name,familia=family,recta_pendiente=True, pendiente_param = params_recta, limites=limites_ejes))
                        else:
                            intercepto1 = 1
                            if on_colores:
                                st.pyplot(grafica_fase_colores(clasificacion, title=selected_object+" "+name,familia=family, limites=limites_ejes))
                            else:
                                st.pyplot(grafica_fase(df, alpha_max, magn_max, title=selected_object+" "+name,familia=family,limites=limites_ejes))

                    #-----------SLC----------------------------
                    with col14:
                        st.subheader(f'Curva de Luz Secular')                        
                        limites_ejes_slc = np.array([float(xmin_slc),float(xmax_slc),float(ymin_slc),float(ymax_slc)])    

                        if on_corrfase:
                            if on_colores:
                                st.pyplot(SLC_colores_corr(clasificacion, title=selected_object+" "+name,familia=family,intercepto=intercepto1,limites=limites_ejes_slc))
                            else:
                                st.pyplot(grafica_SLC_corr(df, title=selected_object+" "+name,familia=family,intercepto=intercepto1,limites=limites_ejes_slc))

                        else:
                            if on_colores:
                                st.pyplot(SLC_colores(clasificacion, title=selected_object+" "+name,familia=family,intercepto=intercepto1,limites=limites_ejes_slc))
                            else:
                                st.pyplot(grafica_SLC(df, title=selected_object+" "+name,familia=family,intercepto=intercepto1,limites=limites_ejes_slc))
            #--- --------------------REPORTE PRELIMINAR ---------------------------
                    st.divider()
                    st.subheader("Reporte preliminar")
                    col28,col29,col30 = st.columns(3)
                    with col28: 
                        clasificacion = st.radio("Actividad:", ["Positiva", "Negativa", "Marginal", "Revisar"],index=None)
                    with col29:
                        comentario = st.text_area("Comentario (opcional)")
                    with col30:
                        if st.button("Guardar en Supabase"):
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            data = {
                                    "Asteroide": selected_object,
                                    "Nombre": name,
                                    "Familia": family,
                                    "Clasificacion": clasificacion,
                                    "Pendiente": pendiente,
                                    "Intercepto": intercepto,
                                    "comentario": comentario,
                                    "fecha_hora": timestamp,
                                }
                            
                            supabase.table("clasificaciones").upsert(data, on_conflict="Asteroide").execute()
                            st.success("✅ Clasificación guardada/actualizada en Supabase")

#---------COMETAS--------------------------------------------
    if st.session_state.object_type=='Cometa':
        if st.session_state.get("datos_cargados", False):
            df_inicial = st.session_state.df_inicial
            df_inicial_COBS = st.session_state.df_inicial_COBS
            df = st.session_state.df_inicial.copy()
            df_COBS = df_inicial_COBS.copy()
            orbital_period = st.session_state.orbital_period
            date_perihelion = st.session_state.date_perihelion
            name = st.session_state.name
            selected_object = st.session_state.selected_object
            
            # --- Barra de navegación (Tabs) ---
            tab1, tab2, tab3 = st.tabs(["Información", "Descargar datos", "Graficas preliminares"])

            #informacion
            with tab1:
                st.subheader('Información')
                st.write(f"Cometa ID: {selected_object}")
                st.write(f"Nombre: {name}")
                st.write(f'Periodo: {round(float(orbital_period),2)} años ({round(float(orbital_period)*365,2)} días)')
                st.write(f'Fecha del perihelio: {date_perihelion} (JD: {round(Time(date_perihelion.to_pydatetime(), scale="utc").jd,2)})')       

            #Descargas
            with tab2:
                st.subheader('Descargar datos')
                st.write(f'Desde {fecha_inicial.replace(' ','/')} hasta {fecha_final.replace(' ','/')}')
                col9, col10= st.columns(2)
                with col9:
                    Total_obs = len(df_inicial)
                    Total_obs_COBS = len(df_inicial_COBS)
                    st.write(f'Total observaciones en MPC: {Total_obs}')
                    st.write(f'Total observaciones en COBS: {Total_obs_COBS}')
                with col10:
                    def convert_for_download(df):
                        return df.to_csv(sep='\t', index=False, header=False).encode("utf-8")
                    txt = convert_for_download(df_inicial)
                    txt_COBS = convert_for_download(df_inicial_COBS)

                    st.download_button(label="Descargar datos MPC(.txt)",
                                    data=txt,
                                    file_name=selected_object + "_MPC.txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore")
                    st.download_button(label="Descargar datos COBS(.txt)",
                                    data=txt_COBS,
                                    file_name=selected_object + "_COBS.txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore")
        
            #GRAFICAS
            with tab3:
                col11,col12,col13 = st.columns([0.2,0.4,0.4],border=True)
                
                #Configuracion de las graficas
                with col11:
                    with st.container():
                        #Clasificacion por periodos
                        on_colores = st.toggle("**Colores periodos orbitales MPC**",value=False)
                        clasificacion, lim_peri = clasificacion_periodos(df_inicial,float(orbital_period)*365,Time(date_perihelion.to_pydatetime(), scale="utc").jd)
                        if on_colores:
                            fechas_periodos = [st.checkbox(f'{julian_to_date(lim_peri[i+1])} - {julian_to_date(lim_peri[i])}',value=True) for i in range(len(lim_peri)-1)]
                            #clasificacion_final=clasificacion.copy()
                            for i in range(len(clasificacion)):
                                if fechas_periodos[i]==False:
                                    clasificacion[i]=pd.DataFrame({'Anio':[],'Mes':[],'Dia':[],'t-Tq':[],'Delta':[],'r':[],'Fase':[],'Magn_obs':[],'Magn_redu':[],'Magn_Corr_Fase':[],'Date':[],'JD':[]})

                        #Clasificacion por periodos
                        on_colores_COBS = st.toggle("**Colores periodos orbitales COBS**",value=False)
                        if not df_inicial_COBS.empty:
                            clasificacion_COBS, lim_peri_COBS = clasificacion_periodos(df_inicial_COBS,float(orbital_period)*365,Time(date_perihelion.to_pydatetime(), scale="utc").jd)
                        else:
                            clasificacion_COBS, lim_peri_COBS = [], []

                        if on_colores_COBS:
                            fechas_periodos = [st.checkbox(f'{julian_to_date(lim_peri_COBS[i+1])} - {julian_to_date(lim_peri_COBS[i])}',value=True) for i in range(len(lim_peri_COBS)-1)]
                            #clasificacion_final=clasificacion_COBS.copy()
                            for i in range(len(clasificacion_COBS)):
                                if fechas_periodos[i]==False:
                                    clasificacion_COBS[i]=pd.DataFrame({'Anio':[],'Mes':[],'Dia':[],'t-Tq':[],'Delta':[],'r':[],'Fase':[],'Magn_obs':[],'Magn_redu':[],'Magn_Corr_Fase':[],'Date':[],'JD':[]})


                        #Promedio corrido
                        on_prom_corr = st.toggle("**Promedio corrido**",value=False)
                        if on_prom_corr:
                            ventana = int(st.text_input('De:',value=9))
                            df = promedio_corrido(df,'Magn_redu',ventana)
                            df_COBS = promedio_corrido(df_COBS,'Magn_redu',ventana)


                        #Configuración grafico SLC MPC
                        with st.expander("⚙️ Configuración grafico de SLC MPC"):
                            col22, col23, col24 = st.columns([0.2,0.4,0.4])
                            with col22:
                                st.write('**Eje X:**')
                            with col23:
                                xmin_slc = st.text_input('X_Min',value=-max(abs(min(df['t-Tq'])),abs(max(df['t-Tq'])))-20)
                            with col24:
                                xmax_slc = st.text_input('X_Max',value= max(abs(min(df['t-Tq'])),abs(max(df['t-Tq'])))+20)
                            st.divider()
                            col25, col26, col27 = st.columns([0.2,0.4,0.4])
                            with col25:
                                st.write('**Eje Y:**')
                            with col26:
                                ymin_slc = st.text_input('Y_Min',value=int(max(df['Magn_redu']))+1,key=1)
                            with col27:
                                ymax_slc = st.text_input('Y_Max',value=int( min(df['Magn_redu'])-1),key=2)

                        #Configuración grafico SLC COBS
                        if not df_COBS.empty:
                            with st.expander("⚙️ Configuración grafico de SLC COBS"):
                                col22, col23, col24 = st.columns([0.2,0.4,0.4])
                                with col22:
                                    st.write('**Eje X:**')
                                with col23:
                                    xmin_slc_COBS = st.text_input('X_Min',value=-max(abs(min(df_COBS['t-Tq'])),abs(max(df_COBS['t-Tq'])))-20)
                                with col24:
                                    xmax_slc_COBS = st.text_input('X_Max',value= max(abs(min(df_COBS['t-Tq'])),abs(max(df_COBS['t-Tq'])))+20)
                                st.divider()
                                col25, col26, col27 = st.columns([0.2,0.4,0.4])
                                with col25:
                                    st.write('**Eje Y:**')
                                with col26:
                                    ymin_slc_COBS = st.text_input('Y_Min',value=int(max(df_COBS['Magn_redu']))+1,key=3)
                                with col27:
                                    ymax_slc_COBS = st.text_input('Y_Max',value=int( min(df_COBS['Magn_redu'])-1),key=4)
                        else:
                            st.warning("⚠️ No hay datos de COBS disponibles para este objeto.")
                            xmin_slc_COBS, xmax_slc_COBS, ymin_slc_COBS, ymax_slc_COBS = 0, 1, 0, 1    

                #--- VISUALIZACIÓN DE GRÁFICOS ---
             
                #------------SLC MPC-------------------------------
                with col12:
                    st.subheader("MPC - Curva de Luz Secular")
                    limites_ejes_slc = np.array([float(xmin_slc),float(xmax_slc),float(ymin_slc),float(ymax_slc)])    

                    if on_colores:
                        st.pyplot(SLC_colores(clasificacion, title=selected_object+" "+name,familia=None,intercepto=None,limites=limites_ejes_slc))
                    else:
                        st.pyplot(grafica_SLC(df, title=selected_object+" "+name,familia=None,intercepto=None,limites=limites_ejes_slc))


                #------------SLC COBS------------------------------
                with col13:
                    st.subheader(f'COBS - Curva de Luz Secular')               
                    limites_ejes_slc_COBS = np.array([float(xmin_slc_COBS),float(xmax_slc_COBS),float(ymin_slc_COBS),float(ymax_slc_COBS)])    

                    if on_colores_COBS:
                        st.pyplot(SLC_colores(clasificacion_COBS, title=selected_object+" "+name,familia=None,intercepto=None,limites=limites_ejes_slc_COBS))
                    else:
                        st.pyplot(grafica_SLC(df_COBS, title=selected_object+" "+name,familia=None,intercepto=None,limites=limites_ejes_slc_COBS))

#---------OBJETOS INTERESTELARES-----------------------------
    if st.session_state.object_type=='Objeto Interestelar':
        if st.session_state.get("datos_cargados", False):
            df_inicial = st.session_state.df_inicial
            df_inicial_COBS = st.session_state.df_inicial_COBS
            df = st.session_state.df_inicial.copy()
            df_COBS = df_inicial_COBS.copy()
            date_perihelion = st.session_state.date_perihelion
            name = st.session_state.name
            selected_object = st.session_state.selected_object
            
            # --- Barra de navegación (Tabs) ---
            tab1, tab2, tab3 = st.tabs(["Información", "Descargar datos", "Graficas preliminares"])

            #informacion
            with tab1:
                st.subheader('Información')
                st.write(f"Objeto Interestelar ID: {selected_object}")
                st.write(f"Nombre: {name}")
                st.write(f'Fecha del perihelio: {date_perihelion} (JD: {round(Time(date_perihelion.to_pydatetime(), scale="utc").jd,2)})')       

            #Descargas
            with tab2:
                st.subheader('Descargar datos')
                st.write(f'Desde {fecha_inicial.replace(' ','/')} hasta {fecha_final.replace(' ','/')}')
                col9, col10= st.columns(2)
                with col9:
                    Total_obs = len(df_inicial)
                    Total_obs_COBS = len(df_inicial_COBS)
                    st.write(f'Total observaciones en MPC: {Total_obs}')
                    st.write(f'Total observaciones en COBS: {Total_obs_COBS}')
                with col10:
                    def convert_for_download(df):
                        return df.to_csv(sep='\t', index=False, header=False).encode("utf-8")
                    txt = convert_for_download(df_inicial)
                    txt_COBS = convert_for_download(df_inicial_COBS)

                    st.download_button(label="Descargar datos MPC(.txt)",
                                    data=txt,
                                    file_name=selected_object + "_MPC.txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore")
                    st.download_button(label="Descargar datos COBS(.txt)",
                                    data=txt_COBS,
                                    file_name=selected_object + "_COBS.txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore")
        
            #GRAFICAS
            with tab3:
                col11,col12,col13 = st.columns([0.2,0.4,0.4],border=True)
                
                #Configuracion de las graficas
                with col11:
                    with st.container():
                        #Promedio corrido
                        on_prom_corr = st.toggle("**Promedio corrido**",value=False)
                        if on_prom_corr:
                            ventana = int(st.text_input('De:',value=9))
                            df = promedio_corrido(df,'Magn_redu',ventana)
                            df_COBS = promedio_corrido(df_COBS,'Magn_redu',ventana)

                        #Configuración grafico SLC MPC
                        with st.expander("⚙️ Configuración grafico de SLC MPC"):
                            col22, col23, col24 = st.columns([0.2,0.4,0.4])
                            with col22:
                                st.write('**Eje X:**')
                            with col23:
                                xmin_slc = st.text_input('X_Min',value=-max(abs(min(df['t-Tq'])),abs(max(df['t-Tq'])))-20)
                            with col24:
                                xmax_slc = st.text_input('X_Max',value= max(abs(min(df['t-Tq'])),abs(max(df['t-Tq'])))+20)
                            st.divider()
                            col25, col26, col27 = st.columns([0.2,0.4,0.4])
                            with col25:
                                st.write('**Eje Y:**')
                            with col26:
                                ymin_slc = st.text_input('Y_Min',value=int(max(df['Magn_redu']))+1,key=1)
                            with col27:
                                ymax_slc = st.text_input('Y_Max',value=int( min(df['Magn_redu'])-1),key=2)

                        #Configuración grafico SLC COBS
                        if not df_COBS.empty:
                            with st.expander("⚙️ Configuración grafico de SLC COBS"):
                                col22, col23, col24 = st.columns([0.2,0.4,0.4])
                                with col22:
                                    st.write('**Eje X:**')
                                with col23:
                                    xmin_slc_COBS = st.text_input('X_Min',value=-max(abs(min(df_COBS['t-Tq'])),abs(max(df_COBS['t-Tq'])))-20)
                                with col24:
                                    xmax_slc_COBS = st.text_input('X_Max',value= max(abs(min(df_COBS['t-Tq'])),abs(max(df_COBS['t-Tq'])))+20)
                                st.divider()
                                col25, col26, col27 = st.columns([0.2,0.4,0.4])
                                with col25:
                                    st.write('**Eje Y:**')
                                with col26:
                                    ymin_slc_COBS = st.text_input('Y_Min',value=int(max(df_COBS['Magn_redu']))+1,key=3)
                                with col27:
                                    ymax_slc_COBS = st.text_input('Y_Max',value=int( min(df_COBS['Magn_redu'])-1),key=4)
                        else:
                            st.warning("⚠️ No hay datos de COBS disponibles para este objeto.")
                            xmin_slc_COBS, xmax_slc_COBS, ymin_slc_COBS, ymax_slc_COBS = 0, 1, 0, 1    


                #--- VISUALIZACIÓN DE GRÁFICOS ---
             
                #------------SLC MPC-------------------------------
                with col12:
                    st.subheader("MPC - Curva de Luz Secular")
                    limites_ejes_slc = np.array([float(xmin_slc),float(xmax_slc),float(ymin_slc),float(ymax_slc)])    

                    st.pyplot(grafica_SLC(df, title=selected_object+" "+name,familia=None,intercepto=None,limites=limites_ejes_slc))


                #------------SLC COBS------------------------------
                with col13:
                    st.subheader(f'COBS - Curva de Luz Secular')                        
                    limites_ejes_slc_COBS = np.array([float(xmin_slc_COBS),float(xmax_slc_COBS),float(ymin_slc_COBS),float(ymax_slc_COBS)])    

                    st.pyplot(grafica_SLC(df_COBS, title=selected_object+" "+name,familia=None,intercepto=None,limites=limites_ejes_slc_COBS))

#------------------------------Footer-----------------------------------------------
#Pie de pagina
st.markdown(
    """
    <hr>
    <div style='text-align: center; color: gray;'>
        © 2025 | Datos SLC | Desarrollado por eogzaz
    </div>
    """,
    unsafe_allow_html=True
)

