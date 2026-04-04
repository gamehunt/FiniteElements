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
    "7. Дополнительные возможности",
    "8. Спасибо за внимание!"
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
    **CAD (Computer-Aided Design)** — автоматизированное проектирование.

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
    st.header("Что еще умеет FreeCAD?")

    with st.expander("**Архитектура**", expanded=True):
        st.write("Проектирование зданий и сооружений (стены, окна, перекрытия). Совместимость с форматом IFC.")

    with st.expander("**Метод конечных элементов**", expanded=True):
        st.write("Прочностной анализ методом **конечных элементов**. Можно проверить, выдержит ли деталь нагрузку.")

    with st.expander("**Поверхности**", expanded=True):
        st.write("Создание сложных криволинейных форм, кузовов автомобилей, корпусов.")

    with st.expander("**ЧПУ**", expanded=True):
        st.write("Генерация G-code для станков с численным програмным управлением на основе 3D модели.")

    with st.expander("**Расчеты и скрипты**", expanded=True):
        st.write("Встроенная консоль Python. Можно автоматизировать действия или писать свои макросы.")

    st.markdown("---")

elif slide == slides[7]:
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
