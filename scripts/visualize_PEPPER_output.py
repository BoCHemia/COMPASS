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

#### Plot 2: NIST PFAS on ZeroPM ######
reference_folder = 'ZeroPM'
reference_file = 'zeropm'
coordinates = load_coordinates(reference_folder, reference_file)

all_data = coordinates.merge(df, how='left')
predicted_only = all_data.dropna(subset=['logDT50_mean_predicted'])

figure = chemical_space_plot_grey(all_data, hover_data=['INCHIKEY', 'SMILES'], opacity=0.5)
figure = map_input_data(figure, predicted_only, nametag=input_name_tag,
                        hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'SMILES',
                                                                 'logDT50_mean_predicted','logDT50_std_predicted',
                                                                 'non-Persistent', 'Persistent', 'very Persistent'],
                        color_type='continuous',column_for_color_map='logDT50_std_predicted', palette='viridis')

figure.show()
output_filename = f'{reference_file}_{input_name_tag}'
save_figure(figure, output_filename)