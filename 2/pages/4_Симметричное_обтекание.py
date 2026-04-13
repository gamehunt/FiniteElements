import streamlit as st
import pandas as pd
 
menu = st.sidebar.radio('***',
    ("Фрагменты кода", 
    "Визуализации решения",       
    "Расчет циркуляции",
    )
)

if menu == "Фрагменты кода":
    r"""
    ##### Фрагменты кода 
    
    **Сетка**

    """
    
    code = """  
    # Загрузка сетки из файла .xml
    mesh = Mesh("mesh/1.xml")
    boundaries = MeshFunction("size_t", mesh, "mesh/1_facet_region.xml")
    
    ds = Measure("ds", subdomain_data=boundaries)
    """ 
    st.code(code, language="python") 
    
    r"""   
    
    **Конечные элементы**

    """
    
    code = """  
    # Определение функционального пространства
    V = FunctionSpace(mesh, "CG", 2)
    """ 
    st.code(code, language="python")  
      
    r"""
    
    **Граничные условия**
    
    """   
    code = """     
    # Условие на входе в канал
    u_1 = Expression("x[1]", degree=2)

    # Граничные условия
    bcs = [DirichletBC(V, Constant(0.0), boundaries, 1),
           DirichletBC(V, Constant(1.0), boundaries, 2),
           DirichletBC(V, Constant(0.5), boundaries, 5),
           DirichletBC(V, u_1, boundaries, 3)]

    """    
    st.code(code, language="python") 
    
    r"""
    
    **Формулировка задачи**
    
    """  
    code = """     
    # Вариационная задача
    u = TrialFunction(V)
    v = TestFunction(V)
    f = Constant(0.0)  
    a = dot(grad(u), grad(v)) * dx
    L = f * v * dx  
    """ 
    st.code(code, language="python")    
         
    r"""
    
    **Решение**
    
    """   
    code = """     
    # Решение задачи
    u = Function(V)
    solve(a == L, u, bcs)
    """ 
    st.code(code, language="python") 
       
    r"""
    
    **Циркуляция**
    
    """   
    code = """     
    #  Циркуляция 
    n = FacetNormal(mesh)  
    u_n = dot(grad(u), n)  
    Gamma = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=5))
    """ 
    st.code(code, language="python")    

    

    
if menu == "Визуализации решения":
    r"""
    ##### Визуализации решения
    
    """
    
    tab1, tab2, tab3 = st.tabs(["Сетка 1", "Сетка 2", "Сетка 3"])

    with tab1: 
        st.image("pages/figs/b-1.png")
    with tab2:
        st.image("pages/figs/b-2.png")
    with tab3:
        st.image("pages/figs/b-3.png")

     
if menu == "Расчет циркуляции":
    r"""
    ##### Расчет циркуляции
    
    """

    data = {
        "Сетка": ["1 - 206", "2 - 650", "3 - 2357"],
        "p = 1": ["2.14392e-03", "-9.91580e-04", "9.11410e-04"],
        "p = 2": ["1.63833e-04", "-2.11307e-05", "6.26168e-05"],
        "p = 3": ["2.42357e-05", "2.14295e-05", "2.28256e-05"]      
    }
    df = pd.DataFrame(data)

    st.table(df)
    r"""
    Точное значение: $\Gamma = 0$
    
    Рабочий вариант 
    + сетка 3 (число узлов $ - $ 2357)
    + конечно-элементная аппроксимация полиномами второй степени ($p= 2$)
    + число неизвестных $ - $ 9188
    
    
    """    
    
