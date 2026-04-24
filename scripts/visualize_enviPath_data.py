# Visualizing enviPath packages directly from the enviPath website
from seaborn import color_palette

from modules.modeling import *
from modules.visualizing import *
from tqdm import tqdm
import getpass
import molplotly
import time

# Settings

input_path = os.path.join(PROJECT_ROOT, "data")
folder_name = "_USER"
file_name = "enviPath"

# Function to load enviPath data from envipath.org
def load_enviPath_data(from_csv = False, use_legacy=False):
    # where enviPath data is to be stored
    file_path = os.path.join(input_path, folder_name, f'input_{file_name}.csv')

    # Load existing file and return
    if from_csv:
        return pd.read_csv(file_path)

    # Connect to enviPath and fetch data
    # Requires the additional installation fo enviPath_python
    from enviPath_python import enviPath
    if use_legacy:
        print("Fetching data from legacy.envipath.org...")
        eP = enviPath('https://legacy.envipath.org/', new_api=False)
        tag = 'legacy.'
    else:
        print("Fetching data from envipath.org...")
        eP = enviPath("https://envipath.org/api/legacy/", new_api=True)
        username = input("Username: ")
        eP.login(username, getpass.getpass())
        tag= ''

    # fetch packages
    bbd = eP.get_package(f'https://{tag}envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')
    soil = eP.get_package(f'https://{tag}envipath.org/package/5882df9c-dae1-4d80-a40e-db4724271456')
    sludge = eP.get_package(f'https://{tag}envipath.org/package/521c547a-fd2a-491c-ad5b-7eaa1577fb65')
    sediment = eP.get_package(f'https://{tag}envipath.org/package/f05e38d8-e9b4-4c3e-b0d8-9ab29966eccf')
    pfas = eP.get_package(f'https://{tag}envipath.org/package/d2cfb5af-4ea0-4375-9a48-f2e776e44636')
    package_list = [bbd, soil, sludge, sediment, pfas]
    # package_list = [pfas]

    # download all data
    D = {}
    for pkg in package_list:
        print(f'Fetch compounds from {pkg} package')
        cpds = pkg.get_compounds()
        for cpd in tqdm(cpds): # Iterate through compounds in package
            name = cpd.get_name()
            if not name:
                continue
            if "Spike compound" in name: # Skip C14 labelled spike compounds
                continue
            D[cpd.id] = {'PREFERRED_NAME': name,
                         'SMILES': cpd.get_smiles(),
                         'INCHIKEY': cpd.get_inchikey(),
                         'package': pkg.get_name()}

        # save data after each package
        df = pd.DataFrame.from_dict(D, orient='index')
        df.to_csv(file_path, index = False)
    return df

############ Main #################
# load enviPath data
new_df = load_enviPath_data(from_csv=True)

# preprocess
new_fingerprints, new_df = preprocess_data(new_df)
update_df(new_df, folder_name, file_name, 'input')
save_fingerprints(fingerprints=new_fingerprints, file_name=file_name, folder_name=folder_name)
# new_fingerprints = load_fingerprints(file_name=file_name, folder_name=folder_name)

# transform on ZeroPM
reference_folder = 'ZeroPM'
reference_data_name =  'zeropm_partial'

# # Alternatively: transform on NIST
# reference_folder = "PFAS"
# reference_data_name = "pfas_nist"

# Load reference coordinates
reference_coordinates = load_coordinates(reference_folder, reference_data_name)
reference_fingerprints = load_fingerprints(reference_folder, reference_data_name)
# reference_fingerprints, reference_coordinates = preprocess_data(reference_coordinates)
# update_df(reference_coordinates, reference_folder, reference_data_name, 'output')
# save_fingerprints(fingerprints=reference_fingerprints, file_name=reference_data_name, folder_name=reference_folder)


# Load reference model and transform enviPath compounds
model = load_model(reference_data_name, use_joblib=True)
offset = load_model_offset(reference_data_name)

# Get tSNE coordinates for input molecules
# coordinates = lookup_or_transform_target(model, new_fingerprints, offset, reference_coordinates)
# coordinates_lookup = lookup_target(new_fingerprints, reference_coordinates)
coordinates_transform = transform_target(model, new_fingerprints, offset)
# all_coordinates = pd.merge(coordinates_lookup, coordinates_transform, how='left', on='FP_HEX')
# all_coordinates.dropna(inplace=True)
# all_coordinates['diff_1'] = all_coordinates['TSNE1_x'] - all_coordinates['TSNE1_y']
# all_coordinates['diff_2'] = all_coordinates['TSNE2_x'] - all_coordinates['TSNE2_y']
# all_coordinates.drop_duplicates(inplace=True)
# from matplotlib import pyplot as plt
# import seaborn as sns
# sns.scatterplot(data=all_coordinates, x='diff_1', y='diff_2', alpha=0.1)
# plt.show()

coordinates = coordinates_transform

save_coordinates(coordinates=coordinates,
                 folder_name=folder_name,
                 file_name=file_name,
                 reference_name=reference_data_name)
annotated_coordinates = load_coordinates(folder_name, file_name, reference_data=reference_data_name) #enviPath coordinates

# visualize on reference space
eP_colors = {'EAWAG-BBD':'#1681AC', 'EAWAG-SOIL':'#392C20', 'EAWAG-SLUDGE': '#8C7938', 'EAWAG-SEDIMENT':'#008A88',
             'enviPath-PFAS': '#2C653C',
             }

figure = plot_chemical_space(reference_coordinates, nametag='ZeroPM reference space', hover_name='PREFERRED_NAME',
                             hover_data=['SMILES']) # add 'Superclass', 'Class', 'Subclass',
figure = plot_chemical_space(annotated_coordinates, nametag='enviPath', map_on=figure,
                        hover_name='PREFERRED_NAME', hover_data=['SMILES', 'package', 'INCHIKEY'],
                        column_for_color_map='package', color_type='discrete', palette=eP_colors,
                        symbol='diamond', size=7, opacity=0.6
                        )

# Save figure
output_filename = f'{file_name}_on_{reference_data_name}_transform'
save_figure(figure, output_filename)