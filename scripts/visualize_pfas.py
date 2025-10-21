from modules.modeling import *
from modules.visualizing import *

# load reference coordinates
# reference_folder = 'PFAS'
# reference_file = 'pfas_nist'
reference_folder = 'ZeroPM'
reference_file = 'zeropm'
reference_coordinates = load_coordinates(reference_folder, reference_file)

# load input coordinates, to be mapped to reference
input_folder = 'input'
# input_file = 'pfas_envipath'
# new_coordinates = load_coordinates(foldername=input_folder, filename=input_file, reference_data=reference_file)

# load input coordinates, to be mapped to reference
input_file_2 = 'pfas_market_inventory'
new_coordinates_2 = load_coordinates(foldername=input_folder, filename=input_file_2, reference_data=reference_file)


figure = chemical_space_plot_grey(reference_coordinates, hover_data=['INCHIKEY', 'SMILES'], opacity=0.5)
figure = map_input_data(figure, new_coordinates_2, nametag=input_file_2,
                        hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'CAS', 'Synonyms'])
# figure = map_input_data(figure, new_coordinates, nametag=input_file,
#                         hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'SMILES'],
#                         column_for_color_map='SIZE', color_type='continuous', palette='Bluered',
#                         opacity=1, size=5)
figure.show()
# output_filename = f'{reference_file}_{input_file}'
output_filename = f'{reference_file}_{input_file_2}'
save_figure(figure, output_filename)
