import streamlit as st


st.set_page_config(
    page_title="About the project",
    layout="wide",
    page_icon="🧭",
)

st.markdown("""

The maps are constructed using the t-SNE. You can find the exact workflows and algorithm settings here: 
[https://github.com/BoCHemia/COMPASS/blob/main/scripts/README.md](https://github.com/BoCHemia/COMPASS/blob/main/scripts/README.md).

The project is developed by  and is licensed under a Creative Common License
""")