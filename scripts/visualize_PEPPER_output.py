from modules.preprocessing import *
from pathlib import Path
from modules.modeling import *
from modules.visualizing import *
from scripts.visualize_pfas import new_coordinates

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------
# INPUT
# -----------------------------

# Data: output from PEPPER predictions of compounds existing in reference space (ZeroPM)

input_path = os.path.join(PROJECT_ROOT, "data")

folder_name = "ZeroPM"
file_name = "zeropm"

# file with prediction (outside of compass)
df = pd.read_csv("/home/jasmin/Downloads/raw_zeropm_soil_zeropm_all_data.tsv", sep="\t")

#### Plot 2: NIST PFAS on ZeroPM ######
reference_folder = 'ZeroPM'
reference_file = 'zeropm'
reference_coordinates = load_coordinates(reference_folder, reference_file)

new_coordinates = reference_coordinates
reference_coordinates.merge(df, how='left', on='INCHIKEY')

figure = chemical_space_plot_grey(reference_coordinates, hover_data=['INCHIKEY', 'SMILES'], opacity=0.5)
figure = map_input_data(figure, new_coordinates, nametag=input_file,
                        hover_name='PREFERRED_NAME', hover_data=['INCHIKEY', 'CAS', 'Synonyms'])
figure.show()
output_filename = f'{reference_file}_{input_file}'
save_figure(figure, output_filename)