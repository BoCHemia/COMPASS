import streamlit as st


st.set_page_config(
    page_title="About the project",
    layout="wide",
    page_icon="🧭",
)

st.header("Contact")
st.markdown("""
- [Kerstin von Borries](mailto:kejbo@dtu.dk), Technical University of Denmark (DTU), Denmark
- [Jasmin Hafner](mailto:jasmin.hafner@eawag.ch), University of Zurich and Eawag, Switzerland
- José Cordero Solano, Eawag, Switzerland
- [Kathrin Fenner](mailto:kathrin.fenner@eawag.ch), University of Zurich and Eawag, Switzerland 
""")

st.header("Technical")
st.markdown("""

The maps are constructed using the t-SNE. You can find the exact workflows and algorithm settings on GitHub :
 
[https://github.com/BoCHemia/COMPASS/blob/main/scripts/README.md](https://github.com/BoCHemia/COMPASS/blob/main/scripts/README.md)

""")

st.header("License")
st.markdown("""
[CC BY 4.0 Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
""")