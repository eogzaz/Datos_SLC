import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from cleaning_data import Date_to_julian

 # Función de filtrado
def fase_menor_5(data_sin_editar,desde=5):
  data = data_sin_editar.copy()
  fase = data['Fase'].to_numpy()
  data['Fase'] = np.where(fase < desde, np.nan, fase)
  return data.dropna().reset_index(drop=True)

def grafica_fase(df, alpha_max,magn_max,title='none', familia='none', recta_pendiente=False, pendiente_param = [],limites=np.array([0,35,17,10])):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 

    fig, ax = plt.subplots(figsize=(6, 5))

    ax.plot(df['Fase'], df['Magn_redu'].astype(float), 'o', markerfacecolor='cyan', markeredgecolor='blue', markersize=2)
    
    if recta_pendiente==True:
        x = np.linspace(0,40,100)
        pendiente = pendiente_param[0]
        intercep = pendiente_param[1]
        y = intercep + pendiente*x
        ax.plot(x,y,'r-', linewidth=3, label=f'm(1,1,0) = {round(intercep,2)} + {pendiente:.2}α')
        #ax.plot(alpha_max,magn_max,'o', markerfacecolor='red', markeredgecolor='red', markersize=5)
        ax.legend()
    
    if not familia==None:
        ax.set_title(f'{title} ({familia}) - Curva de Fase')
    else:
        ax.set_title(f'{title} - Curva de Fase')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel('α [°]')
    ax.set_ylabel('m(1,1,α)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig

def calc_envolvente(df, bin_width=0.1):
    alpha = df['Fase'].copy().to_numpy()
    m_red = df['Magn_redu'].copy().to_numpy()
    
    brightest_alpha = []
    brightest_mag = []

    for a_min in np.arange(min(alpha), max(alpha), bin_width):
        mask = (alpha >= a_min) & (alpha < a_min + bin_width)
        if np.any(mask):
            idx = np.argmin(m_red[mask])  # punto más brillante
            brightest_alpha.append(alpha[mask][idx])
            brightest_mag.append(m_red[mask][idx])

    brightest_alpha = np.array(brightest_alpha)
    brightest_mag = np.array(brightest_mag)

    slope, intercept, r_value, _, _ = linregress(brightest_alpha, brightest_mag)
    r2 = r_value**2

    return [slope, intercept,brightest_alpha,brightest_mag]

def grafica_SLC(df, title='none', familia='none', intercepto=1, limites=np.array([-800,800,17,10]) ):
  xmin = float(limites[0])
  xmax = float(limites[1])
  ymin = float(limites[2]) 
  ymax = float(limites[3]) 

  fig, ax = plt.subplots(figsize=(6, 5))

  # Second plot (SLC)
  ax.plot(df['t-Tq'], df['Magn_redu'].astype(float), 'o', markerfacecolor='cyan', markeredgecolor='blue', markersize=2)
  
  if not intercepto==None:
    x=np.linspace(xmin,xmax,100)
    y=np.ones_like(np.linspace(xmin,xmax,100))*intercepto
    ax.plot(x,y,'r-', linewidth=3)

  ax.set_ylim(ymin, ymax)
  ax.set_xlim(xmin, xmax)

  if not familia==None:
    ax.set_title(f'{title} ({familia}) - SLC')
  else:
    ax.set_title(f'{title}  - SLC')

  ax.set_xlabel('t-Tq [días]')
  ax.set_ylabel('m(1,1,α)')
  ax.tick_params(direction='in')
  ax.grid()

  return fig

def grafica_SLC_corr(df, title='none', familia='none', intercepto=1, limites=np.array([-800,800,17,10]) ):
  xmin = float(limites[0])
  xmax = float(limites[1])
  ymin = float(limites[2]) 
  ymax = float(limites[3]) 

  fig, ax = plt.subplots(figsize=(6, 5))

  # Second plot (SLC)
  ax.plot(df['t-Tq'], df['Magn_Corr_Fase'].astype(float), 'o', markerfacecolor='cyan', markeredgecolor='blue', markersize=2)
 
  if not intercepto==None:
    x=np.linspace(xmin,xmax,100)
    y=np.ones_like(np.linspace(xmin,xmax,100))*intercepto
    ax.plot(x,y,'r-', linewidth=3)
 
  ax.set_ylim(ymin, ymax)
  ax.set_xlim(xmin, xmax)

  if not familia==None:
    ax.set_title(f'{title} ({familia}) - SLC corr Fase')
  else:
    ax.set_title(f'{title}  - SLC corr Fase')

  ax.set_xlabel('t-Tq [días]')
  ax.set_ylabel('m(1,1,0)')
  ax.tick_params(direction='in')
  ax.grid()

  return fig


def clasificacion_periodos(df,periodo, perihelio):
    df['Date']= [str(df['Anio'][i])+' '+str(df['Mes'][i])+' '+str(df['Dia'][i]) for i in range(len(df))]
    df['JD'] = df['Date'].apply(Date_to_julian)

    num_periodos = int((max(df['JD'])-min(df['JD']))/periodo)+3
    if max(df['JD'])<perihelio:
        limites_entre_periodos = np.ones(num_periodos)
        for i in range(0,num_periodos):
            limites_entre_periodos[i]= perihelio-periodo*i
    else:
        limites_entre_periodos = np.ones(num_periodos)
        for i in range(num_periodos):
            limites_entre_periodos[i]= perihelio-periodo*(i-1)
            
    dic = {}
    for j in range(1,num_periodos):
        array1=df['JD']<limites_entre_periodos[j-1]
        array2=limites_entre_periodos[j]<=df['JD']
        boleanos = [int(a) * int(b) for a, b in zip(array1, array2)]
        b=pd.Series([bool(i) for i in boleanos])
        dic[j-1]=df.where(b).dropna()

    return dic, limites_entre_periodos

def grafica_fase_colores(dic, title='none', familia='none', recta_pendiente=False, pendiente_param = [],limites=np.array([0,35,17,10])):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 

    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['Fase'],dic[i]['Magn_redu'],'o',markersize=2)
    
    if recta_pendiente==True:
        x = np.linspace(0,40,100)
        pendiente = pendiente_param[0]
        intercep = pendiente_param[1]
        y = intercep + pendiente*x
        ax.plot(x,y,'r-', linewidth=3, label=f'm(1,1,0) = {round(intercep,2)} + {pendiente:.2}α')
        ax.legend()
    
    if not familia==None:
        ax.set_title(f'{title} ({familia}) - Curva de Fase')
    else:
        ax.set_title(f'{title} - Curva de Fase')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel('α [°]')
    ax.set_ylabel('m(1,1,α)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig

def SLC_colores(dic, title='none', familia='none', intercepto=1, limites=np.array([-800,800,17,10]) ):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 
    
 
    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['t-Tq'],dic[i]['Magn_redu'],'o',markersize=2)

    if not intercepto==None:
        x=np.linspace(xmin,xmax,100)
        y=np.ones_like(np.linspace(xmin,xmax,100))*intercepto
        ax.plot(x,y,'r-', linewidth=3)
   
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(xmin, xmax)

    if not familia==None:
        ax.set_title(f'{title} ({familia}) - SLC colores')
    else:
        ax.set_title(f'{title}  - SLC colores')

    ax.set_xlabel('t-Tq [días]')
    ax.set_ylabel('m(1,1,α)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig

def SLC_colores_corr(dic, title='none', familia='none', intercepto=1, limites=np.array([-800,800,17,10]) ):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 

    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['t-Tq'],dic[i]['Magn_Corr_Fase'],'o',markersize=2)

    x=np.linspace(xmin,xmax,100)
    y=np.ones_like(np.linspace(xmin,xmax,100))*intercepto
    ax.plot(x,y,'r-', linewidth=3)
   
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(xmin, xmax)

    if not familia==None:
        ax.set_title(f'{title} ({familia}) - SLC corr Fase colores')
    else:
        ax.set_title(f'{title}  - SLC corr Fase colores')

    ax.set_xlabel('t-Tq [días]')
    ax.set_ylabel('m(1,1,0)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig

