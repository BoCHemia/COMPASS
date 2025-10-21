from modules.modeling import *
from modules.visualizing import *

# load reference coordinates
reference_folder = 'COCONUT'
reference_file = 'coconut'
reference_coordinates = load_coordinates(reference_folder, reference_file)

# load input coordinates, to be mapped to reference
input_folder = 'input'
input_file = 'zeropm'
new_coordinates = load_coordinates(foldername=input_folder, filename=input_file, reference_data=reference_file)


figure = chemical_space_plot_grey(reference_coordinates, hover_data=['INCHIKEY', 'SMILES'], opacity=0.5)
figure = map_input_data(figure, new_coordinates, nametag=input_file,
                        hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'IUPAC', 'Synonyms'])

figure.show()
output_filename = f'{reference_file}_{input_file}'
save_figure(figure, output_filename)
