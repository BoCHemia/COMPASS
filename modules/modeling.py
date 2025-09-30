import os
import pickle
import numpy as np
import pandas as pd
from openTSNE.tsne import TSNE
# from openTSNE.sklearn import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
from modules.preprocessing import *
import zipfile
import yaml

### Some comments:
# - Xsmall is just a smaller subset of the training data to make some steps faster
# - Caching was implemented by Sylvain. It is useful but we need to rename it.
# - The model is meant to be pickled, not really in the cache sense.
# -  I am still not so clear whether we really want/need separate preprocessing, modeling and visualization modules.


# -----------------------------
# utils? 
# -----------------------------
def ensure_dirs():
    """
    Ensure that the folders temp and output exist, and if not, create them
    """
    os.makedirs(os.path.join("..", "temp"), exist_ok=True)
    os.makedirs(os.path.join("..", "output"), exist_ok=True)


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

def unzip_and_load_pkl(path_to_zipfile):
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
    with open(os.path.join('..', 'config', params+'.yaml'), 'r') as file:
        hyperparameters = yaml.safe_load(file)
    return hyperparameters['hyperparameters']

# -----------------------------
# Modeling
# -----------------------------

def fit_tsne_model(X):
    """
    Fits the TSNE model on the boolean fingerprint array (X) and saves the fitted embedding object.
    If the pickled object exists, it is loaded instead of training again.

    :param X: input matrix of fingerprints
    :return: fitted model object and coordinates of transformed fingerprints
    """

    # Load hyperparameters of t-SNE from config
    hyperparameters_dict = load_configs('tsne_params')

    # Training
    print('--> Start training')
    tsne = TSNE(**hyperparameters_dict)
    model = tsne.fit(X)
    coordinates = pd.DataFrame(model.transform(X))
    # coordinates, model = tsne.fit_transform(X)
    print('Finished training')
    return model, coordinates

def save_model(model, filename, pickle=True, zip=True):
    """
    Save model as pickle to temp and as zipped pickle to output
    @param model: trained tSNE model
    @param filename: name tag of the original data file (e.g. for 'data_market.csv' the filename would be 'data_market')
    @param pickle: save as pickle file, True by default
    @param zip: compress to zip file, True by default
    """
    ensure_dirs()
    model_path = os.path.join("..", "temp", filename + '_trained_tSNE.pkl')
    model_path_zip = os.path.join("..", "temp", filename + '_trained_tSNE.zip')

    # Saving trained tSNE object to temp folder
    if pickle:
        print("--> Pickle tSNE object")
        save_pickle(model, model_path)
        print(f"Saved fitted tSNE embedding to {model_path}")

    # Saving zipped trained tSNE object to output folder
    if zip:
        print('--> Zip tSNE object')
        with zipfile.ZipFile(model_path_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(model_path)
        print(f"Saved fitted tSNE embedding as zip file to {model_path_zip}")

def save_coordinates(coordinates, filename, inchikeys = None):
    """
    Save coordinates to csv file with the columns TSNE1 and TSNE2

     #todo: check for consistency - ideally we would alsways get the same output here for visualization

    :param coordinates: coordinates as received from model fitting
    :param filename: name tag of the original data file (e.g. for 'data_market.csv')
    :param inchikeys: optional - list of inchikeys, for example from original data file
    """
    coordinates_path = os.path.join("..", "temp", filename + '_coordinates_tSNE.csv')
    # coordinates.columns = ['TSNE1', 'TSNE2']
    if inchikeys:
        coordinates.index = inchikeys
    coordinates.to_csv(coordinates_path, index=True)

def load_coordinates(filename):
    coordinates_path = os.path.join("..", "temp", filename + '_coordinates_tSNE.csv')
    coordinates = pd.read_csv(coordinates_path)
    return coordinates

def load_model(filename, from_zip = False):
    """
    Load model from pickle file (default) or from zip file (not implemented)
    :param filename: name tag of the original data file (e.g. 'data_market' for 'data_market.csv')
    :param from_zip: Load from zip file #todo implement this option
    :return: model object
    """
    if from_zip:
        model_path_zip = os.path.join("..", "temp", filename + '_trained_tSNE.zip')
        model = unzip_and_load_pkl(model_path_zip)
    else:
        model_path = os.path.join("..", "temp", filename + '_trained_tSNE.pkl')
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

def transform_target(model, target_X):
    coordinates_target = model.transform(target_X)
    coordinates_df = pd.DataFrame(coordinates_target, columns=['TSNE1', 'TSNE2'])
    return coordinates_df

# -----------------------------
# Visualization
# -----------------------------
def plot_embedding(target_chemicals_space,
                   fig_path='output/target_space_static_test.tif'):
    """
    Plots the simple scatter as in the original script and saves it.
    Skips re-plot if the file already exists.
    """
    if os.path.exists(fig_path):
        print(f"[cache] Figure already exists at {fig_path}; skipping re-plot.")
        return

    ax = sns.scatterplot(data=target_chemicals_space, x='tsne_v1', y='tsne_v2',
                         s=1, alpha=1, edgecolor='black')
    ax.legend(loc='upper left', bbox_to_anchor=(1.00, 0.75), ncol=1)
    plt.axis('off')
    plt.savefig(fig_path, bbox_inches='tight', dpi=1800)
    plt.close()
    print(f"[out] Saved figure to {fig_path}")

def plot_embedding(coordinates, filename, format = '.tif'):
    """
    Plot a coordinates file #todo define what we really need here
    :param coordinates: coordinates dataframe
    :param filename: name tag
    :param format: output format of the plot (e.g., '.png', '.pdf'). '.tif' by default
    """
    print(f"--> Plotting {filename}")
    ax = sns.scatterplot(data=coordinates, x='TSNE1', y='TSNE2',
                         s=1, alpha=1, edgecolor='black')
    fig_path = os.path.join("..", "output", filename + "plot" + format)
    ax.legend(loc='upper left', bbox_to_anchor=(1.00, 0.75), ncol=1)
    plt.axis('off')
    plt.savefig(fig_path, bbox_inches='tight', dpi=1800)
    plt.close()
    print(f"[out] Saved figure to {fig_path}")


# -----------------------------
# Main
# -----------------------------
def main():
    ensure_dirs()

    # 1) Load training set -> boolean array (subset) with caching
    X = load_training_array()

    # 2) Fit (or load) TSNE model
    embedding_train, _ = fit_tsne_model(X) # _ catches the coordinates

    # 3) Load target dataset fingerprints (bool) with caching
    target_space_fingerprints = load_target_space()

    # 4) Transform target fingerprints into TSNE space (cache npy + csv)
    _, target_chemicals_space = transform_target(embedding_train, target_space_fingerprints)

    # 5) Plot and save figure (skip if already there)
    plot_embedding(target_chemicals_space)


if __name__ == "__main__":
    main()
