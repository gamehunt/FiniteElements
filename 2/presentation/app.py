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
    scenario_metrics,
)
from solve import solve_problem  # noqa: E402
from solve_non_symmetrical import solve_problem_non_symmetrical  # noqa: E402


MESH_ROOT = ROOT_DIR / "mesh"

st.set_page_config(
    page_title="МКЭ: обтекание двух цилиндров",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_cases():
    return discover_mesh_cases(MESH_ROOT)


def solve_selected_case(case, degree):
    if case.family == "height":
        return solve_problem_non_symmetrical(case.name, degree)
    return solve_problem(case.name, degree)


def format_scientific(value):
    value = float(value)
    if value == 0.0:
        return "0"
    exponent = f"{value:.2e}".split("e")[1]
    mantissa = value / (10 ** int(exponent))
    return f"{mantissa:.3f} × 10^{int(exponent)}"


def render_metric_blocks(items):
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items):
        column.markdown(f"**{label}**")
        column.markdown(str(value))


def scenario_selector(title, grouped):
    available_families = [family for family in ["base", "distance", "height"] if grouped[family]]
    if not available_families:
        st.info("В репозитории отсутствуют подходящие сценарии.")
        return None

    selected_family = st.radio(
        title,
        available_families,
        horizontal=True,
        format_func=family_title,
    )
    selected_case = st.selectbox(
        "Сценарий",
        grouped[selected_family],
        format_func=lambda case: case.label,
        key=f"{title}_{selected_family}",
    )
    return selected_case


cases = load_cases()
grouped = group_cases(cases)
reference_case = (
    safe_first(grouped["distance"])
    or safe_first(grouped["height"])
    or safe_first(grouped["base"])
    or safe_first(cases)
)

slide_titles = [
    "Титульный слайд",
    "Постановка задачи",
    "Расчётная область",
    "Граничные условия и параметры задачи",
    "Расчётные сетки",
    "Конечно-элементная аппроксимация",
    "Численные решения",
    "Сравнение результатов и циркуляция",
]

st.sidebar.title("Доклад по задаче")
selected_slide = st.sidebar.radio("Раздел", slide_titles)


def render_title():
    st.title("Численное решение задачи обтекания области с двумя цилиндрами методом конечных элементов")
    st.markdown(
        """
        **Тема доклада**  
        Потенциальное течение в плоском канале с двумя цилиндрическими препятствиями.

        **Основные разделы**  
        Постановка задачи, геометрия области, граничные условия, расчётные сетки,
        конечно-элементная аппроксимация, численные решения и сравнение интегральных характеристик.
        """
    )


def render_problem():
    st.header("Постановка задачи")
    st.markdown(
        r"""
        Рассматривается краевая задача для функции тока $\psi$ в области
        $$
        \Omega = (0, L) \times (0, H) \setminus (\overline{D_1} \cup \overline{D_2}),
        $$
        где $D_1$ и $D_2$ обозначают внутренние цилиндрические границы.

        В области канала решается эллиптическая задача
        $$
        -\Delta \psi = 0 \qquad \text{в } \Omega.
        $$

        Граничные условия задаются на внешней границе канала и на поверхностях цилиндров:
        $$
        \psi = 0 \text{ на } \Gamma_1, \qquad
        \psi = 1 \text{ на } \Gamma_2, \qquad
        \psi = x_2 \text{ на } \Gamma_3,
        $$
        при естественном условии на выходной границе $\Gamma_4$ и постоянных значениях функции тока
        на границах цилиндров.
        """
    )
    st.markdown(
        """
        **Классы вычислительных сценариев**
        - базовая последовательность сеток: анализ влияния параметра дискретизации;
        - симметричные сценарии: изменение продольной координаты второго цилиндра;
        - несимметричные сценарии: изменение вертикальной координаты второго цилиндра.
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
        На схеме показаны внешняя граница канала $\Gamma_1 \cup \Gamma_2 \cup \Gamma_3 \cup \Gamma_4$,
        внутренние границы цилиндров $D_1$ и $D_2$, а также геометрические параметры
        $L$, $H$, $l_1$, $l_2$, $h_1$, $h_2$, $r_1$, $r_2$.
        """
    )


