import os
import time
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import pubchempy as pcp
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.MolStandardize import rdMolStandardize
import pubchempy as pcp
import time


# set project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------
# Data and model loading
# -----------------------------

def prepare_classyfire_data():
    input_path = os.path.join(PROJECT_ROOT, "data")
    classyfire_raw = pd.read_csv(os.path.join(input_path, "ClassyFire", "raw_classyfire.csv"))
    classyfire = classyfire_raw.drop_duplicates() #todo: clean up - his line is not used
    classyfire = classyfire_raw.dropna(subset="Kingdom")

    hierarchy = ["Kingdom", "Superclass", "Class", "Subclass"]

    for i in range(1, len(hierarchy)):
        lower = hierarchy[i]
        higher_levels = hierarchy[:i]

        row_mask = classyfire[higher_levels].eq(classyfire[lower], axis=0).any(axis=1)

        classyfire.loc[row_mask, lower] = np.nan

    classyfire["num_missing"] = classyfire[hierarchy].isna().sum(axis=1)
    classyfire = (classyfire.sort_values("num_missing").drop_duplicates(subset='INCHIKEY', keep="first").drop(columns="num_missing"))

    classyfire.to_csv(os.path.join(input_path, "ClassyFire", "input_classyfire.csv"), index=False)

    return classyfire


def standardize_structures(df):
    
    """
    Function to standardize SMILES and add or complement INCHIKEY column
    
    :param df: Description
    """

    df_std = df.copy()

    if not 'standardized SMILES' in df_std.columns:
        df_std['standardized SMILES'] = standardize_smiles_df(df_std, 'SMILES')

    if not "INCHIKEY" in df_std.columns:
        df_std['INCHIKEY'] = get_inchikeys_df(df_std, 'SMILES')
    elif df_std['INCHIKEY'].isna().any():
        df_std.fillna({'INCHIKEY': get_inchikeys_df(df_std, 'SMILES')}, inplace=True)
        
    return df_std


def calculate_fingerprints(df, radius=2, fpSize=1024, **kwargs):
    """
    Wrapper function to calculate fingerprints
    :param df: input dataframe with standardized SMILES
    :**kwargs: fingerprint calculation parameters in addition to radius and fpSize (defaults provided)
    :return: pandas DataFrame of fingerprints, input df annoated with 'FP_HEX'
    """
    print("Calculating fingerprints ...")
    fps, hex_str =  calculate_descriptors_morgan_df(df, 'standardized SMILES', radius=radius, fpSize=fpSize, **kwargs)
    fingerprints = pd.DataFrame(fps)
    fingerprints['FP_HEX'] = hex_str # use hex str as index
    print("Fingerprints calculated.")

    df['FP_HEX'] = hex_str #add hex_str to coordinates

    return fingerprints, df


def preprocess_data(df, radius=2, fpSize=1024, **kwargs):
    """
    Wrapper function to standardize SMILES, add InChIKeys and calculate fingerprints
    :param df: input dataframe loaded with load_input_file() or provided as user input
    :**kwargs: fingerprint calculation parameters in addition to radius and fpSize (defaults provided)
    :return: pandas DataFrame of fingerprints
    """
    print("Preprocessing data ...")
    
    df = standardize_structures(df) # add standardized SMILES and INCHIKEY columns

    df_fingerprints, df = calculate_fingerprints(df, radius=2, fpSize=1024, **kwargs)
    
    print("Data preprocessed (standardized SMILES, INCHIKEY) and fingerprints calculated.")

    return df_fingerprints, df


def load_input_file(file_name, folder_name):
    """
    Load input file for mapping to reference space
    :param file_name: database name tag
    :param folder_name: "input" database folder name
    """
    print("Loading input file...")
    raw_input_path = os.path.join(PROJECT_ROOT, "data", folder_name, f"input_{file_name}.csv")
    df = pd.read_csv(raw_input_path)
    assert 'SMILES' in df.columns, f"PROBLEM: missing SMILES column in input file under {raw_input_path}"

    return df


def save_fingerprints(fingerprints, folder_name, file_name):
    """
    Save fingerprints to .csv file
    :param fingerprints: fingerprints dataframe
    :param file_name: name tag
    """
    # out_dir = os.path.join(PROJECT_ROOT, "temp", "fingerprints")
    out_dir = os.path.join(PROJECT_ROOT, "data", folder_name)
    os.makedirs(out_dir, exist_ok=True)

    fingerprints_path = os.path.join(out_dir, "fingerprints_" + file_name + '.csv')
    fingerprints.to_csv(fingerprints_path, index=False)
    print("Fingerprints saved to ", fingerprints_path)

def update_df(new_df, folder_name, file_name, target):
    output_path = os.path.join(PROJECT_ROOT, "data", folder_name, target + "_" + file_name + '.csv')
    new_df.to_csv(output_path, index=False)
    print('Saved new dataframe to', output_path)

def save_user_file(user_dataframe, folder_name, file_name):
    """
    Save file input file in user_folder for later use
    :param user_dataframe: typically a file uploaded by the user of the app
    :param folder_name: the user private folder
    :param file_name: file name provided by the user
    """
    # out_dir = os.path.join(PROJECT_ROOT, "temp", "fingerprints")
    out_dir = os.path.join(PROJECT_ROOT, "data", folder_name)
    os.makedirs(out_dir, exist_ok=True)

    user_file_path = os.path.join(out_dir, "input_" + file_name + '.csv')
    user_dataframe.to_csv(user_file_path, index=False)
    print("Target chemicals info saved to ", user_file_path)


def load_fingerprints(folder_name, file_name):
    """

    :param file_name:
    :para folder_name: the folder from which fingerprints should be loaded
    :return:
    """
    fingerprints_df_path = os.path.join(PROJECT_ROOT, "data", folder_name, "fingerprints_" + file_name + '.csv')
    fingerprints = pd.read_csv(fingerprints_df_path)
    return fingerprints

# def load_fingerprints(df): # does not work, but would be nice
#     assert 'FP_HEX' in df.columns, ("FP_HEX is missing from coordinates file. "
#                                                 "Run preprocess data before loading fingerprints")
#     fingerprints = df['FP_HEX'].apply(hex_to_bv)
#
#     fingerprints['FP_HEX'] = df['FP_HEX']
#     return fingerprints
#
#
# def hex_to_bv(hex_str):
#     binary = bytes.fromhex(hex_str)
#     return DataStructs.CreateFromBinaryText(binary)

# -----------------------------
# Structures and features
# -----------------------------

import os
import time
import pandas as pd
import pubchempy as pcp


def get_pubchem_data(df, output_file, id_col, search_columns=[("INCHIKEY", "inchikey"),("CASRN", "name"), ("PREFERRED_NAME", "name")], 
                     resume=True, save_every=50, sleep=0.2):
    """
    Fetches IUPAC name, SMILES, and InChI strings from PubChem for a list of chemicals 
    provided in dataframe with configurable search columns (e.g.InChIKeys, CAS numbers and chemical names), 
    saving regularly to avoid data loss. Allows to resume from last saved compound.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing chemical identifiers.
    output_file : str
        Path to CSV output file.
    id_col : str
        Unique identifier column (for tracking only).
    search_columns : list of tuples
        List defining search hierarchy.
        Each tuple: (df_column_name, pubchem_search_type)
    resume : bool
        If True, resume from existing output_file.
    save_every : int
        Save partial output every N rows.
    sleep : float
        Seconds to sleep between PubChem requests.
    """

    # ------------------------------------------------------------------
    # Resume mode handling
    # ------------------------------------------------------------------
    if resume and os.path.exists(output_file):
        df_out = pd.read_csv(output_file)
        done_set = set(df_out[id_col])
        print(f"Resuming: {len(done_set)} already processed.")
    else:
        df_out = pd.DataFrame(columns=[id_col, 'FoundBy', 'CID', 'PREFERRED_NAME', 'IUPAC', 'INCHI', 'SMILES'])
        done_set = set()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    for idx, row in df.iterrows():

        compound_id = row[id_col]
        if compound_id in done_set:
            continue

        found_data = None
        found_by = None

        # --------------------------------------------------------------
        # Flexible search hierarchy
        # --------------------------------------------------------------
        for df_col, search_type in search_columns:

            search_value = row.get(df_col, None)

            if pd.isna(search_value) or not search_value:
                continue

            try:
                results = pcp.get_compounds(search_value, search_type)
                if results:
                    found_data = results[0]
                    found_by = df_col
                    break
            except Exception:
                pass

        # --------------------------------------------------------------
        # Build result row
        # --------------------------------------------------------------
        if found_data:
            if len(found_data.synonyms)>0:
                compound_name = found_data.synonyms[0] # assuming the first synonym is the best
            else:
                compound_name = found_data.iupac_name

            new_row = {id_col: compound_id, "FoundBy": found_by,
                "CID": found_data.cid,
                "PREFERRED_NAME": compound_name,
                "IUPAC": found_data.iupac_name,
                "INCHI": found_data.inchi,
                "SMILES": found_data.smiles,
            }
        else:
            new_row = {
                id_col: compound_id,
                "FoundBy": None,
                "CID": None,
                "PREFERRED_NAME": None,
                "IUPAC": None,
                "INCHI": None,
                "SMILES": None,
            }

        df_out = pd.concat([df_out, pd.DataFrame([new_row])], ignore_index=True)

        # Periodic save
        if idx % save_every == 0:
            df_out.to_csv(output_file, index=False)
            print(f"Progress saved at index {idx} ({compound_id}).")

        time.sleep(sleep)

    df_out.to_csv(output_file, index=False)
    return df_out


