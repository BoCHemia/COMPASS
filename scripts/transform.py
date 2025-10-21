from modules.modeling import *
from modules.preprocessing import *

# load tSNE model object
reference_data_name = "zeropm"
model = load_model(reference_data_name, from_zip=False)

# load data to plot
new_data_name = 'pfas_market_inventory' # enter here the name of the input data set to transform
folder_name = 'input' #
load_input_file(new_data_name)
new_fingerprints = preprocess_data(folder=folder_name, filename=new_data_name)
save_fingerprints(fingerprints=new_fingerprints, filename=new_data_name)
# new_fingerprints = load_fingerprints(filename=new_data_name)

# transform
coordinates = transform_target(model, new_fingerprints)
save_coordinates(coordinates=coordinates,
                 foldername=folder_name,
                 filename=new_data_name,
                 reference_data=reference_data_name)

