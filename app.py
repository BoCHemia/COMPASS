import streamlit as st
import pandas as pd
import time
import os
from rdkit import Chem
from rdkit.Chem import Draw
import plotly.express as px

from modules.modeling import load_coordinates
from modules.visualizing import detect_color_type, plot_chemical_space, plot_similarity_histograms, plot_similarity_threshold_pie, plot_treemap
from modules.preprocessing import get_demo_assets_root

def main():

    st.set_page_config(page_title="Run COMPASS", page_icon="🧭")

    pg = st.navigation([
        st.Page("pages/0_compass.py", title="COMPASS app", icon="🧭"),
        st.Page("pages/1_userguide.py", title="User guide", icon="⚙️"),
        st.Page("pages/2_about.py", title="About", icon=":material/info:"),
    ])
    pg.run()



if __name__ == '__main__':
    main()
    print('app is running')
    #todo: clear the user folder after the app is closed? or after a certain time period? to prevent storage issues when hosting in EAWAG
    # todo: The u should know that if they install the app locally, the data will be stored on their computer in the /data/_USER folder, and they can delete it whenever they want