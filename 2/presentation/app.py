from pathlib import Path
import sys

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from presentation_data import (  # noqa: E402
    build_circulation_chart,
    build_geometry_figure,
    build_mesh_figure,
    build_solution_figure,
    discover_mesh_cases,
    family_title,
    format_geometry_parameters,
    group_cases,
    safe_first,
)
from solve import solve_problem  # noqa: E402


MESH_ROOT = ROOT_DIR / "mesh"

st.set_page_config(
    page_title="МКЭ: обтекание двух цилиндров",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_cases():
    return discover_mesh_cases(MESH_ROOT)


cases = load_cases()
grouped = group_cases(cases)
reference_case = safe_first(grouped["distance"]) or safe_first(grouped["base"]) or safe_first(cases)
slide_titles = [
    "Титульный слайд",
    "Постановка задачи",
    "Расчётная область",
    "Граничные условия и параметры задачи",
    "Расчётные сетки",
    "Конечно-элементная аппроксимация",
    "Выбор степени полинома p",
    "Численные решения",
    "Сравнение результатов и циркуляция",
    "Выводы",
]

st.sidebar.title("Доклад по задаче")
selected_slide = st.sidebar.radio("Раздел", slide_titles)
selected_degree = st.sidebar.selectbox("Степень аппроксимации p", [1, 2, 3], index=1)
st.sidebar.markdown("---")


def render_title():
    st.title("Численное решение задачи обтекания области с двумя цилиндрами методом конечных элементов")
    st.markdown(
        """
        **Тема доклада**  
        Потенциальное обтекание двух цилиндров в плоском канале.

        **Содержание**  
        Постановка задачи, расчётная область, сетки, конечно-элементная аппроксимация,
        симметричные и несимметричные сценарии, а также сравнение вычисляемых характеристик.
        """
    )
    st.info(f"Текущее значение степени аппроксимации: p = {selected_degree}.")


def render_problem():
    st.header("Постановка задачи")
    st.markdown(
        r"""
        Рассматривается стационарная задача для функции тока $\psi$ в двумерной области канала,
        содержащей два цилиндрических препятствия.

        $$
        - \nabla^2 \psi = 0, \qquad \mathbf{x} \in \Omega.
        $$

        **Классы вычислительных сценариев**
        - симметричные сценарии: изменение продольной координаты второго цилиндра;
        - несимметричные сценарии: изменение вертикальной координаты второго цилиндра;
        - базовая последовательность сеток: изменение параметра дискретизации.
        """
    )


def render_domain():
    st.header("Расчётная область")
    if reference_case is None:
        st.warning("В репозитории не найдены данные для построения расчётной области.")
        return

    st.pyplot(build_geometry_figure(reference_case), use_container_width=True)
    st.markdown(
        r"""
        **Обозначения**
        - $\Omega$ — область течения.
        - $D_1$, $D_2$ — цилиндры.
        - $\Gamma_1$, $\Gamma_2$ — стенки канала.
        - $\Gamma_3$, $\Gamma_4$ — входная и выходная границы.
        """
    )
    parameter_cols = st.columns(4)
    values = dict(format_geometry_parameters(reference_case.parameters))
    for index, key in enumerate(["L", "H", "r_1", "r_2"]):
        if key in values:
            parameter_cols[index].metric(key, values[key])


def render_boundary_conditions():
    st.header("Граничные условия и параметры задачи")
    if reference_case is None:
        st.warning("Недостаточно данных для отображения параметров задачи.")
        return

    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.markdown(
            r"""
            **Граничные условия**
            - на входе: $\psi = x_2$;
            - на выходе: $\dfrac{\partial \psi}{\partial n} = 0$;
            - на верхней и нижней стенках: $\psi = \mathrm{const}$;
            - на границах цилиндров: $\psi = \mathrm{const}$.
            """
        )
        st.markdown(
            """
            **Параметрические серии**
            - по расстоянию между цилиндрами;
            - по вертикальному смещению второго цилиндра;
            - по сеточному сгущению.
            """
        )
    with col_right:
        st.markdown("**Геометрические параметры базового сценария**")
        for label, value in format_geometry_parameters(reference_case.parameters):
            st.write(f"- {label} = {value}")


def render_meshes():
    st.header("Расчётные сетки")
    mesh_cases = grouped["base"] or grouped["distance"] or grouped["height"]
    if not mesh_cases:
        st.warning("В репозитории не найдены сеточные сценарии.")
        return

    selected_case = st.selectbox(
        "Сценарий сетки",
        mesh_cases,
        format_func=lambda case: case.label,
    )
    show_nodes = st.checkbox("Показывать узлы сетки", value=False)
    st.pyplot(build_mesh_figure(selected_case, show_nodes=show_nodes), use_container_width=True)

    st.markdown("**Параметры сеточного сценария**")
    info_cols = st.columns(5)
    info_cols[0].metric("Семейство", family_title(selected_case.family))
    info_cols[1].metric("Параметр N", f"{selected_case.parameters.get('N', 0):.0f}")
    info_cols[2].metric("Вершины", selected_case.vertex_count)
    info_cols[3].metric("Треугольники", selected_case.cell_count)
    info_cols[4].metric("Сценарий", selected_case.label)


def render_fe_space():
    st.header("Конечно-элементная аппроксимация")
    st.markdown(
        """
        Решение ищется в пространстве непрерывных лагранжевых конечных элементов
        на треугольной расчётной сетке.

        **Содержательный смысл аппроксимации**
        - функция тока аппроксимируется непрерывно во всей области;
        - внутри каждого элемента используется полином степени `p`;
        - параметр `p` определяет порядок локальной полиномиальной аппроксимации;
        - в работе рассматриваются варианты `p = 1`, `p = 2`, `p = 3`.
        """
    )
    st.markdown(
        """
        Обозначение `CG(p)` здесь интерпретируется как непрерывное
        лагранжево пространство степени `p`, используемое в конечно-элементной постановке.
        """
    )


def render_degree_choice():
    st.header("Выбор степени полинома p = 1, 2, 3")
    cols = st.columns(3)
    notes = {
        1: "Линейная аппроксимация внутри элемента.",
        2: "Квадратичная аппроксимация внутри элемента.",
        3: "Кубическая аппроксимация внутри элемента.",
    }
    for index, degree in enumerate([1, 2, 3]):
        cols[index].metric("Степень p", degree)
        cols[index].write(notes[degree])
    st.success(f"Для расчётных разделов сейчас используется p = {selected_degree}.")


def select_scenario_groups():
    return {
        "Симметричные": grouped["distance"],
        "Несимметричные": grouped["height"],
    }


def render_solution_slide():
    st.header("Численные решения для симметричных и несимметричных сценариев")
    scenario_groups = select_scenario_groups()
    scenario_kind = st.radio("Класс сценариев", list(scenario_groups.keys()), horizontal=True)
    available_cases = scenario_groups[scenario_kind]

    if not available_cases:
        st.info(f"Для класса «{scenario_kind}» в репозитории не найдены расчётные сценарии.")
        return

    selected_case = st.selectbox(
        "Сценарий",
        available_cases,
        format_func=lambda case: case.label,
    )

    st.markdown(
        f"""
        **Текущий расчёт**
        - класс сценариев: {scenario_kind};
        - параметр сценария: {selected_case.label};
        - степень аппроксимации: p = {selected_degree}.
        """
    )

    try:
        with st.spinner("Выполняется расчёт..."):
            result = solve_problem(selected_case.name, selected_degree)
    except Exception as exc:
        st.warning(f"Не удалось выполнить расчёт: {exc}")
        return

    st.pyplot(build_solution_figure(result["solution"], selected_degree), use_container_width=True)
    metric_cols = st.columns(5)
    metric_cols[0].metric("Γ₁", f"{float(result['gamma1']):.6f}")
    metric_cols[1].metric("Γ₂", f"{float(result['gamma2']):.6f}")
    metric_cols[2].metric("DoF", result["dofs"])
    metric_cols[3].metric("Сценарий", selected_case.label)
    metric_cols[4].metric("p", selected_degree)


def rows_to_table(rows, first_column):
    table = []
    for row in rows:
        table.append(
            {
                first_column: row["label"],
                "p": row["degree"],
                "Γ₁": f"{row['gamma_1']:.6f}",
                "Γ₂": f"{row['gamma_2']:.6f}",
                "|Γ₁-Γ₂|": f"{abs(row['gamma_1'] - row['gamma_2']):.6f}",
                "DoF": row["dofs"],
            }
        )
    return table


def render_comparison_slide():
    st.header("Сравнение результатов и вычисляемых характеристик")
    mode = st.selectbox(
        "Режим сравнения",
        [
            "По степени p для выбранного сценария",
            "Симметричные сценарии при фиксированном p",
            "Несимметричные сценарии при фиксированном p",
        ],
    )

    if mode == "По степени p для выбранного сценария":
        cases_for_degree = grouped["distance"] + grouped["height"]
        if not cases_for_degree:
            st.info("Нет сценариев для сравнения по степени аппроксимации.")
            return

        selected_case = st.selectbox(
            "Сценарий для сравнения по p",
            cases_for_degree,
            format_func=lambda case: f"{family_title(case.family)} | {case.label}",
        )
        rows = []
        try:
            with st.spinner("Выполняется серия расчётов по p..."):
                for degree in [1, 2, 3]:
                    result = solve_problem(selected_case.name, degree)
                    rows.append(
                        {
                            "label": f"p = {degree}",
                            "degree": degree,
                            "gamma_1": float(result["gamma1"]),
                            "gamma_2": float(result["gamma2"]),
                            "dofs": result["dofs"],
                        }
                    )
        except Exception as exc:
            st.warning(f"Не удалось выполнить серию расчётов: {exc}")
            return

        st.dataframe(rows_to_table(rows, "Вариант"), use_container_width=True)
        st.pyplot(build_circulation_chart(rows, [row["label"] for row in rows], "Изменение циркуляции при варьировании p"), use_container_width=True)
        return

    if mode == "Симметричные сценарии при фиксированном p":
        target_cases = grouped["distance"]
        first_column = "Симметричный сценарий"
        chart_title = f"Циркуляция в симметричных сценариях при p = {selected_degree}"
    else:
        target_cases = grouped["height"]
        first_column = "Несимметричный сценарий"
        chart_title = f"Циркуляция в несимметричных сценариях при p = {selected_degree}"

    if not target_cases:
        st.info("Для выбранного класса сценариев в репозитории недостаточно данных.")
        return

    rows = []
    try:
        with st.spinner("Выполняется серия расчётов по сценариям..."):
            for case in target_cases:
                result = solve_problem(case.name, selected_degree)
                rows.append(
                    {
                        "label": case.label,
                        "degree": selected_degree,
                        "gamma_1": float(result["gamma1"]),
                        "gamma_2": float(result["gamma2"]),
                        "dofs": result["dofs"],
                    }
                )
    except Exception as exc:
        st.warning(f"Не удалось выполнить серию расчётов: {exc}")
        return

    st.dataframe(rows_to_table(rows, first_column), use_container_width=True)
    st.pyplot(build_circulation_chart(rows, [row["label"] for row in rows], chart_title), use_container_width=True)
    st.markdown(
        """
        На этом слайде циркуляция показывается непосредственно по интегралам
        вдоль границ первого и второго цилиндров, вычисляемым в процессе решения.
        """
    )


def render_conclusion():
    st.header("Краткие содержательные выводы по задаче")
    st.markdown(
        """
        - Задача сводится к эллиптической краевой постановке для функции тока в области с двумя цилиндрами.
        - Последовательность сеток позволяет анализировать влияние дискретизации на численное решение.
        - Симметричные и несимметричные сценарии задаются различным положением второго цилиндра.
        - Параметр `p = 1, 2, 3` определяет порядок конечно-элементной аппроксимации и влияет на вычисляемые характеристики.
        - Циркуляция по границам цилиндров включена в итоговое сравнение как одна из основных интегральных характеристик.
        """
    )


renderers = {
    "Титульный слайд": render_title,
    "Постановка задачи": render_problem,
    "Расчётная область": render_domain,
    "Граничные условия и параметры задачи": render_boundary_conditions,
    "Расчётные сетки": render_meshes,
    "Конечно-элементная аппроксимация": render_fe_space,
    "Выбор степени полинома p": render_degree_choice,
    "Численные решения": render_solution_slide,
    "Сравнение результатов и циркуляция": render_comparison_slide,
    "Выводы": render_conclusion,
}

renderers[selected_slide]()
