import streamlit as st

menu = st.sidebar.radio(
    "***",
    (
        "Постановка задачи",
        "Декомпозиция решения",
        "Конечно-элементная аппроксимация",
    ),
)

if menu == "Постановка задачи":
    r"""
    ##### Постановка задачи
    
    **Уравнение**
    
    $$
    - \Delta \psi = 0, \quad \mathbf{x} \in \Omega
    $$
    
    **Краевые условия**
    
    Внешняя граница
    
    $$
    \psi(\mathbf{x}) = 0, \quad \mathbf{x} \in \Gamma_1
    $$
    
    $$
    \psi(\mathbf{x}) = H, \quad \mathbf{x} \in \Gamma_2
    $$
    
    $$
    \psi(\mathbf{x}) = H x_2, \quad \mathbf{x} \in \Gamma_3
    $$
    
    $$
    \frac{\partial \psi}{\partial n}(\mathbf{x}) = 0, \quad \mathbf{x} \in \Gamma_4
    $$
    
    Внутренняя граница 
    
    $$
    \psi(\mathbf{x}) = \mathrm{const}, \quad \mathbf{x} \in \gamma,
    \quad \oint_{\gamma} \frac{\partial \psi}{\partial n}(\mathbf{x}) \, d\mathbf{x} = \Gamma
    $$
    """

if menu == "Декомпозиция решения":
    st.markdown("### Декомпозиция решения")

    st.markdown("**Решение:**")
    st.markdown(r"""
    $$
    \psi(x) = \psi_1(x) + \kappa_1 \psi_2(x) + \kappa_2 \psi_3(x)
    $$
    """)

    st.markdown("**Задача для $\psi_1(x)$:**")
    st.markdown(r"""
    $$
    -\Delta \psi_1 = 0, \quad x \in \Omega
    $$
    $$
    \psi_1 = 0, \quad x \in \Gamma_1
    $$
    $$
    \psi_1 = H, \quad x \in \Gamma_2
    $$
    $$
    \psi_1 = x_2, \quad x \in \Gamma_3
    $$
    $$
    \frac{\partial \psi_1}{\partial n} = 0, \quad x \in \Gamma_4
    $$
    $$
    \psi_1 = 0, \quad x \in \gamma_1
    $$
    $$
    \psi_1 = 0, \quad x \in \gamma_2
    $$
    """)

    st.markdown("**Задача для $\psi_2(x)$:**")
    st.markdown(r"""
    $$
    -\Delta \psi_2 = 0, \quad x \in \Omega
    $$
    $$
    \psi_2 = 0, \quad x \in \Gamma_1 \cup \Gamma_2 \cup \Gamma_3
    $$
    $$
    \frac{\partial \psi_2}{\partial n} = 0, \quad x \in \Gamma_4
    $$
    $$
    \psi_2 = 1, \quad x \in \gamma_1
    $$
    $$
    \psi_2 = 0, \quad x \in \gamma_2
    $$
    """)

    st.markdown("**Задача для $\psi_3(x)$:**")
    st.markdown(r"""
    $$
    -\Delta \psi_3 = 0, \quad x \in \Omega
    $$
    $$
    \psi_3 = 0, \quad x \in \Gamma_1 \cup \Gamma_2 \cup \Gamma_3
    $$
    $$
    \frac{\partial \psi_3}{\partial n} = 0, \quad x \in \Gamma_4
    $$
    $$
    \psi_3 = 0, \quad x \in \gamma_1
    $$
    $$
    \psi_3 = 1, \quad x \in \gamma_2
    $$
    """)

    st.markdown("**Постоянные $\kappa_1, \kappa_2$:**")
    st.markdown(r"""
    $$
    \begin{pmatrix}
        \displaystyle \oint_{\gamma_1} \frac{\partial \psi_2}{\partial n} dx &
        \displaystyle \oint_{\gamma_2} \frac{\partial \psi_2}{\partial n} dx \\
        \displaystyle \oint_{\gamma_1} \frac{\partial \psi_3}{\partial n} dx &
        \displaystyle \oint_{\gamma_2} \frac{\partial \psi_3}{\partial n} dx
    \end{pmatrix}
    \begin{pmatrix}
        \kappa_1 \\
        \kappa_2
    \end{pmatrix}
    =
    \begin{pmatrix}
        -\Gamma_1 \\
        -\Gamma_2
    \end{pmatrix}
    $$
    """)

if menu == "Конечно-элементная аппроксимация":
    st.markdown("### Конечно-элементная аппроксимация")

    st.markdown(
        "Задача свелась к решению трёх смешанных краевых задач для уравнения Лапласа"
    )

    st.markdown("**Интегро-дифференциальные равенства**")

    st.markdown("Например, $\\psi_2(x) \\in V$ из выполнения:")

    st.markdown(r"""
    $$
    \int_{\Omega} \nabla \psi_2 \cdot \nabla v \, dx = 0
    $$
    """)

    st.markdown("для всех $v(x) \\in V_0$")

    st.markdown("**Пространства**")

    st.markdown(r"""
    $$
    V = \{ v \mid v \in H^1(\Omega),\ v = 0 \text{ на } \Gamma_1 \cup \Gamma_3,\ v = H \text{ на } \Gamma_2,\ v = c_\alpha \text{ на } \gamma_\alpha \}
    $$
    
    $$
    V_0 = \{ v \mid v \in H^1(\Omega),\ v = 0 \text{ на } \Gamma_1 \cup \Gamma_2 \cup \Gamma_3 \cup \gamma_1 \cup \gamma_2 \}
    $$
    """)

    st.markdown("**Конечно-элементная аппроксимация**")

    st.markdown("Конечномерные подпространства")

    st.markdown(r"""
    $$
    V^h \subset V, \quad V_0^h \subset V_0
    $$
    """)

    st.markdown("""
    - треугольные сетки  
    - лагранжевые конечные элементы степени $p = 1,2,3$
    """)

    st.markdown("**Нестандартный элемент**")

    st.markdown("Вычисление интегралов")

    st.markdown(r"""
    $$
    \oint_{\gamma_k} \frac{\partial \psi_i}{\partial n}(x)\, dx,
    \quad i = 1,2,3,\ k = 1,2
    $$
    """)
