"""
Preprocess
    - enviPath
    - PREMIER DAS compounds

IMPORTANT NOTE: requires the installation of enviPath-python (not in the requirements)
install using pip:
    $ pip install enviPath-python
"""
from modules.modeling import *
from modules.visualizing import *
from tqdm import tqdm
import getpass

# Settings

input_path = os.path.join(PROJECT_ROOT, "data")
folder_name = "_USER"

# Function to load enviPath data from envipath.org
def load_enviPath_data(from_csv = False):
    # where enviPath data is to be stored
    file_name = "enviPath"
    file_path = os.path.join(input_path, folder_name, f'input_{file_name}.csv')

    # Load existing file and return
    if from_csv:
        return pd.read_csv(file_path)

    # Connect to enviPath and fetch data
    # Requires the additional installation fo enviPath_python
    from enviPath_python import enviPath

    print("Fetching data from envipath.org...")
    eP = enviPath("https://envipath.org/api/legacy/", new_api=True)
    username = input("Username: ")
    eP.login(username, getpass.getpass())

    # fetch packages
    bbd = eP.get_package(f'https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')
    soil = eP.get_package(f'https://envipath.org/package/5882df9c-dae1-4d80-a40e-db4724271456')
    sludge = eP.get_package(f'https://envipath.org/package/521c547a-fd2a-491c-ad5b-7eaa1577fb65')
    sediment = eP.get_package(f'https://envipath.org/package/f05e38d8-e9b4-4c3e-b0d8-9ab29966eccf')
    pfas = eP.get_package(f'https://envipath.org/package/87a49584-d937-482c-9c33-25928dcb02a8')
    package_list = [bbd, sludge, sediment, pfas, soil]
    df = pd.DataFrame(columns = ['PREFERRED_NAME', 'SMILES', 'INCHIKEY', 'package'])
    # download all data
    for pkg in package_list:
        D = {}
        print(f'Fetch compounds from {pkg} package')
        cpds = pkg.get_compounds()
        for cpd in tqdm(cpds): # Iterate through compounds in package
            try:
                name = cpd.get_name()
            except ValueError:
                print(f'Skipping {cpd.get_id()}')
                continue
            if "Spike compound" in name: # Skip C14 labelled spike compounds
                continue
            D[cpd.id] = {'PREFERRED_NAME': name,
                         'SMILES': cpd.get_smiles(),
                         'INCHIKEY': cpd.get_inchikey(),
                         'package': pkg.get_name()}

        # save data after each package
        this_df = pd.DataFrame.from_dict(D, orient='index')
        df = pd.concat([df, this_df], ignore_index=True)
        df.to_csv(file_path, index = False)
    return df

def convert_PREMIER_DAS_download(from_csv = False):
    # where PREMIER data is to be stored
    file_name = "PREMIER"
    file_path = os.path.join(input_path, folder_name, f'input_{file_name}.csv')
    path_to_downloads = '~/Downloads' # Wherever the files were downloaded to
    # Load existing file and return
    if from_csv:
        return pd.read_csv(file_path)

    data_list = ['307', '308', '314B']
    all_data = pd.DataFrame(columns = ['PREFERRED_NAME', 'SMILES', 'Data type'])
    for data_type in data_list:
        df = pd.read_csv(os.path.join(path_to_downloads, f'PREMIER_export_OECD{data_type}.txt'), sep='\t')
        df.drop_duplicates(subset='Compound SMILES', inplace=True)
        column_smiles = 'Compound SMILES'
        column_name = 'Compound name'
        df['PREFERRED_NAME'] = df[column_name]
        df['SMILES'] = df[column_smiles]
        df['Data type'] = 'OECD ' + data_type
        df = df[['PREFERRED_NAME', 'SMILES', 'Data type']]
        all_data = pd.concat([all_data, df], ignore_index=True)

    all_data.to_csv(file_path, index = False)

def count_F(smiles_list):
    f_count = []
    for smiles in smiles_list:
        f_count.append(smiles.count('F'))
    return f_count

############ Main #################
# Save PREMIER data (all types)
PREMIER_data = convert_PREMIER_DAS_download(from_csv=True)

# load and save enviPath data
enviPath_data = load_enviPath_data(from_csv=True)

# Save file with PFAS only
file_path_pfas = os.path.join(input_path, folder_name, f'input_enviPath-PFAS.csv')
df_PFAS = enviPath_data[enviPath_data['package']=='enviPath-PFAS'].copy()
df_PFAS['F count'] = count_F(df_PFAS['SMILES'])
df_PFAS.to_csv(file_path_pfas, index = False)

# Save file with soil data only
file_path_pesticides = os.path.join(input_path, folder_name, f'input_EAWAG-SOIL.csv')
enviPath_data[enviPath_data['package']=='EAWAG-SOIL'].to_csv(file_path_pesticides, index = False)