def myMolFromSmiles(smiles):
    """ Function to create mol object from SMILES performing partial sanitization when necessary

    Inputs
    ----------
    smiles : str, mandatory
        SMILES string

    Outputs
    ----------
    mol: object
        RDKit mol object

    """

    smiles = smiles if isinstance(smiles, str) else ""
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:  # try partial sanitization
        try:
            mol = Chem.MolFromSmiles(smiles, sanitize=False)
            mol.UpdatePropertyCache(strict=False)
            Chem.SanitizeMol(mol,
                             Chem.SanitizeFlags.SANITIZE_FINDRADICALS | Chem.SanitizeFlags.SANITIZE_KEKULIZE |
                             Chem.SanitizeFlags.SANITIZE_SETAROMATICITY | Chem.SanitizeFlags.SANITIZE_SETCONJUGATION |
                             Chem.SanitizeFlags.SANITIZE_SETHYBRIDIZATION | Chem.SanitizeFlags.SANITIZE_SYMMRINGS,
                             catchErrors=True)
            print('Partial sanitization: ' + smiles)
        except:
            print('Partial sanitization failed - return none: ' + smiles)

    return mol


def remove_stereochemistry(smiles):
    """ Support function to remove stereochemical information from SMILES

    Inputs
    ----------
    smiles : str, mandatory
        SMILES string

    Outputs
    ----------
    res_smiles: str
        SMILES string without stereochemical information

    """

    mol = myMolFromSmiles(smiles)

    if mol is None:
        res_smiles = ""
    else:
        Chem.RemoveStereochemistry(mol) 
        res_smiles = Chem.MolToSmiles(mol)

    return res_smiles


def create_tautomer_smiles(smiles):
    """ Function creates tautomer SMILES 

    Inputs
    ----------
    smiles : str, mandatory
        SMILES string

    Outputs
    ----------
    tautomer_smiles : str
        tautomer SMILES string

    """

    if myMolFromSmiles(smiles) is None:
        new_mol = None
    else:
        mod_smi = Chem.MolToSmiles(myMolFromSmiles(smiles))
        new_mol = myMolFromSmiles(mod_smi)

    if new_mol is None:  # return empty string if still no mol
        print('No mol: ' + smiles)
        return ''
    else:
        # Tautomerize
        try:
            enumerator = rdMolStandardize.TautomerEnumerator()
            new_mol = enumerator.Canonicalize(new_mol)
        except:
            print('No tautomerization:' + smiles)


        tautomer_smiles = Chem.MolToSmiles(new_mol)
        return tautomer_smiles


def standardize_smiles(smiles, tautomerize=False):
    """ Wrapper function that standardizes SMILES by removing stereochemistry and optional tautomerizing 
    Inputs
    ----------
    smiles : str, mandatory
        The SMILES string

    Outputs
    ----------
    smiles_std: str,
        The standardized SMILES string
    """ 
    if tautomerize:
        smiles = create_tautomer_smiles(smiles)

    smiles_std = remove_stereochemistry(smiles)

    return smiles_std


def standardize_smiles_df(df, col_smiles, **kwargs):
    """ Wrapper function that calculates Morgan fingerprints for a series of SMILES

    Inputs
    ----------
    df : pandas dataframe, mandatory
        The dataframe containing the series of SMILES
    col_smiles: string, mandatory
        The column name containing the SMILES
    **kwargs: optional
        Pass in any arguments taken by rdkit.Chem.rdMolDescriptors.GetMorganFingerprintAsBitVect such as radius and fpSize

    Outputs
    ----------
    series of standardized SMILES
    """
    smiles_df = df[col_smiles].apply(standardize_smiles, **kwargs)
    return smiles_df


