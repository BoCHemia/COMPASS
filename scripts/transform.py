from modules.modeling import *
from modules.preprocessing import *

# load tSNE model object
reference_file_name = "coconut"
model = load_model(reference_file_name, from_zip=False)

# load data to plot
folder_name = "DrugBank"
file_name = 'drugbank_5.1.13_partial' # enter here the name of the input data set to transform

new_df = load_input_file(file_name, folder_name=folder_name)
new_fingerprints = preprocess_data(new_df)
save_fingerprints(fingerprints=new_fingerprints, folder_name=folder_name, file_name=file_name,)
# new_fingerprints = load_fingerprints(filename=new_data_name)

# transform
coordinates = transform_target(model, new_fingerprints)
save_coordinates(coordinates=coordinates,
                 folder_name=folder_name,
                 file_name=file_name,
                 reference_name=reference_file_name)
