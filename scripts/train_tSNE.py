import pandas as pd
import numpy as np
import os
from modules.modeling import *
from modules.preprocessing import *


#### input ####
input_data_name = "pfas_nist" # file "data_market.csv" should be saved under "data"

#### preprocessing and calculating fingerprints ####
# df_fingerprints = preprocess_data(input_data_name)
# save_fingerprints(df_fingerprints, input_data_name)
df_fingerprints = load_fingerprints(input_data_name)

#### load training_array from fingerprints file ####
# --> can be used if fingerprints are already calculated and available in output folder
# training_array, inchikeys = load_training_array(input_data_name,
#                                       use_subset=True,
#                                       subset_n=1000) # subset for testing
training_array, inchikeys = load_training_array(input_data_name) # full set

#### train model ####
trained_model, coordinates = fit_tsne_model(training_array)
# trained_model = load_model(input_data_name)
save_model(trained_model, input_data_name)
save_coordinates(coordinates, input_data_name, inchikeys)


