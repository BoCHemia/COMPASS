from modules.preprocessing import *
from pathlib import Path
from modules.modeling import *
from modules.visualizing import *

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------
# INPUT
# -----------------------------

# Data: output from PEPPER predictions for compounds of the reference space
input_path = os.path.join(PROJECT_ROOT, "data")

# Reference space: ZeroPM
reference_folder = 'ZeroPM'
reference_file = 'zeropm'

# Predictions: provide a name tag and the path to the predictions file obtained from pepper
input_name_tag = 'soil_predictions' # here: soil half-life predictions including uncertainty
input_file_path = os.path.join(PROJECT_ROOT, "temp", "filtered_zeropm_smiles_soil_zeropm_all_data.tsv")

# Read predictions file
df = pd.read_csv(input_file_path, sep="\t")

# Ensure that the SMILES column corresponds to the original input SMILES to ensure correct mapping to the reference file
df.rename(columns={'SMILES': 'new_SMILES'}, inplace=True)
df.rename(columns={'original_SMILES': 'SMILES'}, inplace=True)

# Load reference coordinates
coordinates = load_coordinates(reference_folder, reference_file)

# Merge reference coordinates with predictions on SMILES
all_data = coordinates.merge(df, how='left', on='SMILES')

# Print statistics
print('Number of substances', len(all_data))
all_data['saltiness'] = all_data['SMILES'].str.count(r'\.') # number of salts
print('Number of salts:\n', all_data['saltiness'].value_counts())
predicted_only = all_data.dropna(subset=['logDT50_mean_predicted'])
print('Predictions:', len(predicted_only))

# Plot predicted endpoints - here for half-life predictions
hover_data = ['INCHIKEY', 'SMILES', 'logDT50_mean_predicted', 'logDT50_std_predicted',
              'non-Persistent', 'Persistent', 'very Persistent']

# plotting function
def visualize_column(plotted_name_tag, color_type, column_for_color_map, palette):
    # Plot reference chemical space
    figure = plot_chemical_space(df=all_data, nametag=reference_folder, map_on=None,
                                 hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'SMILES'], opacity=0.5)
    # Plot chemicals with predictions from PEPPER
    figure = plot_chemical_space(df=predicted_only, nametag=plotted_name_tag, map_on=figure,
                                 hover_name='PREFERRED_NAME', hover_data=hover_data,
                                 color_type=color_type, column_for_color_map=column_for_color_map, palette=palette)
    # Show and save figure
    figure.show()
    output_filename = f'{reference_file}_{input_name_tag}_{plotted_name_tag}'
    save_figure(figure, output_filename)


# plot uncertainty
visualize_column(plotted_name_tag='logDT50_std', color_type='continuous',
                 column_for_color_map='logDT50_std_predicted', palette='RdBu_r')

# plot half-lives
visualize_column(plotted_name_tag='logDT50_mean', color_type='continuous',
                 column_for_color_map='logDT50_mean_predicted', palette='Turbo')

# plot p(P)
visualize_column(plotted_name_tag='p(P)', color_type='continuous',
                 column_for_color_map='Persistent', palette='Agsunset_r')

# plot p(nP)
visualize_column(plotted_name_tag='p(nP)', color_type='continuous',
                 column_for_color_map='non-Persistent', palette='Blackbody')

# plot Exact_Mass (from PubChem)
visualize_column(plotted_name_tag='Exact_Mass', color_type='continuous',
                 column_for_color_map='Exact_Mass', palette='Agsunset_r')


