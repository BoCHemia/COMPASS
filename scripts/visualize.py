from modules.modeling import *
from modules.visualizing import *

# load reference coordinates
reference_folder = 'PFAS'
reference_file = 'pfas_nist'
reference_coordinates = load_coordinates(reference_folder, reference_file)

# load input coordinates, to be mapped to reference
input_folder = 'input'
input_file = 'pfas_envipath'
new_coordinates = load_coordinates(foldername=input_folder, filename=input_file)

# plot - todo: not working yet
# chemical_space_plot_grey(reference_coordinates)
# chemical_space_plot(new_coordinates)