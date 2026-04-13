import streamlit as st
import pandas as pd
 
menu = st.sidebar.radio('***',
    ("Фрагменты кода", 
    "Расчетные данные",
    )
)

if menu == "Фрагменты кода":
    r"""
    ##### Фрагменты кода 
    
    **Украшательство**

    """
    
    code = """  
    import matplotlib.patches as patches
    
    # Круговая стрелка
    ax = plt.gca()
    arc = patches.Arc([0.75,0.5],0.2,0.2,0,0,250,color='black')
    ax.add_patch(arc)
    endX=0.75+0.1*np.cos(np.radians(250)) #Do trig to determine end position
    endY=0.5+0.1*np.sin(np.radians(250))
    ax.add_patch(patches.RegularPolygon((endX, endY),3, 0.2/9, np.radians(250),color='black'))
    """ 
    st.code(code, language="python") 
           
if menu == "Расчетные данные":
    r"""
    ##### Расчетные данные
    
    """
    
    tab1, tab2, tab3 = st.tabs(["$\Gamma$ = 0", "$\Gamma$ = 0.5", "$\Gamma$  = 1"])

    with tab1: 
        st.image("pages/figs/c-1.png")
    with tab2:
        st.image("pages/figs/c-2.png")
    with tab3:
        st.image("pages/figs/c-3.png")
        
    r"""        
    Функция тока $\psi = c = \operatorname{const}$ на границе цилиндра
    
    """

    data = {
        "Циркуляция": ["0", "0.5", "1"],
        "c": ["4.99988e-01", "5.96104e-01", "6.92220e-01"],
    }
    df = pd.DataFrame(data)

    st.table(df)
    
    r"""
    
    Для $\Gamma = 0$ точное значение: $\ c = 0.5$
    """
    
    