def render_boundary_conditions():
    st.header("Граничные условия и параметры задачи")
    if reference_case is None:
        st.warning("Недостаточно данных для отображения параметров задачи.")
        return

    parameter_case = scenario_selector("Семейство параметров", grouped)
    if parameter_case is None:
        return

    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.markdown(
            r"""
            **Граничные условия**
            - нижняя стенка канала $\Gamma_1$: $\psi = 0$;
            - верхняя стенка канала $\Gamma_2$: $\psi = 1$;
            - входная граница $\Gamma_3$: $\psi = x_2$;
            - выходная граница $\Gamma_4$: естественное условие;
            - поверхности цилиндров: $\psi = \mathrm{const}$.
            """
        )
        st.markdown(
            """
            **Параметрические варианты**
            - в симметричных сценариях изменяется положение второго цилиндра по координате `l_2`;
            - в несимметричных сценариях изменяется положение второго цилиндра по координате `h_2`;
            - в базовой серии варьируется параметр сеточного сгущения.
            """
        )
    with col_right:
        st.markdown("**Параметры расчётной области и цилиндров**")
        st.caption(f"Показан набор параметров для сценария: {parameter_case.label}.")
        for label, value in format_geometry_parameters(parameter_case.parameters):
            st.write(f"- {label} = {value}")


def render_meshes():
    st.header("Расчётные сетки")
    available_families = [family for family in ["base", "distance", "height"] if grouped[family]]
    if not available_families:
        st.warning("В репозитории не найдены расчётные сетки.")
        return

    selected_family = st.radio(
        "Семейство сценариев",
        available_families,
        horizontal=True,
        format_func=family_title,
    )
    selected_case = st.selectbox(
        "Вариант сетки",
        grouped[selected_family],
        format_func=lambda case: case.label,
    )
    show_nodes = st.checkbox("Показывать узлы сетки", value=False)
    st.pyplot(build_mesh_figure(selected_case, show_nodes=show_nodes), use_container_width=True)

    st.markdown("**Параметры выбранного сеточного сценария**")
    render_metric_blocks(scenario_metrics(selected_case))
    st.caption(f"Семейство сценариев: {family_title(selected_case.family)}.")


def render_fe_space():
    st.header("Конечно-элементная аппроксимация")
    st.markdown(
        """
        Решение ищется на треугольной расчётной сетке области в пространстве непрерывных лагранжевых
        конечных элементов. Это означает, что функция тока аппроксимируется непрерывно во всей области,
        а внутри каждого элемента задаётся локальным полиномом степени `p`.
        """
    )
    st.markdown(
        """
        **Используемое пространство**
        - конечно-элементное пространство строится на текущей треугольной сетке;
        - используются непрерывные лагранжевы элементы;
        - параметр `p` задаёт степень локальной полиномиальной аппроксимации;
        - в расчётах рассматриваются варианты `p = 1`, `p = 2`, `p = 3`.
        """
    )
    st.markdown(
        """
        В реализации это соответствует построению пространства `FunctionSpace(mesh, "CG", p)`,
        однако содержательно здесь важен именно выбор порядка конечно-элементной аппроксимации.
        """
    )


def render_solution_slide():
    st.header("Численные решения")
    scenario_groups = {
        "Симметричные": grouped["distance"],
        "Несимметричные": grouped["height"],
    }
    scenario_kind = st.radio("Класс сценариев", list(scenario_groups.keys()), horizontal=True)
    available_cases = scenario_groups[scenario_kind]

    if not available_cases:
        st.info(f"Для класса «{scenario_kind}» в репозитории не найдены расчётные сценарии.")
        return

    degree = st.select_slider("Степень полинома p", options=[1, 2, 3], value=2)
    selected_case = st.selectbox("Сценарий", available_cases, format_func=lambda case: case.label)

    st.markdown(
        f"""
        **Текущий расчёт**
        - класс сценариев: {scenario_kind};
        - параметр сценария: {selected_case.label};
        - порядок конечно-элементной аппроксимации: p = {degree}.
        """
    )

    try:
        with st.spinner("Выполняется расчёт..."):
            result = solve_selected_case(selected_case, degree)
    except Exception as exc:
        st.warning(f"Не удалось выполнить расчёт: {exc}")
        return

    st.pyplot(build_solution_figure(result["solution"], degree), use_container_width=True)

    items = [
        (r"$I_1$", format_scientific(result["gamma1"])),
        (r"$I_2$", format_scientific(result["gamma2"])),
    ]
    if selected_case.family == "height":
        items.extend(
            [
                (r"$\kappa_1$", format_scientific(result["kappa1"])),
                (r"$\kappa_2$", format_scientific(result["kappa2"])),
            ]
        )
    render_metric_blocks(items)

    st.markdown(
        r"""
        Здесь
        $$
        I_1 = \int_{\partial D_1} \partial_n \psi \, ds, \qquad
        I_2 = \int_{\partial D_2} \partial_n \psi \, ds
        $$
        используются как интегральные характеристики по границам цилиндров.
        """
    )

    if selected_case.family == "height":
        st.markdown(
            """
            Для несимметричных сценариев итоговое поле строится как линейная комбинация основного и двух
            вспомогательных решений. Коэффициенты `kappa_1`, `kappa_2` определяются из системы на компенсацию
            интегральных характеристик по границам цилиндров.
            """
        )
    else:
        st.markdown(
            """
            Для симметричных сценариев отображается прямое решение краевой задачи на выбранной геометрии
            при заданном порядке конечно-элементной аппроксимации.
            """
        )


