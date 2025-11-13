from modules.modeling import *
from modules.visualizing import *

###### Plot 1: COCONUT on its own #####
input_folder = 'COCONUT'
input_file = 'coconut'
coordinates = load_coordinates(folder_name=input_folder, file_name=input_file)

figure = plot_chemical_space(coordinates, nametag='COCONUT', hover_name='PREFERRED_NAME', 
                             hover_data=['SMILES'])

output_filename = f'{input_file}'
save_figure(figure, output_filename)


