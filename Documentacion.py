import streamlit as st
st.title("Documentación")
st.markdown("""
## Descripción General

 Esta aplicación web, desarrollada con Streamlit, permite la **obtención, análisis y reporte de datos astronómicos** relacionados con curvas de luz secular (SLC) de objetos del Sistema Solar, como asteroides y cometas. El objetivo principal es facilitar el acceso y procesamiento de observaciones, efemérides y resultados preliminares para investigadores y entusiastas de la astronomía.

## Estructura de la Aplicación
### Menú de Navegación

AL lado izquierdo se encuentra un menú de navegación que permite acceder a las siguientes secciones:

- **Análisis individual preliminar**:  
  Permite seleccionar un objeto astronómico, definir un rango de fechas y obtener datos observacionales y efemérides para análisis preliminar.

- **Reporte preliminar de actividad**:  
  Muestra una tabla con los resultados de análisis preliminares de múltiples objetos, permitiendo filtrar y visualizar clasificaciones y comentarios.

- **Obtención datos listado**:  
  Permite cargar una lista de objetos (por ejemplo, desde un archivo `.txt`) y obtener datos de todos ellos de manera automatizada.

- **Documentación**:  
  Sección dedicada a explicar el funcionamiento, uso y conceptos detrás de la aplicación.

            

### Datos observacionales  
El **Minor Planet Center (MPC)**, entre sus variadas funciones, se encarga de recopilar información fotométrica de cada una de las observaciones realizadas sobre cuerpos menores del sistema solar, incluyendo asteroides. Esta base de datos puede ser consultada en el enlace: [MPC Explorer](https://data.minorplanetcenter.net/explorer/).  

Ahí encontrará una aplicación web intuitiva que permite buscar un objeto, determinar su identidad y recuperar información sobre su designación, efemérides, órbita y observaciones. En este explorador propio del MPC usan la última versión de la **API de Identificador de Designación**, la cual aún está en desarrollo. Antiguamente los datos estaban en otra base de datos del MPC y aún se pueden explorar en: [MPC DB Search](https://www.minorplanetcenter.net/db_search).  

En este notebook se usa la **API oficial para las observaciones del MPC**, la cual es un endpoint **REST** y, por lo tanto, se puede usar el lenguaje de programación que se prefiera. En este caso, se utiliza **Python** para enviar solicitudes `GET` a la URL:  
👉 `https://data.minorplanetcenter.net/api/get-obs`  

---
### Datos de efemérides  
Para obtener la **magnitud absoluta**, es decir, una magnitud con la cual se puedan comparar observaciones en distintos puntos de la órbita, es necesario obtener:  

- La **distancia del asteroide al Sol (r)**  
- La **distancia a la Tierra (Δ)**  
- El **ángulo de fase (α)**  

Estos datos se pueden obtener del sistema de efemérides del **JPL**, utilizando su API oficial **Horizons File API**.  

Finalmente, calcula la magnitud absoluta de cada observación con la fórmula:  

$$
m(1,1,0) = m(\Delta, R, \\alpha) - 5 \\log(\Delta R) - \\beta \\alpha
$$
""")
