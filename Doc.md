# Documentación de la Página: Datos para Curva de Luz Secular (SLC)

## Descripción General

Esta aplicación web, desarrollada con Streamlit, permite la **obtención, análisis y reporte de datos astronómicos** relacionados con curvas de luz secular (SLC) de objetos del Sistema Solar, como asteroides y cometas. El objetivo principal es facilitar el acceso y procesamiento de observaciones, efemérides y resultados preliminares para investigadores y entusiastas de la astronomía.

---

## Estructura de la Página

### 1. Banner Principal

Al inicio, la página muestra un banner visual con el título:

> ☄️Datos para Curva de luz secular (SLC)

Este banner utiliza un fondo degradado y texto destacado para resaltar el propósito de la aplicación.

---

### 2. Menú de Navegación

Debajo del banner, se encuentra un menú de navegación que permite acceder a las siguientes secciones:

- **Análisis individual preliminar** (`main.py`):  
  Permite seleccionar un objeto astronómico, definir un rango de fechas y obtener datos observacionales y efemérides para análisis preliminar.

- **Reporte preliminar de actividad** (`reporte.py`):  
  Muestra una tabla con los resultados de análisis preliminares de múltiples objetos, permitiendo filtrar y visualizar clasificaciones y comentarios.

- **Obtención datos listado** (`listado.py`):  
  Permite cargar una lista de objetos (por ejemplo, desde un archivo `.txt`) y obtener datos de todos ellos de manera automatizada.

- **Documentación** (`Documentacion.py`):  
  Sección dedicada a explicar el funcionamiento, uso y conceptos detrás de la aplicación.

---

## Funcionalidades Principales

- Selección de objetos astronómicos por identificador MPC.
- Definición de rangos de fechas para filtrar observaciones.
- Obtención automática de datos desde fuentes externas (MPC, COBS, etc.).
- Procesamiento y análisis preliminar de curvas de luz secular.
- Visualización de resultados en tablas y gráficos.
- Reporte y clasificación de actividad de objetos.
- Exportación y almacenamiento de resultados en bases de datos externas (Supabase).

---

## Público Objetivo

- Investigadores en astronomía y ciencias planetarias.
- Estudiantes y docentes interesados en análisis de datos astronómicos.
- Entusiastas de la observación astronómica.

---

## Recomendaciones de Uso

1. Navega por las secciones usando el menú lateral.
2. Ingresa los identificadores y parámetros solicitados en cada sección.
3. Analiza los resultados y utiliza las herramientas de reporte y exportación según tus necesidades.
4. Consulta la sección de documentación para detalles técnicos y ejemplos de uso.

---

## Contacto y Soporte

Para dudas, sugerencias o reportes de errores, consulta la sección de **Documentación** o contacta al desarrollador principal del proyecto.

---

**¡Explora, analiza y contribuye al conocimiento astronómico con esta herramienta!**