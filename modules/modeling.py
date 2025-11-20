import os
import pickle
import numpy as np
import pandas as pd
from openTSNE.en import TSNE
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from modules.preprocessing import *
import zipfile
import yaml
import joblib

### Some comments:
# - Xsmall is just a smaller subset of the training data to make some steps faster
# - Caching was implemented by Sylvain. It is useful but we need to rename it.
# - The model is meant to be pickled, not really in the cache sense.
# -  I am still not so clear whether we really want/need separate preprocessing, modeling and visualization modules.


# -----------------------------
# utils? 
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent 

def ensure_dirs():
    """
    Ensure that the folders temp and output exist, and if not, create them
    """
    os.makedirs(os.path.join(PROJECT_ROOT, "temp"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "output"), exist_ok=True)


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
        model_path = os.path.join(PROJECT_ROOT, "temp", file_name + '_trained_tSNE.zlib')
        print("--> Joblib tSNE object")
        joblib.dump(model, model_path, compress=5)
        print(f"Saved fitted tSNE embedding to {model_path}")

    elif pickle:
        model_path = os.path.join(PROJECT_ROOT, "temp", file_name + '_trained_tSNE.pkl')
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


def save_coordinates(coordinates, folder_name, file_name, reference_data=""):
    """
    Save coordinates to output file in data folder (data/[folder_name]/output_[file_name].csv)

    :param coordinates: coordinates as received from model fitting with index as InChIKey
    :param folder_name: folder name for saving the input file annotated with TSNE coordinates
    :param file_name: name tag of the original data file (e.g. for 'data_market.csv')
    """
    # load input df
    input_df_path = os.path.join(PROJECT_ROOT, "data", folder_name, "input_" + file_name + ".csv")
    df = pd.read_csv(input_df_path)
    df_coordinates = df.merge(coordinates, on='INCHIKEY', how='left')

    if reference_data:
        file_name += "_on_" + reference_data
    # save df, annotated with TSNE coordinates
    output_path = os.path.join(PROJECT_ROOT, "data", folder_name, "output_" + file_name + '.csv')
    df_coordinates.to_csv(output_path, index=True)
    print(f"Saved coordinates to {output_path}")

    
def load_coordinates(folder_name, file_name, reference_data=""):
    if reference_data:
        file_name += f'_on_{reference_data}'
    coordinates_path = os.path.join(PROJECT_ROOT, "data", folder_name, "output_" + file_name + '.csv')
    coordinates = pd.read_csv(coordinates_path)
    print("Coordinates loaded from {}".format(coordinates_path))
    return coordinates

def load_model(file_name, from_zip = False, use_joblib=False):
    """
    Load model from pickle file (default) or from zip file (not implemented)
    :param file_name: name tag of the original data file (e.g. 'data_market' for 'data_market.csv')
    :param from_zip: Load from zip file #todo implement this option
    :return: model object
    """
    if use_joblib:
        model_path_zip = os.path.join(PROJECT_ROOT, "temp", file_name + '_trained_tSNE.zlib')
        model = joblib.load(filename=model_path_zip)
    elif from_zip:
        model_path_zip = os.path.join(PROJECT_ROOT, "models", file_name + '_trained_tSNE.zip')
        model = unzip_and_load(model_path_zip)
    else:
        model_path = os.path.join(PROJECT_ROOT, "temp", file_name + '_trained_tSNE.pkl')
        model = load_pickle(model_path)
    return model

# -----------------------------
# Modeling (for the target space)
# -----------------------------

def transform_tsne_embedding(tsne, df_fingerprints, col_index='INCHIKEY'):
    """
    Transforms target fingerprints to embed into trained t-SNE space
    """
    fps = np.array(df_fingerprints.iloc[:, -1024:].astype('bool'))
    df_embedding = pd.DataFrame(tsne.transform(fps), columns=['TSNE1', 'TSNE2'])
    df_embedding.index = df_fingerprints[col_index]

    return df_embedding


def transform_target(embedding_train,           # todo: code from José - I simplified it below, what do you think?
                     target_space_fingerprints,
                     emb_cache_path="temp/embedding_target_chemicals.npy",
                     df_cache_path="temp/target_chemicals_space.csv"):
    """
    Transforms target fingerprints into the trained TSNE space, caches both the raw embedding and a CSV.
    """
    if os.path.exists(emb_cache_path) and os.path.exists(df_cache_path):
        print(f"[cache] Loading transformed embedding from {emb_cache_path} and {df_cache_path}")
        embedding_target_chemicals = np.load(emb_cache_path, allow_pickle=False)
        target_chemicals_space = pd.read_csv(df_cache_path)
        return embedding_target_chemicals, target_chemicals_space

    embedding_target_chemicals = embedding_train.transform(target_space_fingerprints)
    target_chemicals_space = pd.DataFrame(embedding_target_chemicals, columns=['tsne_v1', 'tsne_v2'])

    np.save(emb_cache_path, embedding_target_chemicals, allow_pickle=False)
    target_chemicals_space.to_csv(df_cache_path, index=False)
    print(f"[cache] Saved transformed embedding to {emb_cache_path}")
    print(f"[cache] Saved target chemicals space CSV to {df_cache_path}")

    print(target_chemicals_space)
    return embedding_target_chemicals, target_chemicals_space

def transform_target(model, fingerprints):
    # Prepare boolean fingerprint array
    fingerprints.dropna(inplace=True)
    X = np.array(fingerprints.drop(columns=['INCHIKEY']).astype('bool'))
    coordinates_target = model.transform(X)
    coordinates_df = pd.DataFrame(coordinates_target, columns=['TSNE1', 'TSNE2'])
    coordinates_df.index = fingerprints['INCHIKEY']
    return coordinates_df

# def build_surrogate_model(folder_name, file_name, df_fingerprints):
#     # target variables: TSNE coordinates
#     df = load_coordinates(folder_name, file_name)
#     Y1 = df['TSNE1']
#     Y2 = df['TSNE2']
#     # fingerprints
#     df_fingerprints.dropna(inplace=True)
#     X = np.array(df_fingerprints.drop(columns=['INCHIKEY']).astype('bool'))
#
#     return model_1, model_2
