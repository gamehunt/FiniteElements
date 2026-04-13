import streamlit as st
import pandas as pd
 
menu = st.sidebar.radio('***',
    ("Фрагменты кода", 
    "Симметричное обтекание",       
    "Несимметричное обтекание",
    )
)

if menu == "Фрагменты кода":
    r"""
    ##### Фрагменты кода 
    
    **Первая задача декомпозиции**

    """
    
    code = """  
    # Решение первой вспомогательной задачи

    # Граничные условия
    bcs1 = [DirichletBC(V, Constant(0.0), boundaries, 1),
           DirichletBC(V, Constant(1.0), boundaries, 2),
           DirichletBC(V, Constant(0.0), boundaries, 5),
           DirichletBC(V, u_1, boundaries, 3)]

    # Вариационная задача
    a = dot(grad(u), grad(v)) * dx
    L = f * v * dx

    # Решение задачи
    u1 = Function(V)
    solve(a == L, u1, bcs1)

    #  Циркуляция u1
    u_n = dot(grad(u1), n)  
    circ1 = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=5))
    print(f"Циркуляция поля u1: {circ1:.5e}")
    """ 
    st.code(code, language="python") 
    
    r"""   
    
    **Вторая задача декомпозиции**

    """
    
    code = """  
    # Решение второй вспомогательной задачи

    # Граничные условия
    bcs2 = [DirichletBC(V, Constant(0.0), boundaries, 1),
           DirichletBC(V, Constant(0.0), boundaries, 2),
           DirichletBC(V, Constant(1.0), boundaries, 5),
           DirichletBC(V, Constant(0.0), boundaries, 3)]

    # Вариационная задача
    a = dot(grad(u), grad(v)) * dx
    L = f * v * dx

    # Решение задачи
    u2 = Function(V)
    solve(a == L, u2, bcs2)

    #  Циркуляция u2
    u_n = dot(grad(u2), n)  
    circ2 = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=5))
    print(f"Циркуляция поля u2: {circ2:.5e}")
    """ 
    st.code(code, language="python")  
      
    r"""
    
    **Расчет параметра декомпозиции**
    
    """   
    code = """     
    # Параметр взвешивания
    kappa = (Gamma - circ1)/circ2
    """    
    st.code(code, language="python") 
           
    r"""
    
    **Решение**
    
    """   
    code = """     
    # Значения решения в узлах сетки
    u_values = u1.compute_vertex_values(mesh) + kappa*u2.compute_vertex_values(mesh)
    """ 
    st.code(code, language="python") 
    
if menu == "Симметричное обтекание":
    r"""
    ##### Симметричное обтекание
    
    Неподвижный цилиндр: $\ \Gamma = 0$
    
    """
    
    tab1, tab2, tab3 = st.tabs(["Решение 1", "Решение 2", "Решение задачи"])

    with tab1: 
        st.image("pages/figs/n-1.png")
    with tab2:
        st.image("pages/figs/n-2.png")
    with tab3:
        st.image("pages/figs/n-3.png")

     
if menu == "Несимметричное обтекание":
    r"""
    ##### Несимметричное обтекание
    
    """
    
    tab1, tab2, tab3 = st.tabs(["h = 0.5", "h = 0.4", "h = 0.3"])

    with tab1: 
        st.image("pages/figs/h-1.png")
    with tab2:
        st.image("pages/figs/h-2.png")
    with tab3:
        st.image("pages/figs/h-3.png")
        
    r"""        
    Функция тока $\psi = c = \operatorname{const}$ на границе цилиндра
    
    """

    data = {
        "Положение цилиндра": ["h = 0.5", "h = 0.4", "h = 0.3"],
        "c": ["4.99988e-01", "3.79969e-01", "2.52257e-01"],
    }
    df = pd.DataFrame(data)

    st.table(df)
    
    r"""
    
    Для $h = 0.5$ точное значение: $\ c = 0.5$
    """
    
    
