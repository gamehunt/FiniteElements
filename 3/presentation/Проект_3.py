import streamlit as st
import sys
from PIL import Image

sys.path.append(".")

col1, col2 = st.columns([6, 1], vertical_alignment="center")

with col1:
    st.markdown(
        f"<h2 style='text-align: center;'>Филиал МГУ имени М.В. Ломоносова, г. Саров</h2>",
        unsafe_allow_html=True,
    )

with col2:
    image = Image.open("presentation/logo.png")
    st.image(image)

st.markdown(
    f"<br/><br/><h1 style='text-align: center;'>Численное исследование потенциального обтекания двух цилиндров в плоском канале</h1>",
    unsafe_allow_html=True,
)

r"""
\
\
Проект №3:
* Василенко Даниил Олегович
* Демаков Матвей Александрович
* Ивлев Александр Фёдорович
* Лушкина Надежда Михайловна
* Талин Владимир Борисович
"""

st.markdown(
    f"<p style='text-align: center; font-size: 14pt;'>2026 год</p>",
    unsafe_allow_html=True,
)
