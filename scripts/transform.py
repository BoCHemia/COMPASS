from modules.modeling import *
from modules.preprocessing import *

# load tSNE model object
reference_file_name = "drugbank_5.1.13_partial"
model = load_model(reference_file_name, use_joblib=True, from_zip=False)
offset = load_model_offset(reference_file_name) # add to app.py

# load data to plot
folder_name = "ZeroPM"
file_name = 'zeropm_partial' # enter here the name of the input data set to transform

# new_df = load_input_file(file_name, folder_name=folder_name)
# new_fingerprints = preprocess_data(new_df)
# save_fingerprints(fingerprints=new_fingerprints, folder_name=folder_name, file_name=file_name,)
new_fingerprints = load_fingerprints(file_name=file_name, folder_name=folder_name)

# transform
coordinates = transform_target(model, new_fingerprints)
coordinates = coordinates - offset.values # add to app.py

save_coordinates(coordinates=coordinates,
                 folder_name=folder_name,
                 file_name=file_name,
                 reference_name=reference_file_name)
