import pandas as pd
import numpy as np
import os
from modules.modeling import *
from modules.preprocessing import *


import sys
sys.stdout.reconfigure(line_buffering=True)

#### input ####
input_folder_name = "drugbank_5.1.13"
input_data_name = "drugbank"

#### preprocessing and calculating fingerprints ####
df_fingerprints = preprocess_data(input_folder_name, input_data_name, radius=2, fpSize=1024)
save_fingerprints(df_fingerprints, input_data_name)

#### load training_array from fingerprints file ####
# --> can be used if fingerprints are already calculated and available in output folder
# df_fingerprints = load_fingerprints(filename=input_data_name) # --> can be used if fingerprints are already calculated and available in temp folder

#### train model ####
trained_model, coordinates = fit_tsne_model(df_fingerprints=df_fingerprints)
# trained_model = load_model(filename=input_data_name)
# coordinates = load_coordinates(foldername=input_folder_name, filename=input_data_name)
save_model(model=trained_model, file_name=input_data_name, zip=False)
save_coordinates(coordinates=coordinates, foldername=input_folder_name, file_name=input_data_name)
