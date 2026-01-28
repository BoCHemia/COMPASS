# import resource
import streamlit as st
import pandas as pd
import time
import os

def main():
    
    develop = st.checkbox("dev")

    # Some default variables
    users_target_chemicals = None

    # Streamlit app title
    st.title("COMPASS")

    st.markdown("""
                COMPASS (**COMPA**rative chemical **S**pace **S**ystems) acts as a navigation tool for chemical space, offering harmonized reference maps 
                that support transparent visualisation of chemical datasets and model domains. 
                By selecting a reference space (e.g., marketed chemicals, pharmaceuticals, PFAS), 
                you can locate and explore your own substances in relation to known chemical landscapes.
                """)
    
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


    # Dropdown menu for selecting the reference model
    available_ref_spaces_dict = {'DrugBank': ['5.1.13', '5.1.13_partial'],
                                 'PFAS': ['nist'],
                                 'ZeroPM': [None, 'partial'],
                                 'Coconut': None}
    
    # 1st container: Defining the reference space
    with st.container(): # I am using this to prevent the rest of the code from running until the form is submitted
        st.markdown("### Step 1: Configure the reference chemical space for mapping")  # I am still not sure about the wording here
    # Dropdown menu for selecting the reference model
    
        reference_space = st.selectbox('Choose reference space',
                                placeholder='Choose an option',
                                index=None,
                                options=available_ref_spaces_dict.keys(),
                                key='ref_space')
        if reference_space:
            reference_folder_name = str(reference_space)
            reference_file_name = str.lower(reference_space)

        ref_versions = available_ref_spaces_dict.get(reference_space)
        if ref_versions:
            reference_space_version = st.selectbox('Choose version',
                                                placeholder='Choose an option',
                                                index=None,
                                                options=ref_versions,
                                                key='ref_sapce_version')
            if reference_space_version:
                reference_file_name = str.lower(reference_space + "_" + reference_space_version)

    
    # 2nd container: Defining the target space
    with st.container():
        st.markdown("### Step 2: Select your target chemical substances of interest")
        target_space = st.selectbox('Choose which chemical space to map into the reference',
                                placeholder='Choose an option',
                                index=None,
                                options=list(available_ref_spaces_dict.keys()) + ['my_own_substances'],
                                key='target_space')

        if target_space:
            target_folder_name = str(target_space)
            target_file_name = str.lower(target_space)


        target_versions = available_ref_spaces_dict.get(target_space)
        if target_versions: 
            target_space_version = st.selectbox('Choose version',
                                                placeholder='Choose an option',
                                                index=None,
                                                options=target_versions,
                                                key='target_space_version_selectbox')
            if target_space_version:
                target_file_name = str.lower(target_space + "_" + target_space_version)


        # Section to define the target when the user selects 'my_own_substances'
        # Upload CSV file
        if target_space == 'my_own_substances':
            user_target_chemicals = st.file_uploader("Upload a CSV file with your chemical substances of interest", type="csv")
            if user_target_chemicals:
                target_file_name = 'user_target_chemicals' # placeholder to allow user specified naming later
                target_folder_name = '_USER'


                # Load the uploaded data, save to data/_USER folder
                user_target_chemicals = pd.read_csv(user_target_chemicals)
                user_target_chemicals.to_csv(os.path.join('data', '_USER', target_file_name + '.csv'), index=False)

                # Show the input data
                st.write("Uploaded data:", user_target_chemicals)
            else:
                st.info("Please upload a CSV file to proceed.")
                st.stop()
        

    # Submit button to proceed when all necessary information has been provided
    with st.form("config_form", clear_on_submit=False, border=False): 
        submit_message = "Get chemical space mapping"
        submitted = st.form_submit_button(submit_message)  # The form and the button defaults are so ugly, but we can change it later

    if not submitted:
        st.write("Please press the ''{}''  button to proceed.".format(submit_message))
        st.stop()


    # One more section to check if everything is set up correctly
    # If things are missing we will catch them here and we can inform the user

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

    if missing:
        st.warning("Please provide: " + ", ".join(missing))
        st.stop()


    st.write("You have selected to map {} into {}".format(target_space, reference_space))  

    if not develop:
        with st.spinner("Calculating the chemical space mapping; this may take several minutes", show_time=True):
            time.sleep(1)
            progress_bar = st.progress(0)
            from modules.modeling import preprocess_data, save_user_file, save_fingerprints

            progress_bar.progress(5)
            if target_space == 'my_own_substances':
                st.info("Preprocessing user data")
                st.info("User data is preprocessed and saved in user folder")
                st.info("Calculating fingerprints")
                # new_df = load_input_file(file_name, foldername=folder_name)
                # new_df = pd.read_csv(os.path.join('data', target_folder_name, "output_{}.csv".format(target_file_name)))
                new_df = user_target_chemicals
                # todo: This is weird. I would like to have preprocess_data() and get_fingerprints() functions
                new_fingerprints = preprocess_data(new_df)
                save_user_file(user_dataframe=new_fingerprints, folder_name=target_folder_name, file_name=target_file_name )
                save_fingerprints(fingerprints=new_fingerprints, folder_name=target_folder_name, file_name=target_file_name)
                progress_bar.progress(25)
                st.info("Fingerprints have been calculated and saved")
            
            else:
                pass  # For now we only process user data

            st.info("Next the trained reference model is loaded; this takes 1-3 mins")
            # load tSNE model object
            progress_bar.progress(30)
            from modules.modeling import (load_model, transform_target, save_coordinates)
            model = load_model(reference_file_name, use_joblib=True) #use_joblib=False, from_zip=False
            
            st.info("loading model worked")
            progress_bar.progress(75)

            # transform
            st.info("Next the coordinates of the user target chemicals are calculated using the loaded reference model")
            target_coordinates = transform_target(model, new_fingerprints)
            progress_bar.progress(95)
            st.info("getting the new coordinates worked ant they are being saved now")
            save_coordinates(coordinates=target_coordinates,
                                folder_name=target_folder_name,
                                file_name=target_file_name,
                                reference_name=reference_file_name)
            
    else:
        pass

    
    from modules.modeling import load_coordinates
    from modules.visualizing import plot_chemical_space # chemical_space_plot_grey, map_input_data

    
    st.write('Project substances')
    project_progress_bar = st.progress(0)
    
    with st.spinner("Projecting your substances of interest", show_time=True):
        time.sleep(3)
        project_progress_bar.progress(10)
        

        
        ###### Plot 1: Plot user target chemicals on reference space #####
        # load reference coordinates


        reference_coordinates = load_coordinates(reference_folder_name, reference_file_name)
        st.info("loading reference coordinates worked")
        project_progress_bar.progress(50)
        target_coordinates = load_coordinates(target_folder_name,
                                                target_file_name,
                                                reference_data=reference_file_name)
        st.info("loading target coordinates worked")
        project_progress_bar.progress(70)

        # For now let's suppose that the user uploads the coordinates directly
        # In reality the usser-provided-file will be preprocess and transformed. 
        # new_coordinates = users_target_chemicals
        # input_file = 'user_chemicals'
        # Show the coordinates data
        # st.write("Coordinates data:", coordinates_df)
        reference_data_name = str(reference_space)
        # fig_grey = plot_chemical_space(reference_coordinates, nametag=reference_data_name + ' reference space', 
        #                     hover_name='INCHIKEY',  hover_data=['INCHIKEY'], opacity=0.8)
        # figure = plot_chemical_space(target_coordinates, nametag=target_file_name, map_on=fig_grey,
        #             hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'PREFERRED_NAME'],
        #             color='red', opacity=1)
        
        hover_data_ref_preferred = ['Superclass', 'Class', 'Subclass', 'SMILES', 'CAS']
        hover_data_ref_available = [c for c in hover_data_ref_preferred if c in reference_coordinates.columns]

        figure = plot_chemical_space(reference_coordinates, nametag=reference_data_name + ' reference space', 
                                    hover_name='PREFERRED_NAME', hover_data=hover_data_ref_available)
        
        hover_data_preferred = ['Superclass', 'Class', 'Subclass', 'SMILES', 'CAS']
        hover_data_available = [c for c in hover_data_preferred if c in target_coordinates.columns]

        if 'Superclass' in hover_data_available:
            figure = plot_chemical_space(target_coordinates, nametag=target_file_name, map_on=figure,
                                        hover_name='PREFERRED_NAME', hover_data=hover_data_available,
                                        column_for_color_map='Superclass', color_type='discrete', palette="Alphabet",
                                        symbol='diamond', size=3, opacity=0.5)
        else:
            figure = plot_chemical_space(target_coordinates, nametag=target_file_name, map_on=figure,
                    hover_name='INCHIKEY', hover_data=hover_data_available, color='red', size=3, opacity=0.7)

        project_progress_bar.progress(95)    
        st.plotly_chart(figure, use_container_width=True)
        
        #fig_color = chemical_space_plot()  @TODO: I will check later because we need to specify hue_column and so on
        st.write("{} is the reference space shown in grey.".format(reference_space))

        # Load the trained object
        # Transform the user to the reference space of interest. 

        project_progress_bar.progress(100)
        st.success("Done!!!")

    
        

        # # Show the predictions
        # st.markdown(""" ### Predictions: """)
        # config = {
        #     "Structure": st.column_config.ImageColumn(width="medium"),
        # }
        # st.dataframe(predictions_df, column_config=config, row_height=100)


        # This is how I could plot the chemical space with plotly for the Shiny App - assumes input where the user selects a variable for hue (color) - Kerstin
        # @render_widget
        # def chemical_space_plot():
        #     df = loaded_data()  # Use cached data
        #     if df.empty:
        #         return px.scatter(title="No data available")

        #     # Define custom order (equivalent to seaborn's hue_order)
        #     hue_column = input.hue_column()

        #     # Set palette
        #     if hue_column in ['Toxicity [log10 mg/kg-d]', 'Uncertainty [95% CI width]']:
        #         hue_order = sorted(df[hue_column].unique())
        #         if hue_column == 'Toxicity [log10 mg/kg-d]':
        #             hue_order = hue_order[::-1]
        #         colorscale = sns.diverging_palette(250, 10, s=100, l=50, sep=1, n=len(hue_order), center="light")
        #         colors = [mcolors.to_hex(c) for c in colorscale]
        #         color_map = dict(zip(hue_order, colors)) 

        #     else:
        #         hue_order = df[hue_column].value_counts().index.tolist() # sort by frequency
        #         df[hue_column] = pd.Categorical(df[hue_column], categories=hue_order, ordered=True)
        
        #         colors = [mcolors.rgb2hex(c) for c in plt.cm.tab20.colors]
        #         # - repeat colors if more than 20 categories
        #         repeat_colors = (colors * (len(hue_order) // len(colors) + 1))[:len(hue_order)]
        #         color_map = dict(zip(hue_order, repeat_colors))

            
        #     # Scatterplot
        #     df.fillna('not assigned', inplace=True)
        #     fig = px.scatter(df, x="TSNE1", y="TSNE2", color=hue_column,
        #                     color_discrete_map=color_map,
        #                     category_orders = {hue_column: hue_order},
        #                     hover_name = 'Chemical name',
        #                     hover_data=['CAS RN', 'Predicted POD [95% CI]', 'Superclass', 'Class', 'Subclass'],
        #                     render_mode="webgl",
        #                     height=700, width=1200
        #                     )
        #     fig.update_traces(showlegend=False)

        #     fig.update_traces(marker=dict(size=3, opacity=0.3, line=dict(width=0))) # plot markers
        #     fig.update_traces(marker=dict(size=10), opacity=1, selector=dict(legendgroup=True)) # legend markers

        #     # Add custom legend traces to control the opacity of the legend markers
        #     categories = hue_order

        #     for category in categories:
        #         fig.add_trace(go.Scatter(
        #             x=[None], y=[None],  # Invisible points
        #             mode='markers',
        #             marker=dict(color=color_map[category], size=12, opacity=1),  # Full opacity for the legend
        #             legendgroup=category,
        #             showlegend=True,
        #             name=category,
        #         ))

        #     fig.update_layout(
        #         dragmode="zoom",  # - enables zooming
        #         uirevision=True,  # Track the zoom and pan state
        #         xaxis=dict(title="TSNE1",visible=False, showgrid=False, zeroline=False, 
        #                 fixedrange=False),
        #         yaxis=dict(title="TSNE2",visible=False, showgrid=False, zeroline=False, 
        #                 fixedrange=False),
        #         modebar=dict(add=["zoom", "pan", "resetScale"]),
        #         plot_bgcolor="rgba(0,0,0,0)",
        #         paper_bgcolor="rgba(0,0,0,0)",
        #         legend_title_text=hue_column,
        #         legend=dict(itemsizing='constant',  # Control legend item sizing
        #                     itemwidth=30,  # Adjust this value to control the item width
        #                     tracegroupgap=0,  # Gap between legend items
        #                     x=1.0,  # Position the legend towards the right
        #                     y=0.5,  # Center vertically
        #                     xanchor='left',
        #                     yanchor='middle',
        #                     orientation='v',  # Arrange legend vertically
        #                     font=dict(family="Arial", size=10)))
                        
        #     return fig



if __name__ == '__main__':
    main()
    print('app is running')