from modules.modeling import *
from modules.preprocessing import *


import sys
sys.stdout.reconfigure(line_buffering=True)

#### input ####
input_folder_name = "COCONUT"
input_data_name = "coconut" # file "data_market.csv" should be saved under "data/market"

#### preprocessing and calculating fingerprints ####
df_fingerprints = preprocess_data(input_folder_name, input_data_name, radius=2, fpSize=1024)
save_fingerprints(df_fingerprints, input_data_name)

# df_fingerprints = load_fingerprints(filename=input_data_name) # --> can be used if fingerprints are already calculated and available in temp folder

#### train model ####
trained_model, coordinates = fit_tsne_model(df_fingerprints=df_fingerprints)
# trained_model = load_model(filename=input_data_name)
# coordinates = load_coordinates(foldername=input_folder_name, filename=input_data_name)
save_model(model=trained_model, filename=input_data_name)
save_coordinates(coordinates=coordinates, foldername=input_folder_name, filename=input_data_name)
