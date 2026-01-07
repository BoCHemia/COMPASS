import pandas as pd
import numpy as np
from modules.modeling import *
from modules.preprocessing import *

# import sys
# sys.stdout.reconfigure(line_buffering=True)

#### input ####
input_folder_name = "AgroTrak"
input_data_name = "agrotrak_zhang_2025_partial"

#### load preprocessed data and calculate fingerprints ####
df = load_input_file(file_name=input_data_name, folder_name=input_folder_name)
df_fingerprints = calculate_fingerprints(df)
save_fingerprints(df_fingerprints, folder_name=input_folder_name, file_name=input_data_name)

#### load training_array from fingerprints file ####
# --> can be used if fingerprints are already calculated and available in output folder
# df_fingerprints = load_fingerprints(filename=input_data_name) # --> can be used if fingerprints are already calculated and available in temp folder

#### train model ####
trained_model, coordinates = fit_tsne_model(df_fingerprints=df_fingerprints)
# trained_model = load_model(file_name=input_data_name, use_joblib=True)
# coordinates = load_coordinates(folder_name=input_folder_name, file_name=input_data_name)
save_model(model=trained_model, file_name=input_data_name, use_joblib=True)
save_coordinates(coordinates=coordinates, folder_name=input_folder_name, file_name=input_data_name)

### save model offset 
coordinates_re = transform_target(trained_model, df_fingerprints)
offset = coordinates_re.mean().to_frame().T
save_model_offset(offset, input_data_name)
