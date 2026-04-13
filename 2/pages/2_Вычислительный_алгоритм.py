import streamlit as st
from PIL import Image
 
menu = st.sidebar.radio('***',
    ("Постановка задачи", 
    "Декомпозиция решения",
    "Конечно-элементная аппроксимация",     
    )
)

if menu == "Постановка задачи":
    r"""
    ##### Постановка задачи

    **Уравнение**

    $\begin{aligned}
    {-} \nabla^2 \psi = 0,
    \quad \bm x \in \Omega
    \end{aligned}$ 
    
    **Краевые условия**
   
    Внешняя граница
    
    $\begin{aligned}
    \psi(\bm x) = 0,
    \quad \bm x \in \Gamma_1
    \end{aligned}$  
    
    $\begin{aligned}
    \psi(\bm x) = H ,
    \quad \bm x \in \Gamma_2
    \end{aligned}$     
    
    $\begin{aligned}
    \psi(\bm x) = H x_2,
    \quad \bm x \in \Gamma_3
    \end{aligned}$
    
    $\begin{aligned}
    \frac{\partial \psi}{\partial n}(\bm x)  = 0, 
    \quad \bm x \in  \Gamma_4
    \end{aligned}$
    
    Внутренняя граница 
    
    $\begin{aligned}
    \psi (\bm x) = \operatorname{const} ,
    \quad \bm x \in \gamma ,
    \quad \oint_{\gamma} \frac{\partial \psi}{\partial n}(\bm x)  d \bm x = \Gamma
    \end{aligned}$      
              
    """

if menu == "Декомпозиция решения":
    r"""
    ##### Декомпозиция решения 
     
    **Решение**

    $\begin{aligned}
    \psi (\bm x) = \psi_1(\bm x) + \varkappa \, \psi_2(\bm x) ,
    \quad \varkappa = \operatorname{const} 
    \end{aligned}$   
    
    **Задача для** $\psi_1(\bm x)$
    
    $\begin{aligned}
    {-} \nabla^2 \psi_1 = 0,
    \quad \bm x \in \Omega
    \end{aligned}$   
    
    $\begin{aligned}
    \psi_1(\bm x) = 0,
    \quad \bm x \in \Gamma_1
    \end{aligned}$  
    
    $\begin{aligned}
    \psi_1(\bm x) = H ,
    \quad \bm x \in \Gamma_2
    \end{aligned}$     
    
    $\begin{aligned}
    \psi_1(\bm x) = H x_2,
    \quad \bm x \in \Gamma_3
    \end{aligned}$
    
    $\begin{aligned}
    \frac{\partial \psi_1}{\partial n}(\bm x)  = 0, 
    \quad \bm x \in  \Gamma_4
    \end{aligned}$

    $\begin{aligned}
    \psi_1 (\bm x) = 0 ,
    \quad \bm x \in \gamma 
    \end{aligned}$  
    
    **Задача для** $\psi_2(\bm x)$
    
    $\begin{aligned}
    {-} \nabla^2 \psi_2 = 0,
    \quad \bm x \in \Omega
    \end{aligned}$   
    
    $\begin{aligned}
    \psi_2(\bm x) = 0,
    \quad \bm x \in \Gamma_1 + \Gamma_2 + \Gamma_3
    \end{aligned}$  
      
    $\begin{aligned}
    \frac{\partial \psi_2}{\partial n}(\bm x)  = 0, 
    \quad \bm x \in  \Gamma_4
    \end{aligned}$

    $\begin{aligned}
    \psi_2 (\bm x) = 1 ,
    \quad \bm x \in \gamma 
    \end{aligned}$   
     
    **Постоянная** $\varkappa$
      
    $\begin{aligned}
    \varkappa = 
    \left ( \Gamma - \oint_{\gamma} \frac{\partial \psi_1}{\partial n}(\bm x)  d \bm x \right )
    \left ( \oint_{\gamma} \frac{\partial \psi_2}{\partial n}(\bm x)  d \bm x \right )^{-1}
    \end{aligned}$     

    """
    
if menu == "Конечно-элементная аппроксимация":

    r"""
    ##### Конечно-элементная аппроксимация
    
    Задача свелась к решению двух смешанных краевых задач для уравнения Лапласа
    
    **Интегро-дифференциальные равенства**
    
    Например, $\psi_2(\bm x) \in V$ из выполнения
    
    $\begin{aligned}
    \int_{\Omega} \nabla \psi_2 \cdot  \nabla v \, d \bm x = 0 ,
    \quad \bm x \in \gamma
    \end{aligned}$   
    
    для всех $v(\bm x) \in V_0$
    
    Пространства
    
    + $V = \{ v \, | \, v \in H^1(\Omega) , \ v(\bm x) = 0 , \ \bm x \in \Gamma_1 + \Gamma_2 + \Gamma_3, \ v(\bm x) = 1 , \ \bm x \in \gamma \}$
    + $V_0 = \{ v \, | \, v \in H^1(\Omega) , \ v(\bm x) = 0 , \ \bm x \in \Gamma_1 + \Gamma_2 + \Gamma_3 + \gamma \}$   
    
   **Конечно-элементная аппроксимация**
   
    Конечномерные подпространства 
   
    $\begin{aligned}
    V^h \subset V,
    \quad V^h_0 \subset V_0
    \end{aligned}$   
    
    + треугольные сетки
    + лагранжевые конечные элементы степени $p=1, 2$    
    
    **Нестандартный элемент**
    
    Вычисление интегралов
    
    $\begin{aligned}
    \oint_{\gamma} \frac{\partial \psi_i}{\partial n}(\bm x)  d \bm x ,
    \quad i = 1,2
    \end{aligned}$     
 
   """
   
   
   
