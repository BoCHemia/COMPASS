from modules.modeling import *
from modules.visualizing import *

###### Plot 1: Drugbank on ZeroPM #####
# load reference coordinates
reference_folder = 'ZeroPM'
reference_file =  'zeropm'
reference_coordinates = load_coordinates(reference_folder, reference_file)

# load input coordinates, to be mapped to reference
input_folder = 'drugbank_5.1.13'
input_file = 'drugbank'
new_coordinates = load_coordinates(foldername=input_folder, filename=input_file, reference_data=reference_file)

figure = chemical_space_plot_grey(reference_coordinates, hover_data=['INCHIKEY', 'SMILES'], opacity=0.8)
figure = map_input_data(figure, new_coordinates, nametag=input_file,
                        hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'SMILES'],
                        color="red",  opacity=1)
figure.show()

# Save figure
output_filename = f'{reference_file}_{input_file}'
save_figure(figure, output_filename)
