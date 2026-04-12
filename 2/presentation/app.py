from __future__ import annotations

from pathlib import Path

import streamlit as st

from presentation_data import (
    build_geometry_figure,
    build_mesh_figure,
    discover_mesh_cases,
    extract_code_excerpt,
    family_title,
    format_parameters,
    group_cases,
    mesh_summary_table,
    try_compute_solution,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
MESH_ROOT = ROOT_DIR / "mesh"
FIGURE_PATH = ROOT_DIR / "figs" / "5.png"
SOLVE_PATH = ROOT_DIR / "solve.py"
GRID_TEMPLATE_PATH = ROOT_DIR / "grid_template.geo"
GRID_SCRIPT_PATH = ROOT_DIR / "generate_grids.sh"
TASK_PATH = ROOT_DIR / "task.py"


st.set_page_config(
    page_title="МКЭ: потенциальное обтекание",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_cases():
    return discover_mesh_cases(MESH_ROOT)


@st.cache_data
def load_code(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


cases = load_cases()
grouped = group_cases(cases)
base_case = grouped["distance"][1] if len(grouped["distance"]) > 1 else cases[0]
slide_titles = [
    "Титульная страница",
    "Цель работы",
    "Задачи работы",
    "Используемые инструменты",
    "Постановка проблемы",
    "Расчётная область",
    "Расчётная сетка",
    "Математическая постановка",
    "Вариационная постановка",
    "Конечно-элементная аппроксимация",
    "Вычислительный алгоритм",
    "Программная реализация",
    "Интерфейс Streamlit",
    "Параметры задачи",
    "Результаты вычислительных экспериментов",
    "Визуализация решения",
    "Анализ результатов",
    "Выводы",
    "Перспективы развития",
]

st.sidebar.title("Метод конечных элементов")
selected_slide = st.sidebar.radio("Структура презентации", slide_titles)
st.sidebar.markdown("---")
st.sidebar.caption("Основа презентации: файлы каталога `2/` текущего репозитория.")


def render_title():
    st.title("Численное исследование потенциального обтекания двух цилиндров в плоском канале")
    st.subheader("Учебно-исследовательская Streamlit-презентация по материалам репозитория")
    st.markdown(
        """
        **Курс:** «Метод конечных элементов»  
        **Формат:** связка постановки задачи, сетки, вариационной формы, алгоритма и программной реализации  
        **Основа:** `solve.py`, `grid_template.geo`, `generate_grids.sh`, каталог `mesh/`, рисунок `figs/5.png`
        """
    )
    col_left, col_right = st.columns([1.3, 1])
    with col_left:
        st.markdown(
            """
            Презентация оформлена как сопровождение уже существующей практической задачи.
            Математическая модель и численный метод не изменяются: показана текущая реализация,
            сохранённая в репозитории.
            """
        )
    with col_right:
        if FIGURE_PATH.exists():
            st.image(str(FIGURE_PATH), caption="Иллюстрация расчётной области из проекта")


def render_goal():
    st.header("Цель работы")
    st.markdown(
        """
        Показать, как существующая реализация краевой задачи в FEniCS организована
        в виде учебно-исследовательского конвейера:
        от геометрии и сетки до вариационной постановки, кода и интерпретации результатов.
        """
    )
    st.info(
        "В презентации используется только то, что уже присутствует в репозитории: "
        "скрипты, сетки, изображения и формулировки задачи."
    )


def render_tasks():
    st.header("Задачи работы")
    st.markdown(
        """
        - Зафиксировать постановку задачи для функции тока в плоском канале с двумя цилиндрами.
        - Показать, как геометрические параметры переходят в сеточную модель Gmsh.
        - Отразить вариационную постановку и выбор конечно-элементного пространства.
        - Связать вычислительный алгоритм с файлом `solve.py`.
        - Представить доступные в репозитории варианты расчётных сеток и параметрических сценариев.
        - Подготовить единый Streamlit-интерфейс для демонстрации структуры проекта.
        """
    )
    st.caption("Формулировки опираются на `task.py` и генератор сеток `generate_grids.sh`.")


def render_tools():
    st.header("Используемые инструменты")
    col1, col2, col3 = st.columns(3)
    col1.markdown(
        """
        **Моделирование и расчёт**
        - Python
        - FEniCS
        - Метод конечных элементов
        """
    )
    col2.markdown(
        """
        **Геометрия и сетка**
        - Gmsh
        - `.geo`, `.msh`, `.xml`
        - Наборы сеток для нескольких сценариев
        """
    )
    col3.markdown(
        """
        **Представление результатов**
        - Streamlit
        - Matplotlib
        - Статические изображения из репозитория
        """
    )
    st.markdown(
        """
        В текущем проекте не обнаружены прямые артефакты использования PyVista или ParaView,
        поэтому в презентацию они не включаются как фактически задействованные инструменты.
        """
    )


def render_problem():
    st.header("Постановка проблемы")
    st.markdown(
        """
        Рассматривается двумерное потенциальное течение в канале, содержащем два цилиндрических препятствия.
        Вычислительная задача формулируется для функции тока и решается на последовательности сеток,
        а также на нескольких параметрических вариантах взаимного расположения цилиндров.
        """
    )
    st.markdown(
        """
        **Содержательная логика проекта**
        - задаётся геометрия канала и цилиндров;
        - строится сетка в Gmsh;
        - формируется краевая задача в FEniCS;
        - проводится вычисление;
        - анализируются доступные результаты и структура вычислительного эксперимента.
        """
    )


def render_domain():
    st.header("Расчётная область")
    left, right = st.columns([1.05, 1])
    with left:
        st.pyplot(build_geometry_figure(base_case), use_container_width=True)
    with right:
        st.markdown(
            """
            **Обозначения**
            - `Ω` — расчётная область канала.
            - `D1`, `D2` — цилиндры в потоке.
            - `Γ1`, `Γ2` — нижняя и верхняя стенки.
            - `Γ3`, `Γ4` — вход и выход.
            """
        )
        st.markdown("**Параметры базового сценария**")
        for label, value in format_parameters(base_case.parameters):
            st.write(f"- {label}: `{value}`")

    if FIGURE_PATH.exists():
        st.image(str(FIGURE_PATH), caption="Готовое изображение из каталога `2/figs`", use_container_width=True)


def render_mesh():
    st.header("Расчётная сетка")
    base_cases = grouped["base"]
    mesh_index = st.slider("Выбор сетки базовой последовательности", 0, len(base_cases) - 1, len(base_cases) - 1)
    show_nodes = st.checkbox("Показывать узлы сетки", value=False)
    selected_case = base_cases[mesh_index]
    col_left, col_right = st.columns([1.4, 1])
    with col_left:
        st.pyplot(build_mesh_figure(selected_case, show_nodes=show_nodes), use_container_width=True)
    with col_right:
        st.metric("Вершины", selected_case.vertex_count)
        st.metric("Треугольники", selected_case.cell_count)
        st.metric("Параметр N", f"{selected_case.parameters.get('N', 0):.0f}")
        st.markdown(
            """
            Сетка берётся из уже сохранённых файлов `mesh/<case>/`.
            В репозитории присутствуют:
            - три сетки базовой последовательности;
            - три варианта по расстоянию `l2`;
            - три варианта по высоте `h2`.
            """
        )


def render_math():
    st.header("Математическая постановка")
    st.markdown(
        r"""
        **Уравнение**

        $$
        - \nabla^2 \psi = 0, \quad \mathbf{x} \in \Omega
        $$

        **Краевые условия**

        - на входе: $\psi(\mathbf{x}) = x_2$, $\mathbf{x} \in \Gamma_3$;
        - на выходе: $\dfrac{\partial \psi}{\partial n} = 0$, $\mathbf{x} \in \Gamma_4$;
        - на стенках канала: $\psi = 0$ на $\Gamma_1$ и $\psi = H$ на $\Gamma_2$;
        - на границах цилиндров: $\psi = c_\alpha$, $\alpha = 1,2$.
        """
    )
    st.caption("Формулировки повторяют логику `task.py` и постановку, реализованную в `solve.py`.")


def render_variational():
    st.header("Вариационная постановка")
    st.markdown(
        r"""
        Для пробной функции $u$ и тестовой функции $v$ в коде используется билинейная форма

        $$
        a(u, v) = \int_{\Omega} \nabla u \cdot \nabla v \, dx,
        $$

        и правая часть

        $$
        L(v) = \int_{\Omega} 0 \cdot v \, dx.
        $$
        """
    )
    st.code(
        extract_code_excerpt(SOLVE_PATH, "u = TrialFunction(V)", "# Решение задачи"),
        language="python",
    )


def render_fe_space():
    st.header("Конечно-элементная аппроксимация / используемое пространство")
    st.markdown(
        """
        В текущей реализации пространство задаётся как
        `FunctionSpace(mesh, "CG", 2)`.
        Это означает:
        - используется непрерывное пространство Лагранжа;
        - степень полинома внутри элемента равна 2;
        - расчёт выполняется на треугольной сетке из файлов FEniCS XML.
        """
    )
    st.code('V = FunctionSpace(mesh, "CG", 2)', language="python")
    st.markdown(
        """
        В репозитории присутствуют указания на исследование вариантов по степени аппроксимации,
        однако в доступном `solve.py` зафиксирован конкретный вариант `CG(2)`.
        """
    )


def render_algorithm():
    st.header("Вычислительный алгоритм")
    st.markdown(
        """
        1. Выбрать готовый набор сетки или сгенерировать его через `generate_grids.sh`.
        2. Загрузить `mesh`, а также разметку границ из `*_facet_region.xml`.
        3. Построить пространство `CG(2)` и задать граничные условия Дирихле.
        4. Сформировать вариационную задачу для уравнения Лапласа.
        5. Решить систему и получить поле функции тока.
        6. Вычислить интегральные характеристики на границах цилиндров.
        7. Визуализировать решение.
        """
    )
    st.code(load_code(str(GRID_SCRIPT_PATH)), language="bash")


def render_implementation():
    st.header("Программная реализация")
    col_left, col_right = st.columns([1, 1.1])
    with col_left:
        st.markdown(
            """
            **Ключевые файлы проекта**
            - `2/solve.py` — решение задачи в FEniCS.
            - `2/grid_template.geo` — параметрическое описание области.
            - `2/generate_grids.sh` — генерация серий сеток.
            - `2/mesh/...` — сохранённые сетки и разметка границ.
            - `2/figs/5.png` — готовая иллюстрация области.
            - `2/task.py` — ранняя Streamlit-форма представления постановки.
            """
        )
    with col_right:
        st.code(
            extract_code_excerpt(SOLVE_PATH, "mesh = Mesh", "c = plot"),
            language="python",
        )


def render_streamlit_interface():
    st.header("Интерфейс Streamlit")
    st.markdown(
        """
        Презентация собрана как единое навигационное пространство с последовательным переходом
        от постановки задачи к сетке, коду и доступным результатам. Интерфейс сознательно сделан
        строгим: боковая навигация, короткие блоки, минимум декоративных элементов.
        """
    )
    st.markdown(
        """
        **Используемые элементы управления**
        - `radio` — выбор раздела презентации и семейства экспериментов;
        - `slider` — просмотр базовой последовательности сеток;
        - `selectbox` — выбор конкретного параметрического сценария;
        - `checkbox` — включение дополнительных отображений и опционального расчёта.
        """
    )
    st.code(load_code(str(TASK_PATH))[:1100], language="python")


def render_parameters():
    st.header("Параметры задачи")
    family = st.radio(
        "Семейство сценариев",
        ["base", "distance", "height"],
        format_func=family_title,
        horizontal=True,
    )
    selected_case = st.selectbox(
        "Доступный сценарий",
        grouped[family],
        format_func=lambda case: case.label,
    )

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("**Извлечённые параметры из `.geo` файла**")
        for label, value in format_parameters(selected_case.parameters):
            st.write(f"- {label}: `{value}`")
        st.markdown(
            f"""
            **Файлы сценария**
            - `{selected_case.geo_path.relative_to(ROOT_DIR)}`
            - `{selected_case.xml_path.relative_to(ROOT_DIR)}`
            - `{selected_case.facet_path.relative_to(ROOT_DIR)}`
            """
        )
    with col2:
        st.pyplot(build_geometry_figure(selected_case), use_container_width=True)


def render_experiments():
    st.header("Результаты вычислительных экспериментов")
    st.markdown(
        """
        В репозитории присутствуют реальные данные о наборах сеток и параметрических сценариях.
        Это позволяет показать структуру вычислительного эксперимента даже там, где не сохранены
        отдельные численные таблицы или поля решения.
        """
    )
    st.dataframe(mesh_summary_table(cases), use_container_width=True)
    st.markdown(
        """
        **Что подтверждается содержимым проекта**
        - базовая серия сеток: `5`, `10`, `20`;
        - серия по расстоянию между цилиндрами: `l2 = 1.10`, `1.25`, `1.40`;
        - серия по смещению второго цилиндра: `h2 = 0.35`, `0.50`, `0.65`.
        """
    )
    st.warning(
        "Отдельные таблицы сходимости и сохранённые численные значения в репозитории не обнаружены, "
        "поэтому этот раздел опирается на реальные наборы сценариев и сеточные характеристики."
    )


def render_solution():
    st.header("Визуализация решения")
    case = st.selectbox(
        "Сценарий для построения решения",
        grouped["base"] + grouped["distance"] + grouped["height"],
        format_func=lambda mesh_case: f"{family_title(mesh_case.family)} | {mesh_case.label}",
        key="solution_case",
    )
    run_solver = st.checkbox("Выполнить расчёт при наличии FEniCS в среде запуска", value=False)

    if not run_solver:
        st.info(
            "В текущем репозитории отсутствуют сохранённые поля решения. "
            "Раздел готов к интерактивному запуску того же solver, который уже реализован в `solve.py`."
        )
        st.code(load_code(str(SOLVE_PATH)), language="python")
        return

    fig, fluxes, error_message = try_compute_solution(case)
    if error_message:
        st.warning(error_message)
        st.code(load_code(str(SOLVE_PATH)), language="python")
        return

    st.pyplot(fig, use_container_width=True)
    col1, col2 = st.columns(2)
    col1.metric("Интеграл по границе цилиндра 1", f"{fluxes['Gamma1']:.6f}")
    col2.metric("Интеграл по границе цилиндра 2", f"{fluxes['Gamma2']:.6f}")


def render_analysis():
    st.header("Анализ результатов")
    st.markdown(
        """
        **По доступному содержимому репозитория можно сделать следующие выводы**
        - проект ориентирован на серию вычислительных экспериментов, а не на один единственный расчёт;
        - геометрические параметры вынесены в Gmsh-шаблон и тем самым отделены от solver-части;
        - разметка границ хранится вместе с сеткой, что напрямую поддерживает постановку краевых условий в FEniCS;
        - структура `solve.py` компактна и отражает стандартный учебный цикл решения эллиптической задачи.
        """
    )
    st.markdown(
        """
        **Ограничение текущих артефактов**
        - в репозитории не найдены сохранённые карты поля решения, графики сходимости и отдельные таблицы ошибок;
        - поэтому интерпретация численных эффектов здесь дана в форме аккуратной презентационной рамки,
          а не как расширенный отчёт с готовыми цифрами.
        """
    )


def render_conclusion():
    st.header("Выводы")
    st.markdown(
        """
        - В репозитории уже реализована полноценная вычислительная постановка для задачи потенциального обтекания.
        - Streamlit-презентация переводит эту реализацию в учебный формат с логичной навигацией.
        - Основная связка «геометрия → сетка → вариационная задача → код → результаты» теперь оформлена как единая демонстрация проекта.
        - Исходный вычислительный код сохранён без содержательных изменений.
        """
    )


def render_future():
    st.header("Перспективы развития")
    st.markdown(
        """
        - Подключение сохранения полей решения и графиков непосредственно в репозиторий.
        - Добавление автоматического сравнения сценариев по выбранным численным критериям.
        - Вынос solver-логики в импортируемые функции для повторного использования в интерфейсе.
        - Расширение презентации блоком верификации при появлении таблиц ошибок или эталонных данных.
        """
    )
    st.caption("Этот раздел намеренно сформулирован как направление развития, а не как фиктивно выполненный результат.")


renderers = {
    "Титульная страница": render_title,
    "Цель работы": render_goal,
    "Задачи работы": render_tasks,
    "Используемые инструменты": render_tools,
    "Постановка проблемы": render_problem,
    "Расчётная область": render_domain,
    "Расчётная сетка": render_mesh,
    "Математическая постановка": render_math,
    "Вариационная постановка": render_variational,
    "Конечно-элементная аппроксимация": render_fe_space,
    "Вычислительный алгоритм": render_algorithm,
    "Программная реализация": render_implementation,
    "Интерфейс Streamlit": render_streamlit_interface,
    "Параметры задачи": render_parameters,
    "Результаты вычислительных экспериментов": render_experiments,
    "Визуализация решения": render_solution,
    "Анализ результатов": render_analysis,
    "Выводы": render_conclusion,
    "Перспективы развития": render_future,
}

renderers[selected_slide]()
