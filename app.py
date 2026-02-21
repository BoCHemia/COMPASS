# import resource
import streamlit as st
import pandas as pd
import time
import os
import plotly.express as px

from modules.modeling import load_coordinates
from modules.visualizing import plot_chemical_space, plot_treemap
from modules.preprocessing import get_demo_assets_root

def main():
    st.set_page_config(page_title="COMPASS", page_icon="🧭",
                       layout="wide", initial_sidebar_state="expanded",
                        menu_items={
                            'About': "COMPASS (**COMPA**rative chemical **S**pace **S**ystem) acts as a navigation tool for chemical space,  "
                            "offering harmonized reference maps that support transparent visualisation of chemical datasets and model domains. "
                            "By selecting a reference space (e.g., marketed chemicals, pharmaceuticals, PFAS), "
                            "you can locate and explore chemical data sets in relation to known chemical landscapes. "
                            "You can provide your own data set or select from pre-defined target spaces."})


    # # # ----------- RESOURCE LIMITS -----------
    minimal_columns = ['SMILES', 'INCHIKEY', 'IUPAC', 'PREFERRED_NAME',
       'TSNE1', 'TSNE2', 'Kingdom', 'Superclass',
       'Class', 'Subclass']

    # ----------- APP MODE LOGIC (currently 'demo' or 'full') ----------- 
    # ---------------- The test_demo mode is only for testing the demo assets locally without downloading from Zenodo each time, and should not be exposed to users in the app; this is just for development purposes ----------------
    MODE = os.getenv("COMPASS_MODE", "demo").strip().lower() 
    print(MODE)  # "demo" or "full"
    
    IS_DEMO = MODE == "demo"
    
    # if IS_DEMO:
    if MODE == "demo":
        DEMO_ZIP_URL = os.getenv("COMPASS_DEMO_ZIP_URL", "https://zenodo.org/records/18723920/files/demo_assets.zip")
        DEMO_ZIP_MD5 = os.getenv("COMPASS_DEMO_ZIP_MD5", "16b0ecfa753c9f19ac6da2fad391024c")

        ASSET_ROOT = get_demo_assets_root(DEMO_ZIP_URL, expected_md5=DEMO_ZIP_MD5)
    elif MODE == "test_demo":
        ASSET_ROOT = "demo_assets"  # for testing the demo assets locally without downloading from Zenodo each time
    
    else:
        ASSET_ROOT = "data"    





    # ----------- CONFIGURATION SIDEBAR ----------- 
    # Streamlit app title
    st.sidebar.title("🧭 COMPASS") # could be replaced with an image logo later 
    #st.sidebar.markdown("# COMPASS\n") 
    
    st.sidebar.markdown("""
                        COMPASS (**COMPA**rative chemical **S**pace **S**ystem) acts as a navigation tool for chemical space, 
                        offering harmonized reference maps that support transparent visualisation of chemical datasets and model domains. 
                        By selecting a reference space (e.g., marketed chemicals, pharmaceuticals, PFAS), 
                        you can locate and explore chemical data sets in relation to known chemical landscapes.
                        You can provide your own data set or select from pre-defined target spaces.
                """)
    
    darkmode = st.sidebar.checkbox("dark mode")

    # Step 1: Select reference space
    st.sidebar.markdown("### 1: Select reference chemical space")
    available_ref_spaces_dict = {'DrugBank': ['5.1.13_partial'],  # should this automatically update with what is available in /data?
                                    'PFAS': ['nist_partial'],
                                    'PlastChem': ['db_v1.01_partial'],
                                    'ZeroPM': ['partial'],
                                    'COCONUT': ['partial'],
                                    'AgroTrak': ['zhang_2025_partial']}
    
    reference_space = st.sidebar.selectbox('Select reference chemical space"', label_visibility="collapsed",
                            placeholder='Choose an option',
                            index=None,
                            options=available_ref_spaces_dict.keys(),
                            key='ref_space')
    if reference_space:
        reference_folder_name = str(reference_space)
        reference_file_name = str.lower(reference_space)

        ref_versions = available_ref_spaces_dict.get(reference_space)
        if ref_versions:

            if len(ref_versions) == 1:
                # Automatically select the single available version
                reference_space_version = ref_versions[0]
                st.sidebar.write(f"Version: **{reference_space_version}**")
            else:
                # Let the user choose
                reference_space_version = st.sidebar.selectbox('Choose version',
                                                placeholder='Choose an option',
                                                index=None,
                                                options=ref_versions,
                                                key='ref_space_version')
            if reference_space_version:
                reference_file_name = str.lower(reference_space + "_" + reference_space_version)
    
    # Step 2: Select target chemicals to map into
    st.sidebar.markdown("### 2: Select target chemicals to map into the reference space")
    target_space = st.sidebar.selectbox('Select target chemicals to map into the reference space',  label_visibility="collapsed",
                            placeholder='Choose an option',
                            index=None,
                            options= [None] + list(available_ref_spaces_dict.keys()) + ['my_own_substances'],
                            key='target_space')
    
    if target_space:
        target_folder_name = str(target_space)
        target_file_name = str.lower(target_space)

        target_versions = available_ref_spaces_dict.get(target_space)
        if target_versions: 
            if len(target_versions) == 1:
                # Automatically select the single available version
                target_space_version = target_versions[0]
                st.sidebar.write(f"Version: **{target_space_version}**")
            else:
                # Let the user choose
                target_space_version = st.sidebar.selectbox('Choose version',
                                                placeholder='Choose an option',
                                                index=None,
                                                options=target_versions,
                                                key='target_space_version_selectbox')
            if target_space_version:
                target_file_name = str.lower(target_space + "_" + target_space_version)

    # - Enable .csv upload when the user selects 'my_own_substances'
    if target_space == 'my_own_substances':
        if IS_DEMO:
            st.sidebar.warning("Uploading your own dataset is only available using the full version." \
            "The full versions is distributed using Docker and can be run locally on your machine;" \
            "please follow this [link](https://github.com/BoCHemia/global-chemical-space/tree/develop) and refer to the README for instructions. ")
            
            st.stop()

        user_target_chemicals = st.file_uploader("Upload a CSV file with your chemical substances of interest", type="csv")

        @st.cache_data
        def cache_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode("utf-8")
        example_csv = pd.read_csv(os.path.join('app_data', 'example_target_chemicals.csv'))
        csv = cache_df(example_csv)

        st.sidebar.download_button(
            label="Download example file",
            data=csv,
            file_name="test_space.csv",
            mime="text/csv",
        )
        
        if user_target_chemicals:
            # I could create a userid for each session and save the file with the userid to prevent overwriting when multiple users are using the app at the same time, but for now I will just use a placeholder name and overwrite it each time; this means that if multiple users are using the app at the same time, they will overwrite each other's data, but this is a limitation we can live with for now; if we want to allow multiple users to use the app at the same time in the future, we can implement a user management system and save the files with unique user ids
            target_file_name = 'user_target_chemicals' # placeholder to allow user specified naming later
            target_folder_name = '_USER'

            # Load the uploaded data, save to data/_USER folder
            df_user = pd.read_csv(user_target_chemicals)
            df_user.to_csv(os.path.join('data', '_USER', 'raw_' + target_file_name + '.csv'), index=False)

            # Show the input data
            st.write("Uploaded data:", df_user)
        else:
            st.info("Please upload a CSV file to proceed.")
            st.stop()


    # Step 3: Activate mapping --  Can we make the form/button more beautiful?
    with st.sidebar.form("config_form", clear_on_submit=False, border=False): 
        submit_message = "Get chemical space mapping"
        submitted = st.form_submit_button(submit_message)  
        if submitted:
            st.session_state["submitted"] = True

    if "submitted" not in st.session_state:
        st.write(f"Please press the '{submit_message}' button to proceed.")
        st.stop()
    
    # - Check if everything is set up correctly
    if st.session_state.get("submitted", False):
        missing = []
        if reference_space is None:
            missing.append("reference space")
        if (available_ref_spaces_dict.get(reference_space)) and (reference_space_version is None):
            missing.append("reference version")

        if target_space is None:
            missing.append("target space")

        if (available_ref_spaces_dict.get(target_space)) and (target_space_version is None):
            missing.append("target version")

        if target_space == "my_own_substances" and user_target_chemicals is None:
            missing.append("CSV file with target chemicals")

        # Check that something is missing. 
        if missing:
            st.warning("Please provide: " + ", ".join(missing))
            st.stop()

        # Check that the pair selected is allowed based on the config/allowed_mappings.py file
        from config.allowed_mappings import is_mapping_allowed, ALLOWED_MAPPINGS
        if target_space != "my_own_substances":
            if not is_mapping_allowed(reference_space, target_space):
                # Helpful message: show allowed targets for the chosen reference
                allowed_targets = sorted({t for (r, t) in ALLOWED_MAPPINGS if r == reference_space})
                st.error(
                    f"Due to the nature of the selected spaces, mapping **{target_space} into {reference_space}** is not supported.\n\n"
                    # todo: Please refer to our [Learn more]{st.page_link(pages/learn_more.py)} section for details.  

                    f"Supported targets for **{reference_space}**: "
                    f"{', '.join(allowed_targets) if allowed_targets else '—'}"
                )
                st.stop()

        st.sidebar.info("You have selected to map {} into {}".format(target_space, reference_space)) 
        
        # todo: not sure if this should be here
        # st.cache_resource.clear()  # Clear cached model to prevent memory issues;
        # one problem is that it would clear the cached csv too so consider more targeted cache clearing in the future

    
    
    
    # ----------- END OF CONFIGURATION, START OF APP -----------

    # ----------- DATA LOADING AND TRANSFORMATION SECTION ----------- 
    # - Transform user data and calculate coordinates (if needed)

    # ----------- Full app feature ------------ #todo
    # import Capabilities 
    # APP_MODE = os.getenv("COMPASS_MODE", "demo") # 'demo' or 'full_app'
    # caps = Capabilities.from_mode(APP_MODE)
    # This capabilities thing can be used for an intermediate solution
    # For example "lightweight" app hosted by EAWAG with some of the smaller reference spaces. PFAS? 


    if (not IS_DEMO) and (target_space == 'my_own_substances'):
        with st.spinner("Calculating the chemical space mapping; this may take several minutes", show_time=True):
            time.sleep(1)
            
            progress_bar = st.progress(0)
            status_userdata = st.empty()

            from modules.preprocessing import standardize_structures, calculate_fingerprints, save_user_file, save_fingerprints

            progress_bar.progress(5)
            
            # - preprocessing
            status_userdata.info("Preprocessing user data")
            df_user = standardize_structures(df_user)

            progress_bar.progress(15)
            
            required = {"Superclass", "Class", "Subclass"}
            if not required.issubset(df_user.columns):
                status_userdata.info("No ClassyFire information provided; complementing with available ClassyFire data.")
                classyfire = pd.read_csv(os.path.join('data', 'ClassyFire', 'input_classyfire.csv'))
                df_user = pd.merge(df_user, classyfire, on='INCHIKEY', how='left')

                missing_cf = df_user['Superclass'].isna().sum()
                if missing_cf>0:
                    st.warning(f"ClassyFire information merged; {missing_cf} out of {len(df_user)} substances remain without taxonomy information.  \nConsider adding ClassyFire information to your input file.")
                else:
                    status_userdata.status("ClassyFire information merged; all substances have taxonomy information.")

            save_user_file(user_dataframe=df_user, folder_name=target_folder_name, file_name=target_file_name )
            
            progress_bar.progress(20)
            status_userdata.info("User data was preprocessed and saved in user folder")

            # - fingerprints
            status_userdata.info("Calculating fingerprints")
            new_fingerprints = calculate_fingerprints(df_user)
            save_fingerprints(fingerprints=new_fingerprints, folder_name=target_folder_name, file_name=target_file_name)
            
            progress_bar.progress(30)
            status_userdata.info("Fingerprints have been calculated and saved")
            
            # load tSNE model object
            status_userdata.info("Loading trained reference model; this takes 1-3 mins")

            from modules.modeling import (load_model, load_model_offset, transform_target, save_coordinates)
            st.cache_resource(scope="session", show_spinner=True)(load_model)  # Cache the model loading to prevent reloading on every rerun; scope=session ensures it's loaded once per user session
            model = load_model(reference_file_name, use_joblib=True)

            st.cache_resource(scope="session", show_spinner=False)(load_model_offset) 
            offset = load_model_offset(reference_file_name) 
            
            status_userdata.info("Loading model complete")
            progress_bar.progress(75)

            # transform
            status_userdata.info("Calculating coordinates for user target chemicals mapped into selected reference space")
            target_coordinates = transform_target(model, new_fingerprints, offset) 

            progress_bar.progress(95)
            status_userdata.info("Calculation complete...saving coordinates.")
            save_coordinates(coordinates=target_coordinates,
                                folder_name=target_folder_name,
                                file_name=target_file_name,
                                reference_name=reference_file_name)       
            progress_bar.progress(100)

            # - empty progress bars and status after a short delay
            time.sleep(1)
            progress_bar.empty()
            status_userdata.empty()     



    # ----------- Shared feature full app and demo -------------------------------------
    # - load reference and target coordinates
    project_progress_bar = st.progress(0)
    status = st.empty()





    with st.spinner("Projecting your substances of interest", show_time=True):
        # ###### Check that target coordiantes exist ##### #todo 
        # ###### This should work with user coordinates as well, but needs to be tested
        # target_coordinates_file = os.path.join(target_folder_name, f"{target_file_name}_coordinates.csv")
        # if not os.path.exists(target_coordinates_file):
        #     st.warning(f"Target coordinates file does not exist: {target_coordinates_file}")
        #     st.stop()  # Stop execution if target coordinates don't exist


        time.sleep(3)
        project_progress_bar.progress(10)

        
        
        ###### Load selected datasets #####
        @st.cache_data
        def load_coordinates_to_cache(folder_name, file_name, reference_data=""):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return load_coordinates(folder_name, file_name, reference_data, base_dir=ASSET_ROOT)

        # load reference coordinates
        reference_coordinates_full = load_coordinates_to_cache(reference_folder_name, reference_file_name)
        status.info("Loading reference coordinates complete")
        project_progress_bar.progress(50)


        # The plotly for the reference space is still too much to handle when there are >25k points, so for the demo we will only show a subset of the reference space; for the full app we can show the full reference space since it will be hosted locally and not have the same performance issues as Streamlit Cloud; this is a temporary solution until we can implement more advanced solutions for handling large datasets in Streamlit Cloud (e.g., datashader, server-side rendering, etc.)
        if IS_DEMO:
            MAX_REF_POINTS = 450_000  # tune
            if len(reference_coordinates_full) > MAX_REF_POINTS:
                reference_coordinates = reference_coordinates_full.sample(n=MAX_REF_POINTS, random_state=0)
            else:
                reference_coordinates = reference_coordinates_full
        else:
            reference_coordinates = reference_coordinates_full

        # load target coordinates
        if target_space:
            target_coordinates = load_coordinates_to_cache(target_folder_name, target_file_name, reference_data=reference_file_name)
            status.info("Loading target coordinates complete")
            project_progress_bar.progress(70)
        
        project_progress_bar.progress(100)
        status.success("Done!!!")

        # - empty progress bars and status after a short delay
        time.sleep(1)
        project_progress_bar.empty()
        status.empty()

   # ----------- END DATA LOADING AND TRANSFORMATION SECTION ----------- 


    ### ----------- VISUALIZATION SECTION -----------  ###
    ###### Plot 1: Plot user target chemicals on reference space #####
    @st.fragment
    def fragment_plot_chemical_space():    # defining a fragment functions ensure that Streamlit only reruns this part when selecting hue column
        # - Color settings
        with st.container(border=False):

            def allowed_hue_columns(file_name):
                classyfire = ['Kingdom', 'Superclass', 'Class', 'Subclass']
                if 'zeropm' in file_name:
                    hue_columns = classyfire
                elif 'zhang' in file_name:
                    hue_columns = classyfire + ['Chemical class', 'Primary target class', 'Mode of action', 'Mode of action group']
                else:
                    hue_columns = classyfire

                return hue_columns

            cols = st.columns(2)
            if target_space:
                dataset_to_color = cols[0].selectbox("Choose a dataset to customize coloring", ["Reference", "Target", "None"], index=2)
            else:
                dataset_to_color = cols[0].selectbox("Choose a dataset to customize coloring", ["Reference"], index=0)

            if dataset_to_color == "Reference":
                hue_options_ref = [None] + list(set(reference_coordinates.columns) & set(allowed_hue_columns(reference_file_name)))
                hue_ref = cols[1].selectbox("Color reference by", hue_options_ref, index=0)
                hue_target = None  # reset target coloring
            else:
                if target_space == 'my_own_substances':
                    drop_list = ['PREFERRED_NAME', 'INCHIKEY', 'SMILES', 'standardized SMILES', 'TSNE1', 'TSNE2',  'CASRN', 'IUPAC', 'InChI']
                    hue_options_target = [None] +  [c for c in list(target_coordinates.columns) if c not in drop_list]
                else:
                    hue_options_target =  [None] + list(set(target_coordinates.columns) & set(allowed_hue_columns(target_file_name)))
                hue_target = cols[1].selectbox("Color target by", hue_options_target, index=0)
                hue_ref = None  # reset reference coloring

        # - reference set
        hover_data_ref_preferred = ['Superclass', 'Class', 'Subclass', 'CASRN']
        hover_data_ref_available = [c for c in hover_data_ref_preferred if c in reference_coordinates.columns]

        if hue_ref:
            color_type_ref =  'continuous' if pd.api.types.is_numeric_dtype(reference_coordinates[hue_ref]) else 'discrete'
            palette_ref = 'Alphabet' if color_type_ref == 'discrete' else 'Turbo'

            figure = plot_chemical_space(reference_coordinates, nametag=reference_folder_name + ' reference space', 
                                        hover_name='PREFERRED_NAME', hover_data=hover_data_ref_available,
                                        column_for_color_map=hue_ref, color_type=color_type_ref, palette=palette_ref)
        else:
            color = 'lightgrey'
            if darkmode:
                color = 'dimgrey'
            figure = plot_chemical_space(reference_coordinates, nametag=reference_folder_name + ' reference space', 
                                        hover_name='PREFERRED_NAME', hover_data=hover_data_ref_available, color=color)
        
        # - target set
        if target_space: 
            hover_data_preferred = ['Superclass', 'Class', 'Subclass', 'CASRN']
            hover_data_available = [c for c in hover_data_preferred if c in target_coordinates.columns]

            if hue_target:

                color_type_target =  'continuous' if pd.api.types.is_numeric_dtype(target_coordinates[hue_target]) else 'discrete'
                palette_target = 'Alphabet' if color_type_target == 'discrete' else 'Turbo'

                figure = plot_chemical_space(target_coordinates, nametag=target_folder_name + ' target space', map_on=figure,
                                            hover_name='PREFERRED_NAME', hover_data=hover_data_available,
                                            column_for_color_map=hue_target, color_type=color_type_target, palette=palette_target,
                                            symbol='diamond', size=3, opacity=0.5)
            else:
                color = 'black'
                if darkmode:
                    color = 'white'
                figure = plot_chemical_space(target_coordinates, nametag=target_folder_name + ' target space', map_on=figure,
                                            hover_name='PREFERRED_NAME', hover_data=hover_data_available, color='black', 
                                            symbol='diamond', size=3, opacity=0.7)
        
        st.plotly_chart(figure, use_container_width=True)


    with st.container(border=True):
        fragment_plot_chemical_space()
        

    ###### Plot 2: Treemap #####
    @st.fragment
    def fragment_plot_treemap():
        cols = st.columns(2)
        dataset_for_treemap = cols[0].selectbox("Choose a dataset for the treemap", ["Reference", "Target"], index=0)
        df_treemap = reference_coordinates if dataset_for_treemap == "Reference" else target_coordinates
        
        required = {"Superclass", "Class", "Subclass"}
        if required.issubset(df_treemap.columns):
            figure = plot_treemap(df_treemap)
            st.plotly_chart(figure, use_container_width=True)
        else:
            st.info("Treemap can only be generated for datasets containing ClassyFire taxonomy (Superclass, Class, Subclass).")
        
    with st.container(border=True):
        fragment_plot_treemap()
        

if __name__ == '__main__':
    main()
    print('app is running')
    #todo: clear the user folder after the app is closed? or after a certain time period? to prevent storage issues when hosting in EAWAG
    # todo: The user also should know that if they install the app locally, the data will be stored on their computer in the /data/_USER folder, and they can delete it whenever they want