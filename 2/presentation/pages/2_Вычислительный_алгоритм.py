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
    - \Delta \psi = 0, \quad \bm x \in \Omega .
    $$

    **Краевые условия**

    На внешних границах канала $\Gamma_1, \Gamma_2, \Gamma_3, \Gamma_4$ задаются условия:

    $$
    \psi(\bm x) = 0, \quad \bm x \in \Gamma_1,
    \qquad
    \psi(\bm x) = H, \quad \bm x \in \Gamma_2,
    $$

    $$
    \psi(\bm x) = x_2, \quad \bm x \in \Gamma_3,
    \qquad
    \frac{\partial \psi}{\partial n}(\bm x) = 0, \quad \bm x \in \Gamma_4 .
    $$

    На границах цилиндров $\gamma_1$ и $\gamma_2$ функция тока постоянна, а циркуляции равны нулю:

    $$
    \psi(\bm x) = c_\alpha, \quad \bm x \in \gamma_\alpha,
    \qquad
    \oint_{\gamma_\alpha} \frac{\partial \psi}{\partial n}(\bm x) \, ds = 0,
    \quad \alpha = 1,2 .
    $$
    """

if menu == "Декомпозиция решения":
    st.markdown("### Декомпозиция решения")

    st.markdown(r"""
    Решение строится как сумма базового поля и вкладов от двух цилиндров.
    Базовое поле описывает поток в канале при нулевых значениях на цилиндрах,
    а вспомогательные поля отвечают за единичные значения функции тока на
    границах $\gamma_1$ и $\gamma_2$.
    """)

    st.markdown("**Представление решения:**")
    st.markdown(r"""
    $$
    \psi(\bm x) = \psi_0(\bm x) + \kappa_1 \psi_1(\bm x) + \kappa_2 \psi_2(\bm x).
    $$
    """)

    st.markdown(r"""
    $\psi_0$ — базовое поле течения; $\psi_1$ и $\psi_2$ — вклады первого и второго
    цилиндров; $\kappa_1$ и $\kappa_2$ — коэффициенты линейной комбинации,
    выбираемые из условия нулевой циркуляции на цилиндрах.
    """)

    st.markdown(r"**Задача для $\psi_0(\bm x)$:**")
    st.markdown(r"""
    $$
    -\Delta \psi_0 = 0, \quad \bm x \in \Omega
    $$
    $$
    \psi_0 = 0, \quad \bm x \in \Gamma_1,
    \qquad
    \psi_0 = H, \quad \bm x \in \Gamma_2
    $$
    $$
    \psi_0 = x_2, \quad \bm x \in \Gamma_3,
    \qquad
    \frac{\partial \psi_0}{\partial n} = 0, \quad \bm x \in \Gamma_4
    $$
    $$
    \psi_0 = 0, \quad \bm x \in \gamma_1 \cup \gamma_2
    $$
    """)

    st.markdown(r"**Задача для $\psi_1(\bm x)$:**")
    st.markdown(r"""
    $$
    -\Delta \psi_1 = 0, \quad \bm x \in \Omega
    $$
    $$
    \psi_1 = 0, \quad \bm x \in \Gamma_1 \cup \Gamma_2 \cup \Gamma_3,
    \qquad
    \frac{\partial \psi_1}{\partial n} = 0, \quad \bm x \in \Gamma_4
    $$
    $$
    \psi_1 = 1, \quad \bm x \in \gamma_1,
    \qquad
    \psi_1 = 0, \quad \bm x \in \gamma_2
    $$
    """)

    st.markdown(r"**Задача для $\psi_2(\bm x)$:**")
    st.markdown(r"""
    $$
    -\Delta \psi_2 = 0, \quad \bm x \in \Omega
    $$
    $$
    \psi_2 = 0, \quad \bm x \in \Gamma_1 \cup \Gamma_2 \cup \Gamma_3,
    \qquad
    \frac{\partial \psi_2}{\partial n} = 0, \quad \bm x \in \Gamma_4
    $$
    $$
    \psi_2 = 0, \quad \bm x \in \gamma_1,
    \qquad
    \psi_2 = 1, \quad \bm x \in \gamma_2
    $$
    """)

    st.markdown(r"**Определение коэффициентов $\kappa_1, \kappa_2$:**")
    st.markdown(r"""
    Коэффициенты находятся из условия нулевой циркуляции итогового поля
    на границах цилиндров $\gamma_1$ и $\gamma_2$.
    """)
    st.markdown(r"""
    $$
    \begin{pmatrix}
        \displaystyle \oint_{\gamma_1} \frac{\partial \psi_1}{\partial n}\, ds &
        \displaystyle \oint_{\gamma_1} \frac{\partial \psi_2}{\partial n}\, ds \\
        \displaystyle \oint_{\gamma_2} \frac{\partial \psi_1}{\partial n}\, ds &
        \displaystyle \oint_{\gamma_2} \frac{\partial \psi_2}{\partial n}\, ds
    \end{pmatrix}
    \begin{pmatrix}
        \kappa_1 \\
        \kappa_2
    \end{pmatrix}
    =
    -
    \begin{pmatrix}
        \displaystyle \oint_{\gamma_1} \frac{\partial \psi_0}{\partial n}\, ds \\
        \displaystyle \oint_{\gamma_2} \frac{\partial \psi_0}{\partial n}\, ds
    \end{pmatrix}.
    $$
    """)

if menu == "Конечно-элементная аппроксимация":
    st.markdown("### Конечно-элементная аппроксимация")

    st.markdown(r"""
    Задача сводится к решению смешанных краевых задач для уравнения Лапласа
    с едиными обозначениями внешних границ $\Gamma_1, \Gamma_2, \Gamma_3, \Gamma_4$
    и границ цилиндров $\gamma_1, \gamma_2$.
    """)

    st.markdown("**Интегро-дифференциальные равенства**")

    st.markdown(r"Например, для $\psi_1(\bm x) \in V$ выполняется:")

    st.markdown(r"""
    $$
    \int_{\Omega} \nabla \psi_1 \cdot \nabla v \, d\bm x = 0
    $$
    """)

    st.markdown(r"для всех $v(\bm x) \in V_0$.")

    st.markdown("**Пространства**")

    st.markdown(r"""
    $$
    V = \{ v \mid v \in H^1(\Omega),\ v = 0 \text{ на } \Gamma_1,
    \ v = H \text{ на } \Gamma_2,
    \ v = x_2 \text{ на } \Gamma_3,
    \ v = c_\alpha \text{ на } \gamma_\alpha,\ \alpha = 1,2 \}
    $$

    $$
    V_0 = \{ v \mid v \in H^1(\Omega),\ v = 0 \text{ на }
    \Gamma_1 \cup \Gamma_2 \cup \Gamma_3 \cup \gamma_1 \cup \gamma_2 \}
    $$
    """)

    st.markdown("**Конечно-элементная аппроксимация**")

    st.markdown("Конечномерные подпространства")

    st.markdown(r"""
    $$
    V^h \subset V, \quad V_0^h \subset V_0
    $$
    """)

    st.markdown(r"""
    - треугольные сетки;
    - лагранжевые конечные элементы степени $p = 1,2,3$.
    """)

    st.markdown("**Нестандартный элемент**")

    st.markdown("Вычисление интегралов по границам цилиндров")

    st.markdown(r"""
    $$
    \oint_{\gamma_k} \frac{\partial \psi_i}{\partial n}(\bm x)\, ds,
    \quad i = 0,1,2,\quad k = 1,2 .
    $$
    """)
