from modules.preprocessing import *
from pathlib import Path
from modules.modeling import *
from modules.visualizing import *

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------
# INPUT
# -----------------------------

# Data: output from PEPPER predictions of compounds existing in reference space (ZeroPM)

input_path = os.path.join(PROJECT_ROOT, "data")

folder_name = "ZeroPM"
file_name = "zeropm"

input_name_tag = 'soil_predictions'

# file with prediction (outside of compass)
df = pd.read_csv(os.path.join(PROJECT_ROOT, "temp", "raw_zeropm_soil_zeropm_all_data.tsv"), sep="\t")
df.rename(columns={'SMILES': 'new_SMILES'}, inplace=True)
df.rename(columns={'original_SMILES': 'SMILES'}, inplace=True)

#### Plot 2: NIST PFAS on ZeroPM ######
reference_folder = 'ZeroPM'
reference_file = 'zeropm'
coordinates = load_coordinates(reference_folder, reference_file)

all_data = coordinates.merge(df, how='left', on='SMILES')
print('Number of substances', len(all_data))
all_data['saltiness'] = all_data['SMILES'].str.count(r'\.') # number of salts
print('Number of salts:\n', all_data['saltiness'].value_counts())
predicted_only = all_data.dropna(subset=['logDT50_mean_predicted'])
print('Predictions:', len(predicted_only))

# plot model uncertainties

figure = plot_chemical_space(df=all_data, nametag = 'ZeroPM', map_on=None,
                   hover_name = 'PREFERRED_NAME', hover_data =['INCHIKEY', 'SMILES'], opacity = 0.5)

figure = plot_chemical_space(df=predicted_only, nametag = 'logDT50_std', map_on=figure,
                            hover_name = 'PREFERRED_NAME', hover_data = ['INCHIKEY', 'SMILES',
                                                                         'logDT50_mean_predicted', 'logDT50_std_predicted',
                                                                         'non-Persistent', 'Persistent', 'very Persistent'],
                            color_type = 'continuous', column_for_color_map = 'logDT50_std_predicted', palette = 'RdBu_r')

figure.show()
output_filename = f'{reference_file}_{input_name_tag}_standard_deviation'
save_figure(figure, output_filename)

# plot half-lives

figure = plot_chemical_space(df=all_data, nametag = 'ZeroPM', map_on=None,
                   hover_name = 'PREFERRED_NAME', hover_data =['INCHIKEY', 'SMILES'], opacity = 0.5)


figure = plot_chemical_space(df=predicted_only, nametag = 'logDT50_mean', map_on=figure,
                            hover_name = 'PREFERRED_NAME', hover_data = ['INCHIKEY', 'SMILES',
                                                                         'logDT50_mean_predicted', 'logDT50_std_predicted',
                                                                         'non-Persistent', 'Persistent', 'very Persistent'],
                            color_type = 'continuous', column_for_color_map = 'logDT50_mean_predicted', palette = 'Turbo')

# plot p(P)

figure = plot_chemical_space(df=all_data, nametag = 'ZeroPM', map_on=None,
                   hover_name = 'PREFERRED_NAME', hover_data =['INCHIKEY', 'SMILES'], opacity = 0.5)


figure = plot_chemical_space(df=predicted_only, nametag = 'p(P)', map_on=figure,
                            hover_name = 'PREFERRED_NAME', hover_data = ['INCHIKEY', 'SMILES',
                                                                         'logDT50_mean_predicted', 'logDT50_std_predicted',
                                                                         'non-Persistent', 'Persistent', 'very Persistent'],
                            color_type = 'continuous', column_for_color_map = 'Persistent', palette = 'Agsunset_r') #amp? Reds?

# plot p(P)

figure = plot_chemical_space(df=all_data, nametag = 'ZeroPM', map_on=None,
                   hover_name = 'PREFERRED_NAME', hover_data =['INCHIKEY', 'SMILES'], opacity = 0.5)


figure = plot_chemical_space(df=predicted_only, nametag = 'p(P)', map_on=figure,
                            hover_name = 'PREFERRED_NAME', hover_data = ['INCHIKEY', 'SMILES',
                                                                         'logDT50_mean_predicted', 'logDT50_std_predicted',
                                                                         'non-Persistent', 'Persistent', 'very Persistent'],
                            color_type = 'continuous', column_for_color_map = 'Persistent', palette = 'Agsunset_r') #amp? Reds?

# plot p(nP)

figure = plot_chemical_space(df=all_data, nametag = 'ZeroPM', map_on=None,
                   hover_name = 'PREFERRED_NAME', hover_data =['INCHIKEY', 'SMILES'], opacity = 0.5)


figure = plot_chemical_space(df=predicted_only, nametag = 'p(nP)', map_on=figure,
                            hover_name = 'PREFERRED_NAME', hover_data = ['INCHIKEY', 'SMILES',
                                                                         'logDT50_mean_predicted', 'logDT50_std_predicted',
                                                                         'non-Persistent', 'Persistent', 'very Persistent'],
                            color_type = 'continuous', column_for_color_map = 'non-Persistent', palette = 'Blackbody') #amp? Reds?

figure.show()
output_filename = f'{reference_file}_{input_name_tag}_non-Persistent'
save_figure(figure, output_filename)

