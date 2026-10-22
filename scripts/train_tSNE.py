from modules.modeling import *
from modules.preprocessing import *

#### input ####
input_folder_name = "ZeroPM"
input_data_name = "zeropm_partial"

#### load preprocessed data and calculate fingerprints ####
df = load_input_file(file_name=input_data_name, folder_name=input_folder_name)
df_fingerprints, df = calculate_fingerprints(df)
update_df(df, input_folder_name, input_data_name, 'input')
raw_input_path = os.path.join(PROJECT_ROOT, "data", input_folder_name, f"input_{input_data_name}.csv")
df.to_csv(raw_input_path) # save fingerprint hex to input
save_fingerprints(df_fingerprints, folder_name=input_folder_name, file_name=input_data_name)

#### load training_array from fingerprints file ####
# --> can be used if fingerprints are already calculated and available in output folder
df_fingerprints = load_fingerprints(input_folder_name, input_data_name) # --> can be used if fingerprints are already calculated and available in temp folder

#### train model ####
trained_model, coordinates = fit_tsne_model(df_fingerprints=df_fingerprints)
# trained_model = load_model(file_name=input_data_name)
# trained_model = load_model(file_name=input_data_name)
# coordinates = load_coordinates(folder_name=input_folder_name, file_name=input_data_name)
save_model(model=trained_model, file_name=input_data_name)
save_coordinates(coordinates=coordinates, folder_name=input_folder_name, file_name=input_data_name)

### save model offset ###
offset_init = pd.DataFrame({0:{'TSNE1': 0, 'TSNE':0}}).T
coordinates_re = transform_target(trained_model, df_fingerprints, offset_init)
offset = coordinates_re[['TSNE1', 'TSNE2']].mean().to_frame().T
save_model_offset(offset, input_data_name)

### Optional ###
# Analysis of coordinates obtained from fit_transform vs. transform
# print("Max difference between original and re-trained TSNE model:")
# coordinates_dedup = coordinates_re.drop_duplicates(subset=['FP_HEX'])
# coordinates_re = coordinates_re.merge(coordinates_dedup, how='left', on=['FP_HEX'])
# coordinates_re['diff_tsne1'] = abs(coordinates_re['TSNE1_x'] - coordinates_re['TSNE1_y'])
# coordinates_re['diff_tsne2'] = abs(coordinates_re['TSNE2_x'] - coordinates_re['TSNE2_y'])
# coordinates_re.to_csv('coordinates_re.csv')


### Training ###
# AgroTrak: done
# COCONUT: done
# DrugBank: done
# PFAS: done
# PlastChem: done
# ZeroPM: done
