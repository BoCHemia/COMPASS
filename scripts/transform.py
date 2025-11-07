from modules.modeling import *
from modules.preprocessing import *

# load tSNE model object
reference_data_name = "zeropm"
model = load_model(reference_data_name, from_zip=False)

# load data to plot
folder_name = "DrugBank"
file_name = 'drugbank_5.1.13' # enter here the name of the input data set to transform

new_df = load_input_file(file_name, foldername=folder_name)
new_fingerprints = preprocess_data(new_df)
save_fingerprints(fingerprints=new_fingerprints, filename=file_name)
# new_fingerprints = load_fingerprints(filename=new_data_name)

# transform
coordinates = transform_target(model, new_fingerprints)
save_coordinates(coordinates=coordinates,
                 folder_name=folder_name,
                 file_name=file_name,
                 reference_data=reference_data_name)