def calculate_descriptors_morgan(smiles, **kwargs):
    """ Wrapper function that calculates Morgan fingerprints for a single SMILES

    Inputs
    ----------
    smiles : str, mandatory
        The (standardized) SMILES string
    **kwargs: optional
        Pass in any arguments taken by rdkit.Chem.rdMolDescriptors.GetMorganFingerprintAsBitVect such as radius and fpSize

    Outputs
    ----------
    array of calculated Morgan fingerprints
    """

    mol = myMolFromSmiles(smiles)

    gen = rdFingerprintGenerator.GetMorganGenerator(**kwargs)
    fp = gen.GetFingerprint(mol)
    arr = np.zeros((fp.GetNumBits(),), dtype=float)
    DataStructs.ConvertToNumpyArray(fp, arr)

    if (smiles=="") or (mol is None):
        arr[:] = np.nan

    hex_str = fp.ToBinary().hex()

    return arr, hex_str


def calculate_descriptors_morgan_df(df, col_smiles="standardized SMILES", **kwargs):
    """ Wrapper function that calculates Morgan fingerprints for a series of SMILES

    Inputs
    ----------
    df : pandas dataframe, mandatory
        The dataframe containing the series of (standardized) SMILES
    col_smiles: string, mandatory
        The column name containing the (standardized) SMILES
    **kwargs: optional
        Pass in any arguments taken by rdkit.Chem.rdMolDescriptors.GetMorganFingerprintAsBitVect such as radius and fpSize

    Outputs
    ----------
    dataframe of calculated Morgan fingerprints
    """

    d = df[col_smiles].apply(calculate_descriptors_morgan, **kwargs)
    df = pd.DataFrame.from_records(d)
    matrix = pd.DataFrame.from_records(df[0])
    hex = df[1].values
    return matrix, hex


def get_inchikeys(smiles):

    mol = myMolFromSmiles(smiles)

    if pd.isna(smiles) or (smiles == "") or (mol is None):
        return np.nan
    
    return Chem.MolToInchiKey(mol)


def get_inchikeys_df(df, col_smiles):
    inchikey_df = df[col_smiles].apply(get_inchikeys)
    inchikey_df = inchikey_df.replace("", np.nan) # hack to avoid coersion to empty strings

    return inchikey_df



# -----------------------------
# Retrieve data from Zenodo
# -----------------------------
import streamlit as st
import requests
import hashlib
import zipfile  

def _md5_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def get_demo_assets_root(zip_url: str, expected_md5: str | None = None) -> str:
    """
    Returns local path to extracted demo_assets folder.
    Downloads/extracts only if needed. Uses disk cache (not RAM).
    """
    cache_base = Path.home() / ".cache" / "compass_demo_assets"
    cache_base.mkdir(parents=True, exist_ok=True)

    zip_path = cache_base / "demo_assets.zip"
    extract_root = cache_base / "demo_assets"
    marker = cache_base / ".extracted_ok"

    # Download if missing
    if not zip_path.exists():
        with st.spinner("Downloading demo assets (first run only)..."):
            r = requests.get(zip_url, stream=True, timeout=120)
            r.raise_for_status()
            with zip_path.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

    # Verify checksum (recommended)
    if expected_md5:
        actual = _md5_file(zip_path)
        print(actual)
        if actual.lower() != expected_md5.lower():
            # If corrupted/partial download, delete and fail loudly
            zip_path.unlink(missing_ok=True)
            marker.unlink(missing_ok=True)
            raise RuntimeError(f"MD5 mismatch for demo_assets.zip: expected {expected_md5}, got {actual}")

    # Extract if needed
    if not marker.exists() or not extract_root.exists():
        with st.spinner("Extracting demo assets (first run only)..."):
            # (optional) remove partial extraction
            if extract_root.exists():
                # keep it simple; you can delete recursively if needed
                pass

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(cache_base)

            if not extract_root.exists():
                raise RuntimeError("Expected 'demo_assets/' folder not found after extraction. Check zip structure.")

            marker.write_text("ok")

    return str(extract_root)
