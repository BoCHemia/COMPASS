from enviPath_python import enviPath
from modules.modeling import *
from modules.visualizing import *
from tqdm import tqdm
from getpass import getpass

# settings

input_path = os.path.join(PROJECT_ROOT, "data")
folder_name = "input"
file_name = "enviPath"

# define function
def load_enviPath_data(from_csv = False, use_beta = False):
    # where enviPath data is to be stored
    file_path = os.path.join(input_path, folder_name, f'input_{file_name}.csv')

    # load existing file and return
    if from_csv:
        return pd.read_csv(file_path)

    # connect to enviPath and fetch data
    if use_beta:
        eP = enviPath('https://beta.envipath.org/api/legacy/', new_api=True) # for future
        eP.login(input("enviPath username:"), getpass())
        tag = 'beta.'
    else:
        eP = enviPath('https://envipath.org')
        tag= ''

    # fetch packages
    bbd = eP.get_package(f'https://{tag}envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')
    soil = eP.get_package(f'https://{tag}envipath.org/package/5882df9c-dae1-4d80-a40e-db4724271456')
    sludge = eP.get_package(f'https://{tag}envipath.org/package/521c547a-fd2a-491c-ad5b-7eaa1577fb65')
    sediment = eP.get_package(f'https://{tag}envipath.org/package/f05e38d8-e9b4-4c3e-b0d8-9ab29966eccf')
    package_list = [bbd, soil, sludge, sediment]

    # download all data
    D = {}
    for pkg in package_list:
        print(f'Fetch compounds from {pkg} package')
        cpds = pkg.get_compounds()
        for cpd in tqdm(cpds):
            name = cpd.get_name()
            if "Spike compound" in name: # skip c14 labelled spike compounds
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
new_fingerprints = preprocess_data(new_df)
save_fingerprints(fingerprints=new_fingerprints, file_name=file_name)

# transform on ZeroPM
reference_folder = 'ZeroPM'
reference_data_name =  'zeropm'

# model = load_model(reference_data_name, from_zip=False)
coordinates = transform_target(model, new_fingerprints)
save_coordinates(coordinates=coordinates,
                 folder_name=folder_name,
                 file_name=file_name,
                 reference_data=reference_data_name)
coordinates = load_coordinates(folder_name, file_name, reference_data=reference_data_name) #enviPath coordinates

# visualize with zeropm reference space
eP_colors = {'EAWAG-BBD':'#1681AC', 'EAWAG-SOIL':'#392C20', 'EAWAG-SLUDGE': '#8C7938', 'EAWAG-SEDIMENT':'#008A88',
             # 'enviPath-PFAS': '#2C653C',
             }
reference_coordinates = load_coordinates(reference_folder, reference_data_name)
figure = plot_chemical_space(reference_coordinates, nametag='ZeroPM reference space', hover_name='PREFERRED_NAME',
                             hover_data=['SMILES']) # add 'Superclass', 'Class', 'Subclass',
figure = plot_chemical_space(coordinates, nametag='enviPath', map_on=figure,
                        hover_name='PREFERRED_NAME', hover_data=['SMILES', 'package', 'INCHIKEY'],
                        column_for_color_map='package', color_type='discrete', palette=eP_colors,
                        symbol='diamond', size=7, opacity=0.6
                        )

# Save figure
output_filename = f'{file_name}_on_{reference_data_name}'
save_figure(figure, output_filename)