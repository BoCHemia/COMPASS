import os
import pickle
from unittest.mock import inplace

import numpy as np
import pandas as pd
from openTSNE.sklearn import TSNE
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from modules.preprocessing import *
import zipfile
import yaml
import joblib


# -----------------------------
# utils
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent 

minimal_columns = ['SMILES', 'INCHIKEY', 'PREFERRED_NAME',
       'TSNE1', 'TSNE2', 'Kingdom', 'Superclass',
       'Class', 'Subclass']



def ensure_dirs():
    """
    Ensure that the folders temp and output exist, and if not, create them
    """
    os.makedirs(os.path.join(PROJECT_ROOT, "temp"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "output"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "models"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)


def save_pickle(obj, path):
    """
    Save object as a pickle file
    :param obj: objeckt
    :param path: path to save pickle file
    """
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def load_pickle(path):
    """
    Load pickled file
    :param path: path to saved pickle file
    :return: object in the pickled file
    """
    with open(path, "rb") as f:
        return pickle.load(f)

def unzip_and_load(path_to_zipfile):
    """
    Unzip and unpickle a zip file to load a tSNE  model
    :param path_to_zipfile: Path to zip file
    :return: tSNE model objcet
    """
    archive = zipfile.ZipFile(path_to_zipfile, 'r')
    model_name_pkl = archive.infolist()[0]
    model_pkl = archive.read(model_name_pkl)
    model = pickle.loads(model_pkl)
    return model
    
def load_configs(params = 'tsne_params'):
    """
    Load tSNE configurations from the config folder
    :param params: name of file in config folder (without the .yaml)
    :return: dictionary of hyperparameters to be used for tSNE training
    """
    with open(os.path.join(PROJECT_ROOT, 'config', params+'.yaml'), 'r') as file:
        hyperparameters = yaml.safe_load(file)
    return hyperparameters['hyperparameters']

# -----------------------------
# Modeling
# -----------------------------

def fit_tsne_model(df_fingerprints):
    """
    Fits the TSNE model on the boolean fingerprint array (X) and saves the fitted embedding object.
    If the pickled object exists, it is loaded instead of training again.

    :param df_fingerprints: fingerprints dataframe
    :return: fitted model object and coordinates of transformed fingerprints
    """

    # Load hyperparameters of t-SNE from config
    hyperparameters_dict = load_configs('tsne_params')

    # Prepare boolean fingerprint array
    df_fingerprints.dropna(inplace=True)
    X = np.array(df_fingerprints.drop(columns=['FP_HEX']).astype('bool'))

    # Training
    print('--> Start training')
    tsne = TSNE(**hyperparameters_dict)
    coordinates = pd.DataFrame(tsne.fit_transform(X), columns=['TSNE1', 'TSNE2'])
    coordinates['FP_HEX'] = df_fingerprints['FP_HEX']

    print('Finished training')
    return tsne, coordinates

def save_model(model, file_name, pickle=True, zip=True, use_joblib=False):
    """
    Save model as pickle to temp and as zipped pickle to output
    :param model: trained tSNE model
    :param file_name: name tag of the original data file (e.g. for 'data_market.csv' the file_name would be 'data_market')
    :param pickle: save as pickle file, True by default
    :param zip: compress to zip file, True by default
    :param joblib: save as joblib file, False by default. If joblib is true, no pickle file will be generated
    """
    ensure_dirs()

    # Saving trained tSNE object to temp folder
    if use_joblib:
        model_path = os.path.join(PROJECT_ROOT, "models", file_name + '_trained_tSNE.zlib')
        print("--> Joblib tSNE object")
        joblib.dump(model, model_path, compress=5)
        print(f"Saved fitted tSNE embedding to {model_path}")

    elif pickle:
        model_path = os.path.join(PROJECT_ROOT, "models", file_name + '_trained_tSNE.pkl')
        print("--> Pickle tSNE object")
        save_pickle(model, model_path)
        print(f"Saved fitted tSNE embedding to {model_path}")

        # Saving zipped trained tSNE object to output folder
        if zip:
            model_path_zip = os.path.join(PROJECT_ROOT, "models", file_name + '_trained_tSNE.zip')
            print('--> Zip tSNE object')
            with zipfile.ZipFile(model_path_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(model_path)
            print(f"Saved fitted tSNE embedding as zip file to {model_path_zip}")


def save_model_offset(offset, file_name):
    offset_path = os.path.join(PROJECT_ROOT, "models", file_name + '_offset.csv')
    offset.to_csv(offset_path, index=False)
    print(f"Saved model offset to {offset_path}")

def load_model_offset(file_name):
    offset_path = os.path.join(PROJECT_ROOT, "models", file_name + '_offset.csv')
    offset = pd.read_csv(offset_path)
    print(f"Loaded model offset from {offset_path}")
    return offset

def save_coordinates(coordinates, folder_name, file_name, reference_name=""):
    """
    Save coordinates to output file in data folder (data/[folder_name]/output_[file_name].csv)

    :param coordinates: coordinates as received from model fitting with index as InChIKey
    :param folder_name: folder name for saving the input file annotated with TSNE coordinates
    :param file_name: name tag of the original data file (e.g. for 'data_market.csv')
    """
    # load input df
    user_input_folder = os.path.join(PROJECT_ROOT, "data", folder_name)
    assert user_input_folder
    if user_input_folder:
        input_df_path = os.path.join(user_input_folder, "input_" + file_name + ".csv")
        df = pd.read_csv(input_df_path)
        df_coordinates = df.merge(coordinates, on='FP_HEX', how='left')

    else:
        print("Could find the coordinates, please check coordinates have already being calculated")

    if reference_name:
        file_name += "_on_" + reference_name
    # save df, annotated with TSNE coordinates
    # Refacting note: output_path -> coordinates_path
    coordinates_path = os.path.join(PROJECT_ROOT, 'data', folder_name, "output_" + file_name + '.csv')
    df_coordinates.to_csv(coordinates_path, index=False)
    print(f"Saved coordinates to {coordinates_path}")

    
def load_coordinates(folder_name, file_name, reference_data="", base_dir="data"):
    """
    Load tSNE coordinates from file

    :param folder_name: name of the folder
    :param file_name: name tag
    :param reference_data: If indicated, load coordinates of mapping of "file_name" on "reference_data"
    :return: tSNE coordinates
    """
    if reference_data:
        file_name += f'_on_{reference_data}'
    coordinates_path = os.path.join(PROJECT_ROOT, base_dir, folder_name, "output_" + file_name + '.csv')
    coordinates = pd.read_csv(coordinates_path) #, usecols=minimal_columns)
    print("Coordinates loaded from {}".format(coordinates_path))
    return coordinates

def load_model(file_name, from_zip=False, use_joblib=False):
    """
    Load model from pickle file (default) or from zip file (not implemented)
    :param file_name: name tag of the original data file (e.g. 'data_market' for 'data_market.csv')
    :param from_zip: Load from zip file #todo implement this option
    :return: model object
    """
    print("--> Loading model")
    if use_joblib:
        model_path = os.path.join(PROJECT_ROOT, "models", file_name + '_trained_tSNE.zlib')
        print("loading joblib model from: " + model_path)
        model = joblib.load(filename=model_path)   
    elif from_zip:
        model_path = os.path.join(PROJECT_ROOT, "models", file_name + '_trained_tSNE.zip')
        print("loading zip model from: " + model_path)
        model = unzip_and_load(model_path) 
    else:
        model_path = os.path.join(PROJECT_ROOT, "models", file_name + '_trained_tSNE.pkl')
        print("loading pickle model from: " + model_path)
        model = load_pickle(model_path)
  
    return model

# -----------------------------
# Modeling (for the target space)
# -----------------------------

def transform_target(model, fingerprints, offset, **kwargs):
    """
    Transform fingerprints using the provided tSNE model

    :param model: trained tSNE model
    :param fingerprints: fingerprint matrix, including a column "INCHIKEY"
    :param offset: model-specific offset values to correct the transformed coordinates
    :return: coordinates of the input compounds in the tSNE space
    """
    # Prepare boolean fingerprint array
    print(f"--> Calculating mapping for {fingerprints.shape[0]} compounds")
    fingerprints.dropna(inplace=True)
    X = np.array(fingerprints.drop(columns=['FP_HEX'])).astype('bool')
    print("Starting to transform")
    coordinates_target = model.transform(X, **kwargs)
    print("Transforming worked")
    coordinates_df = pd.DataFrame(coordinates_target, columns=['TSNE1', 'TSNE2'])
    coordinates_df = coordinates_df - offset.values
    coordinates_df['FP_HEX'] = fingerprints['FP_HEX']
    return coordinates_df

def lookup_target(fingerprints, reference_data):
    """
    Looks up TSNE coordinates in the reference data.
    If the compound cannot be found, NaN is provided instead of spatial coordinates

    :param fingerprints: fingerprints dataframe
    :param reference_data: reference data with TSNE coordinates
    :return: dataframe with TSNE coordinates for compounds present in the reference data
    """
    fingerprints.dropna(inplace=True)
    # create a lookup map based on Fingerprints string
    lookup_map = reference_data.loc[:,['FP_HEX', 'TSNE1', 'TSNE2']]
    print("Lookup map loaded:", lookup_map.shape)
    lookup_map.drop_duplicates(subset=['FP_HEX'], inplace=True)

    # fetch coordinates where available based on first 14 letters inchikey (basic structure)
    print("Lookup map after removing duplicates based FP_HEX:", lookup_map.shape)

    # populate coordinates from lookup map first
    lookup_coordinates_df = pd.DataFrame()
    lookup_coordinates_df['FP_HEX'] = fingerprints['FP_HEX']
    lookup_coordinates_df = lookup_coordinates_df.merge(lookup_map, how='left', on='FP_HEX')
    lookup_coordinates_df.index = lookup_coordinates_df['FP_HEX']
    lookup_coordinates_df.drop(columns=['FP_HEX'], inplace=True)
    found_compounds = lookup_coordinates_df.dropna(subset=['TSNE1']).shape[0]
    print(f'{found_compounds} compounds (out of {fingerprints.shape[0]}) could be found in the reference space')
    return lookup_coordinates_df

def lookup_or_transform_target(model, fingerprints, offset, reference_data):
    """
    Looks up TSNE coordinates in the reference data. For compounds that could not be found in the reference,
    TSNE coordinates are calculated via the provided tSNE model.

    :param model: tSNE model object
    :param fingerprints: fingerprints dataframe
    :param reference_data: reference data with TSNE coordinates
    :return: coordinates for all input compounds
    """
    # lookup coordinates in reference_data
    lookup_coordinates_df = lookup_target(fingerprints, reference_data)

    # Get compounds for which no coordinates could be found in the reference space
    remaining_compounds_df = lookup_coordinates_df[lookup_coordinates_df['TSNE1'].isnull()].drop(columns=['TSNE1','TSNE2'])
    print(f'The remaining {remaining_compounds_df.shape[0]} compounds (out of {fingerprints.shape[0]}) need to be transformed')

    # get fingerprints for wich TSNE coordinates are missing
    transform_fingerprints = remaining_compounds_df.merge(fingerprints, how='left', on='FP_HEX')

    # transform fingerprints
    transform_coordinates_df =  transform_target(model, transform_fingerprints, offset)

    # add coordinates from lookup
    lookup_coordinates = lookup_coordinates_df.dropna(subset=['TSNE1'])
    coordinates_df = pd.concat([transform_coordinates_df, lookup_coordinates], axis=0)
    return coordinates_df

# -----------------------------
# Similarity calculation
# -----------------------------

from FPSim2 import FPSim2Engine
from FPSim2.io import create_db_file

def filter_valid_smiles(df, smiles_col="SMILES"):
    valid_smiles = []
    valid_idx = []

    for i, smi in enumerate(df[smiles_col].values):
        if not isinstance(smi, str) or smi == "":
            continue

        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue

        valid_smiles.append(smi)
        valid_idx.append(i)

    return valid_smiles, valid_idx


def create_fpsim2_engine(df, file_name, smiles_col="SMILES"):
    smiles, valid_idx = filter_valid_smiles(df, smiles_col=smiles_col)
    smiles_list = list(zip(smiles, valid_idx))

    create_db_file(
        mols_source=smiles_list,
        filename=file_name,
        mol_format='smiles',
        fp_type='Morgan',
        fp_params={'radius': 2, 'fpSize': 512}
    )

    engine = FPSim2Engine(file_name)

    return engine, valid_idx


def compute_similarity_fpsim2(engine, df_ref, smiles_col='SMILES', k=10):
       
    smiles_ref, valid_idx_ref = filter_valid_smiles(df_ref, smiles_col=smiles_col)

    knn_result = [engine.top_k(smi, k=k, threshold=0.0, metric='tanimoto') for smi in smiles_ref] # setting n_workers did not improve speed
    
    return knn_result, valid_idx_ref


def extract_knn_results(knn_result, valid_idx_ref, k):
    n_query = len(valid_idx_ref)
    sim_array = np.zeros((n_query, k), dtype=np.float32)
    idx_array = np.zeros((n_query, k), dtype=int)

    for row_idx, results in enumerate(knn_result):
        for col_idx, (db_idx, sim) in enumerate(results):
            sim_array[row_idx, col_idx] = sim
            idx_array[row_idx, col_idx] = db_idx # note: this is already valid_idx 

    df_sim = pd.DataFrame(sim_array, index=valid_idx_ref, columns=[f'knn_{i+1}_similarity' for i in range(k)])
    df_idx = pd.DataFrame(idx_array, index=valid_idx_ref, columns=[f'knn_{i+1}_index' for i in range(k)])

    return df_sim, df_idx

