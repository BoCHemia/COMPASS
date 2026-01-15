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

    :param X: input matrix of fingerprints
    :return: fitted model object and coordinates of transformed fingerprints
    """

    # Load hyperparameters of t-SNE from config
    hyperparameters_dict = load_configs('tsne_params')

    # Prepare boolean fingerprint array
    df_fingerprints.dropna(inplace=True)
    X = np.array(df_fingerprints.drop(columns=['INCHIKEY']).astype('bool'))

    # Training
    print('--> Start training')
    tsne = TSNE(**hyperparameters_dict)
    coordinates = pd.DataFrame(tsne.fit_transform(X), columns=['TSNE1', 'TSNE2'])
    coordinates.index = df_fingerprints['INCHIKEY']

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
        df_coordinates = df.merge(coordinates, on='INCHIKEY', how='left')

    else:
        print("Could find the coordinates, please check coordinates have already being calculated")

    if reference_name:
        file_name += "_on_" + reference_name
    # save df, annotated with TSNE coordinates
    output_path = os.path.join(PROJECT_ROOT, "data", folder_name, "output_" + file_name + '.csv')
    df_coordinates.to_csv(output_path, index=False)
    print(f"Saved coordinates to {output_path}")

    
def load_coordinates(folder_name, file_name, reference_data=""):
    """
    Load tSNE coordinates from file

    :param folder_name: name of the folder
    :param file_name: name tag
    :param reference_data: If indicated, load coordinates of mapping of "file_name" on "reference_data"
    :return: tSNE coordinates
    """
    if reference_data:
        file_name += f'_on_{reference_data}'
    coordinates_path = os.path.join(PROJECT_ROOT, "data", folder_name, "output_" + file_name + '.csv')
    coordinates = pd.read_csv(coordinates_path)
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

def transform_target(model, fingerprints):
    """
    Transform fingerprints using the provided tSNE model

    :param model: trained tSNE model
    :param fingerprints: fingerprint matrix, including a colunnd "INCHIKEY"
    :return: coordinates of the input compounds in the tSNE space
    """
    # Prepare boolean fingerprint array
    print(f"--> Calculating mapping for {fingerprints.shape[0]} compounds")
    fingerprints.dropna(inplace=True)
    X = np.array(fingerprints.drop(columns=['INCHIKEY']).astype('bool'))
    print("Starting to transform")
    coordinates_target = model.transform(X, **kwargs)
    print("Transforming worked")
    coordinates_df = pd.DataFrame(coordinates_target, columns=['TSNE1', 'TSNE2'])
    coordinates_df.index = fingerprints['INCHIKEY']

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
    # create a lookup map with
    lookup_map = reference_data.loc[:,['TSNE1', 'TSNE2']]
    lookup_map['INCHIKEY_first14'] = reference_data['INCHIKEY'].str.split('-', expand=True)[0]
    print("Lookup map loaded:", lookup_map.shape)
    lookup_map.drop_duplicates(subset=['INCHIKEY_first14'], inplace=True)

    # fetch coordinates where available based on first 14 letters inchikey (basic structure)
    print("Lookup map after removing duplicates based on first14:", lookup_map.shape)
    fingerprints['INCHIKEY_first14'] = fingerprints['INCHIKEY'].str.split('-', expand=True)[0]

    # populate coordinates from lookup map first
    lookup_coordinates_df = fingerprints.loc[:,['INCHIKEY_first14', 'INCHIKEY']]
    lookup_coordinates_df = lookup_coordinates_df.merge(lookup_map, how='left', on='INCHIKEY_first14')
    lookup_coordinates_df.index = fingerprints['INCHIKEY']
    lookup_coordinates_df.drop(columns=['INCHIKEY', 'INCHIKEY_first14'], inplace=True)
    found_compounds = lookup_coordinates_df.dropna(subset=['TSNE1']).shape[0]
    print(f'{found_compounds} compounds (out of {fingerprints.shape[0]}) could be found in the reference space')
    return lookup_coordinates_df

def lookup_or_transform_target(model, fingerprints, reference_data):
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
    transform_fingerprints = remaining_compounds_df.merge(fingerprints, how='left', on='INCHIKEY')

    # transform fingerprints
    transform_coordinates_df =  transform_target(model, transform_fingerprints)

    # add coordinates from lookup
    lookup_coordinates = lookup_coordinates_df.dropna(subset=['TSNE1'])
    coordinates_df = pd.concat([transform_coordinates_df, lookup_coordinates], axis=0)
    return coordinates_df