def rows_to_table(rows, first_column, include_degree=False, include_kappa=False):
    table = []
    for row in rows:
        item = {
            first_column: row["label"],
            "I_1": format_scientific(row["gamma_1"]),
            "I_2": format_scientific(row["gamma_2"]),
            "|I_1 - I_2|": format_scientific(abs(row["gamma_1"] - row["gamma_2"])),
        }
        if include_degree:
            item["p"] = row["degree"]
        if include_kappa:
            item["kappa_1"] = format_scientific(row["kappa1"])
            item["kappa_2"] = format_scientific(row["kappa2"])
        table.append(item)
    return table


def render_comparison_slide():
    st.header("Сравнение результатов и циркуляция")
    st.markdown(
        r"""
        В этом разделе под циркуляцией понимаются вычисляемые интегральные характеристики
        $I_1$, $I_2$ по границам цилиндров. В программной реализации они возвращаются как
        `gamma1`, `gamma2`, а для несимметричной постановки вычисляются уже для компенсированного итогового поля.
        """
    )

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
                    result = solve_selected_case(selected_case, degree)
                    rows.append(
                        {
                            "label": f"p = {degree}",
                            "degree": degree,
                            "gamma_1": float(result["gamma1"]),
                            "gamma_2": float(result["gamma2"]),
                            "kappa1": float(result["kappa1"]) if "kappa1" in result else None,
                            "kappa2": float(result["kappa2"]) if "kappa2" in result else None,
                        }
                    )
        except Exception as exc:
            st.warning(f"Не удалось выполнить серию расчётов: {exc}")
            return

        st.dataframe(rows_to_table(rows, "Вариант", include_degree=True), use_container_width=True)
        st.pyplot(
            build_circulation_chart(rows, [row["label"] for row in rows], "Изменение интегральных характеристик при варьировании p"),
            use_container_width=True,
        )
        return

    degree = st.select_slider("Степень полинома p", options=[1, 2, 3], value=2, key="comparison_degree")

    if mode == "Симметричные сценарии при фиксированном p":
        target_cases = grouped["distance"]
        first_column = "Симметричный сценарий"
        chart_title = f"Интегральные характеристики в симметричных сценариях при p = {degree}"
        include_kappa = False
    else:
        target_cases = grouped["height"]
        first_column = "Несимметричный сценарий"
        chart_title = f"Интегральные характеристики в несимметричных сценариях при p = {degree}"
        include_kappa = True

    if not target_cases:
        st.info("Для выбранного класса сценариев в репозитории недостаточно данных.")
        return

    rows = []
    try:
        with st.spinner("Выполняется серия расчётов по сценариям..."):
            for case in target_cases:
                result = solve_selected_case(case, degree)
                rows.append(
                    {
                        "label": case.label,
                        "degree": degree,
                        "gamma_1": float(result["gamma1"]),
                        "gamma_2": float(result["gamma2"]),
                        "kappa1": float(result["kappa1"]) if "kappa1" in result else None,
                        "kappa2": float(result["kappa2"]) if "kappa2" in result else None,
                    }
                )
    except Exception as exc:
        st.warning(f"Не удалось выполнить серию расчётов: {exc}")
        return

    st.dataframe(
        rows_to_table(rows, first_column, include_degree=False, include_kappa=include_kappa),
        use_container_width=True,
    )
    st.pyplot(build_circulation_chart(rows, [row["label"] for row in rows], chart_title), use_container_width=True)


renderers = {
    "Титульный слайд": render_title,
    "Постановка задачи": render_problem,
    "Расчётная область": render_domain,
    "Граничные условия и параметры задачи": render_boundary_conditions,
    "Расчётные сетки": render_meshes,
    "Конечно-элементная аппроксимация": render_fe_space,
    "Численные решения": render_solution_slide,
    "Сравнение результатов и циркуляция": render_comparison_slide,
}

renderers[selected_slide]()
