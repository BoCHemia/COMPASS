from modules.modeling import *
from modules.visualizing import *


###### Plot 0: ZeroPM on its own (Superclass) #####
input_folder = 'ZeroPM'
input_file = 'zeropm_partial'
coordinates = load_coordinates(folder_name=input_folder, file_name=input_file)

figure = plot_chemical_space(coordinates, nametag='ZeroPM',
                        hover_name='PREFERRED_NAME', hover_data=['Superclass', 'Class', 'Subclass', 'SMILES'],
                        column_for_color_map='Superclass', color_type='discrete', palette="Alphabet",
                        )

output_filename = f'{input_file}_superclass'
save_figure(figure, output_filename)

###### Plot 1: Drugbank on its own (Superclass) #####
input_folder = 'DrugBank'
input_file = 'drugbank_5.1.13_partial'
coordinates = load_coordinates(folder_name=input_folder, file_name=input_file)

figure = plot_chemical_space(coordinates, nametag='DrugBank',
                        hover_name='PREFERRED_NAME', hover_data=['Superclass', 'Class', 'Subclass', 'SMILES'],
                        column_for_color_map='Superclass', color_type='discrete', palette="Alphabet",
                        )

output_filename = f'{input_file}_superclass'
save_figure(figure, output_filename)

###### Plot 2: Drugbank on ZeroPM (Superclass) #####
# load reference coordinates
reference_folder = 'ZeroPM'
reference_file =  'zeropm_partial'
reference_coordinates = load_coordinates(reference_folder, reference_file)

# load input coordinates, to be mapped to reference
input_folder = 'DrugBank'
input_file = 'drugbank_5.1.13_partial'
new_coordinates = load_coordinates(folder_name=input_folder, file_name=input_file, reference_data=reference_file)

figure = plot_chemical_space(reference_coordinates, nametag='ZeroPM reference space', hover_name='PREFERRED_NAME', 
                             hover_data=['Superclass', 'Class', 'Subclass', 'SMILES'])
figure = plot_chemical_space(new_coordinates, nametag='DrugBank', map_on=figure,
                        hover_name='PREFERRED_NAME', hover_data=['Superclass', 'Class', 'Subclass', 'SMILES'],
                        column_for_color_map='Superclass', color_type='discrete', palette="Alphabet",
                        symbol='diamond'
                        )

# Save figure
output_filename = f'{reference_file}_{input_file}_Superclass'
save_figure(figure, output_filename)

###### Plot 3: Drugbank on COCONUT (Superclass) #####
# load reference coordinates
reference_folder = 'COCONUT'
reference_file =  'coconut'
reference_coordinates = load_coordinates(reference_folder, reference_file)

# load input coordinates, to be mapped to reference
input_folder = 'DrugBank'
input_file = 'drugbank_5.1.13_partial'
new_coordinates = load_coordinates(folder_name=input_folder, file_name=input_file, reference_data=reference_file)

figure = plot_chemical_space(reference_coordinates, nametag='COCONUT reference space', hover_name='PREFERRED_NAME', 
                             hover_data=['SMILES'])
figure = plot_chemical_space(new_coordinates, nametag='DrugBank', map_on=figure,
                        hover_name='PREFERRED_NAME', hover_data=['Superclass', 'Class', 'Subclass', 'SMILES'],
                        column_for_color_map='Superclass', color_type='discrete', palette="Alphabet",
                        symbol='diamond'
                        )

# Save figure
output_filename = f'{reference_file}_{input_file}_Superclass'
save_figure(figure, output_filename)
