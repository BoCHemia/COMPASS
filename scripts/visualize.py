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

# load input coordinates, to be mapped to reference
input_file_2 = 'pfas_market_inventory'
new_coordinates_2 = load_coordinates(foldername=input_folder, filename=input_file_2)

# plots
# figure = chemical_space_plot(reference_coordinates, hue_column=None, color_map=None, hover_data=['INCHIKEY', 'SMILES'])
# save_figure(figure, input_file)
# quit()

figure = chemical_space_plot_grey(reference_coordinates, hover_data=['INCHIKEY', 'SMILES'], opacity=0.5)
figure = map_input_data(figure, new_coordinates_2, nametag=input_file_2,
                        hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'CAS', 'Synonyms'])
# figure = map_input_data(figure, new_coordinates, nametag=input_file,
#                         hover_name='SMILES', hover_data=['INCHIKEY'],
#                         color='SIZE')
figure.show()
save_figure(figure, input_file)
# chemical_space_plot(new_coordinates)