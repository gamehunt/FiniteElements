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
    "Выбор степени полинома p",
    "Численные решения",
    "Сравнение результатов и циркуляция",
    "Выводы",
]

st.sidebar.title("Доклад по задаче")
selected_slide = st.sidebar.radio("Раздел", slide_titles)
selected_degree = st.sidebar.selectbox("Степень аппроксимации p", [1, 2, 3], index=1)
st.sidebar.markdown("---")


def solve_selected_case(case, degree):
    if case.family == "height":
        return solve_problem_non_symmetrical(case.name, degree)
    return solve_problem(case.name, degree)


def render_title():
    st.title("Численное решение задачи обтекания области с двумя цилиндрами методом конечных элементов")
    st.markdown(
        """
        **Тема доклада**  
        Потенциальное течение в плоском канале с двумя цилиндрическими препятствиями.

        **Основные разделы**  
        Постановка задачи, геометрия области, граничные условия, расчётные сетки, конечно-элементная аппроксимация,
        сравнение симметричных и несимметричных сценариев, а также анализ интегральных характеристик по границам цилиндров.
        """
    )
    st.info(f"Во всех расчётных разделах используется выбранная степень аппроксимации: p = {selected_degree}.")


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
            **Сценарии расчёта**
            - в симметричном случае варьируется параметр `l_2`;
            - в несимметричном случае варьируется параметр `h_2`;
            - для несимметричных конфигураций используется отдельная вычислительная ветвь
              с основным и вспомогательными решениями, после чего строится компенсированное итоговое поле.
            """
        )
    with col_right:
        st.markdown("**Геометрические параметры опорной конфигурации**")
        for label, value in format_geometry_parameters(reference_case.parameters):
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
    metrics = scenario_metrics(selected_case)
    info_cols = st.columns(len(metrics))
    for column, (label, value) in zip(info_cols, metrics):
        column.metric(label, value)

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


def render_degree_choice():
    st.header("Выбор степени полинома p = 1, 2, 3")
    cols = st.columns(3)
    notes = {
        1: "Линейная аппроксимация внутри каждого элемента.",
        2: "Квадратичная аппроксимация внутри каждого элемента.",
        3: "Кубическая аппроксимация внутри каждого элемента.",
    }
    for index, degree in enumerate([1, 2, 3]):
        cols[index].metric("Степень p", degree)
        cols[index].write(notes[degree])
    st.success(f"Текущее значение для численных экспериментов: p = {selected_degree}.")


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

    selected_case = st.selectbox("Сценарий", available_cases, format_func=lambda case: case.label)

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
            result = solve_selected_case(selected_case, selected_degree)
    except Exception as exc:
        st.warning(f"Не удалось выполнить расчёт: {exc}")
        return

    st.pyplot(build_solution_figure(result["solution"], selected_degree), use_container_width=True)

    metric_count = 6 if selected_case.family == "height" else 5
    metric_cols = st.columns(metric_count)
    metric_cols[0].metric("I_1", f"{float(result['gamma1']):.6f}")
    metric_cols[1].metric("I_2", f"{float(result['gamma2']):.6f}")
    metric_cols[2].metric("DoF", result["dofs"])
    metric_cols[3].metric("Сценарий", selected_case.label)
    metric_cols[4].metric("p", selected_degree)
    if selected_case.family == "height":
        metric_cols[5].metric("kappa_1, kappa_2", f"{float(result['kappa1']):.4f}, {float(result['kappa2']):.4f}")

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
            при заданной степени конечно-элементной аппроксимации.
            """
        )


def rows_to_table(rows, first_column):
    table = []
    for row in rows:
        item = {
            first_column: row["label"],
            "p": row["degree"],
            "I_1": f"{row['gamma_1']:.6f}",
            "I_2": f"{row['gamma_2']:.6f}",
            "|I_1 - I_2|": f"{abs(row['gamma_1'] - row['gamma_2']):.6f}",
            "DoF": row["dofs"],
        }
        if row.get("kappa1") is not None:
            item["kappa_1"] = f"{row['kappa1']:.6f}"
            item["kappa_2"] = f"{row['kappa2']:.6f}"
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
                            "dofs": result["dofs"],
                            "kappa1": float(result["kappa1"]) if "kappa1" in result else None,
                            "kappa2": float(result["kappa2"]) if "kappa2" in result else None,
                        }
                    )
        except Exception as exc:
            st.warning(f"Не удалось выполнить серию расчётов: {exc}")
            return

        st.dataframe(rows_to_table(rows, "Вариант"), use_container_width=True)
        st.pyplot(
            build_circulation_chart(rows, [row["label"] for row in rows], "Изменение интегральных характеристик при варьировании p"),
            use_container_width=True,
        )
        return

    if mode == "Симметричные сценарии при фиксированном p":
        target_cases = grouped["distance"]
        first_column = "Симметричный сценарий"
        chart_title = f"Интегральные характеристики в симметричных сценариях при p = {selected_degree}"
    else:
        target_cases = grouped["height"]
        first_column = "Несимметричный сценарий"
        chart_title = f"Интегральные характеристики в несимметричных сценариях при p = {selected_degree}"

    if not target_cases:
        st.info("Для выбранного класса сценариев в репозитории недостаточно данных.")
        return

    rows = []
    try:
        with st.spinner("Выполняется серия расчётов по сценариям..."):
            for case in target_cases:
                result = solve_selected_case(case, selected_degree)
                rows.append(
                    {
                        "label": case.label,
                        "degree": selected_degree,
                        "gamma_1": float(result["gamma1"]),
                        "gamma_2": float(result["gamma2"]),
                        "dofs": result["dofs"],
                        "kappa1": float(result["kappa1"]) if "kappa1" in result else None,
                        "kappa2": float(result["kappa2"]) if "kappa2" in result else None,
                    }
                )
    except Exception as exc:
        st.warning(f"Не удалось выполнить серию расчётов: {exc}")
        return

    st.dataframe(rows_to_table(rows, first_column), use_container_width=True)
    st.pyplot(build_circulation_chart(rows, [row["label"] for row in rows], chart_title), use_container_width=True)

    if mode == "Несимметричные сценарии при фиксированном p":
        st.markdown("**Коэффициенты компенсации для итогового решения**")
        kappa_rows = [
            {
                "Сценарий": row["label"],
                "kappa_1": f"{row['kappa1']:.6f}",
                "kappa_2": f"{row['kappa2']:.6f}",
            }
            for row in rows
        ]
        st.dataframe(kappa_rows, use_container_width=True)


def render_conclusion():
    st.header("Краткие содержательные выводы по задаче")
    st.markdown(
        """
        - Краевая задача формулируется в канальной области с двумя внутренними цилиндрическими границами.
        - Последовательность сеток позволяет проследить влияние дискретизации на поле функции тока и интегральные характеристики.
        - Параметр `p = 1, 2, 3` определяет порядок конечно-элементной аппроксимации и влияет на вычисляемые значения `I_1`, `I_2`.
        - Симметричные и несимметричные конфигурации различаются не только геометрией, но и вычислительной процедурой построения решения.
        - Для несимметричной постановки итоговое поле формируется с использованием вспомогательных решений и коэффициентов компенсации `kappa_1`, `kappa_2`.
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
