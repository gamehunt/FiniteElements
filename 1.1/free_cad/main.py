import streamlit as st

st.set_page_config(
    page_title="FreeCAD",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Проект № 3")

slides = [
    "1. FreeCAD",
    "2. Что такое CAD системы?",
    "3. Основная идея FreeCAD: Верстаки",
    "4. Верстак Part Design",
    "5. Верстак Assembly",
    "6. Верстак TechDraw",
    "7. Верстак FEM",
    "8. Подготовка модели к расчету",
    "9. Граничные условия",
    "10. Решение",
    "11. Анализ результатов",
    "12. Возможности и ограничения FEM",
    "13. Дополнительные возможности",
    "14. Спасибо за внимание!"
]

slide = st.sidebar.radio(
    "О FreeCAD:",
    slides
)

st.sidebar.markdown("---")

if slide == slides[0]:
    st.markdown("<h1 style='text-align: center;'>FreeCAD</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Параметрическое 3D моделирование для всех</h3>",
                unsafe_allow_html=True)

    st.image("logo.png", use_container_width=True)

    st.markdown("---")

elif slide == slides[1]:
    st.header("Что такое CAD системы?")
    st.markdown("""
    **CAD (Computer-Aided Design)** — системы автоматизированного проектирования.

    Это технология, позволяющая инженерам и дизайнерам создавать точные 2D-чертежи и 3D-модели.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Проприетарные аналоги")
        st.markdown("""
        - SolidWorks
        - Autodesk Inventor
        - Компас-3D
        - Creo
        """)
    with col2:
        st.subheader("Свободное ПО")
        st.markdown("""
        - **FreeCAD**
        - LibreCAD
        - OpenSCAD
        - SolveSpace
        """)

    st.markdown("**FreeCAD** — Полностью бесплатное и кросплатформенное ПО.")

    st.markdown("---")
    
    st.image("interface.png", use_container_width=True)
    
    st.markdown(
        "<p style='text-align: center; color: gray;'>Интерфейс программы</p>",
        unsafe_allow_html=True)

elif slide == slides[2]:
    st.header("Верстаки")
    st.markdown("""
    Интерфейс FreeCAD организован по принципу **верстаков**. 
    Каждый верстак содержит набор инструментов, специфичных для определенной задачи:
    
    - Твердотельное моделирование.
    - Сборки.
    - Оформление технической документации.
    
    В стандартной установке FreeCAD присутствует множество различных верстаков.
    """)

    st.image("workbench_menu.png")

    st.markdown(
        "<p style='text-align: center; color: gray;'>Меню верстаков</p>",
        unsafe_allow_html=True)

    st.markdown("""
    Так же пользователь может устанавливать сторонние верстаки в виде модулей.
    """)

elif slide == slides[3]:
    st.header("Верстак Part Design")
    st.markdown("**Главный инструмент для моделирования твердотельных деталей.**")

    st.markdown("""
    **Основные возможности:**
    - Создание 2D эскизов.
    - Выдавливание, вращение, вырезы.
    - Создание фасок, скруглений, уклонов.
    - Логические операции.
    """)

    st.markdown("---")
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.image("sketch.png", use_container_width=True)
        st.markdown("<p style='text-align: center; color: gray;'>Эскиз с размерами</p>", unsafe_allow_html=True)
    with col_img2:
        st.image("model.png", use_container_width=True)
        st.markdown("<p style='text-align: center; color: gray;'>Готовая 3D деталь</p>", unsafe_allow_html=True)

    st.info("**Параметричность**: Все изменения можно откатить в любой момент, меняя параметры в дереве модели.")

elif slide == slides[4]:
    st.header("Верстак Assembly")
    st.markdown("Используется для создания сборок из спроектированных деталей.")
    st.markdown("Также во FreeCAD есть несколько верстаков устанавливаемых отдельно: A2plus, Assembly4 и др.")

    st.markdown("""
    **Суть работы:**
    1. Импортируем несколько готовых деталей.
    2. Накладываем связи (совпадение осей, плоскостей, касание).
    3. Собираем механизм.

    *Сборка может быть как статичной, так и кинематической (проверка движения).*
    """)

    st.markdown("---")

    st.image("assembly.gif", use_container_width=True)

    st.markdown(
        "<p style='text-align: center; color: gray;'>Кинематическая сборка из нескольких деталей</p>",
        unsafe_allow_html=True)

elif slide == slides[5]:
    st.header("Оформление чертежей (TechDraw)")
    st.markdown("Верстак для создания технической документации на основе 3D модели.")

    st.markdown("""
    **Что умеет:**
    - Создавать виды спереди, сбоку, сверху, изометрию.
    - Разрезы и выносные элементы.
    - Простановка размеров, допусков, обозначений шероховатости.
    - Экспорт в SVG или PDF для печати.
    """)


    st.image("drawing.png", use_container_width=True)

    st.markdown(
        "<p style='text-align: center; color: gray;'>Пример чертежа</p>",
        unsafe_allow_html=True)

elif slide == slides[6]:
    st.header("Верстак FEM — Инженерный анализ")
    st.markdown("**FEM (Finite Element Method)** — метод конечных элементов.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Зачем это нужно?
        - Проверить деталь на прочность **до того**, как она будет изготовлена
        - Оптимизировать форму и массу конструкции
        - Найти слабые места и зоны концентрации напряжений
        - Смоделировать деформации под нагрузкой
        """)
    with col2:
        st.markdown("""
        ### Принцип работы:
        1. **Разбиение** сложной детали на множество маленьких простых элементов (конечных элементов)
        2. **Решение** системы уравнений для каждого элемента
        3. **Визуализация** результатов (напряжения, деформации, запас прочности)
        """)

    st.markdown("---")

elif slide == slides[7]:
    st.header("Подготовка модели к расчету")
    st.markdown("### Этапы работы в на верстаке FEM")

    step1, step2, step3, step4 = st.columns(4)
    with step1:
        st.markdown("**1. Модель**")
        st.image("fem_detail.png", use_container_width=True)
        st.markdown("<p style='color: gray;'>Готовая 3D деталь из Part Design</p>", unsafe_allow_html=True)

    with step2:
        st.markdown("**2. Граничные условия**")
        st.image("fem_constraints.png", use_container_width=True)
        st.markdown("<p style='color: gray;'>Где закреплено, куда давит сила</p>", unsafe_allow_html=True)

    with step3:
        st.markdown("**3. Материал**")
        st.image("fem_material.png", use_container_width=True)
        st.markdown("<p style='color: gray;'>Сталь, алюминий, пластик...</p>", unsafe_allow_html=True)

    with step4:
        st.markdown("**4. Сетка**")
        st.image("fem_mash.png", use_container_width=True)
        st.markdown("<p style='color: gray;'>Разбиение на элементы</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    ### Материалы в FreeCAD
    - Встроенная библиотека материалов (стали, алюминиевые сплавы, титан, пластики)
    - Можно задать пользовательские свойства:
        - Модуль упругости
        - Коэффициент Пуассона
        - Предел текучести
        - Плотность
    """)

elif slide == slides[8]:
    st.header("Граничные условия")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Типы закреплений")
        st.markdown("""
        - **Fixed constraint** — жесткая заделка (деталь приварена или привинчена)
        - **Displacement constraint** — ограничение перемещений по направлениям
        - **Fixed rotation** — запрет поворота
        """)

    with col_right:
        st.markdown("### Типы нагрузок")
        st.markdown("""
        - **Force load** — сила, приложенная к грани
        - **Pressure load** — равномерное давление
        - **Gravity load** — сила тяжести (собственный вес)
        - **Centrifugal load** — центробежная сила (для вращающихся деталей)
        - **Temperature load** — температурное расширение
        """)

    st.markdown("---")
    st.info("**Важно**: Правильное задание граничных условий — ключ к точному расчету. Неправильные условия → неправильные результаты!")

elif slide == slides[9]:
    st.header("Решение")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Процесс решения")
        st.markdown("""
        1. **Выбор решателя**:
            - CalculiX (стандартный, предустановлен)
            - Elmer (гидродинамика, тепло)
            - Z88
    
        2. **Запуск расчета**
    
        3. **Визуализация результатов**
        """)

    with col_right:
        st.image("fem_solver.png", use_container_width=True)
        st.markdown("<p style='color: gray;'>Меню решателя</p>", unsafe_allow_html=True)

    st.markdown("---")

elif slide == slides[10]:
    st.header("Анализ результатов")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Напряжения")

        st.markdown("""
        **Von Mises stress (эквивалентные напряжения)**
        - Показывает, где материал нагружен сильнее всего
        - Красные зоны — потенциальные места разрушения
        """)

    with col_right:
        st.image("fem_von_mises.png", use_container_width=True)
        st.markdown(
            "<p style='text-align: center; color: gray;'>Цветовая карта напряжений</p>",
            unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Деформации")

        st.markdown("""
        **Displacement (перемещения)**
        - Показывает, как изменится форма детали под нагрузкой
        - Коэффициент масштабирования обычно увеличен для наглядности
        """)

    with col_right:
        st.image("fem_displacement.png", use_container_width=True)
        st.markdown(
            "<p style='text-align: center; color: gray;'>Деформированная деталь</p>",
            unsafe_allow_html=True)


    st.markdown("### И многое другое")

    st.markdown("""
            - Температурные поля
            - Реакции в опорах
            - Собственные частоты и формы колебаний
            - Критическая нагрузка потери устойчивости
            """)


    st.markdown("---")

elif slide == slides[11]:
    st.header("FEM во FreeCAD: возможности и ограничения")

    col_plus, col_minus = st.columns(2)

    with col_plus:
        st.markdown("### Возможности")
        st.markdown("""
        - **Полностью бесплатно**
        - Интеграция с моделированием (не надо экспортировать/импортировать)
        - Поддержка нескольких решателей
        - Активно развивается
        - Хорошая документация и сообщество
        - Python API для автоматизации
        """)

    with col_minus:
        st.markdown("### Ограничения")
        st.markdown("""
        - Медленнее коммерческих аналогов (Ansys, Abaqus)
        - Меньше типов элементов
        - Сложнее с нелинейными задачами (контакты, пластичность)
        - Требует больше ручной настройки
        - Нет встроенной оптимизации топологии
        """)
        
    st.image("fem_final.png", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    ### Когда использовать FEM во FreeCAD?

    - **Образовательные цели** — понять принципы МКЭ
    - **Небольшие задачи** — детали машин, узлы, кронштейны
    - **Начальные проверки** — прикинуть напряжения до покупки коммерческого ПО
    - **Хобби и DIY проекты** — 3D печать, самодельные конструкции
    """)


elif slide == slides[12]:
    st.header("Что еще умеет FreeCAD?")

    with st.expander("**Архитектура**", expanded=True):
        st.write("Проектирование зданий и сооружений (стены, окна, перекрытия). Совместимость с форматом IFC.")

    with st.expander("**Поверхности**", expanded=True):
        st.write("Создание сложных криволинейных форм, кузовов автомобилей, корпусов.")

    with st.expander("**ЧПУ**", expanded=True):
        st.write("Генерация G-code для станков с численным програмным управлением на основе 3D модели.")

    with st.expander("**Расчеты и скрипты**", expanded=True):
        st.write("Встроенная консоль Python. Можно автоматизировать действия или писать свои макросы.")

    st.markdown("---")

elif slide == slides[13]:
    st.markdown("<h1 style='text-align: center;'>Спасибо за внимание!</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Вопросы?</h3>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    **Полезные ссылки:**
    - [Официальный сайт FreeCAD](https://www.freecad.org/)
    - [Документация](https://wiki.freecad.org/)
    - [Форум сообщества](https://forum.freecad.org/)
    """)

    st.balloons()
